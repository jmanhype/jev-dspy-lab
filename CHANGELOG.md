# Changelog

## [0.2.0] — 2026-09-17

### New Features

- **Threshold sensitivity reporting:** Benchmark reports now include coverage,
  accuracy, and selective risk across confidence gates from 0.0 through 1.0, so
  you can see whether a selected gate is robust instead of judging it from a
  single operating point.
- **Programmatic threshold sweeps:** The public Python API now includes
  `evaluate_threshold_sweep` and `ThresholdPoint`, making it easier to analyze
  selective-prediction behavior in your own evaluation tooling.

### Improvements

- **Clearer statistical boundaries:** Reports explicitly mark the selected gate
  and identify the sweep as exploratory, helping prevent a post-hoc threshold
  choice from being misrepresented as an independently confirmed result.
- **Safe empty-gate reporting:** Gates with no answered decisions use `null`
  accuracy and selective risk instead of implying a measured zero rate.

### Breaking Changes

- None. Existing report fields, metric definitions, selected-gate results, CLI
  arguments, and offline replay behavior remain compatible.

## [0.1.0] — 2026-09-17

### New Features

- Released the reproducible offline benchmark for Jev / TypeSafe decisions in
  DSPy-style workflows.
- Included confidence gating, selective-risk and calibration metrics,
  deterministic replay hashes, latency and token reporting, modeled cost, CLI
  report generation, and live response recording.
