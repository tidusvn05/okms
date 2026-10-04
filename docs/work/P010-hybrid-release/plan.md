---
type: Plan
title: P010 · Publish Hybrid Team
description: Package Hybrid Team for curl installation and publish the user-authorized GitHub prerelease.
work_status: done
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
| [P010-MS02 · Commit, push, and publish](P010-MS02-publication.md) | P010-MS01 | done | Remote main and annotated tag contain release source 2cd287d57de0bfaecb4730d7e78a3b76b83d4533. Public GitHub prerelease hosts all three uploaded assets with matching API/download hashes. The actual unauthenticated curl installer passes dry-run, new setup, repeated customized setup, copied helper join/status and doctor in a disposable dirty Git project; notes, docs, instructions, deny rules, HEAD, index bytes and staging are preserved. Required checker passes 178 documents/seven bundles and all 76 tests pass. |

## Resume

- Current: none; all scoped work is complete.
- Next: none.
- Blocker: none.

## Result

Published [Hybrid Team 0.1.0 (experimental)](https://github.com/tidusvn05/okms/releases/tag/hybrid-team-v0.1.0) from commit 2cd287d57de0bfaecb4730d7e78a3b76b83d4533. The commit includes the authorized review/delegation work, Hybrid Team profile/evidence, curl installer, deterministic builder, and distribution tests. The release tag remains pinned to that source; this completed publication checkpoint is recorded afterward without replacing the tag/assets.

Public assets match the locally checked build:

- Archive SHA256: 0fd9a27a172ad83226df7fca437e299c34aab07ae1fc3af06a45c4a12acb121e.
- Installer SHA256: ef86a4a44cdc2ef1d942a59b009239d1b7d6ee82a6ed3cdc8ccded699cba5bc4.
- SHA256SUMS SHA256: caa58a5704dfee29eb920950b70adf269b6cb0bc25d294c9927cb3a865946f40.

Actual public-download verification is retained locally in ignored `.pilot-runs/hybrid-release-v0.1.0/`. Installation selects docs/okms beside existing docs and keeps subsequent context/runtime customizations. The copied helper works after temporary source cleanup. Doctor reports runtime 0.1.0 and the real Git baseline; readiness remains false because the disposable fixture intentionally has no configured application checks. Its coordinator identity is a scripted local helper owner, not a provider task session. No new task agent or application example verification was run. Native trust, platform/model observations, and the retained live-pilot limits remain unchanged.
