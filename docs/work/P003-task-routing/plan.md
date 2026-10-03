---
type: Plan
title: P003 · Add task routing and bounded goal loops
description: Expand portable workflows with task blueprints, selective routing, recoverable goals, and observed evaluation.
work_status: in_progress
---

# P003 · Add task routing and bounded goal loops

## Goal

Ship okms v0.2 with six task-specific micro spec blueprints, a general fallback, automatic selection through a small catalog, and a Goal contract with bounded portable execution and capability-based native integration guidance. Preserve the three installed profiles, historical work, and just-in-time spec creation. Verify routing and goal recovery in actual independent agent sessions, then push the checked source to the authorized repository.

Out of scope: an installer, autonomous background service, model classifier dependency, hard-coded unsupported native APIs, and treating a small pilot as guaranteed classification.

## Approach

- Keep Intent / Constraints / Acceptance / Verify and the existing plan table; select a task kind independently of the installed profile.
- Share catalog, blueprints, and goal guidance across self-contained payloads; change all profile versions to `0.2.0` together.
- Preserve kindless legacy specs. Store `kind` in new specs, and load only the chosen blueprint for the next outcome.
- Goals reference plans, reserve a bounded attempt before execution, and preserve counters and checkpoints across sessions. Budget exhaustion leaves incomplete work incomplete.
- Extend static guards and negative fixtures; reuse the existing external trace observer for fresh routing and loop pilots without modifying historical measurements.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P003-MS01 · Portable task contracts](P003-MS01-task-contracts.md) | — | done | Shared YAML and byte comparisons pass across all profiles; seven micro spec contracts keep four sections and Goal defines bounded execution. Workflow links follow in MS02. |
| [P003-MS02 · Routing and goal workflow](P003-MS02-routing-loop.md) | P003-MS01 | done | All links resolve; each profile has 16 Markdown files at v0.2.0. Routing, bounded execution, upgrade guidance, and illustrative walkthrough reviewed. |
| [P003-MS03 · Contract validation](P003-MS03-validation.md) | P003-MS02 | done | Checker passes 106 Markdown files and 12 setup scenarios; all 18 contract tests pass. Maintainer docs and all three 16-file payloads pass okbase L1 with zero diagnostics. |
| [P003-MS04 · Observed routing pilots](P003-MS04-routing-pilots.md) | P003-MS03 | done | `evals/routing-report.md` retains 15 fresh conversations across two drafts, 240 independent behavior executions, and 47 original test executions. Eight of nine latest scenarios meet every criterion; blocked Goal retains one extra general blueprint read. All seven latest output bundles pass L1 with zero diagnostics. |
| [P003-MS05 · Final review and publication](P003-MS05-publication.md) | P003-MS04 | in_progress | Final source and measurements are checked; publication pending. |

## Resume

- Current: P003-MS05.
- Next: review final source, links, and published measurements; complete required checks and push the authorized commit, verifying remote SHA and a clean tree.
- Blocker: none.

## Result

Pending. P001 and P002 remain historical evidence for v0.1.
