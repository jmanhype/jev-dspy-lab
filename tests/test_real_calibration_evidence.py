from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest

from jev_dspy_lab.calibration import CalibrationArtifact, load_calibration_report
from jev_dspy_lab.cli import main
from jev_dspy_lab.replay import canonical_request_hash, load_replay_index, system_one_request_hash

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "evidence" / "calibration" / "jev-latest"
DATASET = ROOT / "fixtures" / "tickets.jsonl"
RESPONSES = ROOT / "evidence" / "live" / "jev-latest-responses.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def replay_provenance() -> tuple[
    list[dict[str, object]], dict[str, dict[str, object]], dict[str, str]
]:
    cases = read_jsonl(DATASET)
    response_index = load_replay_index(RESPONSES)
    request = dict[str, str]()
    for case in cases:
        request[str(case["case_id"])] = system_one_request_hash(
            case["request"]["document"],  # type: ignore[index,union-attr]
            case["request"]["questions"],  # type: ignore[index,union-attr]
            model=case["model"],  # type: ignore[arg-type]
        )
    return cases, response_index, request


def test_real_calibration_artifact_has_replayable_provenance():
    report = load_calibration_report(REPORT_DIR / "calibration.json")
    artifact = report.artifact
    cases, response_index, input_hashes = replay_provenance()

    assert artifact.field == "owner"
    assert artifact.selected_threshold == pytest.approx(0.7)
    assert artifact.split_seed == 17
    assert artifact.train_fraction == pytest.approx(0.5)
    assert artifact.returned_models == ("jev-1.13.0",)
    assert len(artifact.train_ids) == len(artifact.held_out_ids) == 12
    assert set(artifact.train_ids).isdisjoint(artifact.held_out_ids)
    assert set(artifact.train_ids) | set(artifact.held_out_ids) == set(input_hashes)
    assert artifact.input_hashes == input_hashes
    assert REPORT_DIR.joinpath("request_hashes.txt").read_text(
        encoding="utf-8"
    ).splitlines() == list(input_hashes.values())
    assert artifact.input_fingerprint == CalibrationArtifact.fingerprint_for_split(
        artifact.train_ids, artifact.held_out_ids, input_hashes
    )

    benchmark = json.loads(REPORT_DIR.joinpath("benchmark.json").read_text(encoding="utf-8"))
    assert [row["case_id"] for row in benchmark["gated_decisions"]] == [
        str(case["case_id"]) for case in cases
    ]
    assert [row["request_hash"] for row in benchmark["gated_decisions"]] == list(
        input_hashes.values()
    )
    response_rows = []
    for case, request_hash in zip(cases, input_hashes.values(), strict=True):
        response = response_index[request_hash]
        response_rows.append(
            {
                "case_id": case["case_id"],
                "model": response["model"],
                "answer": response["answers"]["owner"],
            }
        )
    expected_models = tuple(sorted({row["model"] for row in response_rows}))
    expected_fingerprint = canonical_request_hash(
        {
            "models": expected_models,
            "field": "owner",
            "expected": sorted(str(case["expected"]["owner"]) for case in cases),
            "noul_true_threshold": 0.5,
            "responses": sorted(response_rows, key=lambda row: row["case_id"]),
        }
    )
    assert artifact.model_fingerprint == expected_fingerprint
    assert artifact.returned_models == expected_models
    assert {response_index[hash]["model"] for hash in input_hashes.values()} == {"jev-1.13.0"}
    artifact.validate_replay(
        input_hashes=input_hashes, model_fingerprint=artifact.model_fingerprint
    )


def test_pre_metadata_calibration_artifact_remains_loadable(tmp_path: Path):
    payload = json.loads((REPORT_DIR / "calibration.json").read_text(encoding="utf-8"))
    for key in ("field", "split_seed", "train_fraction", "returned_models"):
        payload["artifact"].pop(key, None)
    legacy = tmp_path / "legacy-calibration.json"
    legacy.write_text(json.dumps(payload), encoding="utf-8")

    report = load_calibration_report(legacy)

    assert report.artifact.field == "unspecified"
    assert report.artifact.split_seed is None
    assert report.artifact.train_fraction is None
    assert report.artifact.returned_models == ()


def test_real_calibration_metrics_and_reliability_identities():
    report = load_calibration_report(REPORT_DIR / "calibration.json")
    payload = json.loads(REPORT_DIR.joinpath("calibration.json").read_text(encoding="utf-8"))

    expected = {
        "raw": {
            "total": 12,
            "answered": 12,
            "abstained": 0,
            "correct": 12,
            "incorrect": 0,
            "log_loss": 0.031471834272,
            "brier": 0.004125,
            "ece": 0.029166666666,
            "selective_risk": 0.0,
            "coverage": 1.0,
        },
        "calibrated": {
            "total": 12,
            "answered": 10,
            "abstained": 2,
            "correct": 10,
            "incorrect": 0,
            "log_loss": 0.133808994108,
            "brier": 0.015846544346,
            "ece": 0.125132515456,
            "selective_risk": 0.0,
            "coverage": 0.833333333333,
        },
    }
    assert payload["raw"] == expected["raw"]
    assert payload["calibrated"] == expected["calibrated"]
    assert report.raw.correct == report.raw.answered - report.raw.incorrect
    assert report.calibrated.correct == report.calibrated.answered - report.calibrated.incorrect

    for name, metrics in (("raw", report.raw), ("calibrated", report.calibrated)):
        assert metrics.coverage == pytest.approx(metrics.answered / metrics.total)
        assert metrics.selective_risk == pytest.approx(metrics.incorrect / metrics.answered)
        rows = payload[f"{name}_reliability"]
        assert len(rows) == report.artifact.bin_count == 10
        assert [row["lower_bound"] for row in rows] == [index / 10 for index in range(10)]
        assert [row["upper_bound"] for row in rows] == [(index + 1) / 10 for index in range(10)]
        assert sum(row["count"] for row in rows) == metrics.answered
        for row in rows:
            if row["count"]:
                assert row["absolute_gap"] == pytest.approx(
                    abs(row["mean_confidence"] - row["empirical_accuracy"])
                )
                assert row["weighted_ece_contribution"] == pytest.approx(
                    row["absolute_gap"] * row["count"] / metrics.answered
                )
            else:
                assert (
                    row["mean_confidence"],
                    row["empirical_accuracy"],
                    row["absolute_gap"],
                    row["weighted_ece_contribution"],
                ) == (0.0, 0.0, 0.0, 0.0)
        assert sum(row["weighted_ece_contribution"] for row in rows) == pytest.approx(metrics.ece)
        assert math.isfinite(metrics.log_loss)


def test_documented_real_calibration_replay_is_byte_identical(tmp_path):
    checked = (REPORT_DIR / "calibration.json").read_bytes()
    exit_code = main(
        [
            "--dataset",
            str(DATASET),
            "--responses",
            str(RESPONSES),
            "--output",
            str(tmp_path),
            "--field",
            "owner",
            "--threshold",
            "0.7",
            "--bootstrap-samples",
            "2000",
            "--seed",
            "17",
            "--calibration",
            "--calibration-train-fraction",
            "0.5",
            "--calibration-bins",
            "10",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "calibration.json").read_bytes() == checked
    for filename in ("benchmark.json", "benchmark.md", "request_hashes.txt"):
        assert (tmp_path / filename).read_bytes() == (REPORT_DIR / filename).read_bytes()
    assert load_calibration_report(tmp_path / "calibration.json") == load_calibration_report(
        REPORT_DIR / "calibration.json"
    )
