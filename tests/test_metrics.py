from __future__ import annotations

import math

import pytest

from jev_dspy_lab.metrics import (
    DecisionMetrics,
    confidence_for_decision,
    evaluate_decisions,
    evaluate_threshold_sweep,
    gate_decision,
)


def make_decision(**overrides):
    decision = {
        "case_id": "case-1",
        "field": "owner_team",
        "kind": "choice",
        "predicted": "infra",
        "expected": "infra",
        "probabilities": {"infra": 0.91, "billing": 0.09},
        "latency_ms": 120.0,
        "cost_usd": 0.000042,
        "input_tokens": 100,
        "output_tokens": 20,
    }
    decision.update(overrides)
    return decision


def test_confidence_for_decision_uses_selected_choice_probability():
    assert confidence_for_decision(make_decision(kind="choice", predicted="infra")) == 0.91


def test_confidence_for_decision_uses_noul_true_probability():
    assert confidence_for_decision(make_decision(kind="noul", probability=0.73)) == 0.73


def test_gate_decision_fails_closed_below_threshold():
    gated = gate_decision(make_decision(), threshold=0.95)

    assert gated.predicted is None
    assert gated.abstained is True
    assert gated.confidence == 0.91


def test_gate_decision_preserves_answer_at_threshold():
    gated = gate_decision(make_decision(), threshold=0.91)

    assert gated.predicted == "infra"
    assert gated.abstained is False


def test_metrics_report_accuracy_brier_ece_and_selective_risk():
    decisions = [
        make_decision(
            case_id="1",
            predicted="infra",
            expected="infra",
            probabilities={"infra": 0.9, "billing": 0.1},
        ),
        make_decision(
            case_id="2",
            predicted="billing",
            expected="infra",
            probabilities={"infra": 0.2, "billing": 0.8},
        ),
        make_decision(
            case_id="3",
            predicted="infra",
            expected="infra",
            probabilities={"infra": 0.65, "billing": 0.35},
        ),
    ]

    metrics = evaluate_decisions(decisions, threshold=0.7, bootstrap_samples=100, seed=7)

    assert isinstance(metrics, DecisionMetrics)
    assert metrics.total == 3
    assert metrics.answered == 2
    assert metrics.abstained == 1
    assert metrics.correct == 1
    assert metrics.accuracy == 0.5
    assert metrics.selective_risk == 0.5
    assert metrics.coverage == pytest.approx(2 / 3)
    # Cases one and two remain. Their multiclass Brier scores are 0.02 and 1.28.
    assert metrics.brier == pytest.approx((0.02 + 1.28) / 2)
    assert metrics.ece == pytest.approx(0.45)
    assert metrics.latency_ms_p50 == pytest.approx(120.0)
    assert metrics.average_cost_usd == pytest.approx(0.000042)
    assert metrics.total_input_tokens == 300
    assert metrics.total_output_tokens == 60
    assert metrics.average_input_tokens == 100
    assert metrics.average_output_tokens == 20
    assert metrics.accuracy_ci95[0] <= metrics.accuracy <= metrics.accuracy_ci95[1]


def test_metrics_reject_empty_input():
    with pytest.raises(ValueError, match="At least one decision"):
        evaluate_decisions([], threshold=0.5)


def test_threshold_sweep_reports_coverage_accuracy_and_risk():
    decisions = [
        make_decision(
            case_id="low",
            predicted="infra",
            expected="infra",
            probabilities={"infra": 0.2, "billing": 0.8},
        ),
        make_decision(
            case_id="middle",
            predicted="billing",
            expected="infra",
            probabilities={"infra": 0.4, "billing": 0.6},
        ),
        make_decision(
            case_id="high",
            predicted="infra",
            expected="infra",
            probabilities={"infra": 0.8, "billing": 0.2},
        ),
    ]

    sweep = evaluate_threshold_sweep(decisions, thresholds=(0.0, 0.5, 0.9))

    assert [(point.threshold, point.answered) for point in sweep] == [
        (0.0, 3),
        (0.5, 2),
        (0.9, 0),
    ]
    assert sweep[0].coverage == pytest.approx(1.0)
    assert sweep[0].accuracy == pytest.approx(2 / 3)
    assert sweep[0].selective_risk == pytest.approx(1 / 3)
    assert sweep[1].correct == 1
    assert sweep[1].incorrect == 1
    assert sweep[1].accuracy == pytest.approx(0.5)
    assert sweep[1].selective_risk == pytest.approx(0.5)
    assert sweep[2].coverage == 0.0
    assert sweep[2].accuracy is None
    assert sweep[2].selective_risk is None


def test_threshold_sweep_rejects_invalid_thresholds():
    decisions = [make_decision()]

    with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
        evaluate_threshold_sweep(decisions, thresholds=(0.5, 1.1))

    with pytest.raises(ValueError, match="thresholds must be unique"):
        evaluate_threshold_sweep(decisions, thresholds=(0.5, 0.5))


def test_invalid_threshold_takes_precedence_over_probability_validation():
    invalid_probability = make_decision(probabilities={"infra": 0.9, "billing": 0.3})

    with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
        evaluate_decisions(
            [invalid_probability],
            threshold=1.2,
        )

    with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
        evaluate_threshold_sweep([invalid_probability], thresholds=(1.2,))


def test_probability_validation_rejects_nan():
    with pytest.raises(ValueError, match="finite probability"):
        evaluate_decisions(
            [
                make_decision(
                    kind="noul",
                    predicted=True,
                    expected=True,
                    probability=math.nan,
                    probabilities=None,
                )
            ],
            threshold=0.5,
        )


def test_probability_validation_rejects_unnormalized_choice_distribution():
    with pytest.raises(ValueError, match=r"Choice probabilities.*must sum"):
        evaluate_decisions(
            [
                make_decision(
                    probabilities={"infra": 0.9, "billing": 0.3},
                )
            ],
            threshold=0.5,
        )
