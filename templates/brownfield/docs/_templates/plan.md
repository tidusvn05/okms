---
type: Template
title: Plan template
description: Outline the goal, approach, dependencies, progress, and checkpoint for a scoped implementation.
work_status: planned
---

# {{PLAN_ID}} · {{TITLE}}

## Goal

{{EXPECTED_OUTCOME}}

Out of scope: {{EXCLUSIONS_OR_NONE}}.

## Baseline

- Existing behavior: {{OBSERVED_BEHAVIOR_AND_RELEVANT_CODE_OR_TEST_PATHS}}.
- Checks: {{ACTUAL_BASELINE_COMMANDS_AND_RESULTS_OR_UNAVAILABLE_REASON}}.
- Known failures: {{KNOWN_FAILURES_WITH_EVIDENCE_OR_NONE}}.

## Compatibility

- Preserve or intentionally change: {{PUBLIC_BEHAVIOR_INTERFACES_DATA_AND_INVARIANTS}}.
- Migration, rollout, and rollback: {{RELEVANT_ACTIONS_AND_VERIFICATION_OR_NOT_APPLICABLE_WITH_REASON}}.

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
