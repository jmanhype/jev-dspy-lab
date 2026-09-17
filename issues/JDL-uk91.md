---
id: JDL-uk91
title: "Reduce metrics complexity warnings"
status: open
priority: 2
type: task
created_at: 2026-09-17T20:27:42Z
created_by: speed
updated_at: 2026-09-17T20:28:12Z
content_hash: "sha256:b2a42d0714d1e9f4368ebba6f3bd202c056ac9969d572d4cfacebfdcd5f8b202"
parent: JDL-7kit
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


## History


## Links
- Parent: [[JDL-7kit]]

## Comments
