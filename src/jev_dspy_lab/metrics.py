"""Decision calibration and selective-risk metrics."""

from __future__ import annotations

import math
import random
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

DecisionKind = Literal["noul", "choice", "score"]


@dataclass(frozen=True)
class Decision:
    """One typed Jev decision with enough metadata to evaluate calibration."""

    case_id: str
    field: str
    kind: DecisionKind
    predicted: Any
    expected: Any
    probability: float | None = None
    probabilities: Mapping[Any, float] | None = None
    confidence: float | None = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class GatedDecision:
    """A decision after applying a confidence threshold."""

    case_id: str
    field: str
    kind: DecisionKind
    predicted: Any
    expected: Any
    confidence: float
    abstained: bool
    probability: float | None = None
    probabilities: Mapping[Any, float] | None = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class DecisionMetrics:
    """Aggregate quality, calibration, coverage, timing, and cost statistics."""

    total: int
    answered: int
    abstained: int
    correct: int
    incorrect: int
    accuracy: float
    selective_risk: float
    coverage: float
    abstain_rate: float
    brier: float
    ece: float
    latency_ms_p50: float
    latency_ms_p95: float
    average_cost_usd: float
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    average_input_tokens: float
    average_output_tokens: float
    accuracy_ci95: tuple[float, float]
    selective_risk_ci95: tuple[float, float]


@dataclass(frozen=True)
class ThresholdPoint:
    """Selective-prediction statistics at one confidence gate."""

    threshold: float
    answered: int
    abstained: int
    coverage: float
    correct: int
    incorrect: int
    accuracy: float | None
    selective_risk: float | None


def _coerce_decision(value: Decision | Mapping[str, Any]) -> Decision:
    if isinstance(value, Decision):
        return value
    return Decision(**dict(value))


def confidence_for_decision(decision: Decision | Mapping[str, Any]) -> float:
    """Return the confidence score used by the gate.

    Choice uses the probability assigned to the selected option. Noul uses the
    probability that the answer is true. Score falls back to the model-reported
    confidence when present.
    """

    item = _coerce_decision(decision)
    if item.kind == "choice":
        if item.probabilities is None:
            raise ValueError(f"Choice decision {item.case_id!r} must include probabilities")
        if item.predicted not in item.probabilities:
            raise ValueError(
                f"Choice decision {item.case_id!r} has no probability for {item.predicted!r}"
            )
        confidence = float(item.probabilities[item.predicted])
    elif item.kind == "noul":
        if item.probability is None:
            raise ValueError(f"Noul decision {item.case_id!r} must include probability")
        confidence = float(item.probability)
    else:
        if item.confidence is None:
            raise ValueError(f"Score decision {item.case_id!r} must include confidence")
        confidence = float(item.confidence)

    _validate_probability(confidence, f"confidence for {item.case_id!r}")
    return confidence


def gate_decision(
    decision: Decision | Mapping[str, Any],
    *,
    threshold: float,
) -> GatedDecision:
    """Apply a confidence threshold and fail closed by abstaining when uncertain."""

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")

    item = _coerce_decision(decision)
    confidence = confidence_for_decision(item)
    abstained = confidence < threshold
    return GatedDecision(
        case_id=item.case_id,
        field=item.field,
        kind=item.kind,
        predicted=None if abstained else item.predicted,
        expected=item.expected,
        confidence=confidence,
        abstained=abstained,
        probability=item.probability,
        probabilities=item.probabilities,
        latency_ms=item.latency_ms,
        cost_usd=item.cost_usd,
        input_tokens=item.input_tokens,
        output_tokens=item.output_tokens,
    )


def evaluate_decisions(
    decisions: Iterable[Decision | Mapping[str, Any]],
    *,
    threshold: float,
    bootstrap_samples: int = 1_000,
    seed: int = 0,
    calibration_bins: int = 10,
) -> DecisionMetrics:
    """Compute decision metrics after confidence gating.

    Accuracy and selective risk are conditional on answered decisions. Coverage
    and abstention rate describe the full population. Brier score and expected
    calibration error are computed over answered decisions only.
    """

    items = _validated_decisions(
        decisions,
        bootstrap_samples=bootstrap_samples,
        calibration_bins=calibration_bins,
    )
    gated = [gate_decision(item, threshold=threshold) for item in items]
    _validate_gated_inputs(items)
    answered = [decision for decision in gated if not decision.abstained]
    if not answered:
        raise ValueError("The confidence threshold abstained from every decision")

    correct = [decision.predicted == decision.expected for decision in answered]
    accuracy = sum(correct) / len(answered)
    selective_risk = sum(not value for value in correct) / len(answered)
    brier = _brier_score(answered)
    ece = _expected_calibration_error(answered, bins=calibration_bins)
    latencies = sorted(decision.latency_ms for decision in gated)
    costs = [decision.cost_usd for decision in gated]
    input_tokens = [decision.input_tokens for decision in gated]
    output_tokens = [decision.output_tokens for decision in gated]

    return DecisionMetrics(
        total=len(gated),
        answered=len(answered),
        abstained=len(gated) - len(answered),
        correct=sum(correct),
        incorrect=len(answered) - sum(correct),
        accuracy=accuracy,
        selective_risk=selective_risk,
        coverage=len(answered) / len(gated),
        abstain_rate=(len(gated) - len(answered)) / len(gated),
        brier=brier,
        ece=ece,
        latency_ms_p50=_percentile(latencies, 0.5),
        latency_ms_p95=_percentile(latencies, 0.95),
        average_cost_usd=sum(costs) / len(costs),
        total_cost_usd=sum(costs),
        total_input_tokens=sum(input_tokens),
        total_output_tokens=sum(output_tokens),
        average_input_tokens=sum(input_tokens) / len(input_tokens),
        average_output_tokens=sum(output_tokens) / len(output_tokens),
        accuracy_ci95=_bootstrap_binary_rate(correct, bootstrap_samples, seed),
        selective_risk_ci95=_bootstrap_binary_rate(
            [not value for value in correct], bootstrap_samples, seed + 1
        ),
    )


