from __future__ import annotations

import json

from jev_dspy_lab.cli import main
from jev_dspy_lab.replay import system_one_request_hash


def test_cli_creates_report(tmp_path, monkeypatch):
    dataset = tmp_path / "tickets.jsonl"
    responses = tmp_path / "responses.jsonl"
    output = tmp_path / "out"
    case = {
        "case_id": "cli",
        "model": "jev-latest",
        "request": {"document": {"ticket": "API errors"}, "questions": {"impact": "noul"}},
        "expected": {"impact": True},
    }
    row = {
        "request_hash": system_one_request_hash(
            case["request"]["document"],
            case["request"]["questions"],
            model=case["model"],
        ),
        "response": {
            "answers": {"impact": {"noul": 0.88}},
            "usage": {"input_tokens": 8, "output_tokens": 2},
            "latency_ms": 70.0,
        },
    }
    dataset.write_text(json.dumps(case) + "\n")
    responses.write_text(json.dumps(row) + "\n")

    exit_code = main(
        [
            "--dataset",
            str(dataset),
            "--responses",
            str(responses),
            "--output",
            str(output),
            "--field",
            "impact",
            "--threshold",
            "0.7",
        ]
    )

    assert exit_code == 0
    assert json.loads((output / "benchmark.json").read_text())["metrics"]["total"] == 1
