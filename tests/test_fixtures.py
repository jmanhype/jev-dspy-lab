from __future__ import annotations

import importlib.util
from pathlib import Path

from jev_dspy_lab.replay import system_one_request_hash


def load_fixture_builder():
    path = Path(__file__).parents[1] / "scripts" / "build_fixtures.py"
    spec = importlib.util.spec_from_file_location("build_fixtures", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_fixture_has_valid_and_selective_probabilities():
    module = load_fixture_builder()
    cases, responses = module.build_rows()

    assert len(cases) == 24
    assert len(responses) == 24
    for case, row in zip(cases, responses, strict=True):
        assert case["model"] == "jev-latest"
        question = case["request"]["questions"]["owner"]
        assert question["type"] == "choice"
        assert isinstance(question["instructions"], str)
        assert set(question["criteria"]) == set(module.OWNERS)
        assert row["request_hash"] == system_one_request_hash(
            case["request"]["document"],
            case["request"]["questions"],
            model=case["model"],
        )
    selected_probabilities = []
    for row in responses:
        answer = row["response"]["answers"]["owner"]
        probabilities = answer["probabilities"]
        assert abs(sum(probabilities.values()) - 1.0) < 1e-6
        selected = probabilities[answer["choice"]]
        assert 0.0 < selected < 1.0
        selected_probabilities.append(selected)
    assert any(probability < 0.7 for probability in selected_probabilities)
