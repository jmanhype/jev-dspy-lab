# Live `jev-latest` recording

## Run

- Date: 2026-09-17
- Requested alias: `jev-latest`
- Resolved response model: `jev-1.13.0`
- Cases: 24 synthetic support-ticket owner-routing decisions
- Confidence gate: 0.700
- Requests: sequential `TypeSafeClient.system_one` calls
- SDK: `typesafe-sdk==0.6.0`
- Authentication: `TYPESAFE_API_KEY` supplied only to the process environment

The API key was not written to the repository, request log, response fixture, benchmark report, or Git history.

## Result

See [`jev-latest/benchmark.md`](jev-latest/benchmark.md).

- 23 answered, 1 abstained
- 95.8% coverage
- 0.913 accuracy among answered decisions
- 0.087 selective risk
- 0.1546 Brier score
- 0.0583 expected calibration error
- 191.5 ms latency p50
- 405.6 ms latency p95
- 11,101 input tokens
- 1,328 output tokens
- $0.000019 average modeled input cost

Cost uses TypeSafe's published `$0.042 / 1M` input-token price; output tokens are free.

## Reproduction

Replay the recording without an API key:

```bash
uv run jev-dspy-benchmark \
  --dataset ../../fixtures/tickets.jsonl \
  --responses jev-latest-responses.jsonl \
  --output /tmp/jev-live-replay \
  --field owner \
  --threshold 0.7 \
  --bootstrap-samples 2000 \
  --seed 17
```

The persisted report was compared against a fresh replay; both `benchmark.json` and `benchmark.md` were byte-identical.

## Limitations

- The 24 cases are synthetic and narrowly cover first-response owner routing.
- Accuracy is conditional on the 0.700 confidence gate.
- Latency was measured from the client process, not the server request queue alone.
- The bootstrap intervals are frequentist percentile intervals over the answered outcomes.
- This recording does not represent general Jev accuracy outside this task distribution.
