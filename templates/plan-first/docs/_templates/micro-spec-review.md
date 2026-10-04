---
type: Template
kind: review
title: Review micro spec template
description: Assess a defined artifact or revision and report supported findings, examined scope, and verification limits.
---

# {{SPEC_ID}} · {{TITLE}}

## Intent

Review {{ARTIFACT_OR_REVISION_AND_COMPARISON_BASE}} for {{REVIEW_CRITERIA}} and save findings in {{REPORT_PATH}}.

## Constraints

- Always: identify the actual scope and revision, distinguish supported findings from assumptions, and retain {{PROTECTED_FILES_AND_CONTRACTS}}.
- Never: turn review into an unrequested repair or imply that no findings proves the entire system correct.

## Acceptance

- The report identifies the examined scope/revision, criteria, and checked areas.
- Each actionable finding includes a location, impact or severity, and supporting code reasoning, observation, or test evidence; uncertainty is explicit.
- Document links target actual files; put source line numbers in the link text rather than appending them to the filename.
- A report with no findings still identifies coverage and limits. Unavailable evidence required for a conclusion leaves that conclusion incomplete.

## Verify

- Method: {{CHECK_FINDINGS_AGAINST_ACTUAL_ARTIFACT_AND_REQUIRED_PROJECT_CHECKS}}.
- Expected: {{SUPPORTED_FINDINGS_OR_BOUNDED_NO_FINDINGS_WITH_LIMITS}}.
- Tests: {{NECESSARY_PROBES_OR_JUSTIFIED_REVIEW_ONLY_SCOPE}}.
