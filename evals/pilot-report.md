# Independent agent pilot

All seven fresh Codex conversations met the observed criteria after correcting one grader defect. Independent grading passed 160 behavior-case executions and 16 original test-method executions across the five code-grading stages. The deliberately unavailable integration gate failed as designed; that agent correctly left its work blocked.

Observed on October 4, 2026 in Asia/Tokyo. The first run manifest started at October 3, 2026, 17:57 UTC. Agent: `codex-cli 0.159.0`, existing login, existing default model without an override. The model ID was not emitted or recorded. Payload version: `0.1.0`; no template payload changes were needed.

## Outcomes

| Fresh conversation | Independent behavior cases | Observed project tests | End state | Workflow |
| --- | --- | --- | --- | --- |
| Initial setup with existing docs | — | 3 passed | No implementation started | Pass |
| Repeated setup | — | 3 passed | Existing installation reused | Pass |
| Lite parser fix | 20 passed | 7 passed | `done` | Pass |
| Plan-first parser checkpoint | 20 passed | 7 passed | `in_progress`; endpoint deferred as requested | Pass |
| Fresh-session endpoint resumption | 40 passed | 15 passed | `done` | Pass |
| Brownfield shared validation | 60 passed | Baseline 4; final 14 passed | `done` | Pass |
| Unavailable required verification | 20 passed | 6 passed; integration gate exited 2 | `blocked` | Pass |

Each code-grading stage separately reran the original test text outside the agent's editable test directory. Those 16 test-method executions passed. Counts above are executions, including repeated parser cases during resumption, rather than 160 distinct requirements. All five fixture projects passed their original baseline tests before agents ran.

## Observed workflow evidence

- **Adoption:** the README setup prompt selected `docs/okms/`, preserved existing docs, code, tests, and agent instructions, filled context from actual files, and added one namespaced pointer. The second fresh conversation preserved all previously observed files, including context, without another pointer.
- **Lite:** the first spec snapshot was `planned` at 99.1 seconds and `in_progress` at 99.3; the first parser change was at 141.3. The project suite passed at 141.5, and the spec became `done` with an actual Result at 191.3. Its closed Active work pointer was removed.
- **Plan-first:** the plan and first spec were saved at 119.9 seconds, before the parser changed at 168.0. After tests passed, the first item became `done`; the second remained a plain `planned` row, with no second spec or endpoint change. The checkpoint recorded the remaining endpoint scope.
- **Resumption:** a different conversation received only “Continue the article pagination feature from the saved project files. Complete the remaining scope and required checks.” It saved the second spec at 112.6 seconds and changed the endpoint at 180.1. The parser was not rewritten. Both items became `done` after the full suite passed. Work progress stayed in the plan rather than its owned specs.
- **Brownfield:** the actual four-test baseline passed at 49.1 seconds. The plan saved Baseline and Compatibility at 124.8, before source changes at 282.1. The final suite and independent endpoint matrix passed, covering defaults, bounds, syntax, response shapes, item data, and authorization before validation.
- **Blocked verification:** the protected integration gate was attempted and exited 2 with an offline-service message. The file remained unchanged. Unit tests and independent parser checks passed, but the plan and its item remained `blocked`, with the failed command and next action recorded.
- **Selective reading:** neither Plan-first conversation emitted any of the 200 unrelated historical body canaries. The agent selected current work and its saved checkpoint. This measures emitted evidence; it does not prove that no historical file was opened without printing its body.

Times are relative to each conversation's observer start. The [portable measurements](pilot-results.json) retain all criterion results, distinct conversation IDs, command counts, check events, state/source timelines, and prompt/trace/source fingerprints.

## Repository and OKF checks

The repository document checker passed: 64 Markdown files, seven distributed/maintainer bundles, and 12 temporary onboarding scenarios. Runner/checker syntax checks and `git diff --check` passed. Published JSON was checked against every raw trace, prompt, source fingerprint, distinct conversation ID, and measured total.

Actual okbase L1 lint reported zero errors and warnings for maintainer docs (18 documents) and the five observed final bundles: adopted setup (7), Lite (8), Plan-first including history (212), Brownfield (10), and blocked verification (10). A valid knowledge base can still contain honestly blocked work; lint success does not imply that the unavailable integration gate passed.

## Grader correction

The initial setup grades rejected 11 valid links from adopted context to code, AGENTS.md, and existing docs in the consuming project. The grader had reused the exported-payload boundary, which requires links to stay inside the copied bundle. This was a grading defect: project-specific context can reference project files.

The checker now accepts an explicit consuming-project link boundary for adopted bundles. Its default still checks exported payload independence. Focused checks confirmed that these project links pass, the stricter default still rejects them, and links outside the consuming project remain rejected. The actual adopted setup bundle also passed okbase L1 with no errors or warnings.

Original rejected grades were retained as `grade-initial.json`. The same seven traces and final projects were regraded; no conversation was replaced or omitted to obtain the result. Template payloads stayed unchanged.

## Reproduction and limits

Follow the [runner instructions](README.md). With the maintainer environment and an already logged-in CLI:

```sh
.venv/bin/python evals/run_agent_pilot.py --run-dir .pilot-runs/my-run
```

Raw events, stderr, prompts, snapshots, original checks, and generated projects remain locally under `.pilot-runs/20261004-pilot/`, `.pilot-runs/20261004-handoff/`, and `.pilot-runs/20261004-compatibility/`. These ignored artifacts are outside the agent's writable project and are not distributed with templates. Published measurements contain fingerprints and selected evidence; rerunning produces new traces and may produce different agent behavior.

This was one default CLI configuration, seven conversations, and small Python fixtures. Polling supplies observed save order, supplemented by command and file-change events; equal ticks cannot establish order. History canaries measure bodies emitted in tool output. The fixtures do not test the applications described by the illustrative examples, large-project migration, every possible input, or other agents/models. The intentionally unavailable required gate remains unverified. These results support the workflow for the exercised cases without guaranteeing compliance elsewhere.
