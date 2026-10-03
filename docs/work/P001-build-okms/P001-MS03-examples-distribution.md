---
type: MicroSpec
title: P001-MS03 · Document adoption and examples
description: Help users choose and adopt a workflow while preserving their documents and understanding honest examples.
---

# P001-MS03 · Document adoption and examples

## Intent

Provide English setup instructions, a copyable agent prompt, contribution guidance, and one worked example per profile so users can apply the templates without an installer or losing existing work.

## Constraints

- Always: copy only into a new destination, use docs/okms/ when docs already exists, and add the agent rule only once.
- Always: identify example verification as unexecuted and keep fictional application paths and commands out of actual evidence.
- Never: overwrite project context, agent instructions, or active work during repeated setup or an upgrade.

## Acceptance

- Given an empty project, When setup follows the README, Then the selected payload lives in docs/ and its workflow is referenced by the agent entrypoint.
- Given existing docs and agent instructions, When setup is repeated, Then the original content survives and the workflow pointer appears only once.
- Given a worked example, When users read its plan and specs, Then behavior, dependencies, recovery, and verification expectations are clear without claiming application tests passed.
- Given maintainers, When they read contribution guidance, Then the document checks and manual workflow scenarios can be repeated.

## Verify

Review README instructions against all three payloads; inspect examples and their pending evidence; verify link targets and the complete MIT OR Apache-2.0 license texts. Exercise adoption and repeat setup in temporary projects during the final validation spec.
