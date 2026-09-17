from __future__ import annotations

import json

from jev_dspy_lab.cli import main


def test_cli_creates_report(tmp_path, monkeypatch):
    dataset = tmp_path / "tickets.jsonl"
    responses = tmp_path / "responses.jsonl"
    output = tmp_path / "out"
    case = {
        "case_id": "cli",
        "request": {"document": {"ticket": "API errors"}, "questions": {"impact": "noul"}},
        "expected": {"impact": True},
    }
    request_hash_field = "request_hash"
    from jev_dspy_lab.replay import canonical_request_hash

    row = {
        request_hash_field: canonical_request_hash(case["request"]),
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
