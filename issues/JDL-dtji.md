---
id: JDL-dtji
title: "Release jev-dspy-lab 0.2.0"
status: in_progress
priority: 1
type: task
created_at: 2026-09-17T23:02:22Z
created_by: speed
updated_at: 2026-09-17T23:02:43Z
content_hash: "sha256:e7d120bfb56c836d77caeb00a16648d15cdbe852570ff630df60c7ff95192460"
parent: JDL-d67r
assignee: dev-JDL-dtji
---

## Description
## Description
Bump and verify package metadata, publish user-facing release notes, build 0.2.0 artifacts, tag the accepted release, and create a GitHub Release with source distribution and wheel assets. PyPI publication is out of scope unless separately authorized.

## Acceptance Criteria
- [ ] AC #1: `pyproject.toml` and `uv.lock` both identify `jev-dspy-lab` as version `0.2.0`.
- [ ] AC #2: A user-facing changelog documents v0.2.0 threshold-sensitivity functionality, artifact/report changes, and the no-breaking-changes boundary.
- [ ] AC #3: Python 3.11, 3.12, 3.13, and 3.14 dev+live suites pass with no skipped tests.
- [ ] AC #4: Coverage, formatting, linting, lock consistency, package build, `pvg verify`, metric gates, and whitespace checks pass.
- [ ] AC #5: Regenerated synthetic and recorded-live reports remain byte-identical.
- [ ] AC #6: Built source distribution and wheel are versioned `0.2.0`, installable/metadata-inspectable, and published as GitHub Release assets.
- [ ] AC #7: `v0.2.0` is an annotated tag on the accepted release commit, and the GitHub Release points to that tag with the changelog notes.
- [ ] AC #8: No PyPI publication occurs without separate explicit authorization.

## Design
Add a permanent release-metadata test that keeps `pyproject.toml`, `uv.lock`, and the changelog synchronized. Generate release artifacts from the accepted story commit and publish them through the repository-owned GitHub Release.

## Notes
Base SHA: `ef3a2dc4b48cba373ebf8559bf1f7ff4aafe3b4d`.

## Acceptance Criteria


## Design


## Notes


## History
- 2026-09-17T23:02:24Z status: open -> in_progress
- 2026-09-17T23:02:24Z claimed by dev-JDL-dtji

## Links
- Parent: [[JDL-d67r]]

## Comments
