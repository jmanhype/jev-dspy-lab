---
id: JDL-igfc
title: "Release threshold-sensitivity reporting"
status: in_progress
priority: 1
type: feature
created_at: 2026-09-17T20:04:42Z
created_by: speed
updated_at: 2026-09-17T20:16:22Z
content_hash: "sha256:7bc688a2634986c253e3b73fe720640cee27ffdc824891f96ba58795b0dc381a"
parent: JDL-0hgz
assignee: dev-JDL-igfc
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
## Implementation Evidence (DELIVERED 2026-09-17)
PROOF:

### CI/Test Results
- Coverage command: `uv run --with pytest-cov --group dev --group live pytest -q --cov=src/jev_dspy_lab --cov-report=term`
- Coverage result: **32 passed; 91% total coverage; 547 statements; 50 missed**.
- Python matrix evidence:
  - `uv run --python 3.11 --group dev --group live pytest -q` — **32 passed**
  - `uv run --python 3.12 --group dev --group live pytest -q` — **32 passed**
  - `uv run --python 3.13 --group dev --group live pytest -q` — **32 passed**
  - `uv run --python 3.14 --group dev --group live pytest -q` — **32 passed**
- Quality evidence:
  - `uv run ruff format --check .` — **passed**
  - `uv run ruff check .` — **passed**
  - `uv build` — **source distribution and wheel built**
  - repeated benchmark reports — **byte-identical**
  - regenerated fixtures — **byte-identical**
  - `git diff --check` — **passed**
- Rework-day focused checks:
  - `uv run ruff format --check .` — **passed**
  - `uv run ruff check .` — **passed**
  - `uv run pytest -q` — **32 passed**
  - `git diff --check` — **passed**

### Working Tree
- Branch: `story/JDL-igfc`
- Base SHA: `b6a916201c260dbc2f6bb6eacf4a216d078e2bf2`
- Source commit SHA: none yet — deliberately withheld under AC #7 pending explicit operator authorization.

### pvg verify
- Command: `pvg verify README.md src/jev_dspy_lab/__init__.py src/jev_dspy_lab/benchmark.py src/jev_dspy_lab/metrics.py tests/test_benchmark.py tests/test_metrics.py evidence/threshold-sweep.md --include-tests`
- Result: **VERIFY: PASSED (5 files scanned, 0 issues)**

### AC Verification
| AC | Requirement | Result |
|---|---|---|
| 1 | Deterministic sweep metrics with null rates for empty gates | PASS — `evaluate_threshold_sweep` and `ThresholdPoint` in `src/jev_dspy_lab/metrics.py`; tested in `tests/test_metrics.py` |
| 2 | JSON/Markdown persistence with selected-gate warning | PASS — `BenchmarkReport.threshold_sweep`, `_write_report`, `_render_markdown`; tested in `tests/test_benchmark.py` |
| 3 | Non-grid selected threshold included exactly once | PASS — `0.750` test asserts one selected sweep row |
| 4 | README and recorded-live evidence explain exploratory boundary | PASS — README and `evidence/live/README.md` updated |
| 5 | Python 3.11–3.14 dev+live tests pass | PASS — 32 passed on each version; 91% coverage |
| 6 | Formatting, lint, build, repeatability, fixtures, whitespace pass | PASS — commands and results recorded above |
| 7 | Changes remain uncommitted until explicit authorization | PASS — story branch created, but no source commit/push made |

LEARNINGS:
- Compute confidence once per decision before iterating gates; repeated extraction was unnecessary and easier to get wrong.
- Empty-answer gates must use null accuracy/risk, not zero, because zero falsely implies a measured rate.
- Threshold sweeps need an explicit exploratory warning to prevent post-hoc selection from being reported as confirmatory.
- A technically green delivery still needs the full Paivot proof contract, including coverage and LEARNINGS; the first PM rejection was process-valid.
- `pvg verify --help` advertises `--format`, but pvg 1.64.0 rejects it; the supported no-flag command passes.

### OBSERVATIONS
- [ISSUE] `pvg verify --format=text` returns `unknown flag "--format=text"` although `pvg verify --help` documents that flag. The equivalent command without `--format` passes.

### DISCOVERED_BUG
  title: pvg verify help advertises unsupported --format flag
  context: During JDL-igfc pre-delivery verification, `pvg verify --help` documented `--format text|json`, but `pvg verify ... --format=text` failed with `unknown flag "--format=text"`. Removing the flag succeeded. This affects reproducible machine-readable verification on pvg 1.64.0.
  affected_files: /Users/speed/Jev/paivot-ai/pvg/cmd/pvg/main.go
  discovered_during: JDL-igfc

## nd_contract
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-09-17.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


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
- 2026-09-17T20:15:00Z status: open -> in_progress
- 2026-09-17T20:15:00Z claimed by dev-JDL-igfc
- 2026-09-17T20:16:22Z status: in_progress -> in_progress

## Links
- Parent: [[JDL-0hgz]]

## Comments

### 2026-09-17T20:14:20Z speed
## PM Decision
REJECTED [2026-09-17]:
EXPECTED: The canonical delivery proof must include exact commands, pass/fail counts, the result SHA/working-tree basis, coverage percentage, AC-by-AC verification, and a LEARNINGS section for Retro.
DELIVERED: The story records exact commands, Python 3.11-3.14 pass counts, formatting/lint/build/repeatability evidence, the working-tree base SHA, and checked AC verification. The PM fresh check produced 32 passed and 91% total coverage. The delivered proof does not record a coverage percentage and has no LEARNINGS section.
GAP: Implementation evidence is technically strong, but the delivery contract is incomplete for PM acceptance and downstream retro processing.
FIX: Append the coverage command and 91% result (32 passed; total 547 statements, 50 missed) plus a concise LEARNINGS section, then redeliver JDL-igfc. No source-code change is required.

## nd_contract
status: rejected

### evidence
- PM reviewed the changed source/tests/docs and the delivery proof.
- PM fresh verification: `uv run --with pytest-cov --group dev --group live pytest -q --cov=src/jev_dspy_lab --cov-report=term` — 32 passed, 91% total coverage.
- Delivery proof missing: recorded coverage percentage and LEARNINGS section.

### proof
- [ ] AC #5-supporting evidence: coverage percentage must be recorded by the developer.
- [ ] Retro input: LEARNINGS section must be present.
