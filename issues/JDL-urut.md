---
id: JDL-urut
title: "E2e: check in recorded jev-latest calibration report"
status: closed
priority: 0
type: task
labels: [e2e, capstone, delivered]
parent: JDL-42n1
created_at: 2026-09-20T19:49:18Z
created_by: speed
updated_at: 2026-09-20T20:14:43Z
content_hash: "sha256:f44697852eabc6581953093a5f118dc8153f83834143ba53c841bf811524616e"
assignee: dev-JDL-urut
closed_at: 2026-09-20T20:14:43Z
close_reason: "Accepted: real offline calibration report, complete provenance, portable byte-identical replay, negative result documented honestly, local gates and all required CI checks pass."
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
## PM Decision
ACCEPTED [2026-09-20]: Independently reviewed the artifact/provenance diff, fixed legacy pre-metadata artifact loading, added a regression test, reran targeted/full suites on Python 3.11 and 3.14, offline replay, lint, format, scoped verifier, and whitespace checks. Quantization makes report bytes portable without weakening checks. PR 2 required checks passed on Python 3.11, 3.12, and 3.13 with CLEAN merge state. The larger generated-evidence line count is intentional and dominated by deterministic checked-in benchmark/calibration outputs.

## Implementation Evidence

Commands run:

- `UV_OFFLINE=1 uv run --python 3.11 --group dev pytest -q` - 43 passed, 1 existing optional SDK skip.
- `UV_OFFLINE=1 uv run --python 3.14 --group dev pytest -q` - 43 passed, 1 existing optional SDK skip.
- Offline replay on Python 3.11 and 3.14 - all four report files byte-identical.
- `UV_OFFLINE=1 uv run --group dev ruff check .` - all checks passed.
- `UV_OFFLINE=1 uv run --group dev ruff format --check .` - 29 files formatted.
- `pvg verify ...` - 3 files, 0 issues.

### CI/Test Results

- Portable calibration boundary values are quantized to 12 decimal places.
- Benchmark JSON floats are similarly normalized before serialization.
- The original Python 3.11 CI floating-point drift is fixed without weakening byte-identity checks.

Summary: portable deterministic report generation verified on Python 3.11 and 3.14.

Commit SHA: 3c98fae32489b4a42c5dbd9c294042f4e69b69bd

## nd_contract
status: delivered

### evidence
- Updated commit `3c98fae32489b4a42c5dbd9c294042f4e69b69bd`.

### proof
- [x] Deterministic replay is portable across Python 3.11 and 3.14.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-09-20.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

Commands run:

- `UV_OFFLINE=1 uv run --group dev pytest -q tests/test_calibration.py tests/test_real_calibration_evidence.py` - 9 passed.
- `UV_OFFLINE=1 uv run --group dev pytest -q` - 43 passed, 1 existing optional live-SDK skip.
- `UV_OFFLINE=1 uv run --group dev ruff check .` - all checks passed.
- `UV_OFFLINE=1 uv run --group dev ruff format --check .` - 29 files already formatted.
- Offline CLI replay to a temporary directory - calibration.json, benchmark.json, benchmark.md, and request_hashes.txt all byte-identical.
- `pvg verify src/jev_dspy_lab/benchmark.py src/jev_dspy_lab/calibration.py tests/test_real_calibration_evidence.py --include-tests --format=text` - PASSED, 3 files, 0 issues.
- `git diff --check` and `git diff --cached --check` - pass.

### CI/Test Results

- Targeted calibration/evidence suites: 9/9 passed.
- Full suite: 43 passed, 1 pre-existing optional `typesafe_sdk` skip.
- Ruff check/format: pass.
- Offline deterministic replay: pass.
- Scoped verifier: 3 files, 0 issues.

### AC Verification

| AC | Result | Evidence |
|---|---|---|
| 1. Offline recorded replay | PASS | Generated only from checked-in tickets and live response recording with `UV_OFFLINE=1`. |
| 2. Complete provenance | PASS | Artifact records owner field, 0.7 threshold, seed 17, 0.5 split, 12/12 disjoint IDs, 24 case hashes, jev-1.13.0 returned models, and both fingerprints. |
| 3. Required metrics | PASS | Raw/calibrated Brier, log loss, ECE, counts, selective risk, and coverage checked. |
| 4. Reliability rows | PASS | All 10 bins and weighted ECE identities checked. |
| 5. Regression test | PASS | Independent hashes, provenance, metrics, bins, and replay checked. |
| 6. Honest interpretation | PASS | README calls the result negative and disclaims general model quality. |
| 7. Deterministic regeneration | PASS | Four report outputs are byte-identical under documented offline replay. |
| 8. Existing compatibility | PASS | Full suite green; pre-metadata calibration artifact loading regression added and passing. |

Summary: preserved the first real recorded-distribution Jev calibration report. The 12-case held-out Platt result is negative: coverage falls from 100% to 83.3%, selective risk remains 0, and Brier/log loss/ECE worsen. This is recorded honestly rather than claimed as an improvement.

Commit SHA: 6894a242cd57f0196584c9c8148f11a28362bb84

## nd_contract
status: delivered

### evidence
- Required command outputs above.
- Commit `6894a242cd57f0196584c9c8148f11a28362bb84`.

### proof
- [x] AC #1: Report is offline replay only.
- [x] AC #2: Split, model, input, field, threshold, and bin provenance are complete.
- [x] AC #3: Raw/calibrated metrics are complete and regression-pinned.
- [x] AC #4: All reliability rows and ECE identities are verified.
- [x] AC #5: Checked-in artifact/provenance regression test passes.
- [x] AC #6: Negative result and limits are documented honestly.
- [x] AC #7: Documented replay is byte-identical.
- [x] AC #8: Existing and legacy calibration behavior remains compatible.

## History
- 2026-09-20T19:51:06Z status: open -> in_progress
- 2026-09-20T19:51:06Z claimed by dev-JDL-urut
- 2026-09-20T20:07:32Z status: in_progress -> in_progress
- 2026-09-20T20:14:43Z status: in_progress -> closed

## Links
- Parent: [[JDL-42n1]]

## Comments
