---
type: Plan
title: P013 · Setup follows project conventions
description: Make portable setup link to existing project rules instead of copying them and respect the host project's documentation conventions.
work_status: done
---

# P013 · Setup follows project conventions

## Goal

Portable setup in a project with rich agent instructions and its own documentation site must not duplicate those instructions or break that site. Change the Lite and Plan-first setup prompts, manual setup, and the context blueprint accordingly.

Out of scope: Hybrid Team's installer and payload (a doc change there needs a new runtime version), an install manifest for portable profiles, and checker enforcement of prose behavior.

## Baseline

Builds on P012 (0.4.1). Observed in a real adoption: a Rust repository whose AGENTS.md already listed rules, CI commands, and layout, with Vietnamese documentation built by MkDocs and a CLAUDE.md that imports AGENTS.md. Following the 0.4.0 prompt, the agent copied those rules and commands into an English context.md, which immediately duplicated AGENTS.md and contradicted the language convention; the MkDocs strict build had to be fixed by hand. Checker and tests pass as in P012 (185 files, 84 tests).

## Compatibility

Existing context, pointers, and installations stay untouched; repeated setup still preserves them. The prompts keep their structure, step numbering, and the extracted `Set up okms` block used by `evals/run_agent_pilot.py`. No payload file is added or removed.

## Approach

- One implementation spec: prompt steps 4–6, manual setup text, and the final instruction of the Lite and Plan-first `context.md` blueprint.
- Prefer links to the source section over copies; follow the project's documentation language; place the pointer only in an imported instruction file; run the host project's existing documentation check when the copy lives inside a documentation site.
- Ship with P012 in 0.4.1; no further version change.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P013-MS01 · Convention-aware setup](P013-MS01-setup.md) | — | done | `python3 scripts/check_docs.py`: PASS, 188 Markdown files, seven bundles, 10 onboarding scenarios. `python3 -m unittest discover -s tests`: 84 tests OK. `setup_prompt()` in `evals/run_agent_pilot.py` still extracts the Plan-first prompt. No agent pilot ran; agent compliance with the new prose is unobserved. |

## Resume

- Current: complete.
- Next: observe the new prompt with an agent pilot in a project that has a documentation site and existing instructions.
- Blocker: none.

## Result

Setup prompts and the context blueprint now direct agents to link to existing rules and commands, follow the project's documentation language, avoid duplicate pointers in imported instruction files, and keep the host project's documentation check passing. Structural checks pass; behavioral effect awaits an agent pilot.
