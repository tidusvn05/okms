# okms

**Micro specs and recoverable workflows for coding agents.**

Copy a template into your project, point your agent at its workflow, and complete one small verifiable outcome at a time. Plans track progress and the next action; code and deliverable documents hold details. A small catalog selects task-specific contracts, and explicit Goals add bounded loop execution. Everything is Markdown and works with ordinary file reads.

## Choose a template

| Template | Use it for | Workflow |
| --- | --- | --- |
| [Lite](templates/lite/docs/workflow.md) | One independent fix, report, or small outcome | Select a kind → save a micro spec → execute → check. Use its Plan-first fallback when scope grows. |
| [Plan-first](templates/plan-first/docs/workflow.md) | Work with multiple outcomes or dependencies | Save a plan → repeat select → spec → execute → check → checkpoint → check the whole plan. |

Each template contains 16 Markdown files, including a workflow, context, task catalog, seven micro spec blueprints, Plan and Goal blueprints, Goal execution guidance, and directory indexes. The copied bundle has no runtime dependencies.

Choose the workflow by the work's size and dependencies. Both workflows apply baseline and compatibility obligations when the affected scope includes existing contracts, including shared integration effects from new code. The agent identifies those obligations from the project.

## Set up with your agent

Open your agent in the destination project, choose a profile below, and paste its full prompt as-is. The agent needs project file access and network access to fetch the public repository; it obtains the template for you.

<details open>
<summary>Plan-first — multiple outcomes or dependencies (default)</summary>

```text
Set up okms in the current project using the plan-first template from:
https://github.com/tidusvn05/okms

1. Inspect existing project docs and applicable agent instructions.
2. Reuse an existing okms installation referenced by the project's
   instructions, or look for one at docs/workflow.md or
   docs/okms/workflow.md. Recognize it by its template and template_version
   metadata; if the intended installation is ambiguous, ask which to use.
   Reuse it without fetching or switching profiles.
3. For a new installation, fetch the repository with a shallow HTTPS
   clone or archive download into a new temporary directory outside this
   project. Use templates/plan-first/docs/ from that checkout.
   Choose docs/ if it is absent or empty; otherwise choose docs/okms/.
   Copy only the selected docs payload into a new or empty destination.
   If that destination contains other content, choose an empty
   destination. Do not overwrite existing project files.
4. Fill context.md from actual project files: purpose, durable rules,
   applicable docs, and real required checks/test commands. Preserve
   existing context on repeated setup. Mark undiscovered information
   as unknown; never execute placeholders or invent commands.
5. Reuse a pointer to this installation if one already exists. Otherwise
   add this instruction once to the project's AGENTS.md, adapting paths:
   For substantive project tasks, read and follow [the workflow](docs/workflow.md),
   starting with [the docs index](docs/index.md).
   Preserve existing instructions. If this agent uses a different
   instruction entrypoint, add the same pointer there instead.
6. Check the copied links and report the selected profile and location.
   Remove the temporary source checkout created for this setup, if any.
   Keep okbase optional; there is no need to install it for this setup.
```

</details>

<details>
<summary>Lite — one small independent outcome</summary>

```text
Set up okms in the current project using the lite template from:
https://github.com/tidusvn05/okms

1. Inspect existing project docs and applicable agent instructions.
2. Reuse an existing okms installation referenced by the project's
   instructions, or look for one at docs/workflow.md or
   docs/okms/workflow.md. Recognize it by its template and template_version
   metadata; if the intended installation is ambiguous, ask which to use.
   Reuse it without fetching or switching profiles.
3. For a new installation, fetch the repository with a shallow HTTPS
   clone or archive download into a new temporary directory outside this
   project. Use templates/lite/docs/ from that checkout.
   Choose docs/ if it is absent or empty; otherwise choose docs/okms/.
   Copy only the selected docs payload into a new or empty destination.
   If that destination contains other content, choose an empty
   destination. Do not overwrite existing project files.
4. Fill context.md from actual project files: purpose, durable rules,
   applicable docs, and real required checks/test commands. Preserve
   existing context on repeated setup. Mark undiscovered information
   as unknown; never execute placeholders or invent commands.
5. Reuse a pointer to this installation if one already exists. Otherwise
   add this instruction once to the project's AGENTS.md, adapting paths:
   For substantive project tasks, read and follow [the workflow](docs/workflow.md),
   starting with [the docs index](docs/index.md).
   Preserve existing instructions. If this agent uses a different
   instruction entrypoint, add the same pointer there instead.
6. Check the copied links and report the selected profile and location.
   Remove the temporary source checkout created for this setup, if any.
   Keep okbase optional; there is no need to install it for this setup.
```

