from __future__ import annotations

import pytest

from jev_dspy_lab.live import _build_question

pytest.importorskip("typesafe_sdk")


def test_build_question_converts_all_public_sdk_question_types():
    from typesafe_sdk import Choice, Noul, Score

    assert isinstance(
        _build_question(
            {
                "type": "choice",
                "instructions": "Pick an owner",
                "criteria": {"infra": None, "billing": None},
            }
        ),
        Choice,
    )
    assert isinstance(
        _build_question({"type": "noul", "instructions": "Is this urgent?"}),
        Noul,
    )
    assert isinstance(
        _build_question(
            {
                "type": "score",
                "instructions": "Rate urgency",
                "criteria": ["low", "high"],
            }
        ),
        Score,
    )
