---
type: Template
title: Worker result template
description: Return scoped observations and actual evidence to the parent progress owner with remaining gaps and a next action.
---

# {{RESULT_TITLE}}

## Reference

- Parent/assignment: {{ACTUAL_CONTRACT_AND_ASSIGNMENT_REFERENCES}}.
- Examined scope/revision/worktree: {{ACTUAL_SCOPE_AND_REVISION_WITH_CHANGED_PATHS_IF_ANY}}.

## Result

{{FINDINGS_OR_CHANGED_PATHS_WITH_SUPPORTING_LOCATIONS_AND_IMPACT}}

## Evidence

{{ACTUAL_COMMAND_OR_REVIEW_METHOD_RESULT_AND_ARTIFACT_REFERENCES}}

## Remaining

{{PARTIAL_COVERAGE_FAILED_OR_UNEXECUTED_CHECKS_AND_BLOCKER_OR_NONE}}

## Next

{{CONCRETE_ACTION_FOR_THE_COORDINATOR_TO_VERIFY_OR_CONTINUE_THE_PARENT_OUTCOME}}
