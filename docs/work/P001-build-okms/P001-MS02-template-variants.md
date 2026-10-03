---
type: MicroSpec
title: P001-MS02 · Package template variants
description: Provide three self-contained copyable workflows for small changes, planned features, and existing systems.
---

# P001-MS02 · Package template variants

## Intent

Package Lite, Plan-first, and Brownfield as seven-file Markdown bundles that work after copying to a project's docs directory without okbase, a generator, or an external template dependency.

## Constraints

- Always: keep the shared micro spec format and use relative links within each copied bundle.
- Always: keep each work item's progress in the plan or, for standalone Lite work, in the micro spec.
- Never: require a human approval pause after saving a plan or execute an unresolved placeholder as a command.

## Acceptance

- Given Lite and one independent change, When an agent starts implementation, Then it saves a standalone micro spec and records checks in Verify.
- Given Plan-first, When implementation starts, Then a plan is persisted and specs are created just before each item is implemented.
- Given Brownfield, When a change is planned, Then the baseline and compatibility obligations are recorded before implementation, with migration and rollback details when relevant.
- Given any payload copied to a different directory, When its links are followed, Then its workflow, context, blueprints, and work index resolve inside that payload.

## Verify

Parse each payload's YAML, inspect its workflow rules, and verify the seven-file inventory and all local link targets after copying the payload into a temporary directory. Compare common blueprints and check Brownfield's additional sections.
