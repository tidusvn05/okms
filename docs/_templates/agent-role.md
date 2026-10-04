---
type: Template
title: Agent role template
description: Define reusable specialist instructions independently of task acceptance, progress, or native agent configuration.
---

# {{ROLE_NAME}}

## Mission

{{SPECIALIST_RESPONSIBILITY_AND_BOUNDARY}}

## Trigger

Use for {{APPLICABLE_ASSIGNMENTS}}. {{WHEN_ANOTHER_ROLE_OR_MAIN_AGENT_SHOULD_HANDLE_THE_WORK}}

## Authority

Follow the caller's referenced project instructions and parent contract. {{PERMITTED_READ_WRITE_SCOPE_AND_RUNTIME_TOOLS}}. Shared plan, index, and progress updates belong to the coordinator.

## Output

Return {{EXPECTED_RESULT_AND_EVIDENCE_SHAPE}} for the assigned scope. Distinguish actual evidence, assumptions, partial coverage, and unexecuted checks.

## Escalation

Return {{MISSING_INPUT_OR_OUT_OF_SCOPE_CONDITION}} with the next action. Do not expand scope, redefine acceptance, or declare the parent work complete.
