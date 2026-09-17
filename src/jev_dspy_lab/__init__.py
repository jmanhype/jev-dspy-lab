"""Reproducible Jev / TypeSafe decision benchmarking for DSPy workflows."""

from jev_dspy_lab.benchmark import BenchmarkDecision, BenchmarkReport, run_benchmark
from jev_dspy_lab.live import collect_live_decisions, load_required_api_key, run_live_benchmark
from jev_dspy_lab.metrics import (
    Decision,
    DecisionMetrics,
    GatedDecision,
    ThresholdPoint,
    confidence_for_decision,
    evaluate_decisions,
    evaluate_threshold_sweep,
    gate_decision,
)
from jev_dspy_lab.replay import (
    RecordingClient,
    ReplayClient,
    canonical_request_hash,
    load_replay_index,
    system_one_request_hash,
)

__all__ = [
    "BenchmarkDecision",
    "BenchmarkReport",
    "Decision",
    "DecisionMetrics",
    "GatedDecision",
    "RecordingClient",
    "ReplayClient",
    "ThresholdPoint",
    "canonical_request_hash",
    "collect_live_decisions",
    "confidence_for_decision",
    "evaluate_decisions",
    "evaluate_threshold_sweep",
    "gate_decision",
    "load_replay_index",
    "load_required_api_key",
    "run_benchmark",
    "run_live_benchmark",
    "system_one_request_hash",
]
