---
type: Plan
title: P006 · Consolidate workflow profiles
description: Keep two standalone workflows and select existing-system obligations from the affected scope rather than a separate profile.
work_status: done
---

# P006 · Consolidate workflow profiles

## Goal

Publish Lite and Plan-first as the two workflows. Automatically apply baseline and compatibility obligations when an outcome affects existing behavior, interfaces, or data. Remove the separate Brownfield distribution without a legacy alias, as the project has no users.

Out of scope: changing task-kind or Goal contracts, rewriting historical work or measurements, and activating a native agent runtime.

## Baseline

- Starting source: clean `main` at `3837251`, distributing three version 0.2.0 profiles. Brownfield uses the Plan-first loop and adds Baseline and Compatibility to its plan.
- Actual recorded checks at that source: P005 document verification passed 115 Markdown files, seven bundles, three payloads, and 12 onboarding scenarios; GitHub rendering and default prompt extraction passed.
- Known evidence limit: the historical v0.2 blocked Goal pilot read an extra general blueprint, and native execution was not exercised. This change does not claim to resolve those observations.

## Compatibility

- Preserve Lite and Plan-first identifiers, micro spec kinds and common sections, Plan and Goal progress rules, adoption preservation, and historical evidence.
- Intentionally remove the Brownfield payload and setup choice; its obligations become conditional guidance within both workflows. Both remaining payloads move to version 0.3.0.
- The project has no users, so there is no deployed installation migration. Fresh setup continues to preserve preexisting project content.

## Approach

- Select implementation for the contract, presentation, and validation outcomes; save each micro spec when its dependencies are ready.
- Keep the standard small plan format, with instructions for conditional Baseline and Compatibility sections. Lite records concise evidence and invariants in its current micro spec.
- Apply obligations to the affected scope, including shared dependencies and mixed new/existing changes; an existing repository alone does not require extra plan sections.
- Publish the changed contracts as version 0.3.0 in both payloads and the maintainer workflow. Keep prior plans and evaluation reports as historical evidence.
- Reduce README setup to two complete prompts, reframe the existing-system example as a Plan-first scenario, and update checks and pilot fixtures for the current profiles.
- Run required document and contract checks, copied-bundle validation, README rendering, and targeted opt-in agent pilots for Lite and Plan-first existing-system work.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P006-MS01 · Scope-based existing-system guidance](P006-MS01-workflow-contracts.md) | — | done | Both copied 16-file bundles pass contract/link checks at 0.3.0 and share the plan/catalog. Review covers standalone existing-code fixes, conditional plan sections, unaffected reports, and shared integration effects. Brownfield distribution removed. |
| [P006-MS02 · Two-workflow setup and examples](P006-MS02-setup-examples.md) | P006-MS01 | done | Two prompts are byte-identical to the prior Plan-first and Lite prompts; default extraction and GitHub rendering pass. Repository links and all three illustrative example bundles pass. Current guidance uses the two workflows and labels prior reports historical. |
| [P006-MS03 · Validation and observed compatibility](P006-MS03-validation.md) | P006-MS02 | done | Required document check passes 105 Markdown files, six bundles, two payloads, and eight onboarding scenarios; 22 contract tests pass. Two fresh CLI pilots pass all criteria, 80 independent behavior cases, and seven original test-method executions. Baseline and contracts precede code changes. All six repository bundles and both observed bundles pass okbase L1 without diagnostics; source/trace/grade hashes match. |

## Resume

- Current: none; P006-MS01 through P006-MS03 are done.
- Next: use either README setup prompt and let the affected scope determine baseline and compatibility obligations.
- Blocker: none.

## Result

Version 0.3.0 distributes two self-contained 16-file workflows: Lite and Plan-first. The separate Brownfield payload and setup choice are removed, with no legacy alias. Both workflows apply existing-system obligations from the affected scope; Lite keeps concise evidence and invariants in its standalone spec, while plans add Baseline and Compatibility only when applicable. README setup, worked examples, maintainer checks, and current pilot fixtures agree with that model.

Required document and contract checks pass, along with copied-bundle checks, GitHub README rendering, eight onboarding scenarios, and OKF L1 lint. Two targeted fresh agent conversations preserve the exercised contracts and record actual baseline evidence before source changes; Lite remains standalone. Published measurements in `evals/workflow-results.json` identify the observed payload and grading sources, and `evals/workflow-report.md` records the outcomes and limits. Twenty-eight prior work and measurement files remain byte-identical. The full routing and Goal matrix was not rerun; native execution remains untested, and section omission is covered by structural fixtures.
