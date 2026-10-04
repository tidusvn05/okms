---
type: Guide
title: Lite workflow
description: Complete one independent change through a saved micro spec and use a plan when work needs coordination.
template: lite
template_version: "0.4.0"
---

# Lite workflow

## Start here

Follow the project's applicable agent instructions and the user's task. Read [the index](index.md) and [project context](context.md), then identify the work item matching the task. Explore relevant code, manifests, tests, and existing docs before choosing an approach. Exploration does not require a plan.

For a substantive work unit, read [the task catalog](_templates/catalog.md), classify the next requested outcome, and open only its selected blueprint. Honor explicit scope and matching checkpoints; a short status reply or explanation needs no new work document. The installed profile controls planning; the chosen `kind` controls the micro spec. Save new contracts before executing the scoped outcome.

For explicitly requested Goal or loop execution, also follow [bounded goal execution](goal-loop.md). Create or resume a Goal contract without silently changing this profile.

During setup, fill context from actual project files. Mark undiscovered commands as unknown, and resolve missing decisions that block the task. Never execute a `{{PLACEHOLDER}}` as a command or invent a test runner.

For one independent outcome, save a standalone micro spec using its selected catalog blueprint before executing the work. Use Plan-first when the task has multiple outcomes, dependencies, or uncertain scope. Continue after saving documents unless the user requested review or an important decision is missing.

## Read only what the task needs

Start with project-wide context, the current plan, the current micro spec, and its dependencies. Follow links to applicable conventions and affected components. Search for callers, shared invariants, and other affected behavior when needed. Use ordinary file reads and searches; okbase is optional.

The root index's Active work section points to open work. Historical work and `_templates/` are available for lookup, not an instruction to load the entire corpus. If multiple plans are open, select the one matching the task rather than assuming the newest is current.

## Existing-system obligations

Inspect the affected implementation, callers, interfaces, stored data, and shared dependencies. When the outcome changes or decides changes to existing contracts, record the current behavior and actual baseline check results before implementation or the decision. Include known failures and their evidence. If a check cannot run, record why; missing necessary evidence remains incomplete.

Identify behavior, interfaces, data, and invariants to preserve, plus intentional contract changes. Acceptance and verification must cover retained behavior and the requested change. Include migration, rollout, and rollback only when the change needs them. Ask when a breaking change lacks a clear requirement.

For a standalone micro spec, put concise baseline evidence in Verify and retained or intentionally changed contracts in Constraints and Acceptance. Existing code alone does not require a plan; use the Plan-first fallback only when the scope needs coordination. In a plan, add Baseline and Compatibility before Approach when these obligations apply. Omit them for outcomes that affect no existing contracts, such as an isolated new component or a report. Check shared integration effects before treating new code as isolated.

## Standalone loop

1. Save `work/MS001-short-title.md` with `type: MicroSpec`, a specific title and description, and `work_status: planned`. Allocate the next unused `MS` ID.
2. Replace every placeholder, add the file to [the work index](work/index.md) and the root index's Active work section, then set `work_status: in_progress`.
3. Execute the scoped outcome and check its deliverable or diff against every acceptance criterion. Run the project's required checks and relevant tests; add tests when needed.
4. Record actual methods, results, and justified test skips under `Result:` in Verify, then update `work_status`. Missing necessary verification leaves the item incomplete.
5. When done, remove its Active work pointer and keep the file and historical index entry at their existing paths.

For interrupted standalone work, record the next action and blocker under Verify. Resume from that note, inspect the working tree, and confirm recorded evidence.

If the task grows, use [the plan template](_templates/plan.md) and the Plan-first loop below. Keep the existing spec's ID and path, link it from the plan, move its progress and results into the Work table, and remove its `work_status` and checkpoint from the spec. The plan then owns progress and recovery.

## Plan-first fallback

