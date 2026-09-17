---
id: JDL-igfc
title: "Release threshold-sensitivity reporting"
status: open
priority: 1
type: feature
created_at: 2026-09-17T20:04:42Z
created_by: speed
updated_at: 2026-09-17T20:14:20Z
content_hash: "sha256:4eb7a48b5998ff641a1f1cb13626992fba579768ae34799d2c7153382c6a52d2"
labels: [delivered]
parent: JDL-0hgz
---

## Description
## Description
Ship the completed threshold-sensitivity increment from the current working tree. The selected confidence gate remains the confirmatory result; the sweep is explicitly labeled exploratory.

## Acceptance Criteria
- [ ] AC #1: `evaluate_threshold_sweep` deterministically reports coverage, answered/correct/incorrect counts, accuracy, and selective risk at each requested gate, with `null` accuracy/risk when no decisions pass.
- [ ] AC #2: Benchmark JSON persists `threshold_sweep`; Markdown renders the sweep, marks the selected gate, and warns against post-hoc threshold selection.
- [ ] AC #3: A non-grid selected threshold is included exactly once.
- [ ] AC #4: README and recorded-live evidence document the exploratory-statistics boundary.
- [ ] AC #5: Python 3.11, 3.12, 3.13, and 3.14 with dev+live groups each pass all tests.
- [ ] AC #6: Formatting, lint, package build, report repeatability, fixture regeneration, and whitespace checks pass.
- [ ] AC #7: Changes remain uncommitted until the operator explicitly authorizes commit/push.

## Design
Use the existing validated `Decision` inputs and confidence extraction. Compute each confidence once, then count decisions satisfying each threshold. Keep sweep metrics separate from `DecisionMetrics` so the preselected gate remains the headline result.

## Notes
- Implementation and test changes are present in the current working tree.
- Verification evidence is recorded in `evidence/threshold-sweep.md`.
- Existing fixed-gate synthetic/live metrics remain unchanged.

## Acceptance Criteria


## Design


## Notes
## Implementation Evidence
### CI/Test Results
- Python 3.11 dev+live: 32 passed.
- Python 3.12 dev+live: 32 passed.
- Python 3.13 dev+live: 32 passed.
- Python 3.14 dev+live: 32 passed.
- `uv run ruff format --check .`: passed.
- `uv run ruff check .`: passed.
- `uv build`: source distribution and wheel built.
- Repeated benchmark reports: byte-identical.
- Regenerated fixtures: byte-identical.
- `git diff --check`: passed.

Commands run:
- `uv run --python 3.11 --group dev --group live pytest -q`
- `uv run --python 3.12 --group dev --group live pytest -q`
- `uv run --python 3.13 --group dev --group live pytest -q`
- `uv run --python 3.14 --group dev --group live pytest -q`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv build`
- `uv run jev-dspy-benchmark ... --output evidence/benchmark ...`
- `uv run jev-dspy-benchmark ... --output evidence/live/jev-latest ...`
- `uv run python scripts/build_fixtures.py --output-dir <temporary-directory>`
- `git diff --check`

Summary: Deterministic threshold-sensitivity metrics, persisted JSON/Markdown sweep output, tests, documentation, and evidence are implemented. The selected gate remains confirmatory and the sweep is labeled exploratory.
SHA: b6a916201c260dbc2f6bb6eacf4a216d078e2bf2 (working-tree base; no source commit created yet)

### AC Verification
- [x] AC #1: `evaluate_threshold_sweep` reports deterministic counts/rates and uses null for empty gates.
- [x] AC #2: `benchmark.json` persists `threshold_sweep`; `benchmark.md` renders the selected gate and exploratory warning.
- [x] AC #3: Tests include and uniquely select a non-grid `0.750` gate.
- [x] AC #4: README and recorded-live evidence document the post-hoc-selection boundary.
- [x] AC #5: Python 3.11–3.14 dev+live suites each passed 32 tests.
- [x] AC #6: Formatting, lint, build, repeatability, fixture regeneration, and whitespace checks passed.
- [x] AC #7: Source changes remain uncommitted pending explicit operator authorization.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-09-17.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## History
- 2026-09-17T20:04:55Z status: open -> in_progress
- 2026-09-17T20:04:55Z claimed by dev-JDL-igfc
- 2026-09-17T20:04:55Z status: in_progress -> in_progress
- 2026-09-17T20:05:44Z status: in_progress -> in_progress
- 2026-09-17T20:14:20Z status: in_progress -> open
- 2026-09-17T20:14:20Z released by speed

## Links
- Parent: [[JDL-0hgz]]

## Comments
