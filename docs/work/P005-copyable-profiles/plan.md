---
type: Plan
title: P005 · Copyable setup for every profile
description: Present complete setup prompts for all three profiles using GitHub-supported expandable README sections.
work_status: done
---

# P005 · Copyable setup for every profile

## Goal

Let readers choose Plan-first, Lite, or Brownfield and copy a complete setup prompt without editing profile names or source paths. Keep Plan-first expanded by default.

Out of scope: changing template contracts, adding a website or runtime, or rerunning the full agent evaluation matrix for a README layout change.

## Approach

- Select implementation for the requested change to the README's setup experience.
- Use three HTML details sections with Markdown code blocks; keep Plan-first first and open so the existing pilot extractor retains its default.
- Repeat the complete public-URL prompt for each profile, preserving installation reuse, project content, instruction pointers, actual context, and temporary source cleanup.
- Review all three prompts and their section structure, render the README through GitHub's Markdown API, check the existing extractor, and run the required document checker.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P005-MS01 · Expandable profile prompts](P005-MS01-profile-prompts.md) | — | done | Three profile-normalized prompts match the previous prompt exactly; the pilot extractor retains Plan-first. GitHub's Markdown API preserves all summaries and fenced prompts, with only Plan-first open. The document checker passes 115 Markdown files and 12 onboarding scenarios; `git diff --check` passes. |

## Resume

- Current: none; P005-MS01 is done.
- Next: copy the complete prompt from the README section matching the intended profile.
- Blocker: none.

## Result

The README now offers complete setup prompts for Plan-first, Lite, and Brownfield in expandable sections. Plan-first is first and open by default. Each prompt uses the public GitHub URL and its own payload path, with the previous adoption rules preserved exactly. GitHub's Markdown API rendering, direct prompt assertions, existing pilot extraction, document checks, and diff checks pass. Distributed payloads and historical evaluation artifacts are unchanged. No new agent adoption session or application tests ran for this layout change.
