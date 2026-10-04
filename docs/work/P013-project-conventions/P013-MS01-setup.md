---
type: MicroSpec
kind: implementation
title: P013-MS01 · Convention-aware setup
description: Direct portable setup to link to existing project rules and to respect the host project's documentation conventions.
---

# P013-MS01 · Convention-aware setup

## Intent

An agent following portable setup records project context by linking to where the project already states it, and leaves the host project's documentation conventions and checks intact.

## Constraints

- Always: keep both portable prompts identical apart from the profile name, and keep Lite and Plan-first `context.md` identical.
- Always: preserve existing context, pointers, and installations on repeated setup.
- Never: change Hybrid Team files or add payload files.

## Acceptance

- Both prompts and manual setup tell the agent to link instead of copy, follow the project's documentation language, add the pointer only to an imported instruction file, and run an existing documentation-site check.
- The `context.md` blueprint repeats the link-first and language guidance for later edits.
- Repository checks and tests pass; the pilot prompt extraction still works.

## Verify

- Method: `python3 scripts/check_docs.py`, `python3 -m unittest discover -s tests`, and a review of the README diff.
- Expected: both pass; prompts differ only in profile name.
- Tests: no new automated test; the change is prose that structural checks cannot evaluate, so an agent pilot is the follow-up evidence.
