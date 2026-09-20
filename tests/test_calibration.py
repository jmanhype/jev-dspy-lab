from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from jev_dspy_lab.benchmark import run_benchmark
from jev_dspy_lab.calibration import (
    CalibrationFingerprintMismatch,
    DegenerateCalibrationTargets,
    EmptyCalibrationTargets,
    dump_calibration_report,
    evaluate_calibration,
    fit_platt_scaling,
    load_calibration_report,
    split_decisions,
)
from jev_dspy_lab.cli import main
from jev_dspy_lab.metrics import Decision


def make_decision(case_id: str, confidence: float, correct: bool) -> Decision:
    return Decision(
        case_id=case_id,
        field="impact",
        kind="noul",
        predicted=True if correct else f"wrong-{case_id}",
        expected=True,
        probability=confidence,
    )


def mixed_decisions() -> list[Decision]:
    values = [
        ("low-wrong", 0.25, False),
        ("middle-right", 0.55, True),
        ("high-right", 0.85, True),
        ("highest-wrong", 0.95, False),
        ("held-low", 0.20, False),
        ("held-right", 0.75, True),
        ("held-wrong", 0.90, False),
    ]
    return [make_decision(*value) for value in values]


def make_report(*, bins: int, threshold: float):
    decisions = mixed_decisions()
    train, held_out = split_decisions(decisions, train_fraction=0.5, seed=19)
    return evaluate_calibration(
        train,
        held_out,
        bins=bins,
        threshold=threshold,
        input_hashes={item.case_id: f"hash-{item.case_id}" for item in decisions},
        model_fingerprint="model-a",
    )


def test_split_is_deterministic_complete_and_disjoint():
    decisions = mixed_decisions()

    first_train, first_held_out = split_decisions(decisions, train_fraction=0.5, seed=19)
    second_train, second_held_out = split_decisions(decisions, train_fraction=0.5, seed=19)

    assert (first_train, first_held_out) == (second_train, second_held_out)
    train_ids = {item.case_id for item in first_train}
    held_out_ids = {item.case_id for item in first_held_out}
    assert train_ids.isdisjoint(held_out_ids)
    assert train_ids | held_out_ids == {item.case_id for item in decisions}

    duplicate = [make_decision("same", 0.6, True), make_decision("same", 0.7, False)]
    with pytest.raises(ValueError, match="Duplicate calibration case_id: 'same'"):
        split_decisions(duplicate, train_fraction=0.5, seed=1)


def test_fit_rejects_invalid_targets_and_probabilities():
    with pytest.raises(EmptyCalibrationTargets, match="At least one training decision"):
        fit_platt_scaling([])
    for correct in (True, False):
        with pytest.raises(DegenerateCalibrationTargets, match="correct and incorrect"):
            fit_platt_scaling([make_decision("same", confidence=0.8, correct=correct)])
    with pytest.raises(ValueError, match="finite probability"):
        fit_platt_scaling([make_decision("nan", math.nan, True), make_decision("ok", 0.5, False)])


def test_reliability_rows_and_calibration_metrics():
    report = make_report(bins=4, threshold=0.6)

    raw_bins = report.raw_reliability
    bounds = [(index / 4, (index + 1) / 4) for index in range(4)]
    assert [(row.lower_bound, row.upper_bound) for row in raw_bins] == bounds
    assert sum(row.count for row in raw_bins) == report.raw.answered
    empty = next(row for row in raw_bins if row.count == 0)
    assert (empty.absolute_gap, empty.weighted_ece_contribution) == (0.0, 0.0)
    occupied = next(row for row in raw_bins if row.count > 0)
    assert occupied.absolute_gap == pytest.approx(
        abs(occupied.mean_confidence - occupied.empirical_accuracy)
    )
    assert occupied.weighted_ece_contribution == pytest.approx(
        occupied.absolute_gap * occupied.count / report.raw.answered
    )
    assert sum(row.weighted_ece_contribution for row in raw_bins) == pytest.approx(report.raw.ece)
    assert len(report.calibrated_reliability) == 4
    train = [make_decision("low-wrong", 0.25, False), make_decision("high-right", 0.85, True)]
    held_out = [
        make_decision("out-low", 0.20, False),
        make_decision("middle-right", 0.70, True),
        make_decision("high-wrong", 0.90, False),
    ]

    report = evaluate_calibration(
        train,
        held_out,
        bins=4,
        threshold=0.6,
        input_hashes={item.case_id: f"hash-{item.case_id}" for item in train + held_out},
        model_fingerprint="model-a",
    )

    assert (report.raw.total, report.raw.answered, report.raw.abstained) == (3, 2, 1)
    assert (report.raw.correct, report.raw.incorrect) == (1, 1)
    for metrics in (report.raw, report.calibrated):
        assert metrics.total == 3
        assert metrics.answered == metrics.correct + metrics.incorrect
        assert metrics.selective_risk == pytest.approx(metrics.incorrect / metrics.answered)
        assert metrics.coverage == pytest.approx(metrics.answered / metrics.total)
        assert all(value >= 0.0 for value in (metrics.log_loss, metrics.brier, metrics.ece))

    expected_log_loss = -(math.log(0.7) + math.log(1 - 0.9)) / 2
    assert report.raw.log_loss == pytest.approx(expected_log_loss)
    assert report.raw.brier == pytest.approx(((0.7 - 1.0) ** 2 + (0.9 - 0.0) ** 2) / 2)


