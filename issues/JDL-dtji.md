---
id: JDL-dtji
title: "Release jev-dspy-lab 0.2.0"
status: in_progress
priority: 1
type: task
created_at: 2026-09-17T23:02:22Z
created_by: speed
updated_at: 2026-09-17T23:08:00Z
content_hash: "sha256:8858eecc215662353b86a2f4e96d2e974f542b9b0bfd9945b183f88b45251a7b"
parent: JDL-d67r
assignee: dev-JDL-dtji
labels: [delivered]
---

## Description
## Description
Bump and verify package metadata, publish user-facing release notes, build 0.2.0 artifacts, tag the accepted release, and create a GitHub Release with source distribution and wheel assets. PyPI publication is out of scope unless separately authorized.

## Acceptance Criteria
- [ ] AC #1: `pyproject.toml` and `uv.lock` both identify `jev-dspy-lab` as version `0.2.0`.
- [ ] AC #2: A user-facing changelog documents v0.2.0 threshold-sensitivity functionality, artifact/report changes, and the no-breaking-changes boundary.
- [ ] AC #3: Python 3.11, 3.12, 3.13, and 3.14 dev+live suites pass with no skipped tests.
- [ ] AC #4: Coverage, formatting, linting, lock consistency, package build, `pvg verify`, metric gates, and whitespace checks pass.
- [ ] AC #5: Regenerated synthetic and recorded-live reports remain byte-identical.
- [ ] AC #6: Built source distribution and wheel are versioned `0.2.0`, installable/metadata-inspectable, and published as GitHub Release assets.
- [ ] AC #7: `v0.2.0` is an annotated tag on the accepted release commit, and the GitHub Release points to that tag with the changelog notes.
- [ ] AC #8: No PyPI publication occurs without separate explicit authorization.

## Design
Add a permanent release-metadata test that keeps `pyproject.toml`, `uv.lock`, and the changelog synchronized. Generate release artifacts from the accepted story commit and publish them through the repository-owned GitHub Release.

