---
type: MicroSpec
kind: implementation
title: P006-MS02 · Two-workflow setup and examples
description: Present two directly copyable setup choices and illustrate existing-system obligations within the current workflows.
---

# P006-MS02 · Two-workflow setup and examples

## Intent

Help readers choose Lite or Plan-first by the work's size and dependencies. Explain that existing-system obligations are selected from the affected scope and illustrate both a standalone fix and a coordinated compatible refactor.

## Constraints

- Always: Preserve the complete setup prompts and existing adoption safeguards; keep Plan-first first and open by default.
- Never: Offer a legacy Brownfield payload, rewrite historical measurements, or claim the worked examples executed application checks.

## Acceptance

- Given the README, when choosing setup, then only Lite and Plan-first appear and each prompt can be copied without substituting a path or profile.
- Given a reader with an existing system, when reading the guidance, then baseline and compatibility apply according to affected contracts in either workflow.
- Given the examples, when reviewing a small fix or compatible refactor, then Lite uses concise spec evidence and Plan-first uses conditional plan sections, with verification honestly unexecuted.
- Given contribution and evaluation guidance, when following current commands, then all paths and profile choices exist and historical reports remain identified as prior-version evidence.

## Verify

- Method: Check Markdown links, compare the two prompts to their previous versions, render the README through GitHub's Markdown API, and review examples and current instructions.
- Expected: Two correctly labeled rendered prompts with preserved safeguards, resolvable paths, and honest scenario evidence.
- Tests: Document review and direct prompt/link checks cover this presentation change; the next item updates automated validation and pilot fixtures.