def test_artifact_round_trip_and_provenance_fail_closed(tmp_path):
    report = make_report(bins=5, threshold=0.65)
    artifact = report.artifact
    hashes = dict(artifact.input_hashes)
    assert set(artifact.train_ids).isdisjoint(artifact.held_out_ids)
    assert set(hashes) == set(artifact.train_ids) | set(artifact.held_out_ids)
    assert artifact.schema_version == "calibration.v1" and artifact.method == "platt"
    assert artifact.selected_threshold == 0.65
    assert artifact.bin_count == 5
    path = tmp_path / "calibration.json"
    dump_calibration_report(report, path)
    restored = load_calibration_report(path)
    assert restored == report

    artifact.validate_replay(input_hashes=hashes, model_fingerprint="model-a")
    with pytest.raises(CalibrationFingerprintMismatch, match="Model fingerprint mismatch"):
        artifact.validate_replay(input_hashes=hashes, model_fingerprint="model-b")

    keys = sorted(hashes)
    renamed = {**hashes, keys[0]: hashes[keys[1]], keys[1]: hashes[keys[0]]}
    with pytest.raises(CalibrationFingerprintMismatch, match="Input fingerprint mismatch"):
        report.artifact.validate_replay(input_hashes=renamed, model_fingerprint="model-a")
    with pytest.raises(CalibrationFingerprintMismatch, match="Input fingerprint mismatch"):
        report.artifact.validate_replay(
            input_hashes=hashes,
            model_fingerprint="model-a",
            train_ids=artifact.held_out_ids,
            held_out_ids=artifact.train_ids,
        )
    overlap = make_decision("same", confidence=0.7, correct=True)
    with pytest.raises(ValueError, match="train and held-out IDs overlap"):
        evaluate_calibration(
            [overlap, make_decision("other", 0.6, False)],
            [overlap, make_decision("held", 0.8, True)],
            bins=2,
            threshold=0.5,
            input_hashes={"same": "h", "other": "h", "held": "h"},
            model_fingerprint="model-a",
        )
    with pytest.raises(ValueError, match="non-empty model_fingerprint"):
        training = mixed_decisions()
        fit_platt_scaling(training, input_hashes={item.case_id: "h" for item in training})
    with pytest.raises(ValueError, match="non-empty input_hashes"):
        fit_platt_scaling(
            [make_decision("low", 0.2, False), make_decision("high", 0.8, True)],
            input_hashes={},
            model_fingerprint="model-a",
        )


def test_calibration_disabled_compatibility_and_cli_output(tmp_path):
    root = Path(__file__).resolve().parents[1]
    dataset = root / "fixtures" / "tickets.jsonl"
    responses = root / "evidence" / "live" / "jev-latest-responses.jsonl"
    output = tmp_path / "report"
    output.mkdir()
    stale = output / "calibration.json"
    stale.write_text("{}\n", encoding="utf-8")

    report = run_benchmark(
        dataset=dataset,
        responses=root / "fixtures" / "typesafe_responses.jsonl",
        output_dir=output,
        field="owner",
        threshold=0.7,
        seed=17,
    )

    assert report.calibration is None
    assert not stale.exists()

    exit_code = main(
        [
            f"--dataset={dataset}",
            f"--responses={responses}",
            f"--output={output}",
            "--field=owner",
            "--threshold=0.7",
            "--calibration",
            "--calibration-train-fraction=0.5",
            "--calibration-bins=3",
        ]
    )

    assert exit_code == 0
    payload = json.loads((output / "calibration.json").read_text(encoding="utf-8"))
    artifact = payload["artifact"]
    assert (artifact["bin_count"], len(artifact["input_hashes"])) == (3, 24)
    assert (len(artifact["train_ids"]), len(artifact["held_out_ids"])) == (12, 12)
    assert set(artifact["train_ids"]).isdisjoint(artifact["held_out_ids"])
