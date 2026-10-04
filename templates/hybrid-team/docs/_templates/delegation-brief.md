---
type: Template
title: Delegation brief template
description: Assign a bounded part of the current micro spec with sufficient context, explicit ownership, and a required result.
---

# {{ASSIGNMENT_TITLE}}

## Reference

- Parent contract/progress owner: {{ACTUAL_SPEC_AND_PLAN_OR_STANDALONE_SPEC_REFERENCES}}.
- Context: {{REVISION_OR_WORKTREE_NECESSARY_FILES_AND_INSTRUCTIONS}}.

## Intent

{{BOUNDED_PART_OF_THE_PARENT_OUTCOME_AND_REQUIRED_RESULT}}

## Constraints

- Scope/ownership: {{PERMITTED_READS_AND_EXPLICITLY_OWNED_WRITES_OR_READ_ONLY}}.
- Shared progress and index updates belong to {{COORDINATOR}}. {{STOP_RETURN_CONDITION_AND_EXISTING_LIMITS}}.

## Acceptance

Apply {{REFERENCED_PARENT_CRITERIA}} to the assigned scope. Return {{RESULT_LOCATION_OR_MESSAGE_AND_COVERAGE}}; do not redefine parent acceptance.

## Verify

{{ACTUAL_REVIEW_OR_CHECK_METHOD_AND_REQUIRED_EVIDENCE}}. Return missing or unexecuted necessary checks to the coordinator; do not close the parent work.
