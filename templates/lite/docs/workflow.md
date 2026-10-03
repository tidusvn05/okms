---
type: Guide
title: Lite workflow
description: Complete one independent change through a saved micro spec and use a plan when work needs coordination.
template: lite
template_version: "0.1.0"
---

# Lite workflow

## Start here

Follow the project's applicable agent instructions and the user's task. Read [the index](index.md) and [project context](context.md), then identify the work item matching the task. Explore relevant code, manifests, tests, and existing docs before choosing an approach. Exploration does not require a plan.

During setup, fill context from actual project files. Mark undiscovered commands as unknown, and resolve missing decisions that block the task. Never execute a `{{PLACEHOLDER}}` as a command or invent a test runner.

For one independent change, save a standalone micro spec using [the micro spec template](_templates/micro-spec.md) before editing implementation. Use Plan-first when the task has multiple outcomes, dependencies, or uncertain scope. Continue after saving documents unless the user requested review or an important decision is missing.

## Read only what the task needs

Start with project-wide context, the current plan, the current micro spec, and its dependencies. Follow links to applicable conventions and affected components. Search for callers, shared invariants, and other affected behavior when needed. Use ordinary file reads and searches; okbase is optional.

The root index's Active work section points to open work. Historical work and `_templates/` are available for lookup, not an instruction to load the entire corpus. If multiple plans are open, select the one matching the task rather than assuming the newest is current.

## Standalone loop

1. Save `work/MS001-short-title.md` with `type: MicroSpec`, a specific title and description, and `work_status: planned`. Allocate the next unused `MS` ID.
2. Replace every placeholder, add the file to [the work index](work/index.md) and the root index's Active work section, then set `work_status: in_progress`.
3. Implement the behavior and check the diff against every acceptance criterion. Run the project's required checks and relevant tests; add tests when needed.
4. Record actual methods, results, and justified test skips under `Result:` in Verify, then update `work_status`. Missing necessary verification leaves the item incomplete.
5. When done, remove its Active work pointer and keep the file and historical index entry at their existing paths.

For interrupted standalone work, record the next action and blocker under Verify. Resume from that note, inspect the working tree, and confirm recorded evidence.

If the task grows, use [the plan template](_templates/plan.md) and the Plan-first loop below. Keep the existing spec's ID and path, link it from the plan, move its progress and results into the Work table, and remove its `work_status` and checkpoint from the spec. The plan then owns progress and recovery.

## Plan-first fallback

1. Save Goal, Approach, Work, Resume, and Result in a new plan, or read the checkpoint in an existing plan.
2. Select one planned item whose dependencies are done. Inspect its relevant code and save a micro spec with the intended behavior and verification method.
3. Add the created file to its directory index, turn its plan entry into a link, and set the item's State to `in_progress`.
4. Implement the item. Update its spec and plan before continuing if requirements or scope change; do not rewrite acceptance to excuse a failed implementation.
5. Check the diff against every acceptance criterion. Run relevant project checks and tests; add tests when needed to prove behavior.
6. Record evidence, update State and Resume, and proceed to the next ready item. At plan completion, check interactions between specs and finish the project's required checks.

Checkpoint at state or scope changes, handoff, and interruption. Record the current item, next concrete action, and blocker in Resume; avoid logging every tool call. On resumption, inspect the working tree and recorded evidence before deciding what remains.

## Document contracts

Micro specs use **Intent / Constraints / Acceptance / Verify**. Describe one observable outcome, essential Always/Never invariants, and meaningful success and failure cases. Approximately 100–250 words and 2–5 acceptance criteria are writing guides, not limits. Include implementation details only when required for correctness or compatibility. Verify names a real command or review method, expected result, and relevant test scope.

Plans use **Goal / Approach / Work / Resume / Result**. Include exclusions in Goal and important decisions or assumptions in Approach. Work columns are **Spec / Depends on / State / Evidence**. List future items as text; link them only after their files exist. Use `P001`, `P002`, … for plans and `P001-MS01`, `P001-MS02`, … for their specs. Allocate the next unused ID; keep assigned IDs and paths stable. One writer updates a plan at a time.

Create plans under `work/P001-short-title/` with `index.md`, `plan.md`, and their micro specs. Render blueprints by replacing every `{{PLACEHOLDER}}` and setting `type`, `title`, and `description` to the actual document. Types are `Plan` and `MicroSpec`; reusable blueprints keep `type: Template`. Keep an index in every directory and list each immediate document or subdirectory with a useful description.

## State and evidence

For standalone work, its micro spec owns progress and evidence in Verify. For planned work, the plan's Work table owns each spec's progress and results; do not duplicate work state in its micro specs. Standalone micro spec and plan frontmatter use `work_status`: `planned`, `in_progress`, `blocked`, `done`, or `cancelled`. OKF `status` has separate lifecycle values: `draft`, `stable`, or `deprecated`; it is optional here.

Mark an item `done` only when acceptance is supported by recorded evidence. Evidence names the actual command or method and its result, with code/test paths when useful. Tests may be skipped with a reason; acceptance checks and required project checks still apply. Missing necessary verification leaves the item incomplete. Failed checks return to diagnosis and implementation for that item.

Use `blocked` for work that cannot progress, with the missing input or dependency and next action. Continue other ready items when possible. Use `cancelled` only for withdrawn or superseded scope and record why. Mark the plan done after all remaining scoped items and required checks are complete; record summary and verification limits in Result.

## History

Add a plan or standalone spec to the root index's Active work section when starting it; remove that pointer when it closes. Keep directory indexes complete and retain completed documents at their existing paths. Completed specs describe the work at that time, not automatically today's requirements. New changes receive a new spec or plan according to their scope. Promote enduring rules into project context or the applicable current documentation, linking to existing sources instead of copying code details.
