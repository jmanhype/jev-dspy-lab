# Recorded `jev-latest` leakage-safe calibration report

This report replays the checked-in 24-case recording. It made no network or API calls,
used no credentials, and did not modify the recorded requests, responses, expected labels,
or request hashes.

## Confirmatory replay

- Requested alias: `jev-latest`
- Returned model on every response: `jev-1.13.0`
- Decision field: `owner`
- Selected confidence gate: `0.700`
- Calibration split seed: `17`
- Calibration training fraction: `0.500` (12 cases)
- Disjoint held-out fraction: `0.500` (12 cases)
- Reliability bins: 10
- Deterministic Platt parameters: `a = 12.468810810673`, `b = -10.469163689807`
- Model/input fingerprints are recorded in `calibration.json`

The full-benchmark result in `benchmark.md` remains the preselected confirmatory
result: 23 of 24 cases answered (95.8% coverage), 0.913 accuracy among answered
decisions, and 0.087 selective risk. Its threshold sweep is exploratory context only.

## Raw versus calibrated held-out result

Platt scaling was fitted only on the 12 training cases. The metrics below are
computed only on the disjoint 12 held-out cases.

| Metric | Raw | Calibrated |
| --- | ---: | ---: |
| Total | 12 | 12 |
| Answered | 12 | 10 |
| Abstained | 0 | 2 |
| Correct | 12 | 10 |
| Incorrect | 0 | 0 |
| Coverage | 100.0% | 83.3% |
| Selective risk | 0.0000 | 0.0000 |
| Brier score | 0.004125 | 0.015847 |
| Log loss | 0.031472 | 0.133809 |
| Expected calibration error | 0.029167 | 0.125133 |

On this particular held-out split, calibration reduced confidence enough to abstain on
two decisions, but every raw and calibrated answered decision was correct. It did not
improve selective risk and made Brier score, log loss, and ECE worse. This is a negative
calibration result, not a claimed improvement.

Both raw and calibrated reliability tables contain all 10 declared bins in
`calibration.json`, including empty bins, with count, mean confidence, empirical
accuracy, absolute gap, and weighted ECE contribution.

## Interpretation and limits

- This is an evaluation on one recorded, synthetic-ticket, owner-routing distribution.
- It does not estimate general Jev or `jev-1.13.0` quality, accuracy on other tasks, or
  production latency.
- The held-out sample is small, so these point estimates are noisy.
- The full-distribution choice Brier score in `benchmark.json` is not interchangeable
  with the binary correctness Brier scores in `calibration.json`.
- Threshold-sweep rows are sensitivity context and must not be selected and re-reported
  as an independent confirmatory result.

## Reproduction

From the repository root, with no API key configured:

```bash
uv run --group dev jev-dspy-benchmark \
  --dataset fixtures/tickets.jsonl \
  --responses evidence/live/jev-latest-responses.jsonl \
  --output evidence/calibration/jev-latest \
  --field owner \
  --threshold 0.7 \
  --bootstrap-samples 2000 \
  --seed 17 \
  --calibration \
  --calibration-train-fraction 0.5 \
  --calibration-bins 10
```

The checked-in `calibration.json`, `benchmark.json`, `benchmark.md`, and
`request_hashes.txt` are byte-identical to a fresh replay of this command. The
regression test in `tests/test_real_calibration_evidence.py` verifies that identity,
the split/model/input provenance, and the reported metrics.
Calibration boundary values are quantized to 12 decimal places so report bytes remain
stable across supported Python platforms.
