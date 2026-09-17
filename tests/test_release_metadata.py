from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "0.2.0"


def test_project_and_lock_release_metadata_are_synchronized() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["name"] == "jev-dspy-lab"
    assert project["project"]["version"] == RELEASE_VERSION

    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    match = re.search(
        r'name = "jev-dspy-lab"\nversion = "([^"]+)"',
        lock,
    )
    assert match is not None
    assert match.group(1) == RELEASE_VERSION


def test_changelog_documents_current_release() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    current = re.search(rf"^## \[{re.escape(RELEASE_VERSION)}\].*$", changelog, re.MULTILINE)
    assert current is not None
    assert "threshold sensitivity" in changelog[current.end() :].lower()
