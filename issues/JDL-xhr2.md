---
id: JDL-xhr2
title: "E2e: refit calibration on own decision distribution"
status: in_progress
priority: 1
type: task
parent: JDL-k6fx
created_at: 2026-09-20T17:10:43Z
created_by: speed
updated_at: 2026-09-20T18:41:32Z
content_hash: "sha256:caba01dff5c363dc68cb445e30ac3fa2817e0ead302d0a4fd7d4029614c432aa"
labels: [e2e, capstone, walking-skeleton]
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

## Links
- Parent: [[JDL-k6fx]]

## Comments