## Notes
Base SHA: `ef3a2dc4b48cba373ebf8559bf1f7ff4aafe3b4d`.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-09-17.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence
Commands run:
- `uv run pytest tests/test_release_metadata.py -q`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run pytest -q`
- `uv run --with pytest-cov --group dev --group live pytest -q --cov=src/jev_dspy_lab --cov-report=term`
- `uv run --python 3.11 --group dev --group live pytest -q`
- `uv run --python 3.12 --group dev --group live pytest -q`
- `uv run --python 3.13 --group dev --group live pytest -q`
- `uv run --python 3.14 --group dev --group live pytest -q`
- `uv lock --check`
- `uv build --out-dir /tmp/jev-dspy-release-0.2.0-final.LzSw3T`
- `pvg verify CHANGELOG.md tests/test_release_metadata.py --include-tests`
- `pvg gates src/jev_dspy_lab tests/test_release_metadata.py --format text`
- `git diff --check`
- `git tag -a v0.2.0 -m 'jev-dspy-lab 0.2.0'`
- `git push origin v0.2.0`
- `gh release create v0.2.0 ...`
- `gh release download v0.2.0 ...`
Summary: jev-dspy-lab 0.2.0 metadata, changelog, tests, artifacts, annotated tag, and GitHub Release are complete; all release gates pass and release assets match local SHA-256 hashes.
SHA: e7cc32cf6c13fc88ac1dbd53d69573fb4c3b8c67

### CI/Test Results
- Red baseline: release metadata tests initially failed because project/lock versions were `0.1.0` and `CHANGELOG.md` did not exist.
- Final focused release metadata tests: **2 passed**.
- Full suite: **35 passed**.
- Python matrix: 3.11, 3.12, 3.13, and 3.14 each **35 passed**.
- Coverage: **91%**; 550 statements, 48 missed.
- Ruff format/check: passed.
- `uv lock --check`: passed.
- Package build: source distribution and wheel built successfully.
- Paivot verify: **PASSED (1 file scanned, 0 issues)**.
- Paivot gates: **PASS (0 warn, 0 skipped)**.
- Whitespace check: passed.
- Regenerated synthetic and recorded-live reports: byte-identical to checked evidence.

### Release Artifacts
GitHub Release: https://github.com/jmanhype/jev-dspy-lab/releases/tag/v0.2.0

Wheel SHA-256:

```text
49fb27944e0d9886b9e9749ced2e90fae4fabbe38de1b325a7f1fefb75d4fcb4  jev_dspy_lab-0.2.0-py3-none-any.whl
```

Source distribution SHA-256:

```text
7fb4e031325bf111eff3bb2778d93e5c9546e7a230e0d253b52c2abb3616a01f  jev_dspy_lab-0.2.0.tar.gz
```

Downloaded release assets matched both local hashes. Wheel metadata reports `Name: jev-dspy-lab` and `Version: 0.2.0`; sdist `PKG-INFO` reports the same. A clean Python 3.14 wheel installation ran the CLI successfully and produced 11 threshold-sweep points.

### Tag
- Tag: `v0.2.0`
- Type: annotated
- Commit: `e7cc32cf6c13fc88ac1dbd53d69573fb4c3b8c67`
- Pushed to `origin/v0.2.0`

### AC Verification
| AC | Requirement | Result |
|---|---|---|
| 1 | Project and lock use version 0.2.0 | PASS — `pyproject.toml` and `uv.lock` synchronized; focused test passes |
| 2 | User-facing changelog documents release | PASS — `CHANGELOG.md` and GitHub Release notes published |
| 3 | Python 3.11-3.14 suites pass | PASS — 35 passed each |
| 4 | Coverage/format/lint/lock/build/verify/gates/whitespace pass | PASS — results recorded above |
| 5 | Synthetic/live reports remain byte-identical | PASS — final regenerated reports matched |
| 6 | Versioned artifacts install and are GitHub Release assets | PASS — wheel/sdist metadata, clean wheel CLI smoke, and hashes verified |
| 7 | Annotated tag and GitHub Release point to release commit | PASS — `v0.2.0` at `e7cc32c...` |
| 8 | No PyPI publication | PASS — no PyPI command used or credential requested |

LEARNINGS:
- Preserve an existing high-revision `uv.lock` format and change only the project version entry; running an older local `uv lock` rewrote unrelated upload-time metadata.
- Permanent metadata synchronization tests caught both stale version metadata and the initially missing changelog before release.
- Publishing artifacts from the exact amended release commit avoids hash drift when lockfile formatting is corrected.
- `pvg gates` still requires the separated `--format text` form; its equals form rejects the flag similarly to the already-fixed `pvg verify` issue.

### OBSERVATIONS
- [ISSUE] `pvg gates ... --format=text` exits with `unknown flag "--format=text"` although help advertises `--format text|json`; separated `--format text` works. This is unrelated to the jev-dspy-lab release.

## nd_contract
status: delivered

### evidence
- Full command results, release URL, tag commit, and artifact hashes recorded above.

### proof
- [x] AC #1: package metadata is synchronized at 0.2.0.
- [x] AC #2: changelog and GitHub Release notes are published.
- [x] AC #3: Python 3.11-3.14 all pass 35 tests.
- [x] AC #4: all release quality gates pass.
- [x] AC #5: synthetic and live reports are byte-identical.
- [x] AC #6: versioned artifacts are verified and attached to GitHub Release.
- [x] AC #7: annotated v0.2.0 tag points to the release commit.
- [x] AC #8: PyPI was not touched.

## History
- 2026-09-17T23:02:24Z status: open -> in_progress
- 2026-09-17T23:02:24Z claimed by dev-JDL-dtji
- 2026-09-17T23:08:00Z status: in_progress -> in_progress

## Links
- Parent: [[JDL-d67r]]

## Comments
