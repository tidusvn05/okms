---
type: Template
title: Goal template
description: Define an explicit bounded outcome, linked plans, completion evidence, stop conditions, and a persistent loop checkpoint.
work_status: planned
execution: portable
max_iterations: 5
iterations_used: 0
stop_reason: none
---

# {{GOAL_ID}} · {{TITLE}}

## Goal

{{OBSERVABLE_FINAL_OUTCOME}}

## Scope

- Included: {{AUTHORIZED_WORK}}.
- Excluded: {{EXCLUSIONS_OR_NONE}}.
- Work plans: {{PLAN_IDS_AS_TEXT_OR_LINKS_TO_CREATED_PLANS}}.

## Completion

- [ ] {{MEASURABLE_COMPLETION_CRITERION_AND_REQUIRED_EVIDENCE}}.
- [ ] {{REQUIRED_INTERACTION_OR_PROJECT_CHECKS}}.

## Execution

- Mode: portable; use native only with an actual configured goal capability.
- Limit: 5 attempts unless the user specifies another limit; set `max_iterations` to the selected value.
- Adapter: {{NONE_FOR_PORTABLE_OR_ACTUAL_NATIVE_MAPPING_AND_RUNTIME_REFERENCE}}.
- Plans own item states and evidence; this file owns the overall goal and its attempt counter.

## Stop

- Stop when Completion is supported and linked scoped plans are closed, when the attempt limit is reached, when work cannot progress, or when the user stops it.
- Budget exhaustion preserves incomplete work and records `stop_reason: iteration_limit`; completion requires evidence.

## Resume

- Current: {{CURRENT_PLAN_ITEM_AND_ATTEMPT_OR_NOT_STARTED}}.
- Next: {{NEXT_CONCRETE_ACTION}}.
- Blocker: {{MISSING_INPUT_OR_NONE}}.

## Result

Pending.
