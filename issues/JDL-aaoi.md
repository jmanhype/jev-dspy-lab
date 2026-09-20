---
id: JDL-aaoi
title: "Publish jev-dspy-lab 0.2.0 to PyPI"
status: blocked
priority: 1
type: task
created_at: 2026-09-17T23:15:13Z
created_by: speed
updated_at: 2026-09-20T19:49:32Z
content_hash: "sha256:6c2703969a01502c66067c93f9cd89f97406cf2e91b5959f7a12ab2ef7d92da8"
---

## Description
Publish the verified v0.2.0 wheel and sdist to PyPI. Current blocker: the local ~/.pypirc contains a correctly shaped __token__/pypi- API token, but upload.pypi.org rejected it with 403 Invalid or non-existent authentication information. The project name remains available and no artifact was uploaded. A fresh account-scoped PyPI API token or configured GitHub trusted publisher is required; never paste the token into chat.

## Acceptance Criteria


## Design


## Notes
BLOCKED: PyPI rejected the existing local API token with 403 Invalid or non-existent authentication information. Verified artifact hashes: wheel 49fb27944e0d9886b9e9749ced2e90fae4fabbe38de1b325a7f1fefb75d4fcb4; sdist 7fb4e031325bf111eff3bb2778d93e5c9546e7a230e0d253b52c2abb3616a01f. PyPI reports the project name as still available. No GitHub repository PyPI secret exists.
## MANDATORY SKILLS

- None identified; blocked credential story requires no code skill.

## Observable Outcome

The user can see a failed upload attempt and a precise credential blocker; no artifact is published.

## History
- 2026-09-17T23:15:13Z status: open -> blocked

## Links


## Comments
