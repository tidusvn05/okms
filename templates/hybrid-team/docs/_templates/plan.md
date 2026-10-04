---
type: Template
title: Plan template
description: Outline the goal, approach, dependencies, progress, and checkpoint for a scoped implementation.
work_status: planned
---

# {{PLAN_ID}} · {{TITLE}}

> Authoring guidance: When the outcome changes or decides changes to existing contracts, insert Baseline and Compatibility between Goal and Approach. Baseline records affected behavior, relevant paths, actual check results or unavailability, and known failures. Compatibility records retained contracts and intentional changes, with migration, rollout, and rollback only when needed. Omit both sections when no existing contracts are affected. Remove this guidance from the saved plan.

## Goal

{{EXPECTED_OUTCOME}}

Out of scope: {{EXCLUSIONS_OR_NONE}}.

## Approach

- {{APPROACH_AND_IMPORTANT_DECISIONS}}

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| {{PLAN_ID}}-MS01 · {{FIRST_OUTCOME}} | — | planned | Pending. |

## Resume

- Current: {{PLAN_ID}}-MS01.
- Next: inspect the relevant code and save its micro spec before implementation.
- Blocker: none.

## Result

Pending.
