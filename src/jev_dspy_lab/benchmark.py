"""Offline benchmark runner for replayed Jev/TypeSafe decisions."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jev_dspy_lab.metrics import Decision, DecisionMetrics, evaluate_decisions, gate_decision
from jev_dspy_lab.replay import canonical_request_hash, load_replay_index

TYPESAFE_INPUT_USD_PER_MILLION = 0.042


@dataclass(frozen=True)
class BenchmarkDecision:
    """One confidence-gated decision with replay provenance."""

    request_hash: str
    case_id: str
    field: str
    kind: str
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
class BenchmarkReport:
    """The complete result of a deterministic benchmark run."""

    field: str
    threshold: float
    metrics: DecisionMetrics
    gated_decisions: tuple[BenchmarkDecision, ...]
    output_dir: Path


def run_benchmark(
    *,
    dataset: str | Path,
    responses: str | Path,
    output_dir: str | Path,
    field: str,
    threshold: float,
    bootstrap_samples: int = 1_000,
    seed: int = 0,
    noul_true_threshold: float = 0.5,
) -> BenchmarkReport:
    """Evaluate a JSONL dataset against hash-matched TypeSafe response fixtures."""

    cases = _load_jsonl(Path(dataset))
    _validate_cases(cases, field=field)
    replay_index = load_replay_index(Path(responses))
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    decisions: list[Decision] = []
    request_hashes: list[str] = []
    for case in cases:
        request_hash = canonical_request_hash(case["request"])
        request_hashes.append(request_hash)
        if request_hash not in replay_index:
            raise KeyError(
                f"No replay response for case {case['case_id']!r}; request hash {request_hash}"
            )
        decisions.append(
            Decision(
                **_decision_from_response(
                    case=case,
                    response=replay_index[request_hash],
                    request_hash=request_hash,
                    field=field,
                    noul_true_threshold=noul_true_threshold,
                )
            )
        )

    metrics = evaluate_decisions(
        decisions,
        threshold=threshold,
        bootstrap_samples=bootstrap_samples,
        seed=seed,
    )
    gated = tuple(gate_decision(decision, threshold=threshold) for decision in decisions)
    benchmark_decisions = tuple(
        BenchmarkDecision(
            request_hash=request_hash,
            case_id=decision.case_id,
            field=decision.field,
            kind=decision.kind,
            predicted=gated_decision.predicted,
            expected=decision.expected,
            confidence=gated_decision.confidence,
            abstained=gated_decision.abstained,
            probability=decision.probability,
            probabilities=decision.probabilities,
            latency_ms=decision.latency_ms,
            cost_usd=decision.cost_usd,
            input_tokens=decision.input_tokens,
            output_tokens=decision.output_tokens,
        )
        for request_hash, decision, gated_decision in zip(
            request_hashes, decisions, gated, strict=True
        )
    )

    report = BenchmarkReport(
        field=field,
        threshold=threshold,
        metrics=metrics,
        gated_decisions=benchmark_decisions,
        output_dir=output,
    )
    _write_report(report)
    return report


def _decision_from_response(
    *,
    case: Mapping[str, Any],
    response: Mapping[str, Any],
    request_hash: str,
    field: str,
    noul_true_threshold: float,
) -> dict[str, Any]:
    answers = response.get("answers", {})
    if field not in answers:
        raise ValueError(f"Case {case['case_id']!r} response has no answer for field {field!r}")
    answer = answers[field]
    usage = response.get("usage", {})
    input_tokens = int(usage.get("input_tokens", 0))
    output_tokens = int(usage.get("output_tokens", 0))
    latency_ms = float(response.get("latency_ms", 0.0))
    expected = case.get("expected", {}).get(field)

    if "noul" in answer:
        probability = float(answer["noul"])
        decision = {
            "case_id": str(case["case_id"]),
            "field": field,
            "kind": "noul",
            "predicted": probability >= noul_true_threshold,
            "expected": expected,
            "probability": probability,
            "probabilities": None,
            "latency_ms": latency_ms,
            "cost_usd": _modeled_cost(input_tokens, output_tokens),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    elif "choice" in answer:
        decision = {
            "case_id": str(case["case_id"]),
            "field": field,
            "kind": "choice",
            "predicted": answer["choice"],
            "expected": expected,
            "probability": None,
            "probabilities": answer.get("probabilities", {}),
            "latency_ms": latency_ms,
            "cost_usd": _modeled_cost(input_tokens, output_tokens),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    elif "score" in answer:
        decision = {
            "case_id": str(case["case_id"]),
            "field": field,
            "kind": "score",
            "predicted": float(answer["score"]),
            "expected": expected,
            "probability": None,
            "probabilities": answer.get("probabilities", {}),
            "confidence": float(answer.get("confidence", 0.0)),
            "latency_ms": latency_ms,
            "cost_usd": _modeled_cost(input_tokens, output_tokens),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    else:
        raise ValueError(
            f"Unsupported answer shape for {request_hash}; expected noul, choice, or score"
        )
    return decision


def _modeled_cost(input_tokens: int, output_tokens: int) -> float:
    # TypeSafe's public input price was not available when this fixture was
    # captured. The supplied assumption is explicit and replaceable here.
    return input_tokens * TYPESAFE_INPUT_USD_PER_MILLION / 1_000_000


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            rows.append(row)
    if not rows:
        raise ValueError(f"Dataset is empty: {path}")
    return rows


def _validate_cases(cases: list[dict[str, Any]], *, field: str) -> None:
    case_ids: set[str] = set()
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("Every dataset row requires a non-empty string case_id")
        if case_id in case_ids:
            raise ValueError(f"Dataset contains duplicate case_id: {case_id}")
        case_ids.add(case_id)
        if not isinstance(case.get("request"), dict):
            raise ValueError(f"Case {case_id!r} must include a request object")
        expected = case.get("expected")
        if not isinstance(expected, dict) or field not in expected:
            raise ValueError(f"Case {case_id!r} is missing expected output for field {field!r}")


def _write_report(report: BenchmarkReport) -> None:
    payload = {
        "field": report.field,
        "threshold": report.threshold,
        "metrics": asdict(report.metrics),
        "gated_decisions": [asdict(decision) for decision in report.gated_decisions],
    }
    report.output_dir.joinpath("benchmark.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report.output_dir.joinpath("benchmark.md").write_text(
        _render_markdown(report),
        encoding="utf-8",
    )
    report.output_dir.joinpath("request_hashes.txt").write_text(
        "\n".join(decision.request_hash for decision in report.gated_decisions) + "\n",
        encoding="utf-8",
    )


def _render_markdown(report: BenchmarkReport) -> str:
    metrics = report.metrics
    return f"""# Jev DSPy lab benchmark

- Field: `{report.field}`
- Confidence gate: `{report.threshold:.3f}`
- Total decisions: {metrics.total}
- Answered: {metrics.answered} ({metrics.coverage:.1%} coverage)
- Abstained: {metrics.abstained} ({metrics.abstain_rate:.1%})
- Accuracy among answered: {metrics.accuracy:.3f}
  (95% CI {metrics.accuracy_ci95[0]:.3f}-{metrics.accuracy_ci95[1]:.3f})
- Selective risk: {metrics.selective_risk:.3f}
  (95% CI {metrics.selective_risk_ci95[0]:.3f}-{metrics.selective_risk_ci95[1]:.3f})
- Brier score: {metrics.brier:.4f}
- Expected calibration error: {metrics.ece:.4f}
- Latency p50/p95: {metrics.latency_ms_p50:.1f} ms / {metrics.latency_ms_p95:.1f} ms
- TypeSafe input/output tokens: {metrics.total_input_tokens} / {metrics.total_output_tokens}
- Average modeled cost: ${metrics.average_cost_usd:.6f}

The benchmark is deterministic. `benchmark.json` contains the request hashes and gated decisions;
`request_hashes.txt` contains one canonical request hash per case.
"""
