---
id: JDL-k6fx
title: "Own-distribution calibration and reliability"
status: open
priority: 1
type: epic
created_at: 2026-09-20T17:10:43Z
created_by: speed
updated_at: 2026-09-20T17:10:43Z
content_hash: "sha256:d01441556a843fe9115015bf67b2395460cbd351beab793e676678463306f486"
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


## History


## Links


## Comments
