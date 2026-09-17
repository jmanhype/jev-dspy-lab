# Jev DSPy lab benchmark

- Field: `owner`
- Confidence gate: `0.700`
- Total decisions: 24
- Answered: 18 (75.0% coverage)
- Abstained: 6 (25.0%)
- Accuracy among answered: 0.667
  (95% CI 0.444-0.889)
- Selective risk: 0.333
  (95% CI 0.111-0.556)
- Brier score: 0.4844
- Expected calibration error: 0.2083
- Latency p50/p95: 162.0 ms / 245.1 ms
- TypeSafe input/output tokens: 21852 / 519
- Average modeled cost: $0.000038

## Threshold sensitivity

This sweep is exploratory. Select a gate before evaluating a reported result;
do not choose a threshold from this table and re-report the same run as confirmatory.

| Gate | Answered | Coverage | Accuracy | Selective risk |
| ---: | ---: | ---: | ---: | ---: |
| 0.000 | 24 | 100.0% | 0.750 | 0.250 |
| 0.100 | 24 | 100.0% | 0.750 | 0.250 |
| 0.200 | 24 | 100.0% | 0.750 | 0.250 |
| 0.300 | 24 | 100.0% | 0.750 | 0.250 |
| 0.400 | 24 | 100.0% | 0.750 | 0.250 |
| 0.500 | 24 | 100.0% | 0.750 | 0.250 |
| 0.600 | 23 | 95.8% | 0.739 | 0.261 |
| 0.700 (selected) | 18 | 75.0% | 0.667 | 0.333 |
| 0.800 | 11 | 45.8% | 0.727 | 0.273 |
| 0.900 | 5 | 20.8% | 1.000 | 0.000 |
| 1.000 | 0 | 0.0% | n/a | n/a |

The benchmark is deterministic. `benchmark.json` contains the request hashes and gated decisions;
`request_hashes.txt` contains one canonical request hash per case.
