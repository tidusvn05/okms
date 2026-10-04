# okms

**Micro specs and recoverable workflows for coding agents.**

Copy a template into your project, point your agent at its workflow, and complete small verifiable outcomes. Plans track progress and the next action; code and deliverable documents hold details. Lite and Plan-first are portable Markdown. The optional Hybrid Team profile adds a local runtime for Codex and Claude Code workers.

## Choose a template

| Template | Use it for | Workflow |
| --- | --- | --- |
| [Lite](templates/lite/docs/workflow.md) | One independent fix, report, or small outcome | Select a kind → save a micro spec → execute → check. Use its Plan-first fallback when scope grows. |
| [Plan-first](templates/plan-first/docs/workflow.md) | Work with multiple outcomes or dependencies | Save a plan → repeat select → spec → execute → check → checkpoint → check the whole plan. |
| [Hybrid Team](templates/hybrid-team/docs/workflow.md) | Use Codex and Claude Code together in one project | One coordinator → ready scoped workers → durable messages → isolated integration → root checks → checkpoint. |

Lite and Plan-first each contain 21 Markdown files at version 0.4.1, with eight task kinds and optional delegation contracts. They have no runtime dependencies. Hybrid Team 0.2.0 has 28 documentation files embedded in a standalone Rust CLI, with a bundled SQLite runtime, native configuration, roles, and skills. Binary installation supports Linux/WSL and macOS on x86_64 and arm64, without Python or a Rust compiler. Coordination requires Git with an existing commit and installed/authenticated provider CLIs.

Choose by planning and coordination needs. All profiles apply baseline and compatibility obligations when existing contracts are affected. Task kind remains independent of profile: coordination is not a ninth kind.

The [Rust 0.2.0 report](evals/rust-report.md) records all three final mixed-provider cases passing against a downloaded Actions binary, including exact resume, handoff and incomplete failed-gate work. The historical [Python pilot report](evals/hybrid-report.md) retains the 0.1.0 observations and failures. Native hook trust and automatic-startup limits remain explicit.

## Set up with your agent

Open your agent in the destination project, choose a profile below, and paste its full prompt as-is. The agent needs project file and network access; it obtains the selected template or release for you.

<details open>
<summary>Plan-first — multiple outcomes or dependencies (default)</summary>

```text
Set up okms in the current project using the plan-first template from:
https://github.com/tidusvn05/okms

1. Inspect existing project docs and applicable agent instructions.
2. Reuse an existing okms installation referenced by the project's
   instructions, or look for one at docs/workflow.md or
   docs/okms/workflow.md. Recognize it by its okms_template and
   okms_template_version metadata (template and template_version before
   0.4.1); if the intended installation is ambiguous, ask which to use.
   Reuse it without fetching or switching profiles.
3. For a new installation, fetch the repository with a shallow HTTPS
   clone or archive download into a new temporary directory outside this
   project. Use templates/plan-first/docs/ from that checkout.
   Choose docs/ if it is absent or empty; otherwise choose docs/okms/.
   Copy only the selected docs payload into a new or empty destination.
   If that destination contains other content, choose an empty
   destination. Do not overwrite existing project files.
4. Fill context.md from actual project files: purpose, durable rules,
   applicable docs, and real required checks/test commands. When existing
   instructions or docs already state a rule or command, link to that
   section instead of copying it. Follow the project's documentation
   conventions, including its language. Preserve existing context on
   repeated setup. Mark undiscovered information as unknown; never
   execute placeholders or invent commands.
5. Reuse a pointer to this installation if one already exists. Otherwise
   add this instruction once to the project's AGENTS.md, adapting paths:
   For substantive project tasks, read and follow [the workflow](docs/workflow.md),
   starting with [the docs index](docs/index.md).
   Preserve existing instructions. If this agent uses a different
   instruction entrypoint, add the same pointer there instead. If one
   instruction file imports another, such as CLAUDE.md importing
   AGENTS.md, add the pointer only to the imported file.
6. Check the copied links. If the destination is inside a documentation
   site or build, such as one configured by mkdocs.yml, run the project's
   existing check and keep it passing, following its conventions for
   navigation or exclusion. Report the selected profile and location.
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
   docs/okms/workflow.md. Recognize it by its okms_template and
   okms_template_version metadata (template and template_version before
   0.4.1); if the intended installation is ambiguous, ask which to use.
   Reuse it without fetching or switching profiles.
3. For a new installation, fetch the repository with a shallow HTTPS
   clone or archive download into a new temporary directory outside this
   project. Use templates/lite/docs/ from that checkout.
   Choose docs/ if it is absent or empty; otherwise choose docs/okms/.
   Copy only the selected docs payload into a new or empty destination.
   If that destination contains other content, choose an empty
   destination. Do not overwrite existing project files.
4. Fill context.md from actual project files: purpose, durable rules,
   applicable docs, and real required checks/test commands. When existing
   instructions or docs already state a rule or command, link to that
   section instead of copying it. Follow the project's documentation
   conventions, including its language. Preserve existing context on
   repeated setup. Mark undiscovered information as unknown; never
   execute placeholders or invent commands.
5. Reuse a pointer to this installation if one already exists. Otherwise
   add this instruction once to the project's AGENTS.md, adapting paths:
   For substantive project tasks, read and follow [the workflow](docs/workflow.md),
   starting with [the docs index](docs/index.md).
   Preserve existing instructions. If this agent uses a different
   instruction entrypoint, add the same pointer there instead. If one
   instruction file imports another, such as CLAUDE.md importing
   AGENTS.md, add the pointer only to the imported file.
6. Check the copied links. If the destination is inside a documentation
   site or build, such as one configured by mkdocs.yml, run the project's
   existing check and keep it passing, following its conventions for
   navigation or exclusion. Report the selected profile and location.
   Remove the temporary source checkout created for this setup, if any.
   Keep okbase optional; there is no need to install it for this setup.
```

