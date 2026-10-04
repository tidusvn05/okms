---
type: Template
kind: investigation
title: Investigation micro spec template
description: Answer an observed-system question through bounded hypotheses and reproducible evidence without an implicit repair.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Determine {{QUESTION_ABOUT_OBSERVED_BEHAVIOR}}. Deliver {{FINDINGS_PATH_AND_REQUIRED_CONCLUSION}}.

## Constraints

- Always: distinguish confirmed observations, hypotheses, and remaining uncertainty; stay within {{EVIDENCE_AND_EXPERIMENT_SCOPE}}.
- Never: change application behavior without authorized repair scope or report an unsupported cause as confirmed.

## Acceptance

- Findings connect {{REQUIRED_CONCLUSION_OR_HYPOTHESES}} to specific code, logs, inputs, or experiment results that another reader can reproduce.
- Relevant alternatives are tested or bounded, and unresolved gaps identify the next concrete observation needed.
- If the required conclusion cannot be supported, work remains incomplete with the missing evidence recorded; uncertainty does not silently replace the requested outcome.

## Verify

- Method: {{REAL_OBSERVATION_COMMANDS_AND_EVIDENCE_REVIEW}}.
- Expected: {{EVIDENCE_NEEDED_TO_SUPPORT_OR_RULE_OUT_THE_REQUESTED_EXPLANATION}}.
- Tests: {{BOUNDED_EXPERIMENT_SCOPE_OR_REASON_TESTS_ARE_NOT_NEEDED}}.