def evaluate_threshold_sweep(
    decisions: Iterable[Decision | Mapping[str, Any]],
    *,
    thresholds: Sequence[float] = tuple(index / 10 for index in range(11)),
) -> tuple[ThresholdPoint, ...]:
    """Return sorted selective-prediction statistics for each confidence gate.

    Accuracy and selective risk are conditional on answered decisions. A gate
    that abstains from every decision is retained with ``None`` rates rather
    than being silently dropped.
    """

    items = _validated_decisions(decisions)
    valid_thresholds = _validated_thresholds(thresholds)
    _validate_gated_inputs(items)
    confidences = [confidence_for_decision(item) for item in items]
    return tuple(_threshold_point(items, confidences, threshold) for threshold in valid_thresholds)


def _validated_decisions(
    decisions: Iterable[Decision | Mapping[str, Any]],
    *,
    bootstrap_samples: int | None = None,
    calibration_bins: int | None = None,
) -> list[Decision]:
    items = [_coerce_decision(decision) for decision in decisions]
    if not items:
        raise ValueError("At least one decision is required")
    if bootstrap_samples is not None and bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be positive")
    if calibration_bins is not None and calibration_bins < 1:
        raise ValueError("calibration_bins must be positive")
    return items


def _validated_thresholds(thresholds: Sequence[float]) -> list[float]:
    if not thresholds:
        raise ValueError("At least one threshold is required")

    valid_thresholds: list[float] = []
    for threshold in thresholds:
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
            raise ValueError("threshold must be between 0 and 1")
        value = float(threshold)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        valid_thresholds.append(value)
    if len(set(valid_thresholds)) != len(valid_thresholds):
        raise ValueError("thresholds must be unique")
    return sorted(valid_thresholds)


def _threshold_point(
    items: Sequence[Decision],
    confidences: Sequence[float],
    threshold: float,
) -> ThresholdPoint:
    answered = [
        item for item, confidence in zip(items, confidences, strict=True) if confidence >= threshold
    ]
    correct_count = sum(item.predicted == item.expected for item in answered)
    incorrect_count = len(answered) - correct_count
    return ThresholdPoint(
        threshold=threshold,
        answered=len(answered),
        abstained=len(items) - len(answered),
        coverage=len(answered) / len(items),
        correct=correct_count,
        incorrect=incorrect_count,
        accuracy=None if not answered else correct_count / len(answered),
        selective_risk=None if not answered else incorrect_count / len(answered),
    )


def _validate_gated_inputs(items: Sequence[Decision]) -> None:
    for item in items:
        if item.kind == "noul" and item.probability is not None:
            _validate_probability(float(item.probability), f"probability for {item.case_id!r}")
        if item.probabilities is not None:
            total_probability = sum(
                float(probability) for probability in item.probabilities.values()
            )
            if not math.isclose(total_probability, 1.0, rel_tol=0.0, abs_tol=1e-4):
                raise ValueError(
                    f"Choice probabilities for {item.case_id!r} must sum to 1 "
                    f"(received {total_probability:.6f})"
                )
            for option, probability in item.probabilities.items():
                _validate_probability(
                    float(probability), f"probability for {item.case_id!r}/{option!r}"
                )


def _validate_probability(value: float, label: str) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be a finite probability between 0 and 1")


def _brier_score(decisions: Sequence[GatedDecision]) -> float:
    scores: list[float] = []
    for decision in decisions:
        if decision.kind == "choice":
            if decision.probabilities is None:
                raise ValueError(f"Choice decision {decision.case_id!r} is missing probabilities")
            target = {decision.expected: 1.0}
            options = set(decision.probabilities) | set(target)
            score = sum(
                (float(decision.probabilities.get(option, 0.0)) - target.get(option, 0.0)) ** 2
                for option in options
            )
        elif decision.kind == "noul":
            if decision.probability is None:
                raise ValueError(f"Noul decision {decision.case_id!r} is missing probability")
            target = 1.0 if decision.expected is True else 0.0
            score = (float(decision.probability) - target) ** 2
        else:
            try:
                score = (float(decision.predicted) - float(decision.expected)) ** 2
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Score decision {decision.case_id!r} must have numeric "
                    "predicted and expected values"
                ) from exc
        scores.append(score)
    return sum(scores) / len(scores)


def _expected_calibration_error(decisions: Sequence[GatedDecision], *, bins: int) -> float:
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for decision in decisions:
        index = min(bins - 1, int(decision.confidence * bins))
        buckets[index].append((decision.confidence, decision.predicted == decision.expected))

    total = len(decisions)
    error = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        average_confidence = sum(confidence for confidence, _ in bucket) / len(bucket)
        accuracy = sum(correct for _, correct in bucket) / len(bucket)
        error += len(bucket) / total * abs(average_confidence - accuracy)
    return error


def _bootstrap_binary_rate(
    values: Sequence[bool],
    samples: int,
    seed: int,
) -> tuple[float, float]:
    rng = random.Random(seed)
    rates: list[float] = []
    for _ in range(samples):
        sample = [
            values[index] for index in (rng.randrange(len(values)) for _ in range(len(values)))
        ]
        rates.append(sum(sample) / len(sample))
    rates.sort()
    lower = _percentile(rates, 0.025)
    upper = _percentile(rates, 0.975)
    return lower, upper


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])
