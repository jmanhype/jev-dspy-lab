"""Leakage-safe calibration refitting and reliability reporting."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from jev_dspy_lab.metrics import Decision, confidence_for_decision


class EmptyCalibrationTargets(ValueError):
    """Calibration was requested with no training decisions."""


class DegenerateCalibrationTargets(ValueError):
    """Training outcomes contain only one class and cannot fit Platt scaling."""


class CalibrationFingerprintMismatch(ValueError):
    """A calibration artifact cannot silently replay changed inputs or models."""


_DETERMINISTIC_DIGITS = 12


def _quantize(value: float) -> float:
    """Normalize boundary floating-point arithmetic for portable report bytes."""

    result = round(float(value), _DETERMINISTIC_DIGITS)
    if not math.isfinite(result):
        raise ValueError("Calibration produced a non-finite value")
    return result


@dataclass(frozen=True, slots=True)
class PlattParameters:
    a: float
    b: float


@dataclass(frozen=True, slots=True)
class CalibrationArtifact:
    schema_version: str
    method: str
    parameters: PlattParameters
    train_ids: tuple[str, ...]
    held_out_ids: tuple[str, ...]
    input_hashes: Mapping[str, str]
    model_fingerprint: str
    input_fingerprint: str
    selected_threshold: float = 0.8
    bin_count: int = 10
    field: str = "unspecified"
    split_seed: int | None = None
    train_fraction: float | None = None
    returned_models: tuple[str, ...] = ()

    @staticmethod
    def _digest(payload: Mapping[str, object]) -> str:
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
        return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def fingerprint_for_split(
        train_ids: Iterable[str],
        held_out_ids: Iterable[str],
        input_hashes: Mapping[str, str],
    ) -> str:
        return CalibrationArtifact._digest(
            {
                "train_ids": sorted(train_ids),
                "held_out_ids": sorted(held_out_ids),
                "input_hashes": dict(sorted(input_hashes.items())),
            }
        )

    def validate_replay(
        self,
        *,
        input_hashes: Mapping[str, str],
        model_fingerprint: str,
        train_ids: Sequence[str] | None = None,
        held_out_ids: Sequence[str] | None = None,
    ) -> None:
        if not input_hashes or not model_fingerprint or model_fingerprint == "unspecified":
            raise CalibrationFingerprintMismatch("Calibration provenance is incomplete")
        if any(not isinstance(value, str) or not value for value in input_hashes.values()):
            raise CalibrationFingerprintMismatch("Calibration input hashes must be non-empty")
        train = tuple(self.train_ids if train_ids is None else train_ids)
        held_out = tuple(self.held_out_ids if held_out_ids is None else held_out_ids)
        expected_ids = set(input_hashes)
        if (
            not train
            or not held_out
            or len(expected_ids) != len(train) + len(held_out)
            or len(set(train)) != len(train)
            or len(set(held_out)) != len(held_out)
            or set(train) & set(held_out)
            or expected_ids != set(train) | set(held_out)
        ):
            raise CalibrationFingerprintMismatch(
                "Calibration train/held-out membership mismatch; refit calibration"
            )
        fingerprint = self.fingerprint_for_split(train, held_out, input_hashes)
        if fingerprint != self.input_fingerprint:
            raise CalibrationFingerprintMismatch(
                "Input fingerprint mismatch; refit calibration for the new distribution"
            )
        if model_fingerprint != self.model_fingerprint:
            raise CalibrationFingerprintMismatch(
                "Model fingerprint mismatch; refit calibration before replay"
            )

    def transform(self, probability: float) -> float:
        value = _validate_probability(probability, "confidence to calibrate")
        return _sigmoid(self.parameters.a * value + self.parameters.b)


@dataclass(frozen=True, slots=True)
class CalibrationMetrics:
    total: int
    answered: int
    abstained: int
    correct: int
    incorrect: int
    log_loss: float
    brier: float
    ece: float
    selective_risk: float
    coverage: float


@dataclass(frozen=True, slots=True)
class ReliabilityBin:
    lower_bound: float
    upper_bound: float
    count: int
    mean_confidence: float
    empirical_accuracy: float
    absolute_gap: float
    weighted_ece_contribution: float


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    raw: CalibrationMetrics
    calibrated: CalibrationMetrics
    raw_reliability: tuple[ReliabilityBin, ...]
    calibrated_reliability: tuple[ReliabilityBin, ...]
    artifact: CalibrationArtifact


def _validate_probability(value: float, label: str) -> float:
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ValueError(f"{label} must be a finite probability between 0 and 1")
    return result


def _validate_decisions(decisions: Sequence[Decision]) -> tuple[list[Decision], list[float]]:
    if not decisions:
        raise EmptyCalibrationTargets("At least one training decision is required")
    items = list(decisions)
    probabilities = [
        _validate_probability(confidence_for_decision(item), f"confidence for {item.case_id!r}")
        for item in items
    ]
    ids = [item.case_id for item in items]
    if len(set(ids)) != len(ids):
        duplicate = next(value for value in ids if ids.count(value) > 1)
        raise ValueError(f"Duplicate calibration case_id: {duplicate!r}")
    return items, probabilities


def _validated_input_hashes(
    decisions: Sequence[Decision],
    input_hashes: Mapping[str, str] | None,
) -> dict[str, str]:
    if input_hashes is None or not input_hashes:
        raise ValueError("Calibration requires a non-empty input_hashes mapping")
    hashes = dict(input_hashes)
    expected_ids = {item.case_id for item in decisions}
    if set(hashes) != expected_ids:
        mismatched = expected_ids.symmetric_difference(hashes)
        raise ValueError(f"Input hashes must match decision IDs exactly: {sorted(mismatched)}")
    for case_id, value in hashes.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"Input hash for {case_id!r} must be a non-empty string")
    return hashes


def split_decisions(
    decisions: Sequence[Decision],
    *,
    train_fraction: float,
    seed: int,
) -> tuple[tuple[Decision, ...], tuple[Decision, ...]]:
    """Split unique decisions deterministically into disjoint complete sets."""

    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between zero and one")
    items, _ = _validate_decisions(decisions)
    shuffled = list(items)
    random.Random(seed).shuffle(shuffled)
    train_count = max(1, min(len(shuffled) - 1, int(len(shuffled) * train_fraction)))
    return tuple(shuffled[:train_count]), tuple(shuffled[train_count:])


def _sigmoid(value: float) -> float:
    if value >= 0:
        return _quantize(1.0 / (1.0 + math.exp(-value)))
    exponential = math.exp(value)
    return _quantize(exponential / (1.0 + exponential))


def _log_loss_probability(value: float) -> float:
    return min(1.0 - 1e-15, max(1e-15, value))


def _validate_artifact(artifact: CalibrationArtifact) -> None:
    if artifact.schema_version != "calibration.v1" or artifact.method != "platt":
        raise ValueError("Calibration artifact must use calibration.v1 Platt scaling")
    if not 1 <= artifact.bin_count:
        raise ValueError("Calibration artifact bin_count must be positive")
    _validate_probability(artifact.selected_threshold, "selected threshold")
    if not all(math.isfinite(value) for value in (artifact.parameters.a, artifact.parameters.b)):
        raise ValueError("Calibration parameters must be finite")
    artifact.validate_replay(
        input_hashes=artifact.input_hashes, model_fingerprint=artifact.model_fingerprint
    )


def fit_platt_scaling(
    decisions: Sequence[Decision],
    *,
    input_hashes: Mapping[str, str] | None = None,
    model_fingerprint: str | None = None,
) -> CalibrationArtifact:
    """Fit a two-parameter logistic calibration on training correctness only."""

    items, probabilities = _validate_decisions(decisions)
    targets = [float(item.predicted == item.expected) for item in items]
    if len(set(targets)) != 2:
        raise DegenerateCalibrationTargets("training targets need correct and incorrect")

    mean_target = sum(targets) / len(targets)
    odds = max(mean_target, 1e-6) / max(1.0 - mean_target, 1e-6)
    a, b = 0.0, math.log(odds)
    ridge = 1e-4
    for _ in range(5_000):
        predictions = [_sigmoid(a * probability + b) for probability in probabilities]
        errors = [
            prediction - target for prediction, target in zip(predictions, targets, strict=True)
        ]
        gradient_a = sum(
            error * probability for error, probability in zip(errors, probabilities, strict=True)
        ) / len(items)
        gradient_a += ridge * a
        gradient_b = sum(errors) / len(items) + ridge * b
        a = _quantize(min(20.0, max(-20.0, a - gradient_a)))
        b = _quantize(min(20.0, max(-20.0, b - gradient_b)))

    if not math.isfinite(a) or not math.isfinite(b) or a < 0:
        a = 0.0
        b = math.log(mean_target / (1.0 - mean_target))

    hashes = _validated_input_hashes(items, input_hashes)
    if not isinstance(model_fingerprint, str) or not model_fingerprint:
        raise ValueError("Calibration requires a non-empty model_fingerprint")
    train_ids = tuple(item.case_id for item in items)
    fingerprint = CalibrationArtifact.fingerprint_for_split(train_ids, (), hashes)
    return CalibrationArtifact(
        "calibration.v1",
        "platt",
        PlattParameters(_quantize(a), _quantize(b)),
        train_ids,
        (),
        hashes,
        model_fingerprint,
        fingerprint,
    )


def _calibration_metrics(
    decisions: Sequence[Decision],
    *,
    threshold: float,
    bins: int,
    confidences: Sequence[float],
) -> tuple[CalibrationMetrics, tuple[ReliabilityBin, ...]]:
    items = list(decisions)
    if not items:
        raise ValueError("At least one held-out decision is required")
    rows: list[tuple[float, bool, bool]] = []
    for item, raw_confidence in zip(items, confidences, strict=True):
        probability = _quantize(_validate_probability(raw_confidence, "calibrated probability"))
        accepted = probability >= threshold
        correct = item.predicted == item.expected
        rows.append((probability, accepted, correct))

    answered = [row for row in rows if row[1]]
    if not answered:
        raise ValueError("The calibration threshold abstained from every held-out decision")
    log_loss = _quantize(
        -sum(
            math.log(_log_loss_probability(probability if correct else 1.0 - probability))
            for probability, _, correct in answered
        )
        / len(answered)
    )
    brier = _quantize(
        sum((probability - float(correct)) ** 2 for probability, _, correct in answered)
        / len(answered)
    )

    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for probability, _, correct in answered:
        index = min(bins - 1, int(probability * bins))
        buckets[index].append((probability, correct))
    reliability: list[ReliabilityBin] = []
    ece = 0.0
    for index, bucket in enumerate(buckets):
        count = len(bucket)
        if count:
            mean_confidence = _quantize(sum(value for value, _ in bucket) / count)
            empirical_accuracy = _quantize(sum(correct for _, correct in bucket) / count)
            gap = _quantize(abs(mean_confidence - empirical_accuracy))
            contribution = _quantize(gap * count / len(answered))
        else:
            mean_confidence = empirical_accuracy = gap = contribution = 0.0
        values = (
            index / bins,
            (index + 1) / bins,
            count,
            mean_confidence,
            empirical_accuracy,
            gap,
            contribution,
        )
        reliability.append(ReliabilityBin(*values))
        ece = _quantize(ece + contribution)

    incorrect = sum(not correct for _, _, correct in answered)
    metrics = (
        len(rows),
        len(answered),
        len(rows) - len(answered),
        len(answered) - incorrect,
        incorrect,
        _quantize(log_loss),
        _quantize(brier),
        _quantize(ece),
        _quantize(incorrect / len(answered)),
        _quantize(len(answered) / len(rows)),
    )
    return CalibrationMetrics(*metrics), tuple(reliability)


def evaluate_calibration(
    train: Sequence[Decision],
    held_out: Sequence[Decision],
    *,
    bins: int,
    threshold: float,
    input_hashes: Mapping[str, str],
    model_fingerprint: str,
    field: str | None = None,
    split_seed: int | None = None,
    train_fraction: float | None = None,
    returned_models: Sequence[str] | None = None,
) -> CalibrationReport:
    """Fit on train only and compare raw/calibrated behavior on held_out only."""

    if not 1 <= bins:
        raise ValueError("bins must be positive")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    if not held_out:
        raise ValueError("At least one held-out decision is required")
    train_items, _ = _validate_decisions(train)
    held_out_items, _ = _validate_decisions(held_out)
    train_ids = {item.case_id for item in train_items}
    held_out_ids = {item.case_id for item in held_out_items}
    if train_ids & held_out_ids:
        overlap = sorted(train_ids & held_out_ids)
        raise ValueError(f"Calibration train and held-out IDs overlap: {overlap}")
    hashes = _validated_input_hashes([*train_items, *held_out_items], input_hashes)
    metadata: dict[str, object] = {}
    if field is not None:
        if not field:
            raise ValueError("Calibration field provenance must be non-empty")
        metadata["field"] = field
    if split_seed is not None:
        if isinstance(split_seed, bool) or not isinstance(split_seed, int):
            raise ValueError("Calibration split_seed must be an integer")
        metadata["split_seed"] = split_seed
    if train_fraction is not None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("Calibration train_fraction must be between zero and one")
        metadata["train_fraction"] = train_fraction
    if returned_models is not None:
        models = tuple(sorted(set(returned_models)))
        if not models or any(not isinstance(model, str) or not model for model in models):
            raise ValueError("Calibration returned_models provenance must be non-empty strings")
        metadata["returned_models"] = models
    artifact = fit_platt_scaling(
        train,
        input_hashes={item.case_id: hashes[item.case_id] for item in train_items},
        model_fingerprint=model_fingerprint,
    )
    artifact = replace(
        artifact,
        train_ids=tuple(item.case_id for item in train),
        held_out_ids=tuple(item.case_id for item in held_out),
        input_hashes=hashes,
        input_fingerprint=CalibrationArtifact.fingerprint_for_split(
            artifact.train_ids, tuple(item.case_id for item in held_out), hashes
        ),
        selected_threshold=threshold,
        bin_count=bins,
        **metadata,
    )
    _validate_artifact(artifact)
    raw_confidences = [confidence_for_decision(item) for item in held_out]
    calibrated, calibrated_reliability = _calibration_metrics(
        held_out,
        threshold=threshold,
        bins=bins,
        confidences=[artifact.transform(value) for value in raw_confidences],
    )
    raw, raw_reliability = _calibration_metrics(
        held_out, threshold=threshold, bins=bins, confidences=raw_confidences
    )
    return CalibrationReport(raw, calibrated, raw_reliability, calibrated_reliability, artifact)


def dump_calibration_report(report: CalibrationReport, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def load_calibration_report(path: str | Path) -> CalibrationReport:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    artifact_payload = payload["artifact"]
    if artifact_payload.get("schema_version") != "calibration.v1":
        raise ValueError(f"Unsupported schema: {artifact_payload.get('schema_version')!r}")
    artifact_payload["parameters"] = PlattParameters(**artifact_payload["parameters"])
    artifact_payload["input_hashes"] = dict(artifact_payload["input_hashes"])
    artifact_payload["train_ids"] = tuple(artifact_payload["train_ids"])
    artifact_payload["held_out_ids"] = tuple(artifact_payload["held_out_ids"])
    artifact_payload["returned_models"] = tuple(artifact_payload.get("returned_models", ()))
    artifact = CalibrationArtifact(**artifact_payload)
    for key in ("raw_reliability", "calibrated_reliability"):
        payload[key] = tuple(ReliabilityBin(**row) for row in payload[key])
    report = CalibrationReport(
        CalibrationMetrics(**payload["raw"]),
        CalibrationMetrics(**payload["calibrated"]),
        payload["raw_reliability"],
        payload["calibrated_reliability"],
        artifact,
    )
    _validate_artifact(report.artifact)
    return report