</details>

<details>
<summary>Hybrid Team — Codex and Claude Code together</summary>

```text
Explicitly set up the hybrid-team profile in the current project from:
https://github.com/tidusvn05/okms

1. Inspect existing docs, active work, agent instructions, native settings,
   Git, and available/authenticated Codex and Claude Code CLIs.
   Preserve them; do not install tools or create/copy credentials.
2. If .okms/install.json already identifies Hybrid Team, reuse its docs_path,
   runtime and configuration without upgrading or replacing project edits.
   Otherwise download the release installer into a new temporary file outside
   this project from:
   https://github.com/tidusvn05/okms/releases/latest/download/install.sh
   Run sh INSTALLER_PATH --project PROJECT_PATH --dry-run, review its report,
   then run it without --dry-run, using argument arrays/quoted paths.
   It selects the latest regular Hybrid Team release;
   add --version X.Y.Z to both calls if I requested an exact published version.
   It verifies the bundle, selects an empty docs namespace, and preserves
   other profiles/history. Stop on download, verification, or setup failure.
3. Fill the installed context.md and team-policy.md using actual project
   information. Configure real required checks as argv arrays in
   .okms/team.json. Preserve existing values on repeated setup; mark unknown
   commands as unknown and never run placeholders or invent a test runner.
4. Run .okms/okms doctor and review the installed instructions,
   roles, skills, hooks, links, and preservation report. Ordinary setup must
   not launch provider sessions or application work.
5. Report profile/version/docs_path, prerequisites, and remaining native
   activation steps. Codex project/hooks require native trust review via
   /hooks; Claude Code must load project settings. Do not bypass trust or
   permissions. Configuration alone is not proof of automatic startup.
6. Remove only the temporary installer created for setup. Give me
   the next task instructions: an active coordinator uses ready scoped
   workers, while a second root session stays standby until explicit handoff.
```

</details>

Each prompt performs setup; give the agent a substantive task afterward. Portable setup reuses its existing profile. Hybrid Team is explicit opt-in and preserves a prior profile in its existing namespace.

## Set up manually

For manual Lite or Plan-first setup, download or clone this repository first and use its local checkout path in the commands below.

First reuse an existing okms installation referenced by your project instructions or found at `docs/workflow.md` or `docs/okms/workflow.md`. Its frontmatter identifies the template and version as `okms_template` and `okms_template_version` (`template` and `template_version` before 0.4.1). For a new installation, copy into a destination that does not exist yet. When `docs/` does not exist:

```sh
cp -R /path/to/okms/templates/plan-first/docs ./docs
```

When `docs/` already exists, use this alternative only if `docs/okms/` does not exist:

```sh
cp -R /path/to/okms/templates/plan-first/docs ./docs/okms
```

Fill the copied `context.md` using real project information, linking to existing instructions or docs that already state a rule or command instead of copying them, and following the project's documentation conventions, including its language. If the copy sits inside a documentation site, run the project's existing documentation check. Add this single line once to your existing `AGENTS.md`, or create that file if absent:

```markdown
For substantive project tasks, read and follow [the workflow](docs/workflow.md), starting with [the docs index](docs/index.md).
```

For a namespaced install, use `docs/okms/workflow.md` and `docs/okms/index.md`. Agents that use another instruction entrypoint need the same pointer in that entrypoint. The workflow is project guidance; reading the pointer and following it depend on the agent.

If the destination already contains an okms workflow, reuse it and keep its context, indexes, and work. Review profile switches or upgrades explicitly; do not copy a new payload over an existing installation.

For Hybrid Team, install the standalone CLI and review project setup:

```sh
okms_installer="$(mktemp /tmp/okms-install.XXXXXX)"
curl -fL https://github.com/tidusvn05/okms/releases/latest/download/install.sh -o "$okms_installer"
sh "$okms_installer"
rm -f "$okms_installer"
export PATH="$HOME/.local/bin:$PATH"
okms --version
okms init --project . --dry-run
okms init --project .
.okms/okms doctor
```

The installer requires curl, tar, and sha256sum or shasum. It verifies the archive before executing the binary and installs into `~/.local/bin`; `--bin-dir PATH` selects another location. `--dry-run` verifies without writes, and `--project PATH` also runs preserving project setup. Stop if any command fails.

