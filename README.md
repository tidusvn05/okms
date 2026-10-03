# okms

**Micro specs and recoverable workflows for coding agents.**

Copy a template into your project, point your agent at its workflow, and implement one small behavior contract at a time. Plans track progress and the next action; code holds implementation details. Everything is Markdown and works with ordinary file reads.

## Choose a template

| Template | Use it for | Workflow |
| --- | --- | --- |
| [Lite](templates/lite/docs/workflow.md) | One independent fix or small change | Save a micro spec → implement → check. Use its Plan-first fallback when the scope grows. |
| [Plan-first](templates/plan-first/docs/workflow.md) | Features with multiple outcomes or dependencies | Save a plan → repeat spec → implement → check → checkpoint → check the whole plan. |
| [Brownfield](templates/brownfield/docs/workflow.md) | Changes to an existing system | Plan-first with observed baseline and compatibility obligations. |

Each template contains seven Markdown files: an index, workflow, project context, plan and micro spec blueprints with their index, and a work index. The copied bundle has no runtime dependencies.

## Set up with your agent

Download or clone this repository. Open your agent in the destination project and paste this prompt, replacing the template name and checkout path:

```text
Set up okms using the plan-first template from /path/to/okms.

1. Inspect existing project docs and applicable agent instructions.
2. Reuse an existing okms installation referenced by the project's
   instructions, or look for one at docs/workflow.md or
   docs/okms/workflow.md. Recognize it by its template and template_version
   metadata; if the intended installation is ambiguous, ask which to use.
   For a new installation, choose docs/ if it is absent or empty;
   otherwise choose docs/okms/. Copy templates/plan-first/docs/ from the
   okms checkout only into a new or empty destination. If that destination
   contains other content, choose an empty destination. Do not overwrite
   existing files or switch an installed profile.
3. Fill context.md from actual project files: purpose, durable rules,
   applicable docs, and real required checks/test commands. Preserve
   existing context on repeated setup. Mark undiscovered information
   as unknown; never execute placeholders or invent commands.
4. Add this instruction once to the project's AGENTS.md, adapting paths:
   For implementation tasks, read and follow [the workflow](docs/workflow.md),
   starting with [the docs index](docs/index.md).
   Preserve existing instructions. If this agent uses a different
   instruction entrypoint, add the same pointer there instead.
5. Check the copied links and report the selected profile and location.
   Keep okbase optional; there is no need to install it for this setup.
```

Change both `plan-first` occurrences to `lite` or `brownfield` to select another profile. The setup prompt performs setup; give the agent an implementation task afterward.

## Set up manually

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
For implementation tasks, read and follow [the workflow](docs/workflow.md), starting with [the docs index](docs/index.md).
```

For a namespaced install, use `docs/okms/workflow.md` and `docs/okms/index.md`. Agents that use another instruction entrypoint need the same pointer in that entrypoint. The workflow is project guidance; reading the pointer and following it depend on the agent.

If the destination already contains an okms workflow, reuse it and keep its context, indexes, and work. Review profile switches or upgrades explicitly; do not copy a new payload over an existing installation.

## The micro spec contract

Every micro spec has four sections:

| Section | Contents |
| --- | --- |
| Intent | One observable outcome and why it matters. |
| Constraints | Essential Always/Never invariants. |
| Acceptance | Meaningful success and failure cases, usually Given/When/Then. |
| Verify | A real check or review method, expected result, and relevant test scope. |

Aim for roughly 100–250 words and 2–5 acceptance criteria. These are writing guides, not limits. A useful boundary is one behavior that can be verified; split by behavior rather than lines of code.

Keep critical authorization, data preservation, compatibility, and concurrency rules when they determine correctness. Reference existing code and docs for implementation details. Never weaken acceptance to make a failed implementation appear complete.

Plans use `Goal / Approach / Work / Resume / Result`; Brownfield adds `Baseline / Compatibility`. Save the plan before editing implementation. List future specs and dependencies, then save each spec just before its implementation. Agents continue without a mandatory approval pause unless review was requested or an important decision is missing.

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for maintainer checks and workflow review scenarios. This repository uses its own Plan-first workflow; its [implementation history](docs/work/index.md) records actual work and verification.

The [agent pilot report](evals/pilot-report.md) records seven fresh Codex conversations covering adoption, Lite, Plan-first recovery, Brownfield compatibility, blocked verification, and selective history reads. See the [pilot runner instructions](evals/README.md) to reproduce it explicitly.

## License

MIT OR Apache-2.0, at your option. See [LICENSE-MIT](LICENSE-MIT) and [LICENSE-APACHE](LICENSE-APACHE).
