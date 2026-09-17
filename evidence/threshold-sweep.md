# Threshold-sensitivity verification

Date: 2026-09-17

## Scope

`Jev-432` adds deterministic selective-prediction metrics at every 0.1 confidence gate and
includes the selected gate when it falls between grid points. Empty-answer gates use `null`
accuracy and selective risk rather than fabricating zero rates.

## Verification

- Python 3.11 with dev+live groups: **32 passed**
- Python 3.12 with dev+live groups: **32 passed**
- Python 3.13 with dev+live groups: **32 passed**
- Python 3.14 with dev+live groups: **32 passed**
- Coverage with dev+live groups and transient `pytest-cov`: **32 passed, 91% total
  coverage** (`547` statements, `50` missed)
- `uv run ruff format --check .`: **passed**
- `uv run ruff check .`: **passed**
- `uv build`: **source distribution and wheel built**
- Repeated offline reports from identical dataset/responses/seed inputs: **byte-identical**
- Regenerated fixtures: **byte-identical**
- `git diff --check`: **passed**

The synthetic selected-gate result remains:

```text
answered=18/24 accuracy=0.667 risk=0.333 ece=0.2083
```

The recorded-live selected-gate result remains:

```text
answered=23/24 accuracy=0.913 risk=0.087 ece=0.0583
```

## Learnings

- Confidence values are now computed once per decision before iterating threshold gates,
  avoiding repeated validation work while preserving the existing fail-closed checks.
- Empty-answer gates must retain `null` accuracy and selective risk; representing them as
  zero would falsely imply perfect or maximum-risk behavior.
- Threshold sweeps need an explicit exploratory-data warning because choosing the best row
  from the same run and reporting it as confirmatory would inflate the result.

## Changed artifact hashes

```text
7d82f076af78bbe1cae52c47c03a1d6c693dd1efc7b25b693696a28ab8aadd79  README.md
4a8b1d5962ccebb2d2499402c4b7e861f562ea847ac891b0b30890130eaa0676  src/jev_dspy_lab/metrics.py
ccccdcb698a87cfad5e2a0436b06625d7b2a50d2935bdaa1c4b5deb4bbee01f5  src/jev_dspy_lab/benchmark.py
03bf0a8c23f986fe330748f2734c704a8ac7a9b58b2a7c858cb149bb264d26a5  src/jev_dspy_lab/__init__.py
251ee3b11852063f1707e81e1aafd889c37cf2b2d6e3e512a281f5a55755c112  tests/test_metrics.py
0eed5eb67baf967a0ca6da8d55557c1f7a6a625a13d26c1e23b1549de015b8ed  tests/test_benchmark.py
8e730e40d871fb94ad99e523d644a622bb13d50e851e06377af35de1573c2ae3  evidence/benchmark/benchmark.json
6112249193a17f7deeebdd50f78ed2ea6033ef3e2817cc4e6f2c65498faf4197  evidence/benchmark/benchmark.md
fc829638226b372d31993aed5e3134219b997ad6da4389a11c36aeb3aafbea3c  evidence/live/jev-latest/benchmark.json
00e97a7e7fa1482a50034108e2c771b24b4437f72c84c3641d4d0121f2c5999c  evidence/live/jev-latest/benchmark.md
a21726f8d87b13b61b62be5eb02d0b86840704f8a96edc473e7da5a5f946be72  evidence/live/README.md
```
