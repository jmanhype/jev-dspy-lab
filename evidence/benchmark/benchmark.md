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

The benchmark is deterministic. `benchmark.json` contains the request hashes and gated decisions;
`request_hashes.txt` contains one canonical request hash per case.
