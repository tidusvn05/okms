---
type: Template
kind: implementation
title: Implementation micro spec template
description: Specify one artifact, behavior change, or structural improvement with essential invariants and implementation checks.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

{{OBSERVABLE_OUTCOME_OR_STRUCTURAL_IMPROVEMENT_AND_WHY_IT_IS_NEEDED}}

## Constraints

- Always: {{ESSENTIAL_AUTHORIZATION_DATA_OR_COMPATIBILITY_INVARIANT}}.
- Never: {{FORBIDDEN_CHANGE_OR_SCOPE_EXPANSION}}.

## Acceptance

- Given {{VALID_CONTEXT}}, When {{ACTION}}, Then {{OBSERVABLE_SUCCESS}}.
- Given {{FAILURE_CONTEXT}}, When {{ACTION}}, Then {{EXPECTED_FAILURE_AND_PRESERVED_STATE}}.
- For a behavior-preserving refactor: {{STRUCTURAL_IMPROVEMENT_AND_RETAINED_BEHAVIOR_OR_NOT_APPLICABLE}}.

## Verify

- Method: {{REAL_PROJECT_COMMANDS_AND_ACCEPTANCE_REVIEW_WITH_APPLICABLE_BASELINE}}.
- Expected: {{SUCCESS_AND_FAILURE_BEHAVIOR_PROVEN}}.
- Tests: {{RELEVANT_TEST_SCOPE_OR_JUSTIFIED_SKIP}}.
