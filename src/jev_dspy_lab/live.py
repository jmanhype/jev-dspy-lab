"""Live TypeSafe collection followed immediately by offline replay evaluation."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from jev_dspy_lab.benchmark import BenchmarkReport, run_benchmark
from jev_dspy_lab.replay import RecordingClient

ClientFactory = Callable[[str, str, float], Any]
QuestionBuilder = Callable[[Mapping[str, Any]], Any]


def load_required_api_key(environ: Mapping[str, str] | None = None) -> str:
    """Return the required TypeSafe API key without logging its value."""

    value = (os.environ if environ is None else environ).get("TYPESAFE_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TYPESAFE_API_KEY must be set for a live benchmark run.")
    return value


def collect_live_decisions(
    client: Any,
    *,
    cases: Sequence[Mapping[str, Any]],
    recording_path: str | Path,
    question_builder: QuestionBuilder | None = None,
) -> RecordingClient:
    """Call TypeSafe for every case and persist model-aware replay responses."""

    recorder = RecordingClient(client, recording_path=recording_path)
    builder = question_builder or _build_question
    for case in cases:
        request = case["request"]
        questions = {name: builder(question) for name, question in request["questions"].items()}
        recorder.system_one(
            request["document"],
            questions,
            model=case["model"],
        )
    return recorder


def run_live_benchmark(
    *,
    dataset: str | Path,
    responses: str | Path,
    output_dir: str | Path,
    field: str,
    threshold: float,
    bootstrap_samples: int = 1_000,
    seed: int = 0,
    model_override: str | None = None,
    timeout_seconds: float = 60.0,
    client_factory: ClientFactory | None = None,
    question_builder: QuestionBuilder | None = None,
) -> BenchmarkReport:
    """Collect live responses, then evaluate the same benchmark from replay data."""

    api_key = load_required_api_key()
    cases = _load_jsonl(Path(dataset))
    if model_override is not None:
        for case in cases:
            case["model"] = model_override

    if client_factory is None:
        client_factory = _default_client_factory
    client = client_factory(api_key, model_override or _single_model(cases), timeout_seconds)
    try:
        collect_live_decisions(
            client,
            cases=cases,
            recording_path=Path(responses),
            question_builder=question_builder or _build_question,
        )
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()

    benchmark_arguments = {
        "responses": responses,
        "output_dir": output_dir,
        "field": field,
        "threshold": threshold,
        "bootstrap_samples": bootstrap_samples,
        "seed": seed,
    }
    if model_override is None:
        return run_benchmark(dataset=dataset, **benchmark_arguments)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".jsonl") as temporary_dataset:
        temporary_dataset.write("".join(json.dumps(case, sort_keys=True) + "\n" for case in cases))
        temporary_dataset.flush()
        return run_benchmark(
            dataset=Path(temporary_dataset.name),
            **benchmark_arguments,
        )


def _default_client_factory(api_key: str, model: str, timeout_seconds: float) -> Any:
    from typesafe_sdk import TypeSafeClient

    return TypeSafeClient(
        api_key=api_key,
        model=model,
        timeout=timeout_seconds,
    )


def _build_question(question: Mapping[str, Any]) -> Any:
    question_type = question.get("type")
    if question_type == "choice":
        from typesafe_sdk import Choice

        return Choice(
            instructions=question.get("instructions"),
            criteria=question["criteria"],
        )
    if question_type == "noul":
        from typesafe_sdk import Noul

        return Noul(instructions=question.get("instructions"))
    if question_type == "score":
        from typesafe_sdk import Score

        return Score(
            instructions=question.get("instructions"),
            criteria=question["criteria"],
        )
    raise ValueError(f"Unsupported TypeSafe question type: {question_type!r}")


def _single_model(cases: Sequence[Mapping[str, Any]]) -> str:
    models = {case["model"] for case in cases}
    if len(models) != 1:
        raise ValueError("Live runs require one model unless --model overrides every case")
    return next(iter(models))


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
