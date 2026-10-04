---
type: Plan
title: P011 · Automatic tag releases
description: Automate Hybrid Team releases from versioned tags and document release-aware installation.
work_status: in_progress
---

# P011 · Automatic tag releases

## Goal

Configure GitHub Actions to check, package, and publish every valid Hybrid Team release tag, and update README installation to use the published distribution.

Out of scope: retagging/replacing existing releases, publishing a new runtime version, changing portable profiles, or starting provider task sessions.

## Baseline

The tree is clean at 588fab7 with no Actions workflows. Hybrid Team 0.1.0 has a public manually created prerelease; GitHub Actions is enabled. Current checks pass 178 Markdown files/seven bundles and 76 tests. Installer downloads require a pinned numeric version; prereleases cannot use GitHub's latest stable endpoint. README's agent setup still clones the repository for Hybrid Team.

## Compatibility

Retain the observed runtime payload, preserving adoption, numeric --version and offline installation, existing tag/assets, and portable 0.4.0 contracts. Hybrid Team tags stay namespaced as hybrid-team-vX.Y.Z. Installation may now resolve the newest complete published Hybrid Team release, including prereleases; this does not authorize upgrades of an installed project.

## Approach

- Use implementation for the two artifact changes; save each spec just before executing it.
- Add read-only CI on main/PRs and a tag workflow that checks the committed version before tests/build; use scoped publication permissions and verified action revisions.
- Package and rehearse installation before publishing; preserve prior releases and keep manual workflow dispatch as a nonpublishing rehearsal.
- Resolve complete matching releases by numeric version with pagination, preserving explicit pins and offline assets; document default/latest, version pinning, and tag publication.
- Run required checks, lint workflows, activate the authorized changes on GitHub, and observe CI/manual rehearsal without creating a new release tag.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P011-MS01 · Tag release automation](P011-MS01-automation.md) | — | done | All 77 tests and checker (181 documents/seven bundles) pass. actionlint 1.7.12 accepts both workflows; extracted package/checksum/setup steps execute successfully. Tag mismatch rejects writes and notes pin the version. GitHub activation/rehearsal is included in final verification. |
| [P011-MS02 · Release-aware install and documentation](P011-MS02-install.md) | P011-MS01 | in_progress | All 82 tests, checker (183 documents/seven bundles), installer syntax, actionlint, and extracted workflow steps pass. Genuine public 0.1.0 latest dry-run/new install and pinned repeat preserve project docs/instructions/settings, dirty Git HEAD/index, and custom context; helper works. Evidence: `.pilot-runs/hybrid-latest-install/result.json`. GitHub activation/rehearsal remains. |

## Resume

- Current: P011-MS02.
- Next: push the reviewed workflow/installer/docs, verify the served entrypoint, and observe GitHub CI and the nonpublishing rehearsal.
- Blocker: none.

## Result

Pending.
