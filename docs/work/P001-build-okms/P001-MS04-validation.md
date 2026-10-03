---
type: MicroSpec
title: P001-MS04 · Validate the initial release
description: Verify document interoperability, progress consistency, and repeatable adoption without implying agent compliance was measured.
---

# P001-MS04 · Validate the initial release

## Intent

Give maintainers a repeatable read-only document check and demonstrate payload portability and adoption preservation in temporary projects, then close the repository's implementation plan with actual evidence.

## Constraints

- Always: parse YAML with a real parser and check links, indexes, shared formats, state ownership, dependencies, and truthful completion evidence.
- Always: keep test fixtures outside project work, preserve installed context and history on repeat setup, and distinguish structural checks from an independent agent pilot.
- Never: add an installer or mutate a user's project from the maintainer checker.

## Acceptance

- Given this repository, When the checker runs, Then all seven bundles and repository links pass their metadata, format, index, and progress checks.
- Given fresh and existing-docs fixture projects, When setup rules are exercised twice, Then payload links work and context, work, prior docs, and existing agent instructions are preserved with one pointer.
- Given invalid state, missing verification evidence, duplicate metadata, or a broken link, When checking a fixture, Then the checker reports failure.
- Given a saved checkpoint, When work is resumed, Then the current item and next action are recoverable from files; independent agent-pilot coverage remains explicitly unclaimed.

## Verify

Run `.venv/bin/python scripts/check_docs.py` with the maintainer dependency available. Exercise negative fixtures and read the saved checkpoint before closing work. Run okbase L1 on all seven bundles, and check final files for whitespace errors. Record exact results in the parent plan.