</details>

Each prompt performs setup; give the agent a substantive task afterward. Existing installations keep their current profile; request a profile switch explicitly if needed.

## Set up manually

For manual setup, download or clone this repository first and use its local checkout path in the commands below.

First reuse an existing okms installation referenced by your project instructions or found at `docs/workflow.md` or `docs/okms/workflow.md`. Its frontmatter identifies the template and version. For a new installation, copy into a destination that does not exist yet. When `docs/` does not exist:

```sh
cp -R /path/to/okms/templates/plan-first/docs ./docs
```

When `docs/` already exists, use this alternative only if `docs/okms/` does not exist:

```sh
cp -R /path/to/okms/templates/plan-first/docs ./docs/okms
```

Fill the copied `context.md` using real project information. Add this single line once to your existing `AGENTS.md`, or create that file if absent:

```markdown
For substantive project tasks, read and follow [the workflow](docs/workflow.md), starting with [the docs index](docs/index.md).
```

For a namespaced install, use `docs/okms/workflow.md` and `docs/okms/index.md`. Agents that use another instruction entrypoint need the same pointer in that entrypoint. The workflow is project guidance; reading the pointer and following it depend on the agent.

If the destination already contains an okms workflow, reuse it and keep its context, indexes, and work. Review profile switches or upgrades explicitly; do not copy a new payload over an existing installation.

## Select the task contract automatically

The installed profile controls planning and checkpoints. For each substantive outcome, the agent reads the [task catalog](docs/_templates/catalog.md) and only the selected blueprint:

| Kind | Outcome |
| --- | --- |
| `implementation` | Add or intentionally change behavior. |
| `bugfix` | Correct a reproduced contract violation and check regression. |
| `investigation` | Explain observed behavior with evidence and explicit unknowns. |
| `design` | Record a system decision, viable alternatives, and consequences. |
| `research` | Answer a bounded question with attributable sources and comparison. |
| `runbook` | Author an operator procedure with actual commands and rehearsal limits. |
| `general` | Use the common contract for other verifiable outcomes, such as translation. |

Routing honors explicit scope and open checkpoints, then chooses by the next required output rather than keywords. A plan can contain several kinds: investigation → bugfix → runbook, for example. It lists future outcomes and materializes each spec when ready. Short status replies and explanations can stay in the conversation.

New specs store `kind` in frontmatter. Specs without it retain the common contract, so historical files need no migration. Findings, decisions, reports, and operating steps use their own deliverable formats; their micro specs remain small. All copied profiles include the catalog and every blueprint, and routing does not silently switch the installed profile.

## The micro spec contract

Every micro spec has four sections:

| Section | Contents |
| --- | --- |
| Intent | One observable outcome and why it matters. |
| Constraints | Essential Always/Never invariants. |
| Acceptance | Outcome-specific success and failure criteria; Given/When/Then suits behavior. |
| Verify | A real check or review method, expected result, and relevant test scope. |

Aim for roughly 100–250 words and 2–5 acceptance criteria. These are writing guides, not limits. A useful boundary is one behavior that can be verified; split by behavior rather than lines of code.

Keep critical authorization, data preservation, compatibility, and concurrency rules when they determine correctness. Reference existing code and deliverable docs for details. Verify can mean regression checks, reproducible observations, decision review, source checking, or runbook rehearsal. Never weaken acceptance to make failed or unsupported work appear complete.

Plans use `Goal / Approach / Work / Resume / Result`, adding `Baseline / Compatibility` between Goal and Approach when existing contracts are affected. Save the plan before substantive execution. List future specs and dependencies, then save each spec just before its outcome is executed. Agents continue without a mandatory approval pause unless review was requested or an important decision is missing.

## Work on an existing system

The agent inspects the affected behavior, callers, interfaces, stored data, and shared dependencies. Before changing or deciding changes to existing contracts, it records current behavior, actual baseline checks or their unavailability, and known failures. Acceptance and verification cover the contracts to retain and the intended changes.

Lite keeps baseline evidence in the micro spec's Verify section and compatibility obligations in Constraints and Acceptance. A small fix can remain standalone. Plan-first adds concise Baseline and Compatibility sections when these obligations apply, and omits them for outcomes that affect no existing contracts. Include migration, rollout, and rollback only when the change needs them.

