---
id: JDL-xhr2
title: "E2e: refit calibration on own decision distribution"
status: open
priority: 1
type: task
parent: JDL-k6fx
created_at: 2026-09-20T17:10:43Z
created_by: speed
updated_at: 2026-09-20T17:10:44Z
content_hash: "sha256:3ffcf332050cc534f1712f854b6e012a4d1f2e97719ad18f71a7d801d56fe380"
labels: [e2e, capstone]
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


## History


## Links
- Parent: [[JDL-k6fx]]

## Comments
