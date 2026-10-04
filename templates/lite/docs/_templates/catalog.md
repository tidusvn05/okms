---
type: Guide
title: Task blueprint catalog
description: Select one micro spec blueprint by the next required outcome, independently of the installed workflow profile.
---

# Task blueprint catalog

Read this catalog at task selection, then open only the chosen blueprint. The installed Lite or Plan-first profile controls planning; task kind controls the contract. Apply existing-system obligations from the workflow according to the affected scope, without changing the profile or kind. Goal/loop execution is a separate explicit choice.

Every specialized blueprint already contains the common four-section contract. Read `micro-spec.md` only when selecting `general`; it is a fallback, not a prerequisite for the other kinds. Future planned kinds do not need their blueprints until their outcomes are ready.

| Kind | Choose for the next outcome | Deliverable and required evidence | Blueprint |
| --- | --- | --- | --- |
| implementation | Add or change an artifact, intentionally change behavior, or improve structure while retaining behavior. | Implementation with acceptance checks and applicable tests; refactors include baseline and retained-behavior evidence. | [Implementation](micro-spec-implementation.md) |
| bugfix | Correct demonstrated behavior that contradicts its contract. | A repair, evidence of the original failure, and passing regression checks. | [Bugfix](micro-spec-bugfix.md) |
| review | Assess a defined artifact or change and report actionable findings without repairing it. | A review report identifying scope/revision, findings with location, impact, and evidence, checked areas, and verification limits. | [Review](micro-spec-review.md) |
| investigation | Explain observed behavior, test hypotheses, or locate a cause before deciding the repair. | Findings tied to reproducible observations; separate confirmed facts, hypotheses, and remaining gaps. | [Investigation](micro-spec-investigation.md) |
| design | Make a system or interface decision under project constraints. | A decision document with viable alternatives, tradeoffs, compatibility, and scenario review. | [Design](micro-spec-design.md) |
| research | Answer a scoped question by gathering and comparing source evidence. | A source-backed report with dates, comparison criteria, limits, and supported conclusions. | [Research](micro-spec-research.md) |
| runbook | Document how an operator performs or recovers a procedure. | A runbook with prerequisites, commands, expected results, failure handling, and relevant rehearsal evidence. | [Runbook](micro-spec-runbook.md) |
| general | Produce a verifiable outcome that does not fit the specialized kinds, such as translation. | The requested artifact and a concrete review/check method. | [General](micro-spec.md) |

## Selection rules

1. Honor the user's explicit task kind and scope. Resume matching open work from its checkpoint; do not replace an already saved contract merely because the latest message uses another keyword.
2. Classify the immediate requested outcome, rather than words such as "research", "fix", or "goal" alone. A comparison of sources is research; an architecture decision is design; explaining a local failure is investigation.
3. A repair may need investigation first when ordinary exploration cannot establish a reproducible failure or cause. Keep separate outcomes as separate planned rows; write each spec when its dependencies are ready. An already understood defect can go directly to bugfix with reproduction evidence.
4. Use general for an unsupported category. Read context first and ask only when a missing decision materially changes the task. Do not invent another workflow or silently switch the installed profile.
5. Store the chosen `kind` in the new micro spec. Record a short selection reason in the plan's Approach, or in a standalone spec's Intent. Reassess the next outcome after verification, preserving the evidence and scope of past work.

A behavior-preserving refactor uses implementation: name the structural improvement and the contracts to retain, then check both. A review produces findings; explaining their cause may need investigation, and an authorized repair uses bugfix or implementation. A reviewer is a role, not another kind. For authorized delegation, read [the delegation guide](../delegation.md) only when needed; it does not change the installed profile or create parallel spec execution.

A status question or brief explanation can be answered directly. Save a work contract when starting a substantive unit with a durable deliverable or recoverable execution. Legacy specs without `kind` retain the common contract; do not rewrite historical files to add classification.

Keep the micro spec small. Detailed findings, designs, research, and operating commands belong in their deliverable documents, which use an appropriate format and truthful evidence. Given/When/Then is useful for behavior; other kinds may use outcome-specific acceptance statements.

For an explicitly requested goal or loop, also read [goal execution](../goal-loop.md) and [the Goal blueprint](goal.md). A Goal references plans; those plans still own item progress and evidence.
