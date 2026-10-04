---
type: Template
kind: general
title: Micro spec template
description: Define a small verifiable outcome when no specialized task blueprint fits, retaining the common contract.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

{{ONE_OBSERVABLE_OUTCOME_ITS_PURPOSE_AND_DELIVERABLE}}

## Constraints

- Always: {{ESSENTIAL_INVARIANT}}.
- Never: {{FORBIDDEN_BEHAVIOR}}.

## Acceptance

- Given {{CONTEXT}}, When {{ACTION}}, Then {{OBSERVABLE_RESULT}}.
- Given {{IMPORTANT_FAILURE_CASE}}, When {{ACTION}}, Then {{EXPECTED_FAILURE_AND_PRESERVED_STATE}}.

## Verify

- Method: {{REAL_COMMAND_OR_REVIEW_METHOD}}.
- Expected: {{EXPECTED_RESULT}}.
- Tests: {{RELEVANT_TEST_SCOPE_OR_REASON_TESTS_ARE_UNNECESSARY}}.