## Run an explicit Goal or loop

For an explicitly requested Goal, the agent also reads [bounded goal execution](docs/goal-loop.md) and renders [the Goal blueprint](docs/_templates/goal.md). A Goal records final completion criteria, scope, linked plans, execution mode, limits, stop conditions, and Resume. Plans continue to own their item states and evidence.

Portable mode runs the bounded loop in the current agent session. `max_iterations` defaults to 5 unless the user supplies another positive limit; `iterations_used` reserves one attempt before execution and survives interruption. At the limit, incomplete work remains `in_progress` with `stop_reason: iteration_limit` and a saved next action. Only an explicit extension raises an existing limit. A blocked required check remains incomplete.

Native mode requires actual available goal operations, an adapter mapping, and a saved native identifier. The guide describes start/attach, inspect, complete, and stop behavior while respecting the runtime's own limits and state rules. Without native support the agent can record portable mode, unless native execution is required. These Markdown files do not activate a background service or install an agent integration.

Example request:

```text
Complete this feature using a portable Goal loop with at most two attempts.
Save the Goal and plan first, select each micro spec from the task catalog,
verify each outcome, and checkpoint when complete, blocked, or at the limit.
```

## Progress, checks, and history

Plan work tables own each item's state and evidence. Standalone Lite specs keep `work_status` and a `Result:` entry under Verify. States are `planned`, `in_progress`, `blocked`, `done`, and `cancelled`.

Check acceptance for every item. Run or add automated tests when needed and obey the project's required checks. Record the actual method and result; skipped tests need a reason. Missing necessary verification leaves work incomplete. Mark a plan done after its scoped items, cross-spec interactions, and required checks are complete.

Resume records the current item, next action, and blocker. A new session reads that checkpoint and inspects the current files before continuing. Update the checkpoint at state or scope changes rather than logging every tool call.

Keep completed plans and specs at their existing paths, remove their Active work pointers, and retain their directory index entries. They document historical work. Enduring rules belong in project context or applicable current docs. Agents start with context, current work, and its dependencies; they search history when relevant.

## Optional okbase support

The payloads follow [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md): YAML frontmatter, useful descriptions, and directory indexes. Progress uses `work_status`; OKF `status` retains its lifecycle meaning (`draft`, `stable`, `deprecated`).

[okbase](https://github.com/tidusvn05/okbase) can lint and help agents find or read relevant documents as the knowledge base grows:

```sh
okbase -b docs lint --level L1
# For a namespaced install:
okbase -b docs/okms lint --level L1
```

See [okbase usage](https://github.com/tidusvn05/okbase/blob/main/docs/usage.md) for its CLI and MCP tools. Connect it separately when wanted; these templates do not install or configure it.

## Examples and contributions

Read the [worked examples](examples/README.md) for a small validation fix, device administration, and a compatible pagination refactor. They illustrate documents and checkpoints; they contain no application and claim no application tests were run.

The [routing and Goal walkthrough](examples/routing.md) illustrates mixed task kinds and a bounded Goal contract.

See [CONTRIBUTING.md](CONTRIBUTING.md) for maintainer checks and workflow review scenarios. This repository uses its own Plan-first workflow; its [implementation history](docs/work/index.md) records actual work and verification.

The [v0.3 targeted workflow report](evals/workflow-report.md) observes two fresh conversations: a standalone Lite fix and a Plan-first compatible refactor. Both record baseline evidence before code changes and pass all observed criteria, 80 independent behavior cases, and seven original test-method executions. The full routing and Goal matrix was not rerun for this version.

The [historical v0.2 routing and Goal report](evals/routing-report.md) retains 15 fresh conversations across two drafts, including instruction gaps and affected reruns. All nine latest scenarios choose the expected kinds; eight meet every criterion, with one extra general blueprint read recorded for blocked verification. Independent grading passes 240 behavior-case executions and 47 original test-method executions. Portable Goal exhaustion, explicit extension, recovery, and blocked verification are exercised; native activation is untested.

The historical [v0.1 agent pilot report](evals/pilot-report.md) covers adoption and the original workflows. See the [pilot runner instructions](evals/README.md) for opt-in evaluation; ordinary checks do not launch an agent.

## License

MIT OR Apache-2.0, at your option. See [LICENSE-MIT](LICENSE-MIT) and [LICENSE-APACHE](LICENSE-APACHE).
