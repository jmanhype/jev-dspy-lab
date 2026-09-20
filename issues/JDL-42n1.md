---
id: JDL-42n1
title: "Preserve real own-distribution Jev calibration report"
status: closed
priority: 0
type: epic
labels: [evidence, accepted]
created_at: 2026-09-20T19:49:18Z
created_by: speed
updated_at: 2026-09-20T20:15:10Z
content_hash: "sha256:efd7dd844d99230116c0a8f7e4532cb4adcf8a4fa74ebf3cce1f154adb5131f3"
closed_at: 2026-09-20T20:15:10Z
close_reason: "Accepted: sole child story accepted and merged with green required CI; epic outcomes verified."
---

## Description
## USER INTENT
The operator wants the accepted calibration implementation to produce a durable real report on Jev's own recorded decision distribution.

## Epic Outcomes
- The recorded `jev-latest` decisions are replayed without network access.
- Leakage-safe train/held-out refit produces a checked-in versioned calibration artifact.
- Raw and calibrated Brier, log loss, ECE, selective risk, and coverage are preserved with split/model provenance.
- The report is reproducible and covered by tests and CI.

## OUT OF SCOPE
- Live TypeSafe/Jev inference.
- PyPI publication.
- Modifying recorded requests/responses or request hashes.
- Claiming general Jev quality beyond this recorded distribution.

## nd_contract
status: new

### evidence
- Operator selected a real durable Jev calibration report as the next phase on 2026-09-20.

### proof
- [ ] Pending report story acceptance.

## Acceptance Criteria


## Design


## Notes
## PM Decision
ACCEPTED [2026-09-20]: Child JDL-urut accepted and merged at b65a738c9da2e192197eb65c5af4405ac81b38df after all required Python CI checks passed. The epic outcome is complete: the real recorded distribution now has a durable, provenance-bound, portable calibration report.

## History
- 2026-09-20T20:15:10Z status: open -> closed

## Links


## Comments
