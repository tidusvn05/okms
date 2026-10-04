---
type: Research
title: Task kinds and agent formats for okms
description: Assess catalog coverage and recommend lightweight contracts for reviews, delegation, orchestration, and recovery across Codex and Claude Code.
---

# Task kinds and agent formats for okms

Research date: October 4, 2026. Provider facts below come from official documentation retrieved on that date. Recommendations are this assessment's design proposals, not implemented okms contracts.

## Assessment

The current seven kinds cover the main outcomes of ordinary coding-agent work. The strongest additional candidate is `review`. Behavior-preserving refactoring deserves clearer routing, either through a broader implementation definition or a separate `refactor` kind. Delegation and coordination need different information from a task spec; they should be optional execution contracts rather than new task kinds.

Keep the portable Markdown core. Prototype delegation instructions and result reporting before distributing native agent configurations or a parallel execution workflow. No provider configuration or distributed template is changed by this report.

## Repository evidence and comparison criteria

The [catalog](../../_templates/catalog.md) selects by the next observable outcome and required evidence. The [workflow](../../workflow.md) keeps Intent / Constraints / Acceptance / Verify in every spec and assigns progress to the plan. It requires one writer per plan and describes executing and verifying one micro spec at a time. The repository's `README.md` promises ordinary file access without a runtime dependency; each copied payload currently contains 16 Markdown files.

The published v0.3 pilot in `evals/workflow-report.md` observes two controlled Codex conversations, including a compatible refactor. Its model ID was not recorded. The v0.2 routing pilot in `evals/routing-report.md` covers the kinds and recovery but retains a selective-reading failure. These paths are relative to the repository root. Neither report establishes Claude Code compliance or multi-agent coordination.

Evaluate additions by five criteria: a distinct outcome and evidence requirement, an understandable routing boundary, portability, reading and maintenance cost, and recovery from files. A tool capability alone does not justify another kind. No adoption-frequency or productivity measurement is available for ranking these proposals.

## Are the current kinds sufficient?

| Current kind | Coverage | Remaining issue |
| --- | --- | --- |
| `implementation` | Features and intentional behavior changes, including code and documentation implementations. | Its wording does not clearly cover a pure refactor that must preserve externally observable behavior. |
| `bugfix` | Reproduced contract violations and regression evidence. | Good boundary; unexplained failures may first need investigation. |
| `investigation` | Local observations, tested hypotheses, root causes, and explicit unknowns. | Findings are a deliverable; a subsequent repair remains a separate outcome. |
| `design` | Architecture or interface decisions, alternatives, consequences, and compatibility. | A small decision-record format could help authors; another architecture kind would overlap. |
| `research` | Attributable source comparison and bounded recommendations. | A report format helps keep sources and uncertainty out of the micro spec. |
| `runbook` | Authoring an operating procedure and bounded rehearsal. | Executing a deployment or live recovery is a different outcome from documenting it. |
| `general` | Other verifiable artifacts, explicitly including bounded review. | It provides coverage but gives little guidance for specialized review evidence. |

The broad coverage is adequate; the gaps concern defaults and selection clarity. Keep kinds about outcomes. For example, a reviewer is an agent role, while a review report is a task outcome; either a main agent or a subagent can produce it.

### Candidate additions, ranked

| Candidate | Recommendation | Distinct acceptance and evidence |
| --- | --- | --- |
| `review` | First candidate to prototype. | Identify the reviewed revision/diff and scope; report actionable findings with location, impact, and supporting evidence; record checked areas and limits even when no issue is found. Repair is separate unless requested. |
| `refactor` | Clarify routing now; add a kind if recurring use justifies it. | Name the structural improvement and behavior to retain; baseline and regression evidence cover that behavior. A code diff or a passing unrelated suite alone is insufficient. |
| `migration` | Add only after concrete migration cases expose repeated omissions. | Cover data/interface preservation, supported old/new states, cutover verification, and recovery or an explicit irreversibility constraint. Routine dependency upgrades do not automatically need it. |
| `validation` or `test` | Initially use `general` for a standalone validation report and `implementation` for implementing tests. | A standalone outcome needs a test matrix, actual results, environment, and untested scope; writing tests and executing validation are different outputs. |
| `operation` | Conditional future extension if okms includes operational execution. | Execute a requested procedure against a named environment; verify resulting state, record stop conditions and actual recovery evidence. Runbook authoring remains `runbook`. |
| `documentation`, `security`, `performance` | Start as scope or focus, using the appropriate current kind. | Documentation can be implementation, research, or runbook; security/performance work can be review, investigation, or repair. Create a specialized kind only when evidence requirements repeatedly need their own contract. |
| `subagent`, `orchestrator`, `planner` | Keep as roles or execution choices. | Their names describe who works or how work is assigned, and do not identify the deliverable's acceptance criteria. |

