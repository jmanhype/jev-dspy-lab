#!/usr/bin/env python3
"""Smoke-check RecordingClient and ReplayClient against dspy-typesafeify."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Literal


def require_integration() -> None:
    if (
        importlib.util.find_spec("dspy") is None
        or importlib.util.find_spec("typesafe_dspy") is None
    ):
        raise SystemExit(
            "Install the sibling integration first: "
            "uv pip install -e '../dspy-typesafeify[typesafe]' "
            "&& uv run --no-sync python scripts/verify_integration.py"
        )


def main() -> int:
    require_integration()
    import dspy
    from typesafe_dspy import (
        configure_typesafe,
        disable_typesafe,
        typesafe_results,
        typesafeify,
    )

    from jev_dspy_lab.replay import RecordingClient, ReplayClient, load_replay_index

    recording_path = Path("evidence/integration/recording.jsonl")
    recording_existed = recording_path.exists() and recording_path.stat().st_size > 0

    class CaptureClient:
        def system_one(self, document, questions, *, model=None):
            return SimpleNamespace(
                answers={
                    "owner": SimpleNamespace(
                        choice="option_0",
                        probabilities={"option_0": 0.91, "option_1": 0.09},
                        confidence=0.91,
                    )
                },
                usage=SimpleNamespace(input_tokens=42, output_tokens=7),
            )

    @typesafeify()
    class TicketRouting(dspy.Signature):
        """Route a ticket."""

        ticket: str = dspy.InputField()
        owner: Literal["infra", "billing"] = dspy.OutputField()

    recorder = RecordingClient(CaptureClient(), recording_path=recording_path)
    configure_typesafe(client=recorder, model="integration-test")
    recorded_result = dspy.Predict(TicketRouting)(ticket="Checkout is unavailable")
    recorded_metadata = typesafe_results(recorded_result)["owner"]
    disable_typesafe()

    replay = ReplayClient(load_replay_index(recording_path))
    configure_typesafe(client=replay, model="integration-test")
    replay_result = dspy.Predict(TicketRouting)(ticket="Checkout is unavailable")
    replay_metadata = typesafe_results(replay_result)["owner"]
    disable_typesafe()

    assert recorded_result.owner == replay_result.owner == "infra"
    assert recorded_metadata.probabilities == replay_metadata.probabilities
    assert len(recorder.records) == (0 if recording_existed else 1)
    assert len(load_replay_index(recording_path)) == 1
    print("integration=verified decisions=1 replay_match=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
