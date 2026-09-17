---
id: JDL-igfc
title: "Release threshold-sensitivity reporting"
status: open
priority: 1
type: feature
created_at: 2026-09-17T20:04:42Z
created_by: speed
updated_at: 2026-09-17T20:04:55Z
content_hash: "sha256:7669974822d864fe8c54c1388902474eeadd7ec4ee7e84bc12238835594ccfa2"
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


## History


## Links


## Comments
