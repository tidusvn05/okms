---
type: Guide
title: Hybrid Team runtime guide
description: Operate local CLI workers, durable messages, ownership transfer, isolated integration, and recoverable evidence.
---

# Hybrid Team runtime guide

## Requirements and startup

Use Python 3.10+, Git with an existing commit, and installed/logged-in Codex and Claude Code CLIs. Version 0.1 targets local Linux, macOS, and WSL. Setup installs project files; it does not create accounts, copy credentials, or install the provider CLIs. Native logs/authentication remain under the tools' own management.

Run `python3 .okms/team.py doctor`. Fill real checks as argv arrays in `.okms/team.json`; unknown commands remain unknown. Context discovery belongs to setup with the agent, not invented command defaults. The CLI transport preserves login/model configuration. Writers use Codex workspace-write and Claude acceptEdits, with runtime-command permission; native denials remain failures. No trust/permission bypass flags are used.

Codex requires project and hook trust before nonmanaged hooks run. Open `/hooks` to review the generated definitions. Claude Code must load the project's settings/hooks. A doctor receipt records a hook invocation; it does not independently establish how the native tool granted trust. [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks).

SessionStart returns a coordinator or standby identity. Workers carry their identity/project in the OKMS environment. Lifecycle hooks expose queued messages at startup, prompt submission, and tool completion. Hooks do not interrupt an active tool; an idle interactive coordinator sees updates on its next turn. A waiting headless worker resumes by its saved ID when a peer message arrives. [Codex execution](https://learn.chatgpt.com/docs/non-interactive-mode), [Claude Code execution](https://code.claude.com/docs/en/headless).

## Command interface

In unattended Claude workers, invoke the helper directly with shell-quoted --input-json, or --input FILE prepared in ignored .okms/state. Pure inbox/verify reads need no input. Read artifacts with the native Read tool. Heredocs, compound shell commands, and parsing pipelines may require additional native permission. For root Git inspection, --no-optional-locks avoids Git's optional stat-cache refresh; preserving staging does not require arbitrary external Git readers to leave cache bytes unchanged. [Git status](https://git-scm.com/docs/git-status#_background_refresh).

From the project, use `python3 .okms/team.py COMMAND --identity IDENTITY_FILE --input INPUT_FILE`. Use `--input -` for JSON stdin. Workers omit --identity because their environment is already bound. Input is an object; output is JSON. Errors exit nonzero with incomplete: true. Pass argument arrays when invoking from code; do not interpolate prompts or JSON into shell commands.

| Command | Input and behavior |
| --- | --- |
| doctor | Reports runtime, Git, provider flags/authentication, checks, and hook observations. |
| join | provider and session_id; returns role and a project-local identity file. Use an actual native ID when available; a unique manual session key is a fallback requiring explicit ownership recovery afterward. |
| dispatch | provider, plan, spec, intent, owns, optional context/checks; reserves a scope, snapshots or joins a batch, and launches a worker. launch: false only prepares an assignment. |
| status | Registry and events; optional wait_seconds, 0–50, waits for active drivers. |
| send | to, payload, optional id/type/reply_to; type is request, response, or notice. Address a registered worker ID or coordinator. |
| inbox / ack | Reads pending messages; ack takes their id. Delivery is distinct from acknowledgment. |
| resume | agent_id, optional reason; uses its exact saved native ID and retained worktree. An expired deadline needs explicit extend_seconds. |
| handoff | to for coordinator transfer, or recover: true from standby to fence a lost coordinator. |
| verify | Workers execute only assigned checks. Coordinators execute configured root checks; run_id can reverify an applied_unverified batch. |
| integrate | run_id and acceptance_review; all noncancelled workers must have returned valid results. Optional checks add coordinator-selected argv arrays to configured required checks. |
| checkpoint | plan, spec_id, state, evidence, resume with current/next/blocker. done additionally needs acceptance_review; the last completed row needs an actual result. |
| stop | agent_id and reason; preserves partial work and artifacts. |

The runtime does not create plans or micro specs. Use their blueprints, save contracts and indexes, then dispatch linked ready rows. For each plan, keep the existing Work columns Spec / Depends on / State / Evidence.

## Messages and events

The protocol envelope has schema_version: 1, id, run_id, spec_id, from, to, type, reply_to, payload, and created_at. Event records add an increasing sequence. Store timestamps in UTC; sequence records broker order rather than provider wall-clock order. Reuse an ID to retry an identical send; changed content with the same ID is rejected.

Messages are addressed requests/responses/notices requiring recipient acknowledgment. Events are append-only runtime observations, including assignment_queued, worker_started, message_queued, message_delivered, message_acknowledged, result_ready, worker_failed, integration_applied, and checkpoint_saved. SQLite transactions serialize writes. Retain artifact paths instead of putting large diffs or logs in messages.

A WorkerResult has summary, evidence, remaining, next, and disposition (result_ready or waiting_input). The driver attaches observed revision, changed paths, raw trace references, and errors. Native turn completion does not prove that result schema, scope, evidence, or acceptance passed.

## Worktrees and preservation

Each batch uses a private current-code Git snapshot. It includes tracked and nonignored untracked files, including unstaged edits, without changing the root branch or index. Runtime state and ignored untracked files are excluded. Installed runtime/instruction files omitted by ignore rules receive a bounded overlay in each worker. Other ignored dependencies/configuration are not copied; use actual shared environment commands or configure project preparation before dispatch.

Workers own explicit paths and cannot own shared contracts/native configuration. The default limit is two workers, with 30 minutes per assignment. New turns consume the same deadline. Automatic waking continues an existing waiting assignment; failed or partial execution is never silently retried. Native helpers are parent-managed readers, not additional mixed-provider coordinators.

Integration combines a returned batch in a separate worktree and runs actual checks before applying its delta. Changed root targets, overlaps, out-of-scope edits, provider failures, and failed checks preserve artifacts and incomplete progress. Root checks failing after application leave applied_unverified; fix/check the actual root and explicitly reverify it before closing work.

Runtime identity/token checks govern runtime operations, not every arbitrary filesystem command an agent could issue. Scope validation rejects unowned returned changes; project instructions and native sandbox/permission policies remain applicable. Keep worktrees and refs under runtime management while recovering; no automatic destructive cleanup runs.
