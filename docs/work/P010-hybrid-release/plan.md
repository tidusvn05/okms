---
type: Plan
title: P010 · Publish Hybrid Team
description: Package Hybrid Team for curl installation and publish the user-authorized GitHub prerelease.
work_status: in_progress
---

# P010 · Publish Hybrid Team

## Goal

Commit and push the authorized P007–P009 work together with a usable curl installer, then publish Hybrid Team 0.1.0 as a GitHub prerelease with downloadable assets.

Out of scope: global CLI installation, automated upgrades, provider installation/authentication, and new agent pilots.

## Baseline

Local and remote main are at 2068f31; the repository has no tags or GitHub releases. The authorized changes are uncommitted. Hybrid Team setup requires its complete 44-file source payload; there is no download installer. The required checker passes 174 Markdown files/seven bundles, and all 69 tests pass. The live report retains scoped passes and native startup limits.

## Compatibility

Retain Hybrid Team 0.1.0 and the exact observed runtime payload. Lite and Plan-first remain portable 0.4.0 workflows. Reuse preserving setup without changing project/global configuration beyond its existing contract. Published evaluation observations remain attributable to their frozen sources. Do not distribute credentials, operational state, or raw pilot projects.

## Approach

- Use implementation contracts for distribution and publication; save each spec before its execution.
- Build one deterministic Python-source archive with the complete Hybrid Team payload, licenses, and a file manifest; publish the installer and SHA256SUMS beside it.
- Pin the installer to the named prerelease, verify downloads and extraction before setup, and test both downloaded and offline assets without provider sessions.
- Run required checks, commit all reviewed authorized changes, push main and the release tag without force, and publish assets with experimental/native-activation limits.
- Download the published assets into a disposable project and verify actual curl adoption; retain the results in this plan.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P010-MS01 · Downloadable distribution](P010-MS01-distribution.md) | — | done | Seven distribution tests and all 76 tests pass; checker passes 177 Markdown files/seven bundles; shell syntax and git diff --check pass. Two builds produce identical bytes. Assets contain all 44 unchanged payload files, two licenses, and a hashed release manifest. |
| [P010-MS02 · Commit, push, and publish](P010-MS02-publication.md) | P010-MS01 | in_progress | Pending. |

## Resume

- Current: P010-MS02.
- Next: commit the reviewed work, push main/tag, publish the three verified assets, and test the actual public downloads in a disposable project.
- Blocker: none.

## Result

Pending.
