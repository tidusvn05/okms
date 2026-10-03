---
type: Template
kind: bugfix
title: Bugfix micro spec template
description: Correct an observed contract violation with reproducible failure evidence and focused regression verification.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Correct {{OBSERVED_FAILURE}} so {{EXPECTED_BEHAVIOR}}. Reproduction: {{INPUTS_OR_EXISTING_ISSUE_AND_RELEVANT_PATHS}}.

## Constraints

- Always: {{PUBLIC_CONTRACT_OR_DATA_INVARIANT_TO_PRESERVE}}.
- Never: weaken the regression or acceptance to excuse the original failure; {{OTHER_FORBIDDEN_CHANGE}}.

## Acceptance

- The original failure is demonstrated against the unchanged implementation, or linked to previously recorded reproducible evidence.
- Given {{ORIGINAL_FAILURE_INPUT}}, When {{ACTION_AFTER_REPAIR}}, Then {{CORRECT_RESULT}}.
- Given {{IMPORTANT_UNAFFECTED_CASE}}, When {{ACTION}}, Then {{PRESERVED_RESULT}}.

## Verify

- Method: {{BEFORE_AND_AFTER_REPRODUCTION_COMMANDS_AND_REQUIRED_CHECKS}}.
- Expected: the original defect is observed before repair and the regression passes afterward, with {{COMPATIBILITY_CHECK}}.
- Tests: {{REGRESSION_TEST_PATHS_AND_SCOPE}}.
