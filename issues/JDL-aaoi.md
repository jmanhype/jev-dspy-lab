---
id: JDL-aaoi
title: "Publish jev-dspy-lab 0.2.0 to PyPI"
status: blocked
priority: 1
type: task
created_at: 2026-09-17T23:15:13Z
created_by: speed
updated_at: 2026-09-17T23:15:13Z
content_hash: "sha256:3002e22e201fca69f524ba7f9eb4a50778e3fe63c0a98e2cbe1266446dadeb5e"
---

## Description
Publish the verified v0.2.0 wheel and sdist to PyPI. Current blocker: the local ~/.pypirc contains a correctly shaped __token__/pypi- API token, but upload.pypi.org rejected it with 403 Invalid or non-existent authentication information. The project name remains available and no artifact was uploaded. A fresh account-scoped PyPI API token or configured GitHub trusted publisher is required; never paste the token into chat.

## Acceptance Criteria


## Design


## Notes
BLOCKED: PyPI rejected the existing local API token with 403 Invalid or non-existent authentication information. Verified artifact hashes: wheel 49fb27944e0d9886b9e9749ced2e90fae4fabbe38de1b325a7f1fefb75d4fcb4; sdist 7fb4e031325bf111eff3bb2778d93e5c9546e7a230e0d253b52c2abb3616a01f. PyPI reports the project name as still available. No GitHub repository PyPI secret exists.

## History
- 2026-09-17T23:15:13Z status: open -> blocked

## Links


## Comments
