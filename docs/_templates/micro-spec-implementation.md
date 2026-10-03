---
type: Template
kind: implementation
title: Implementation micro spec template
description: Describe one new or intentionally changed behavior, its essential invariants, and concrete implementation checks.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

{{OBSERVABLE_BEHAVIOR_AND_WHY_IT_IS_NEEDED}}

## Constraints

- Always: {{ESSENTIAL_AUTHORIZATION_DATA_OR_COMPATIBILITY_INVARIANT}}.
- Never: {{FORBIDDEN_CHANGE_OR_SCOPE_EXPANSION}}.

## Acceptance

- Given {{VALID_CONTEXT}}, When {{ACTION}}, Then {{OBSERVABLE_SUCCESS}}.
- Given {{FAILURE_CONTEXT}}, When {{ACTION}}, Then {{EXPECTED_FAILURE_AND_PRESERVED_STATE}}.

## Verify

- Method: {{REAL_PROJECT_COMMANDS_AND_ACCEPTANCE_REVIEW}}.
- Expected: {{SUCCESS_AND_FAILURE_BEHAVIOR_PROVEN}}.
- Tests: {{RELEVANT_TEST_SCOPE_OR_JUSTIFIED_SKIP}}.
