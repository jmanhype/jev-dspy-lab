from __future__ import annotations

import importlib.util
from pathlib import Path


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
    selected_probabilities = []
    for row in responses:
        answer = row["response"]["answers"]["owner"]
        probabilities = answer["probabilities"]
        assert abs(sum(probabilities.values()) - 1.0) < 1e-6
        selected = probabilities[answer["choice"]]
        assert 0.0 < selected < 1.0
        selected_probabilities.append(selected)
    assert any(probability < 0.7 for probability in selected_probabilities)
