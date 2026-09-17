from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from jev_dspy_lab.live import (
    collect_live_decisions,
    run_live_benchmark,
)


def write_case(path: Path) -> dict:
    case = {
        "case_id": "live",
        "model": "jev-latest",
        "request": {
            "document": {"ticket": "Checkout is unavailable"},
            "questions": {
                "owner": {
                    "type": "choice",
                    "instructions": "Select the first-response owner.",
                    "criteria": {"infra": None, "billing": None},
                }
            },
        },
        "expected": {"owner": "infra"},
    }
    path.write_text(json.dumps(case) + "\n", encoding="utf-8")
    return case


class RecordingFriendlyFakeClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def system_one(self, state, questions, *, model=None):
        self.calls.append({"state": state, "questions": questions, "model": model})
        return SimpleNamespace(
            model="jev-1.13.0",
            usage=SimpleNamespace(billing_units=12, input_tokens=34, output_tokens=5),
            answers={
                "owner": SimpleNamespace(
                    choice="infra",
                    confidence=0.91,
                    probabilities={"infra": 0.91, "billing": 0.09},
                )
            },
        )


def test_collect_live_decisions_records_model_aware_responses(tmp_path):
    dataset = tmp_path / "tickets.jsonl"
    case = write_case(dataset)
    client = RecordingFriendlyFakeClient()

    recorder = collect_live_decisions(
        client,
        cases=[case],
        recording_path=tmp_path / "recording.jsonl",
        question_builder=lambda question: question,
    )

    assert len(client.calls) == 1
    assert client.calls[0]["model"] == "jev-latest"
    assert client.calls[0]["state"] == case["request"]["document"]
    assert len(recorder.records) == 1
    assert recorder.records[0]["response"]["answers"]["owner"]["choice"] == "infra"


def test_run_live_benchmark_requires_api_key(tmp_path, monkeypatch):
    dataset = tmp_path / "tickets.jsonl"
    write_case(dataset)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="TYPESAFE_API_KEY must be set"):
        run_live_benchmark(
            dataset=dataset,
            responses=tmp_path / "recording.jsonl",
            output_dir=tmp_path / "report",
            field="owner",
            threshold=0.7,
        )


def test_run_live_benchmark_uses_injected_client_and_records_replayable_response(
    tmp_path,
    monkeypatch,
):
    dataset = tmp_path / "tickets.jsonl"
    write_case(dataset)
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    client = RecordingFriendlyFakeClient()

    report = run_live_benchmark(
        dataset=dataset,
        responses=tmp_path / "recording.jsonl",
        output_dir=tmp_path / "report",
        field="owner",
        threshold=0.7,
        client_factory=lambda api_key, model, timeout: client,
        question_builder=lambda question: question,
    )

    assert report.metrics.total == 1
    assert report.metrics.accuracy == 1.0
    assert report.metrics.total_input_tokens == 34
    recording = json.loads((tmp_path / "recording.jsonl").read_text())
    assert recording["response"]["answers"]["owner"]["choice"] == "infra"


def test_run_live_benchmark_model_override_updates_replay_dataset(tmp_path, monkeypatch):
    dataset = tmp_path / "tickets.jsonl"
    write_case(dataset)
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    client = RecordingFriendlyFakeClient()

    report = run_live_benchmark(
        dataset=dataset,
        responses=tmp_path / "recording.jsonl",
        output_dir=tmp_path / "report",
        field="owner",
        threshold=0.7,
        model_override="jev-1.13.0",
        client_factory=lambda api_key, model, timeout: client,
        question_builder=lambda question: question,
    )

    assert client.calls[0]["model"] == "jev-1.13.0"
    assert report.metrics.total == 1
