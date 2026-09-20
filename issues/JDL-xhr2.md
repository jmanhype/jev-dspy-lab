---
id: JDL-xhr2
title: "E2e: refit calibration on own decision distribution"
status: in_progress
priority: 1
type: task
parent: JDL-k6fx
created_at: 2026-09-20T17:10:43Z
created_by: speed
updated_at: 2026-09-20T18:43:42Z
content_hash: "sha256:b89182a003650e7199786c0e52698045720437ff7783d7e7cbbb95285e141b77"
labels: [e2e, capstone, walking-skeleton, delivered]
assignee: dev-JDL-xhr2
---

## Description
## USER INTENT
A researcher needs to know whether Jev confidence is honest on this project's own recorded decision distribution, not only on the original provider's distribution, and whether a calibration refit improves selective prediction without leakage.

## Context (Embedded)
Current `src/jev_dspy_lab/metrics.py` supports typed decisions, confidence gating, Brier score, expected calibration error, threshold sweeps, bootstrap intervals, latency, tokens, and modeled cost. Current benchmark reports already preserve request hashes and deterministic replay. Missing features are log loss, explicit reliability bins, a deterministic disjoint train/held-out split, fitted calibration parameters, and a versioned calibration artifact.

## OUT OF SCOPE
- Calling TypeSafe or any network service.
- Modifying recorded requests/responses or their hashes.
- Replacing the existing benchmark output format.
- Fitting and evaluating on the same split.
- Claiming cross-model equivalence.

## DIFF BUDGET
- ~7 files, under 750 changed LOC.

## Boundary Map
PRODUCES:
- src/jev_dspy_lab/calibration.py -> ReliabilityBin, CalibrationMetrics, CalibrationReport, CalibrationArtifact, split_decisions(decisions, train_fraction, seed) -> tuple, fit_platt_scaling(train) -> CalibrationArtifact, evaluate_calibration(train, held_out, bins, threshold) -> CalibrationReport
- src/jev_dspy_lab/benchmark.py -> optional calibration report integration with disjoint splits
- src/jev_dspy_lab/cli.py -> explicit calibration controls and output
- tests/test_calibration.py -> deterministic split, reliability, log-loss, refit, leakage, edge-case, and artifact coverage
- README.md -> v0.3 calibration usage and honest-contract documentation

CONSUMES:
- (existing): src/jev_dspy_lab/metrics.py -> Decision, confidence_for_decision(decision), evaluate_decisions(...), evaluate_threshold_sweep(...)
- (existing): src/jev_dspy_lab/benchmark.py -> run_benchmark(...)

## Acceptance Criteria
1. Reliability output has one row per declared bin with lower bound, upper bound, count, mean confidence, empirical accuracy, absolute gap, and weighted ECE contribution.
2. Calibration metrics report log loss, Brier score, ECE, answered count, incorrect count, selective risk, and coverage.
3. Splitting is deterministic for a seed, preserves all unique case IDs, and emits disjoint train/held-out ID sets.
4. Duplicate case IDs are rejected rather than silently allowing split leakage.
5. Platt or temperature scaling is fitted only on the declared training decisions.
6. Raw and calibrated metrics are both evaluated only on the declared held-out decisions.
7. The output artifact records schema version, method, parameters, train IDs, held-out IDs, input hashes, selected threshold, and bin count.
8. A model/input fingerprint mismatch is represented explicitly; replay does not silently reuse stale calibration.
9. Empty or all-positive/all-negative training targets fail with actionable typed errors.
10. Existing v0.2.0 benchmark JSON fields and CLI behavior remain backward compatible.

## Testing Requirements
- Unit: probability validation, log loss, reliability binning, deterministic split, no-overlap invariant, fit and transform, artifact round trip.
- Integration: run calibration over the existing deterministic fixture/live-recording decisions; no network.
- E2e: CLI or benchmark integration must write both benchmark and calibration artifacts with disjoint split IDs.
- Commands:
  - uv run --group dev pytest -q tests/test_calibration.py
  - uv run --group dev pytest -q
  - uv run --group dev ruff check .
  - uv run --group dev ruff format --check .

