---
type: MicroSpec
kind: implementation
title: P005-MS01 · Expandable profile prompts
description: Make every profile's setup prompt directly copyable while preserving existing adoption behavior and default extraction.
---

# P005-MS01 · Expandable profile prompts

## Intent

Give README readers a complete ready-to-paste setup prompt for Plan-first, Lite, or Brownfield inside a labeled expandable section. Plan-first remains the visible default.

## Constraints

- Always: Keep the public repository URL, preservation rules, installed-profile reuse, actual project context, single instruction pointer, and temporary source cleanup in every prompt.
- Never: Require readers to substitute a source path or profile name, change distributed payloads, or rewrite historical pilot evidence.

## Acceptance

- Given a new project, when a reader copies any profile's prompt, then its requested profile and source payload path agree and no source-path placeholder needs replacement.
- Given the README, when it is opened, then Plan-first is the first details section and is expanded by default; Lite and Brownfield each have a labeled closed section and a complete prompt.
- Given existing project content or an okms installation, when the agent follows any prompt, then the existing preservation and reuse instructions still apply.
- Given the existing pilot extractor, when it reads the revised README, then it returns the complete Plan-first prompt unchanged.

## Verify

- Method: Review the three details/code-block structures, compare profile-normalized prompts with the previous prompt, invoke the existing setup extractor, and run `.venv/bin/python scripts/check_docs.py` and `git diff --check`.
- Expected: Three correctly routed complete prompts, unchanged adoption rules and default extraction, valid document links, and a clean diff check.
- Tests: Direct prompt assertions and the required document checker cover this layout change; no new agent session or application tests are needed.