`review` improves a currently explicit general fallback. `refactor` has a stronger compatibility emphasis but also overlaps obligations already added in v0.3. Two reasonable alternatives are to broaden implementation to include behavior-preserving structural improvements, or to give refactors their own blueprint. Prefer the smaller option until routing pilots show a useful distinction.

For review, evidence can be code reasoning, a reproducible probe, or an appropriate test. Require checks that support each claim rather than tests for every finding. A report that finds no defects must describe its examined scope and limits; it cannot establish that all possible defects are absent.

## What the tools actually support

### Project instructions

Codex discovers layered `AGENTS.md` instructions. A short project pointer to the existing workflow fits that mechanism. [Official OpenAI documentation: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Claude Code supports `CLAUDE.md` and, since v2.1.277, direct `AGENTS.md` loading in supported sessions. Its default loads AGENTS.md when no CLAUDE.md or CLAUDE.local.md exists in the working directory or above; otherwise those Claude files take precedence. Existing imports or the Project instructions setting can select both. Preserve the project's entrypoint and verify which rules load. [Anthropic: project instructions](https://code.claude.com/docs/en/memory#agents-md).

### Agent definitions and delegation

Codex project agents use `.codex/agents/*.toml`, with `name`, `description`, and `developer_instructions`; session settings can configure models and sandbox behavior. Its documentation describes delegation on request or through applicable instructions and cautions about concurrent writes. [Official OpenAI documentation: subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

Claude Code project agents use `.claude/agents/*.md`: YAML metadata and a Markdown system prompt. Ordinary subagents start with isolated context; forks inherit the conversation. Metadata controls tools and optional worktree isolation. Project instructions can load, with documented exceptions, so the delegation message still needs the necessary task context. [Anthropic: subagents](https://code.claude.com/docs/en/sub-agents).

These are separate native schemas. A common role description can supply their instruction content, but a portable okms document is not automatically a registered agent or a permission boundary.

### Reusable procedures

Both products document the Agent Skills standard and `SKILL.md`. Codex discovers repository skills in `.agents/skills/`; the file includes a name, description, and instructions loaded when used. [Official OpenAI documentation: skills](https://learn.chatgpt.com/docs/build-skills).

Claude Code supports `.claude/skills/<name>/SKILL.md` and invocation through `/name`. Legacy custom commands remain supported through skills. Claude-specific execution and invocation options should stay in an adapter. [Anthropic: skills](https://code.claude.com/docs/en/skills).

A skill packages a procedure worth repeating, such as reviewing a migration. A micro spec describes one requested result and its proof. Reuse a procedure while keeping each task's scope and acceptance in its own spec.

### Coordination and automation

Claude agent teams coordinate peer sessions through a lead, messaging, and shared tasks. They remain experimental and disabled by default; in-process teammates are not restored by session resumption. [Anthropic: agent teams](https://code.claude.com/docs/en/agent-teams).

Claude also documents dynamic workflows: JavaScript orchestration saved under `.claude/workflows/`, with a metadata block and runtime calls for agents, parallel work, and pipelines. Availability and enablement depend on the documented environment. This is a native executable format, separate from a Markdown execution policy. [Anthropic: dynamic workflows](https://code.claude.com/docs/en/workflows).

Codex supports lifecycle configuration through `hooks.json` or `[hooks]` in `config.toml`. Claude Code also supports lifecycle hooks. Hooks introduce runtime behavior with provider-specific semantics. [Official OpenAI documentation: hooks](https://learn.chatgpt.com/docs/hooks), [Anthropic: hooks](https://code.claude.com/docs/en/hooks-guide).

The documentation supports optional adapters, not a claim that one agent manifest, workflow script, or hook configuration works identically in both tools. A Markdown ownership rule is guidance; tool permissions and runtime checks provide the enforceable controls.

## Which additional portable formats are useful?

These are proposed conventions, not newly required documents. Use links and existing fields where possible; do not make every task produce every artifact.

| Format | Use when | Minimum information | Relationship to current okms |
| --- | --- | --- | --- |
| Role instructions | A specialist is reused across tasks. | Mission, trigger, authority, expected output, escalation. | Reusable instructions for a main agent or native subagent; no task progress. |
| Delegation brief | Another agent needs a bounded assignment. | Parent spec, necessary context, owned scope, requested output, evidence, return/stop condition. | Reference the current spec and its acceptance; carry only assignment-specific details. |
| Worker result | A coordinator consumes another agent's work. | Covered scope/revision, findings or changed paths, actual evidence, gaps/blocker, next action. | Input to the existing progress owner; cannot mark the parent item done by itself. |
| Execution policy | Work needs several agents or repeatable coordination. | Dispatch/dependencies, ownership, concurrency limit, integration owner, verification, failure/recovery. | Initially live in plan Approach; a separate reusable guide is optional. |
| Handoff/checkpoint | Work crosses sessions, people, branches, or worktrees. | Contract links, current revision/working tree, actual evidence, unresolved issue, next action. | Extend the existing Resume checkpoint only with missing information. |
| Deliverable format | The result is a report, decision, or procedure. | Fields needed to judge that particular artifact. | Keep detail outside the micro spec, as the current catalog already requires. |

Useful deliverables include a review report (scope, findings, evidence, limits), a decision record (drivers, alternatives, decision, consequences), and investigation findings (observations, hypotheses, probes, remaining unknowns). Their blueprints can improve authoring without adding corresponding task kinds.

### Should these resemble micro specs?

An assignment should reuse Intent / Constraints / Acceptance / Verify because it still promises an observable result. Reference the parent acceptance instead of copying it. A role definition serves many assignments and needs stable mission, trigger, authority, and reporting rules. A result or handoff records what actually happened and what remains. Giving all three the same four sections would obscure those differences.

Illustrative delegation content, requiring actual parent links, revisions, and paths when used:

```text
Reference: current parent MicroSpec and plan row
Context: reviewed revision/diff and relevant project instruction paths

Intent
Review only the assigned authorization paths against the parent contract.

Constraints
Read-only assignment. No application or plan edits.
State assumptions and request missing evidence from the coordinator.

Acceptance
Return location, impact, and evidence for each finding, plus reviewed scope
and limitations. Use the parent's review criteria; do not redefine them.

Verify
Check findings against the actual code and permitted probes.
Return the method, result, and any unexecuted necessary checks.
```

Illustrative worker result shape:

```text
Reference: parent contract and assigned scope
Revision/worktree: the exact files or revision examined
Result: findings or changed paths, with supporting references
Evidence: actual command/review method, result, and relevant artifact
Remaining: skipped or unavailable checks, partial coverage, blocker
Next: concrete action for the coordinator
```

Neither illustration was executed against an application. A short delegated read can receive this content in its task message. Persist it only when the assignment has an independent durable outcome or needs recovery; it does not automatically require another plan or spec file.

### What the coordinator needs

Use the existing plan as the authority for item progress and evidence. In Approach, specify:

1. Delegate only requested or otherwise authorized independent work; keep dependent steps ordered.
2. Start with parallel readers inside one selected spec. Independent spec execution would require an explicit extension to the current sequential work loop.
3. Assign file ownership before writes. A coordinator alone updates the shared plan, indexes, and ID allocation; a worker reports results back. Worktrees can isolate edits but do not prove integration compatibility.
4. Identify who integrates patches and checks the combined result. A child's passing checks are evidence for its scope, not the integrated parent outcome.
5. Record unavailable or partial work without closing the parent item. Define bounded retries and checkpoint before interruption; do not silently introduce a Goal or reset its counters.
6. Recover from saved contracts, revisions, evidence, and next actions. Recreate runtime agents when necessary rather than assuming old agent identifiers are still live.

One spec can use several readers without becoming several outcomes. Several independently verifiable deliverables can receive separate plan rows/specs. This boundary prevents documentation from growing in proportion to the number of agent threads.

## Recommended next steps and evaluation limits

1. Draft a `review` contract and two examples: a supported defect finding, and a review with no findings but explicit limits. Clarify pure-refactor routing at the same time; do not assume another kind is necessary.
2. Prototype a short delegation brief and worker result inside a plan. Reuse Resume and keep one progress owner. Evaluate whether a standalone role guide is useful before shipping it.
3. If native configuration is desired, keep optional Codex/Claude adapters outside the mandatory payload. Document tested tool versions, instruction loading, permissions, and isolation behavior. Merge entrypoint pointers without replacing existing project rules.
4. Run fresh-session pilots on both tools for review, two parallel readers, missing child verification, integration failure, and recovery without prior chat. Compare required behavior and coordination failures before making speed or cost claims.
5. Consider parallel writers, migration, operational execution, hooks, or workflow scripts only after those pilots establish a need. Every additional core blueprint currently needs consistent maintainer, Lite, and Plan-first copies, catalog/index/checker updates, and relevant evaluation.

Local read-only version checks returned `codex-cli 0.159.0` and `2.1.284 (Claude Code)`. These identify installed binaries only. This research did not launch task sessions, verify native configuration loading, enable teams/workflows, or benchmark either product. Documentation is a current capability reference and may evolve; provider-specific adapters need actual runtime evaluation.

The recommendation is supported as a proportionate design direction. It does not establish that proposed contracts improve agent compliance or throughput. The existing document checker can verify repository structure, but those behavioral claims need the proposed pilots.
