---
type: Plan
title: P004 · Set up directly from GitHub
description: Replace the README agent prompt's local checkout prerequisite with a public repository source and explicit retrieval.
work_status: done
---

# P004 · Set up directly from GitHub

## Goal

Make the default README setup prompt ready to paste into an agent in the destination project, using the public okms URL and fetching its template when necessary.

Out of scope: changing template contracts, installing a runtime, or rerunning the full agent matrix for a small setup documentation change.

## Approach

- Select implementation for the requested setup guidance change; retain the installed-profile and preservation rules.
- Inspect for an existing installation before fetching; retrieve a new source in a temporary directory outside the project and copy the selected payload.
- Verify an actual HTTPS fetch and payload inventory, review the copyable prompt and existing pilot extractor, and run the required document checker.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P004-MS01 · Use a public repository source](P004-MS01-url-setup.md) | — | done | README prompt has the public URL and no source-path placeholder; the existing pilot extractor returns it unchanged. Actual shallow HTTPS clone of main at `3ebf201` contains all 16 matching files in every profile. Document checker passes 112 Markdown files and 12 setup scenarios. |

## Resume

- Current: none; P004-MS01 is done.
- Next: paste the README prompt into an agent in the destination project; select another profile only if needed.
- Blocker: none.

## Result

The README's default setup prompt now uses `https://github.com/tidusvn05/okms` directly, with explicit temporary source retrieval for new installations. Repeated setup preserves the existing installation without fetching or switching profiles. The agent prompt needs no local checkout-path edit; manual setup remains available from a local checkout. Actual HTTPS retrieval, payload byte comparisons, prompt extraction, document links, and setup fixtures pass. No new agent adoption session ran, and historical pilot measurements remain unchanged.
