---
type: Template
kind: research
title: Research micro spec template
description: Answer a bounded question with attributable source evidence, explicit comparison criteria, and stated limits.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Answer {{RESEARCH_QUESTION}} in {{REPORT_PATH}}, using {{SOURCE_SCOPE_AND_RELEVANT_DATE_OR_VERSION}}.

## Constraints

- Always: attribute material claims, distinguish observations from inference, and compare using {{DECISION_CRITERIA}}.
- Never: invent sources, imply incompatible measurements are directly comparable, or silently exceed {{RESEARCH_SCOPE}}.

## Acceptance

- The report answers the scoped question with checked references and a comparison using the stated criteria.
- Conclusions follow from the cited evidence; uncertainty, conflicting findings, source limitations, and unanswered parts are explicit.
- Any recommendation stays within the evidence and requested scope, with a concrete next action when more evidence is needed.

## Verify

- Method: {{OPEN_SOURCES_CHECK_DATES_AND_REVIEW_CLAIM_SUPPORT}}.
- Expected: {{SUPPORTED_ANSWER_AND_COMPARISON_WITH_LIMITS}}.
- Tests: {{NECESSARY_REPRODUCTION_OR_REASON_SOURCE_REVIEW_SUFFICES}}.
