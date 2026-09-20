---
id: JDL-urut
title: "E2e: check in recorded jev-latest calibration report"
status: open
priority: 0
type: task
labels: [e2e]
parent: JDL-42n1
created_at: 2026-09-20T19:49:18Z
created_by: speed
updated_at: 2026-09-20T19:49:18Z
content_hash: "sha256:e7d4cc82e21e4522d01e41b45ee029c1bb66fb00cdf70dd5b35965c25c246664"
---

## Description
## USER INTENT
A researcher needs a checked-in, reproducible calibration report showing whether refitting on this project's own recorded decisions improves honest selective prediction on a disjoint held-out split.

## Context (Embedded)
`evidence/live/jev-latest-responses.jsonl` contains the recorded own-distribution responses with returned-model provenance. Main already contains the accepted leakage-safe calibration implementation and CLI. This story generates and preserves the real report; it does not redesign calibration behavior.

## OUT OF SCOPE
- Network/API calls or credentials.
- PyPI publication.
- Editing recorded responses, requests, expected labels, or request hashes.
- Fitting and evaluating on the same split.
- Presenting exploratory sweep rows as the confirmatory result.

## DIFF BUDGET
- ~5 files, under 250 changed LOC.

## Boundary Map
PRODUCES:
- evidence/calibration/jev-latest/benchmark.json -> replayed benchmark context
- evidence/calibration/jev-latest/benchmark.md -> human-readable benchmark summary
- evidence/calibration/jev-latest/request_hashes.txt -> deterministic request identity
- evidence/calibration/jev-latest/calibration.json -> versioned leakage-safe calibration artifact
- evidence/calibration/jev-latest/README.md -> real-result interpretation and reproduction instructions
- tests/test_real_calibration_evidence.py -> regression and provenance checks

CONSUMES:
- evidence/live/jev-latest-responses.jsonl -> recorded live response distribution
  schema: JSONL response records containing model provenance, answers, usage, and latency
- fixtures/tickets.jsonl -> deterministic case requests and expected labels
  schema: JSONL case records containing case_id, model, request, and expected fields
- src/jev_dspy_lab/benchmark.py -> run_benchmark(...)
  spec: run_benchmark(dataset: Path, responses: Path, output_dir: Path, field: str, threshold: float, ..., calibration: bool = False) -> BenchmarkReport
- src/jev_dspy_lab/calibration.py -> load_calibration_report(...)
  spec: load_calibration_report(path: str | Path) -> CalibrationReport

## Story Contract
The user can inspect and replay one durable real `jev-latest` calibration report with raw and calibrated honest-contract metrics.

1. The report is generated solely from the checked-in live recording with no network access.
2. The artifact records actual returned model provenance, field, threshold, split seed/fraction, disjoint train IDs, held-out IDs, `{case_id: request_hash}` input hashes, and model/input fingerprints.
3. Raw and calibrated metrics expose Brier, log loss, ECE, answered/incorrect counts, selective risk, and coverage.
4. Reliability rows expose every declared bin with count, mean confidence, empirical accuracy, absolute gap, and weighted ECE contribution.
5. A regression test loads the checked-in artifact, validates replay provenance, and asserts metric/report identities.
6. The README honestly distinguishes raw from calibrated results and does not claim general model quality.
7. Re-running the documented command produces byte-identical calibration artifact bytes.
8. Existing calibration and release tests remain green.

## Testing Requirements
- `uv run --group dev pytest -q tests/test_calibration.py tests/test_real_calibration_evidence.py`
- `uv run --group dev pytest -q`
- `uv run --group dev ruff check .`
- `uv run --group dev ruff format --check .`
- `git diff --check`

## MANDATORY SKILLS
- pvg

## nd_contract
status: new

### evidence
- Operator selected the recorded own-distribution report as the next Jev deliverable.

### proof
- [ ] Story #1: No-network replay.
- [ ] Story #2: Complete split/model/input provenance.
- [ ] Story #3: Required raw/calibrated metrics.
- [ ] Story #4: Complete reliability rows.
- [ ] Story #5: Checked-in artifact regression test.
- [ ] Story #6: Honest interpretation.
- [ ] Story #7: Byte-identical regeneration.
- [ ] Story #8: Existing behavior remains green.

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[JDL-42n1]]

## Comments