1. Save Goal, Approach, Work, Resume, and Result, adding applicable Baseline and Compatibility sections, or read the checkpoint in an existing plan.
2. Select one planned item whose dependencies are done. Inspect relevant code or sources, choose its catalog kind, and save the selected micro spec with its outcome and verification method.
3. Add the created file to its directory index, turn its plan entry into a link, and set the item's State to `in_progress`.
4. Execute the scoped outcome. Keep detailed findings, designs, reports, or procedures in their deliverables. Update the spec and plan when scope changes; do not weaken acceptance to excuse a failure.
5. Check the deliverable or diff against every acceptance criterion. Run required project checks and the selected evidence method; add automated tests when needed to prove behavior.
6. Record evidence, update State and Resume, and proceed to the next ready item. At plan completion, check interactions between specs and finish the project's required checks.

Checkpoint at state or scope changes, handoff, and interruption. Retain the literal Resume fields `- Current:`, `- Next:`, and `- Blocker:`; put qualifications after their colons. Record the next concrete action and avoid logging every tool call. On resumption, inspect the working tree and recorded evidence before deciding what remains.

## Document contracts

Micro specs use **Intent / Constraints / Acceptance / Verify**. Describe one observable outcome, essential Always/Never invariants, and meaningful outcome-specific acceptance. Given/When/Then is useful for behavior; source-backed conclusions and document checks suit other kinds. Approximately 100–250 words and 2–5 acceptance criteria are writing guides, not limits. Include implementation details only when required for correctness or compatibility. Verify names a real command or review method, expected result, and relevant test scope or justified skip. A conclusion required by acceptance stays incomplete when supporting evidence is missing.

Plans use **Goal / Approach / Work / Resume / Result**, with **Baseline / Compatibility** between Goal and Approach when existing-system obligations apply. Include exclusions in Goal and important decisions or assumptions in Approach. Work columns are **Spec / Depends on / State / Evidence**. List future items as text; link them only after their files exist. Use `P001`, `P002`, … for plans and `P001-MS01`, `P001-MS02`, … for their specs. Allocate the next unused ID; keep assigned IDs and paths stable. One writer updates a plan at a time.

Create plans under `work/P001-short-title/` with `index.md`, `plan.md`, and their micro specs. Store the catalog-selected `kind` in each new micro spec. Legacy specs without kind remain valid under the common contract; preserve historical metadata. Render blueprints by replacing every `{{PLACEHOLDER}}` and setting `type`, `title`, and `description` to the actual document. Types are `Plan` and `MicroSpec`; reusable blueprints keep `type: Template`. Keep an index in every directory and list each immediate document or subdirectory with a useful description.

Only the copied bundle's root `index.md` has frontmatter, containing `okf_version: "0.2"`. Every child `index.md`, including work, Plan, and Goal directory indexes, starts with a heading and has no frontmatter. Other Markdown documents use concept frontmatter with `type`, `title`, and `description`.

## State and evidence

For standalone work, its micro spec owns progress and evidence in Verify. For planned work, the plan's Work table owns each spec's progress and results; do not duplicate work state in its micro specs. Standalone micro spec and plan frontmatter use `work_status`: `planned`, `in_progress`, `blocked`, `done`, or `cancelled`. OKF `status` has separate lifecycle values: `draft`, `stable`, or `deprecated`; it is optional here.

Mark an item `done` only when acceptance is supported by recorded evidence. Evidence names the actual command or method and its result, with code/test paths when useful. Tests may be skipped with a reason; acceptance checks and required project checks still apply. Missing necessary verification leaves the item incomplete. Failed checks return to diagnosis and implementation for that item.

Use `blocked` for work that cannot progress, with the missing input or dependency and next action. Continue other ready items when possible. Use `cancelled` only for withdrawn or superseded scope and record why. Mark the plan done after all remaining scoped items and required checks are complete; record summary and verification limits in Result.

## Optional delegation

Use [agent delegation](delegation.md) only when the user or applicable project/skill instructions authorize it. Keep assignments within the current spec, one coordinator for shared progress, and actual verification of combined acceptance. Roles and worker reports do not own work state; checkpoint through the existing Resume or standalone Verify fields.

## History

Add a plan or standalone spec to the root index's Active work section when starting it; remove that pointer when it closes. Keep directory indexes complete and retain completed documents at their existing paths. Completed specs describe the work at that time, not automatically today's requirements. New changes receive a new spec or plan according to their scope. Promote enduring rules into project context or the applicable current documentation, linking to existing sources instead of copying code details.
