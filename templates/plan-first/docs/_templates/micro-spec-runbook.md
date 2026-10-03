---
type: Template
kind: runbook
title: Runbook micro spec template
description: Author an operator procedure with prerequisites, expected outputs, failure handling, and honest rehearsal evidence.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Create {{RUNBOOK_PATH}} so {{OPERATOR}} can perform {{PROCEDURE}} when {{TRIGGER}}.

## Constraints

- Always: use actual project commands, identify prerequisites and expected results, and stay within {{AUTHORIZED_REHEARSAL_SCOPE}}.
- Never: imply an unexecuted step was tested or turn runbook authoring into unrequested operational changes.

## Acceptance

- The runbook provides trigger, prerequisites, ordered steps, verification, failure/stop conditions, and rollback or a reason rollback is inapplicable.
- Commands and paths match the project; a relevant dry run or bounded rehearsal supports the procedure, with untested environments and steps identified.
- A reader can determine success and the next action if {{IMPORTANT_FAILURE_CASE}} occurs.

## Verify

- Method: {{REAL_COMMAND_REVIEW_AND_SAFE_REHEARSAL_COMMANDS}}.
- Expected: {{EXPECTED_OUTPUTS_AND_PRESERVED_STATE}}.
- Tests: {{REHEARSAL_SCOPE_AND_EXPLICIT_UNTESTED_LIMITS}}.
