---
id: JDL-k6fx
title: "Own-distribution calibration and reliability"
status: closed
priority: 1
type: epic
created_at: 2026-09-20T17:10:43Z
created_by: speed
updated_at: 2026-09-20T18:45:07Z
content_hash: "sha256:ac81530df7ab78f88482770b4adc14e67f3514f4e6e7e0081bad6e6f96afdc77"
closed_at: 2026-09-20T18:45:06Z
close_reason: "Accepted: sole child story accepted and merged with green required CI; epic outcomes verified."
labels: [accepted]
---

## Description
## Description
Advance Jev DSPy Lab from fixed confidence reporting to leakage-safe, own-distribution calibration and reliability analysis. This answers the ecosystem gap: many projects demo fast Jev-like decisions, but few measure whether confidence is honest after refitting on the deployment distribution.

## Epic Outcomes
- Reliability bins expose where confidence diverges from accuracy.
- Log loss joins Brier and ECE.
- Calibration is fitted only on a declared training split and evaluated on a disjoint held-out split.
- A versioned artifact records method, inputs, split membership, parameters, and hashes.
- Existing v0.2.0 benchmark behavior remains backward compatible.

## OUT OF SCOPE
- Live TypeSafe calls or new API credentials.
- Changing recorded responses or request hashes.
- Claiming a new model is equivalent without replay evidence.
- PyPI publication, which remains separately blocked.

## MANDATORY SKILLS
- pvg

## nd_contract
status: new

### evidence
- Operator selected own-distribution calibration and reliability reporting as the Jev v0.3 direction on 2026-09-20.

### proof
- [ ] Pending calibration story acceptance.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-09-20.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-09-20]: Child JDL-xhr2 is accepted and merged at cbd46bd0c8d4168ae7951c8119590961f685e257 after all required Python CI checks passed. The epic outcome for own-distribution calibration, reliability reporting, leakage-safe splits, and versioned provenance is complete. PyPI publication remains explicitly blocked in JDL-aaoi and outside this epic.

## History
- 2026-09-20T18:45:06Z status: open -> closed

## Links


## Comments
