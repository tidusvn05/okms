---
type: MicroSpec
kind: implementation
title: P011-MS01 · Tag release automation
description: Release checked committed payloads automatically from matching Hybrid Team tags.
---

# P011-MS01 · Tag release automation

## Intent

Make pushing a versioned Hybrid Team tag sufficient to build and publish its verified distribution.

## Constraints

- Always: reject a tag that differs from the committed runtime version before publishing; require repository checks and installation rehearsal.
- Always: limit release writes to the tag publication job, use verified action revisions, and preserve published tags/assets.
- Never: publish from pull requests/manual rehearsals, replace an existing release, or invoke provider task sessions in CI.

## Acceptance

- Main/PR CI checks the documented Python support boundary and current runtime under read-only permissions.
- A valid namespaced tag runs checks, builds archive/installer/checksums and notes, rehearses setup, and creates an experimental prerelease with all three assets.
- Invalid tag/version combinations fail before asset writes; failed checks prevent the publication job.
- Manual dispatch rehearses checks/build/setup without release permission or a publishing job; reruns preserve existing releases.

## Verify

- Method: tag-validation/notes tests, actionlint, required repository checker/test suite, and GitHub workflow observations after activation.
- Expected: current assets remain unchanged; positive build/rehearsal succeeds and mismatch fails before publication.
- Tests: exercise builder validation and generated pinned notes; use actual Actions rehearsal where available without publishing a new tag.
