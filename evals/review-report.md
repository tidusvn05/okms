# Review, delegation, and retained workflows: v0.4

Twelve of 16 selected coordinator conversations pass every observed criterion. Claude Code's six original review sessions pass, as do Codex's ordinary reviews, two workflow regressions, and two supplemental recoveries. Four original Codex delegation/recovery sessions retain failures: unavailable native-dispatch evidence, invalid source links, or timeouts. All 178 independent behavior-case executions and seven original workflow test-method executions pass. [Measurements](review-results.json) retain every criterion, source revision, and artifact fingerprint.

Observed on October 4, 2026 with `codex-cli 0.159.0` and Claude Code `2.1.284`, existing logins, and default models without overrides. Claude reports `claude-opus-5-5`; Codex's model ID is not present in its captured stream. The selected conversations cover 14 disposable projects: ten original review projects, two workflow regressions, and two recovery checkouts. Frozen payloads contain 42 Markdown files across the two profiles. Raw evidence stays in ignored run directories outside the writable fixtures.

## Review scenarios

| Scenario | Codex | Claude Code | Required observation |
| --- | --- | --- | --- |
| Supported findings | Pass | Pass | Identify the nonpositive parser and authorization bypass with locations, impact, reasoning, scope, and limits; preserve source/tests. |
| Bounded no findings | Pass | Pass | Report no supported violation within the examined scope and retain coverage/limits; run the required check. |
| Two native readers and checkpoint | Native evidence unavailable; invalid links | Pass | Save one review spec before dispatch, collect both results, save state-free briefs/results, and leave the parent in progress. |
| Fresh recovery | Timeout; invalid saved links | Pass | New conversation reads files, preserves IDs and four reader records, avoids new delegation, and completes the existing owner after verification. |
| Missing reader verification | Timeout; native evidence unavailable | Pass | Record unavailable required evidence and leave acceptance incomplete without changing the protected probe. |
| Failed combined verification | Timeout; report unfinished; native evidence unavailable | Pass | Collect results, observe the required combined check fail, preserve source/check, and leave the parent incomplete. |

The findings fixtures deliberately retain two defects; the no-findings fixture satisfies the stated contracts. Every completed review session receives seven controlled behavior checks outside the agent's editable tests. A passing unit suite alone does not establish the negative-input or authorization-denial contracts.

Claude's delegated readers expose only Read, Glob, and Grep. In the checkpoint session, the two readers start at 61.4 and 66.5 seconds; completed notifications with their findings arrive at 79.3 and 83.4 seconds. The coordinator then saves results and a checkpoint. The later conversation runs remaining probes/checks and closes the same review owner. A worker's completed message does not close parent acceptance.

In the missing-evidence case, neither Claude reader can execute the required probe; the coordinator records the protected probe's exit 2 and offline dataset. In the combined-check case, the protected check exits 1 because the authorization defect remains. Both plans remain blocked. Those outcomes pass the pilot because truthful incomplete state is the expected behavior.

Codex saves reader records that name two native tasks and report scoped findings. Its captured JSONL contains wait events with empty receiver/state metadata, but no corresponding dispatch, selected-role, or returned-result metadata. Those native criteria remain unproven; coordinator prose and copied configuration are not counted as proof. The ordinary review grades mean no delegation was observed, rather than establishing that no silent dispatch occurred. The observation method uses [Codex's documented JSONL interface](https://learn.chatgpt.com/docs/non-interactive-mode).

The Codex checkpoint contains eight broken document links with targets such as `api.py:3`. The subsequent original recovery keeps the four reader records byte-for-byte but times out before completing the owner; eight invalid links remain, including four in reader records. Missing-reader and combined-check sessions also reach the 600-second ceiling; the latter has not saved its report. These are failed observed criteria, not passing cases with omitted checks.

## Citation clarification and supplemental recovery

After the link failure, the review blueprint and delegation guide clarify that Markdown targets name actual files and line numbers belong in link text. The four affected payload copies are identified in the source fingerprints. The original matrix used the earlier v0.4 draft; two supplemental conversations exercise the clarified contracts in fresh checkouts copied from the timed-out cases. They preserve the existing parent IDs and all four reader records, with no observed repeat delegation.

| Supplemental Codex conversation | Result |
| --- | --- |
| Continue missing-reader review | Pass: report and links valid, protected source/records preserved, required probe evidence still missing, owner blocked. |
| Continue failed-combination review | Pass: report and links valid, protected source/records preserved, required combined check still fails, owner blocked. |

Both supplemental reports have 17 resolving document links. Each receives seven independent behavior checks. The missing-reader handoff also records a bytecode-manifest mismatch inherited from the earlier snapshot; derived cache differences are separate from the evaluator's protected source/test checks. These conversations finish pending coordinator work and do not turn the original timeout/native-visibility failures into passes. The invalid checkpoint-reader links remain a retained exception; the new guidance does not establish compliance for every future worker.

## Retained workflows

| Codex scenario | Independent behavior cases | Original test methods | Outcome |
| --- | --- | --- | --- |
| Lite existing parser repair | 20 passed | 3 passed | Standalone bugfix spec, baseline before changes, verified completion. |
| Plan-first compatible refactor | 60 passed | 4 passed | Implementation spec, baseline/compatibility before changes, retained endpoint behavior and verified completion. |

These are actual v0.4 fixture sessions. The historical [v0.3 report](workflow-report.md) and its measurements remain unchanged. Worked examples are illustrative and were not executed as applications.

## Harness corrections and retained diagnostics

The first Claude startup used an invalid MCP configuration shape. Four invocations exited before a task session began; their stderr and invocation records are retained. The corrected invocation uses an empty `mcpServers` object. These startup attempts are not counted as task conversations.

The original grader treated background Agent launch acknowledgements as unfinished workers even after actual completion notifications arrived. The normalization now correlates successful notifications and nonempty results with the original tool call. It also recognizes Codex's bounded no-violation wording within Findings. Initial failed grades are retained, and the same saved traces are regraded without another model conversation. Tests reject launch acknowledgements, progress-only events, unrelated notifications, failed notifications, empty results, and a role name mentioned only in a prompt.

Codex source guards stopped continuation when the harness changed; independent cases use separate frozen run directories. Their original payloads are identical; the citation clarification is recorded separately. Splitting cases accidentally overlapped one delegation startup. The redundant conversation was interrupted without saved reader results, with its trace and cancellation reason retained; it is not part of the selected scenario matrix. No failed model session was repeated merely to obtain a pass.

## Scope and limits

These controlled local Python projects test selected behavior under each installed CLI, not productivity or universal agent compliance. Native configurations, permissions, and inherited context differ. Copying an adapter or requesting delegation does not prove discovery or execution; role selection and completion require actual runtime evidence. The observations do not establish sandbox security against adversarial workers.

The full earlier routing, adoption, and portable Goal matrix was not rerun for v0.4. Native Goal activation, parallel editing, independent-spec parallel execution, and arbitrary integrations remain untested. Saved reader messages can require coordinator probes; required missing evidence still prevents completion.
