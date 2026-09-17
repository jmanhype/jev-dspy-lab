---
id: JDL-igfc
title: "Release threshold-sensitivity reporting"
status: in_progress
priority: 1
type: feature
created_at: 2026-09-17T20:04:42Z
created_by: speed
updated_at: 2026-09-17T20:04:55Z
content_hash: "sha256:fa83e855dd220c13ca254e9eff972102408aa4bbdfc81f02e97c0170dcacfa21"
assignee: dev-JDL-igfc
labels: [delivered]
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
- 2026-09-17T20:04:55Z status: open -> in_progress
- 2026-09-17T20:04:55Z claimed by dev-JDL-igfc
- 2026-09-17T20:04:55Z status: in_progress -> in_progress

## Links


## Comments
