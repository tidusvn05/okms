---
type: Plan
title: P001 · Build okms v0.1
description: Deliver three portable micro spec workflows with English documentation and checked examples.
work_status: done
---

# P001 · Build okms v0.1

## Goal

Create an open-source collection of standalone Lite, Plan-first, and Brownfield templates that agents can copy into any project. Use English throughout, make okbase optional, retain completed specs as plan history, and let agents continue after saving a plan.

Out of scope: an installer, automatic template upgrades, agent orchestration, and publishing a remote repository or release.

## Approach

- Establish an OKF v0.2-compatible document contract and use Plan-first in this repository.
- Package seven Markdown files per template; keep each copied bundle self-contained.
- Author a micro spec just before its implementation and retain progress in the plan.
- Provide setup instructions that preserve existing docs and add one agent instruction line.
- Supply honest worked examples and verify structure, onboarding, resume behavior, and optional okbase compatibility.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P001-MS01 · Document contract](P001-MS01-document-contract.md) | — | done | YAML and section checks passed for the six concept documents; reviewed progress ownership and the saved-plan checkpoint. |
| [P001-MS02 · Template variants](P001-MS02-template-variants.md) | P001-MS01 | done | All three relocated seven-file payloads passed metadata/link checks; okbase L1 reported zero errors and warnings for every profile. |
| [P001-MS03 · Examples and distribution](P001-MS03-examples-distribution.md) | P001-MS02 | done | README and contribution guidance reviewed; license texts checked; all three illustrative example bundles passed okbase L1 with zero errors and warnings. |
| [P001-MS04 · Validation and final review](P001-MS04-validation.md) | P001-MS03 | done | Checker passed 57 Markdown files, seven bundles, and 12 setup fixtures; nine negative fixtures rejected cleanly; seven okbase L1 runs and git diff --check passed. |

## Resume

- Current: none; all scoped items are done.
- Next: none; v0.1 artifacts are ready for review.
- Blocker: none.

## Result

Delivered Lite, Plan-first, and Brownfield as self-contained seven-file English payloads, with setup instructions, one instruction pointer, worked examples, contribution guidance, and MIT OR Apache-2.0 license texts. This plan and each current micro spec were saved before their implementation; specs were created one at a time.

Verification:

- `.venv/bin/python scripts/check_docs.py`: passed 57 Markdown files, seven OKF bundles, three payloads, and 12 disposable setup scenarios. Repeated setup preserved context, work sentinels, original docs, agent instructions, and the installed profile.
- Nine disposable negative fixtures: broken link, duplicate YAML key, missing done evidence, premature plan completion, duplicate progress ownership, dependency cycle, and non-scalar state/type/version were rejected without tracebacks.
- `okbase -b BUNDLE lint --level L1 --json`, using a CLI built from the neighboring okbase source checkout: all seven bundles reported zero errors and zero warnings.
- `git diff --check`: passed. The saved Resume checkpoint was recovered from files before final review.

Limits: onboarding checks exercise a fixture model of the documented copy guards; they do not invoke an independent agent. Example applications are not included and their application checks were not run. The agent-pilot procedure is documented in CONTRIBUTING.md for a real destination project.
