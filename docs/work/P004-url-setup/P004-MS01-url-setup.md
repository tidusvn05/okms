---
type: MicroSpec
kind: implementation
title: P004-MS01 · Use a public repository source
description: Make the default README setup prompt retrieve its template from GitHub without requiring a user-provided checkout path.
---

# P004-MS01 · Use a public repository source

## Intent

Let a user paste the default setup prompt directly into an agent in their project. The agent obtains the Plan-first payload from the public okms repository when creating a new installation.

## Constraints

- Always: reuse an existing installation first; preserve its profile, project context, docs, work, and instructions.
- Always: keep temporary source retrieval outside the project and copy only the selected docs payload into an empty destination.
- Never: require a local source-path substitution in the agent prompt or report a fetch check as an actual agent adoption session.

## Acceptance

- The default prompt contains the public HTTPS repository URL, an explicit retrieval step, and no source-path placeholder.
- New setup fetches the selected payload; repeated setup reuses its existing installation without fetching or switching profiles.
- Context filling, namespaced adoption, instruction pointer reuse, and link checking remain explicit.
- The existing pilot prompt extractor reads the updated text, and an actual HTTPS fetch contains the complete standalone payloads.

## Verify

Review the prompt, fetch the repository into a disposable temporary directory, compare payload inventories and source bytes, check the pilot extractor, and run `.venv/bin/python scripts/check_docs.py`. Preserve existing measured pilot reports.
