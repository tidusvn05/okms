---
type: Template
kind: design
title: Design micro spec template
description: Make a scoped system decision with explicit drivers, viable alternatives, consequences, and compatibility review.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Decide {{SYSTEM_OR_INTERFACE_QUESTION}} and save {{DECISION_DOCUMENT_PATH}} for {{AFFECTED_CONSUMERS}}.

## Constraints

- Always: honor {{FUNCTIONAL_NONFUNCTIONAL_AND_COMPATIBILITY_DRIVERS}} and distinguish measurements from estimates.
- Never: treat a design decision as authorization for implementation or conceal an unresolved contract change.

## Acceptance

- The decision explains viable alternatives and tradeoffs, or why only one alternative is viable, with consequences and rejected options.
- Review of {{IMPORTANT_SCENARIOS_AND_EXISTING_INTERFACES}} supports the decision and identifies migration or rollout needs when relevant.
- Material unknowns are resolved or recorded as blockers; implementation detail remains in the design artifact and eventual code.

## Verify

- Method: {{REVIEW_AGAINST_CODE_DOCS_REQUIREMENTS_AND_SCENARIOS}}.
- Expected: {{DECISION_SATISFIES_THE_PROJECT_DRIVERS_AND_RETAINED_CONTRACTS}}.
- Tests: {{NECESSARY_SPIKE_OR_MODEL_CHECK_OR_JUSTIFIED_DOCUMENT_REVIEW}}.
