# Jev DSPy lab benchmark

- Field: `owner`
- Confidence gate: `0.700`
- Total decisions: 24
- Answered: 23 (95.8% coverage)
- Abstained: 1 (4.2%)
- Accuracy among answered: 0.913
  (95% CI 0.783-1.000)
- Selective risk: 0.087
  (95% CI 0.000-0.217)
- Brier score: 0.1546
- Expected calibration error: 0.0583
- Latency p50/p95: 191.5 ms / 405.6 ms
- TypeSafe input/output tokens: 11101 / 1328
- Average modeled cost: $0.000019

The benchmark is deterministic. `benchmark.json` contains the request hashes and gated decisions;
`request_hashes.txt` contains one canonical request hash per case.