## MANDATORY SKILLS
None identified.

## nd_contract
status: new

### evidence
- Derived from the operator-selected cross-project calibrated-policy benchmark goal.

### proof
- [ ] Pending implementation.

## Acceptance Criteria


## Design


## Notes
## Implementation Evidence

Commands run: see targeted/full/lint/format/whitespace outputs in this delivery evidence.

### CI/Test Results

- Targeted: 5 passed.
- Full: 39 passed, 1 existing optional skip.
- Ruff check/format and whitespace: pass.

### AC Verification

- [x] All 10 JDL-xhr2 acceptance criteria verified in the delivered proof above.

Summary: own-distribution calibration and reliability reporting delivered.

Commit SHA: e58fafa372d86ad664146cf2db023ac81194ca0d

## Implementation Evidence

Commands run:

- `uv run --group dev pytest -q tests/test_calibration.py` — 5 passed.
- `uv run --group dev pytest -q` — 39 passed, 1 pre-existing optional `typesafe_sdk` skip.
- `uv run --group dev ruff check .` — all checks passed.
- `uv run --group dev ruff format --check .` — 26 files already formatted.
- `git diff --check` — pass.

### CI/Test Results

- Targeted calibration suite: 5/5 passed.
- Full suite: 39 passed, 1 existing optional SDK skip.
- Ruff check: pass.
- Ruff format check: 26 files formatted.
- Whitespace check: pass.

### AC Verification

- [x] AC #1: Every reliability bin has bounds, count, mean confidence, empirical accuracy, absolute gap, and weighted ECE contribution.
- [x] AC #2: Metrics expose log loss, binary-correctness Brier, ECE, answered/incorrect counts, selective risk, and coverage.
- [x] AC #3: Splitting is deterministic, complete, and disjoint by case ID.
- [x] AC #4: Duplicate case IDs fail closed.
- [x] AC #5: Platt fit consumes only declared training decisions.
- [x] AC #6: Raw and calibrated evaluation consume only held-out decisions.
- [x] AC #7: Artifact records schema, method, parameters, split IDs, hashes, threshold, and bins.
- [x] AC #8: Replay/load reject membership, input, model, response/expected distribution, and threshold mismatches.
- [x] AC #9: Empty, degenerate, and invalid targets fail with actionable errors.
- [x] AC #10: v0.2 benchmark JSON/default CLI behavior remains backward compatible.

Summary: added leakage-safe own-distribution calibration, reliability reporting, versioned provenance, and opt-in benchmark/CLI integration.

Commit SHA: `e58fafa372d86ad664146cf2db023ac81194ca0d`

## CI/Test Results

Commands run:

- `uv run --group dev pytest -q tests/test_calibration.py` — 5 passed.
- `uv run --group dev pytest -q` — 39 passed, 1 pre-existing optional `typesafe_sdk` skip.
- `uv run --group dev ruff check .` — all checks passed.
- `uv run --group dev ruff format --check .` — 26 files already formatted.
- `git diff --check` — pass.

Summary: implemented leakage-safe own-distribution Platt calibration, reliability bins, versioned fail-closed artifacts, benchmark/CLI integration, compatibility coverage, and documentation.

Commit SHA: `e58fafa372d86ad664146cf2db023ac81194ca0d`

## AC Verification

