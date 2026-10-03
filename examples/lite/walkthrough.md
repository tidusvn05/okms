---
type: Guide
title: Lite example walkthrough
description: Use a standalone validation spec and record only checks performed in the actual destination project.
---

# Lite example walkthrough

1. Copy the Lite payload into a real project's chosen docs location and fill its project context.
2. Explore the existing pagination parser, error contract, callers, and tests.
3. Save a spec shaped like [MS001](work/MS001-validate-page-size.md), using requirements and verification commands from that project.
4. Set its `work_status` to `in_progress`, implement the behavior, and check every acceptance criterion.
5. Record the actual command or review method and result under Verify. Mark `done` only when acceptance and required checks are supported.

The sample is still `planned`: no application verification was run. A real check may use a test name containing `[ms001]` if its framework supports that convention; no framework or runner is assumed here.

For interruption, append the next action and blocker under Verify. If the task grows into multiple dependent outcomes, create a plan, retain this spec's ID/path, and move its progress and results into that plan as described by the Lite workflow.
