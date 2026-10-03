---
type: MicroSpec
title: P002-MS01 · Prepare an observed pilot runner
description: Capture fresh agent sessions in isolated real-code projects with external workflow and outcome evidence.
---

# P002-MS01 · Prepare an observed pilot runner

## Intent

Make the six documented pilot scenarios executable with real code, checks, and fresh agent conversations, preserving enough evidence to assess workflow order rather than trusting final summaries.

## Constraints

- Always: keep agent projects outside this checkout and observation artifacts outside each agent's writable project.
- Always: use the installed CLI's default model and existing login, and grade behavior with independent checks.
- Never: copy credentials into fixtures, execute a pilot from the ordinary document checker, or label structural simulation as an agent run.

## Acceptance

- Given a pilot invocation, When the CLI runs, Then a fresh non-interactive conversation emits recorded events and the agent can edit only its disposable workspace.
- Given source and work-document changes, When the session progresses, Then external snapshots and command events support assessment of saved-plan/spec order and checkpoint transitions.
- Given generated application code, When grading runs, Then independent behavior checks and original project checks distinguish code success from workflow success.
- Given a second invocation on a checkpointed project, When it starts, Then no prior conversation is supplied and it must recover scope from project files.

## Verify

Confirm CLI execution and inspect a small first run, exercise fixture baseline tests, and validate runner syntax. The actual scenarios and their outcomes are recorded by the next micro spec.