| AC | Result |
|---|---|
| 1. Reliability rows | PASS: bounds/count/mean confidence/accuracy/gap/weighted ECE. |
| 2. Metrics | PASS: log loss, binary-correctness Brier, ECE, counts, selective risk, coverage. |
| 3. Deterministic split | PASS: seed-stable complete disjoint ID sets. |
| 4. Duplicate IDs | PASS: rejected. |
| 5. Train-only fit | PASS: Platt fit consumes training decisions only. |
| 6. Held-out evaluation | PASS: raw/calibrated use held-out only. |
| 7. Versioned artifact | PASS: schema/method/parameters/splits/hashes/fingerprint/threshold/bins. |
| 8. Replay mismatch | PASS: split/input/model/expected/answer/threshold mismatches fail closed. |
| 9. Typed target errors | PASS: empty/degenerate/invalid inputs fail actionably. |
| 10. v0.2 compatibility | PASS: opt-in calibration preserves old JSON/default CLI and clears stale output. |

## nd_contract
status: delivered

### evidence
- Required targeted/full/lint/format/whitespace commands independently rerun with results above.
- Commit `e58fafa372d86ad664146cf2db023ac81194ca0d`.

### proof
- [x] AC #1: Reliability output is complete per bin.
- [x] AC #2: Calibration metrics are complete.
- [x] AC #3: Splitting is deterministic, complete, and disjoint.
- [x] AC #4: Duplicate IDs are rejected.
- [x] AC #5: Calibration is fitted only on training decisions.
- [x] AC #6: Evaluation uses only held-out decisions.
- [x] AC #7: Artifact records all required provenance.
- [x] AC #8: Stale calibration replay fails explicitly.
- [x] AC #9: Invalid/degenerate targets fail with typed errors.
- [x] AC #10: Existing benchmark behavior is backward compatible.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-09-20.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

Commands and independently reproduced results:

- `uv run --group dev pytest -q tests/test_calibration.py`: 5 passed.
- `uv run --group dev pytest -q`: 39 passed, 1 pre-existing optional `typesafe_sdk` skip.
- `uv run --group dev ruff check .`: all checks passed.
- `uv run --group dev ruff format --check .`: 26 files already formatted.
- `git diff --check`: pass.

Changed-line budget: 91 tracked changes plus 429-line calibration module and 225-line test module = 745 total file lines, within the under-750 story budget.

Artifact integrity:
- Canonical split fingerprint binds train IDs, held-out IDs, and `{case_id: request_hash}`.
- Replay/load fail closed on missing provenance, duplicate/overlapping IDs, changed split membership, model/expected/answer distribution, or `noul_true_threshold`.
- Calibration is opt-in; v0.2 benchmark JSON/default CLI behavior remains unchanged and stale calibration output is removed on reuse.

Commit SHA: `e58fafa372d86ad664146cf2db023ac81194ca0d`

## nd_contract
status: delivered

### evidence
- Targeted/full test, lint, format, whitespace, and independent PM rerun outputs above.
- Commit `e58fafa372d86ad664146cf2db023ac81194ca0d`.

### proof
- [x] AC #1: Reliability rows expose bounds, count, mean confidence, empirical accuracy, absolute gap, and weighted ECE contribution.
- [x] AC #2: Calibration metrics expose log loss, binary-correctness Brier, ECE, counts, selective risk, and coverage.
- [x] AC #3: Seed-stable split preserves unique IDs and emits disjoint train/held-out sets.
- [x] AC #4: Duplicate case IDs fail closed.
- [x] AC #5: Platt parameters are fitted only on declared training decisions.
- [x] AC #6: Raw/calibrated metrics use only declared held-out decisions.
- [x] AC #7: Versioned artifact records method, parameters, split IDs, hashes, fingerprint, threshold, and bins.
- [x] AC #8: Replay/load reject stale or identity-mismatched inputs/models.
- [x] AC #9: Empty/degenerate/invalid calibration targets use actionable failures.
- [x] AC #10: Existing v0.2 benchmark JSON and default CLI behavior remain compatible.

## History
- 2026-09-20T17:11:01Z status: open -> in_progress
- 2026-09-20T17:11:01Z claimed by dev-JDL-xhr2
- 2026-09-20T18:41:32Z status: in_progress -> in_progress

## Links
- Parent: [[JDL-k6fx]]

## Comments
