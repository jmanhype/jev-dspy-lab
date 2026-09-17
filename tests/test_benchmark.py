from __future__ import annotations

import json

import pytest

from jev_dspy_lab.benchmark import run_benchmark
from jev_dspy_lab.replay import system_one_request_hash


def test_run_benchmark_writes_reproducible_json_and_markdown(tmp_path):
    dataset = tmp_path / "tickets.jsonl"
    responses = tmp_path / "responses.jsonl"
    output = tmp_path / "report"
    cases = [
        {
            "case_id": "stable",
            "model": "jev-latest",
            "request": {
                "document": {"ticket": "Checkout is down"},
                "questions": {"owner": "choice"},
            },
            "expected": {"owner": "infra"},
        },
        {
            "case_id": "uncertain",
            "model": "jev-latest",
            "request": {"document": {"ticket": "Odd latency"}, "questions": {"owner": "choice"}},
            "expected": {"owner": "billing"},
        },
    ]
    dataset.write_text("\n".join(json.dumps(case) for case in cases) + "\n")
    response_rows = [
        {
            "request_hash": system_one_request_hash(
                cases[0]["request"]["document"],
                cases[0]["request"]["questions"],
                model=cases[0]["model"],
            ),
            "response": {
                "answers": {
                    "owner": {
                        "choice": "infra",
                        "probabilities": {"infra": 0.94, "billing": 0.06},
                        "confidence": 0.94,
                    }
                },
                "usage": {"input_tokens": 10, "output_tokens": 2},
                "latency_ms": 100.0,
            },
        },
        {
            "request_hash": system_one_request_hash(
                cases[1]["request"]["document"],
                cases[1]["request"]["questions"],
                model=cases[1]["model"],
            ),
            "response": {
                "answers": {
                    "owner": {
                        "choice": "infra",
                        "probabilities": {"infra": 0.52, "billing": 0.48},
                        "confidence": 0.52,
                    }
                },
                "usage": {"input_tokens": 12, "output_tokens": 2},
                "latency_ms": 140.0,
            },
        },
    ]
    responses.write_text("\n".join(json.dumps(row) for row in response_rows) + "\n")

    report = run_benchmark(
        dataset=dataset,
        responses=responses,
        output_dir=output,
        threshold=0.7,
        field="owner",
        bootstrap_samples=100,
        seed=11,
    )

    assert report.metrics.total == 2
    assert report.metrics.answered == 1
    assert report.metrics.abstained == 1
    assert report.metrics.accuracy == 1.0
    assert (output / "benchmark.json").exists()
    assert (output / "benchmark.md").exists()
    persisted = json.loads((output / "benchmark.json").read_text())
    assert persisted["metrics"]["answered"] == 1
    assert persisted["gated_decisions"][1]["abstained"] is True
    assert persisted["metrics"]["total_input_tokens"] == 22
    assert persisted["metrics"]["total_output_tokens"] == 4
    assert persisted["gated_decisions"][0]["input_tokens"] == 10
    assert persisted["gated_decisions"][0]["output_tokens"] == 2
    assert output.joinpath("request_hashes.txt").read_text().splitlines() == [
        report.gated_decisions[0].request_hash,
        report.gated_decisions[1].request_hash,
    ]


def test_run_benchmark_rejects_duplicate_case_ids_and_missing_expected_field(tmp_path):
    case = {
        "case_id": "same",
        "model": "jev-latest",
        "request": {"document": {"ticket": "x"}, "questions": {"owner": "choice"}},
        "expected": {"owner": "infra"},
    }
    dataset = tmp_path / "tickets.jsonl"
    dataset.write_text(json.dumps(case) + "\n" + json.dumps(case) + "\n")
    responses = tmp_path / "responses.jsonl"
    responses.write_text("")

    with pytest.raises(ValueError, match="Dataset contains duplicate case_id"):
        run_benchmark(
            dataset=dataset,
            responses=responses,
            output_dir=tmp_path / "report",
            field="owner",
            threshold=0.7,
        )


def test_run_benchmark_rejects_missing_expected_field(tmp_path):
    case = {
        "case_id": "missing-expected",
        "model": "jev-latest",
        "request": {"document": {"ticket": "x"}, "questions": {"owner": "choice"}},
        "expected": {},
    }
    dataset = tmp_path / "tickets.jsonl"
    dataset.write_text(json.dumps(case) + "\n")
    responses = tmp_path / "responses.jsonl"
    responses.write_text("")

    with pytest.raises(ValueError, match="missing expected output for field 'owner'"):
        run_benchmark(
            dataset=dataset,
            responses=responses,
            output_dir=tmp_path / "report",
            field="owner",
            threshold=0.7,
        )


def test_run_benchmark_rejects_missing_model(tmp_path):
    case = {
        "case_id": "missing-model",
        "request": {"document": {"ticket": "x"}, "questions": {"owner": "choice"}},
        "expected": {"owner": "infra"},
    }
    dataset = tmp_path / "tickets.jsonl"
    dataset.write_text(json.dumps(case) + "\n")
    responses = tmp_path / "responses.jsonl"
    responses.write_text("")

    with pytest.raises(ValueError, match="missing a non-empty model"):
        run_benchmark(
            dataset=dataset,
            responses=responses,
            output_dir=tmp_path / "report",
            field="owner",
            threshold=0.7,
        )
