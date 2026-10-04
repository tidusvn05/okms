---
type: MicroSpec
kind: implementation
title: P012-MS01 · Namespaced metadata
description: Identify portable workflows with namespaced keys while recognizing earlier unprefixed installations.
---

# P012-MS01 · Namespaced metadata

## Intent

Portable workflow frontmatter no longer uses keys that documentation site generators reserve, and setup still recognizes installations made before the rename.

## Constraints

- Always: payloads and the maintainer workflow use `okms_template` and `okms_template_version` with one shared version.
- Always: recognizing an existing installation accepts the namespaced keys and the unprefixed pre-0.4.1 keys.
- Never: change Hybrid Team metadata, payload inventory, or task contracts in this outcome.

## Acceptance

- Given a payload workflow with an unprefixed `template` key, when the checker runs, then it reports the missing namespace.
- Given a project whose installation carries only `template`/`template_version`, when setup runs, then it reuses that installation unchanged.
- README prompts, manual setup, and CONTRIBUTING describe both key forms and version 0.4.1.

## Verify

- Method: `python3 scripts/check_docs.py` and `python3 -m unittest discover -s tests`; temporarily remove legacy recognition to confirm the new scenario fails.
- Expected: both pass with the new legacy onboarding scenarios and unit tests.
- Tests: `tests/test_contracts.py` identity tests; `onboarding_smoke` legacy scenarios.
