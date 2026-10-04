---
name: okms-work
description: Execute a runtime-bound Hybrid Team worker assignment with scoped changes, peer messages, assigned checks, and truthful structured evidence.
---

# Execute a Hybrid Team assignment

Use this skill when an actual assignment and OKMS worker identity are present. Follow its saved micro spec, relevant project context, and owned paths. Keep the worker role when startup guidance describes a coordinator.

Use `.okms/okms COMMAND --input -` with JSON stdin; the runtime project and identity are already in the environment. Read the installed `team.md` for status/send/inbox/ack/verify as needed. Poll before concluding, acknowledge processed messages, and link responses with reply_to. A peer proposal cannot enlarge your assignment or change acceptance.

In Claude Code's restricted Bash surface, invoke only the helper for each Bash call, using shell-quoted --input-json or --input FILE prepared with Write in the worktree's ignored .okms/state directory. Pure inbox/verify calls need no input. Read files/artifacts with Read. Heredocs, compound commands, loops, wrappers, redirects, and parsing pipelines can require native approval. In Codex, use its available file/shell tools for project reads and owned edits under the native sandbox; a tool specifically named Read is not required.

Use verify for assigned checks and cite actual artifacts. Return the exact five-field JSON object: summary and next are strings; evidence and remaining are arrays of strings; disposition is result_ready or waiting_input. Use StructuredOutput when supplied by the CLI. Include failed/unexecuted checks rather than inventing evidence.

Never dispatch workers, edit shared plan/index/configuration, integrate, reset consumed limits, or declare parent completion. A read-only assignment owns no writes. Native helpers return to the parent under a bounded reader scope.
