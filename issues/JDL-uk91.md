---
id: JDL-uk91
title: "Reduce metrics complexity warnings"
status: in_progress
priority: 2
type: task
created_at: 2026-09-17T20:27:42Z
created_by: speed
updated_at: 2026-09-17T20:31:43Z
content_hash: "sha256:7a1c03f0ba50996c89ef540fb2193edd6dfef610545e308167bc11ed7e852f08"
parent: JDL-7kit
assignee: dev-JDL-uk91
---

## Description
## Description
Refactor `evaluate_decisions` and `evaluate_threshold_sweep` so `pvg gates` reports zero complexity warnings for `src/jev_dspy_lab/metrics.py`. This is behavior-preserving cleanup only.

## Acceptance Criteria
- [ ] AC #1: `pvg gates src/jev_dspy_lab/metrics.py --format text` exits successfully and reports zero complexity warnings.
- [ ] AC #2: The public metrics API and existing report schema remain unchanged.
- [ ] AC #3: The full test suite passes with no skipped tests.
- [ ] AC #4: Regenerated synthetic and recorded-live benchmark JSON and Markdown reports remain byte-identical to the landed reports.
- [ ] AC #5: Formatting, linting, package build, `pvg verify`, and whitespace checks pass.
- [ ] AC #6: Source changes remain uncommitted until the operator explicitly authorizes commit/push.

## Design
Extract focused private helpers for decision/input validation and threshold-point construction. Keep the public functions orchestration-focused; do not alter formulas, ordering, serialization, or error semantics.

## Notes
Baseline warnings: `evaluate_decisions` CCN 16 and `evaluate_threshold_sweep` CCN 18.

## Acceptance Criteria


## Design


## Notes
## Implementation Evidence (DELIVERED 2026-09-17)
PROOF:

### CI/Test Results
- `uv run ruff format --check .` — **passed; 22 files already formatted**
- `uv run ruff check .` — **passed**
- `uv run pytest -q` — **33 passed**
- `uv build` — **source distribution and wheel built**
- `uv run --with pytest-cov --group dev --group live pytest -q --cov=src/jev_dspy_lab --cov-report=term` — **33 passed; 91% total coverage; 550 statements; 48 missed**
- `pvg verify src/jev_dspy_lab/metrics.py tests/test_metrics.py --include-tests` — **VERIFY: PASSED (2 files scanned, 0 issues)**
- `pvg gates src/jev_dspy_lab/metrics.py --format text` — **GATES: PASS (0 warn, 0 skipped)**
- `git diff --check` — **passed**
- Python matrix:
  - `uv run --python 3.11 --group dev --group live pytest -q` — **33 passed**
  - `uv run --python 3.12 --group dev --group live pytest -q` — **33 passed**
  - `uv run --python 3.13 --group dev --group live pytest -q` — **33 passed**
  - `uv run --python 3.14 --group dev --group live pytest -q` — **33 passed**

### Behavior Preservation
- Public API AST comparison against `origin/main`:
  - `Decision`
  - `DecisionKind`
  - `DecisionMetrics`
  - `GatedDecision`
  - `ThresholdPoint`
  - `confidence_for_decision`
  - `evaluate_decisions`
  - `evaluate_threshold_sweep`
  - `gate_decision`
- Result: **public_api=unchanged**
- Regenerated synthetic benchmark in a temporary directory and compared with `diff -ru` against `evidence/benchmark` — **byte-identical**
- Regenerated recorded-live benchmark in a temporary directory and compared with `diff -ru` against `evidence/live/jev-latest` — **byte-identical**
- Added regression test preserving original error precedence: an invalid threshold is reported before probability-distribution validation.

### Working Tree
- Branch: `story/JDL-uk91`
- Base SHA: `ae0224e7c071dc64cf56fbc02ca5232b99e8eb4a`
- Source commit SHA: none yet — deliberately withheld under AC #6 pending explicit operator authorization.

### pvg verify
- Command: `pvg verify src/jev_dspy_lab/metrics.py tests/test_metrics.py --include-tests`
- Result: **VERIFY: PASSED (2 files scanned, 0 issues)**

### AC Verification
| AC | Requirement | Result |
|---|---|---|
| 1 | Metric gate has zero complexity warnings | PASS — `GATES: PASS (0 warn, 0 skipped)` |
| 2 | Public API/schema unchanged | PASS — AST public-name comparison unchanged; benchmark JSON/Markdown byte-identical |
| 3 | Full suite passes with no skips | PASS — 33 passed, no skipped tests |
| 4 | Synthetic/live reports byte-identical | PASS — both temporary regenerated reports matched landed evidence |
| 5 | Format, lint, build, verify, gates, whitespace pass | PASS — all commands recorded above |
| 6 | Source remains uncommitted until explicit authorization | PASS — changes are only on the working story branch and not committed |

LEARNINGS:
- Extracting validation and per-threshold construction reduced both public functions below the CCN warning boundary without changing formulas.
- Refactors must preserve validation order, not only final results; the first helper version accidentally let probability validation precede invalid-threshold validation.
- AST public-name comparison plus byte-identical generated reports is an efficient behavior-preservation check for metric refactors.
- A failing regression test for error precedence was useful even though normal-output tests already remained green.

## nd_contract
status: delivered

### evidence
- Commands, pass counts, coverage, public API comparison, and byte-identical report comparisons recorded above.
- Working tree is based on origin/main SHA `ae0224e7c071dc64cf56fbc02ca5232b99e8eb4a`.

### proof
- [x] AC #1: `pvg gates` reports zero warnings for metrics.
- [x] AC #2: public API and report schema are unchanged.
- [x] AC #3: 33 tests pass with no skips.
- [x] AC #4: regenerated synthetic and live reports are byte-identical.
- [x] AC #5: all quality/build/verify/whitespace gates pass.
- [x] AC #6: source changes remain uncommitted pending explicit authorization.

## History
- 2026-09-17T20:28:12Z status: open -> in_progress
- 2026-09-17T20:28:12Z claimed by dev-JDL-uk91

## Links
- Parent: [[JDL-7kit]]

## Comments