Use `--version 0.2.0` to pin [this release](https://github.com/tidusvn05/okms/releases/tag/hybrid-team-v0.2.0). `--release-dir PATH` installs offline from its selected platform archive and SHA256SUMS. `okms init --docs RELATIVE_PATH` chooses a documentation namespace. By default, setup selects an empty namespace and installs the project-local `.okms/okms` helper. Provider CLIs and authentication must already be available.

Repeated setup preserves project edits. Existing Python 0.1.0 copies are refused by Rust setup and require a deliberate reviewed migration that retains active work, operational state, context and native customizations. The [historical prerelease](https://github.com/tidusvn05/okms/releases/tag/hybrid-team-v0.1.0) keeps its original assets and installer.

To build from a source checkout, install Rust 1.88+ and a C compiler for bundled SQLite:

```sh
cargo build --release --locked --manifest-path /path/to/okms/Cargo.toml
/path/to/okms/target/release/okms init --project . --dry-run
/path/to/okms/target/release/okms init --project .
.okms/okms doctor
```

New `hybrid-team-vX.Y.Z` tags matching Cargo and template versions are checked and published as regular releases by [GitHub Actions](.github/workflows/release.yml); see [maintainer instructions](CONTRIBUTING.md#build-and-publish-hybrid-team).

Setup merges native hooks, chooses available agent/skill names, adds workflow pointers, and ignores operational state. It preserves existing instructions, settings, docs, active work, and project customizations. It launches no agents. Fill actual checks/context before task execution. Review Codex hook trust and Claude project settings; then open either CLI for a coordinator session. Read [the runtime guide](templates/hybrid-team/docs/team.md) for explicit join when startup hooks are unavailable, messages, handoff, and recovery.

The default is two workers and 30 minutes per assignment, with separate worktrees from the current dirty working tree. Results need coordinator review, combined checks, and root verification. Failed or unavailable verification stays incomplete. Native permissions must allow runtime Git/state operations and external CLI startup; restrictions remain visible rather than being bypassed. Desktop/IDE and remote sessions are outside this release.

## Select the task contract automatically


The installed profile controls planning and checkpoints. For each substantive outcome, the agent reads the [task catalog](docs/_templates/catalog.md) and only the selected blueprint:

| Kind | Outcome |
| --- | --- |
| `implementation` | Add/change an artifact or behavior, or improve structure while retaining behavior. |
| `bugfix` | Correct a reproduced contract violation and check regression. |
| `review` | Assess a defined scope/revision and report supported findings, coverage, and limits. |
| `investigation` | Explain observed behavior with evidence and explicit unknowns. |
| `design` | Record a system decision, viable alternatives, and consequences. |
| `research` | Answer a bounded question with attributable sources and comparison. |
| `runbook` | Author an operator procedure with actual commands and rehearsal limits. |
| `general` | Use the common contract for other verifiable outcomes, such as translation. |

Routing honors explicit scope and open checkpoints, then chooses by the next required output rather than keywords. A plan can contain several kinds: investigation → bugfix → runbook, for example. It lists future outcomes and materializes each spec when ready. Short status replies and explanations can stay in the conversation.

New specs store `kind` in frontmatter. Specs without it retain the common contract, so historical files need no migration. Findings, decisions, reports, and operating steps use their own deliverable formats; their micro specs remain small. All copied profiles include the catalog and every blueprint, and routing does not silently switch the installed profile.

A pure refactor uses `implementation`: specify the structural improvement, preserve the named behavior, and record baseline/regression evidence. A review produces findings without an unrequested repair. A no-findings report still records its scope and verification limits.

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

## Optional agent contracts

For authorized delegation, read the copied [delegation guide](docs/delegation.md). Use the current micro spec for acceptance, a reusable role for specialist instructions, a brief for assigned scope/context/ownership, and a worker result for observations and actual evidence. Short assignments/results can stay in messages; save optional records only for reuse or recovery.

The coordinator owns shared plan/index updates and verifies combined acceptance. Portable delegation permits parallel readers within one spec and orders edits/plan outcomes. Hybrid Team additionally permits ready independent writer scopes with runtime fencing, worktrees, and durable messages/events. Roles, briefs, results, and TeamSpec policy remain separate from outcome MicroSpecs and plan-owned progress.

[Optional native reviewer examples](adapters/README.md) sit outside portable payloads; Lite/Plan-first adoption never installs them. Hybrid Team explicitly installs preserving project-native roles/hooks/skills. The [review and delegation walkthrough](examples/review-delegation.md) illustrates supported findings and recovery; [the Hybrid Team walkthrough](examples/hybrid-team.md) illustrates mixed-provider work and incomplete checks.

## Examples and contributions

Read the [worked examples](examples/README.md) for a small validation fix, device administration, and a compatible pagination refactor. They illustrate documents and checkpoints; they contain no application and claim no application tests were run.

The [routing and Goal walkthrough](examples/routing.md) illustrates mixed task kinds and a bounded Goal contract.

See [CONTRIBUTING.md](CONTRIBUTING.md) for maintainer checks and workflow review scenarios. This repository uses its own Plan-first workflow; its [implementation history](docs/work/index.md) records actual work and verification.

The [v0.4 review and delegation report](evals/review-report.md) records Codex/Claude Code review, native-reader observations, saved recovery, and incomplete verification. It retains native-trace gaps, document-link failures, and deadline limits alongside passing cases. Both targeted Codex workflow regressions pass 80 independent behavior cases and seven original test-method executions.

The historical [v0.3 targeted workflow report](evals/workflow-report.md) observes a standalone Lite fix and a Plan-first compatible refactor with baseline evidence before code changes. The full earlier routing and Goal matrix was not rerun for v0.4.

The [historical v0.2 routing and Goal report](evals/routing-report.md) retains 15 fresh conversations across two drafts, including instruction gaps and affected reruns. All nine latest scenarios choose the expected kinds; eight meet every criterion, with one extra general blueprint read recorded for blocked verification. Independent grading passes 240 behavior-case executions and 47 original test-method executions. Portable Goal exhaustion, explicit extension, recovery, and blocked verification are exercised; native activation is untested.

The historical [v0.1 agent pilot report](evals/pilot-report.md) covers adoption and the original workflows. See the [pilot runner instructions](evals/README.md) for opt-in evaluation; ordinary checks do not launch an agent.

## License

MIT OR Apache-2.0, at your option. See [LICENSE-MIT](LICENSE-MIT) and [LICENSE-APACHE](LICENSE-APACHE).
