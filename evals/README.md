# Observed agent pilots

The [runner](run_agent_pilot.py) explicitly invokes the installed Codex CLI against disposable Python projects. It uses the existing login and default model; it does not install a CLI, create credentials, or change user settings. The normal document checker never invokes it.

Read the [observed report](pilot-report.md) and [portable measurements](pilot-results.json) for the completed run.

Use the maintainer Python environment from [CONTRIBUTING.md](../CONTRIBUTING.md). Codex must already be on `PATH` and logged in. Prepare the fixtures and check their original baselines without launching an agent:

```sh
.venv/bin/python evals/run_agent_pilot.py --fixtures-only --run-dir .pilot-runs/my-run
```

Run the seven fresh conversations across five projects:

```sh
.venv/bin/python evals/run_agent_pilot.py --run-dir .pilot-runs/my-run
```

Use `--cases lite`, for example, to select a project. A run directory retains completed sessions, so another invocation can finish the remaining cases without repeating them. Regrade saved sessions with `--grade-only`. An interrupted session retains its artifacts; use a new run directory for a fresh attempt. The default timeout is 900 seconds per conversation and can be changed with `--timeout`.

## Scenarios

| Project | Fresh conversations | Observed behavior |
| --- | --- | --- |
| Setup | Initial and repeated adoption | Run the README prompt with existing docs and instructions; use `docs/okms/`, preserve content, and avoid duplicate pointers. |
| Lite | One fix | Save a standalone spec before changing the parser; check its behavior and record results. |
| Plan-first | Parser checkpoint and endpoint resumption | Save two dependent outcomes; stop after the first as requested; resume from files in a new conversation and create the second spec when needed. |
| Brownfield | One refactor | Record actual baseline and compatibility before edits, share validation, and retain endpoint behavior. |
| Blocked verification | One fix with an unavailable integration gate | Implement the parser, attempt the required gate, preserve it, and leave work blocked with truthful evidence. |

Plan-first includes 200 unrelated cancelled historical specs with body canaries. The observer counts canaries emitted in tool output; absence means no historical body was observed in that output, rather than proof that no file was ever opened.

## Evidence and limits

Projects live under a temporary directory outside this checkout. Artifacts live in the ignored `.pilot-runs/` directory, outside the agent's writable workspace: prompts, CLI commands/version, JSONL events, stderr, timestamped observations, file snapshots, final projects, baseline results, independent behavior matrices, original test results, and grades.

Each conversation runs `codex exec --ephemeral --json` with workspace write access and never receives an earlier conversation. A resume prompt asks only to continue the feature from saved files. Behavior is graded outside the project against independently specified inputs; the original test text is also rerun outside the agent's editable test directory.

File polling supplements command and file-change events. Different snapshot ticks support observed save order. Equal ticks cannot establish order and need trace review; the runner does not silently count them as a pass. Grading separates code outcomes from workflow contracts and failed required verification. Review unexpected grades against the trace before changing a template or grader.

The method follows the official [non-interactive Codex interface](https://developers.openai.com/codex/noninteractive) and [trace-based skill evaluation guidance](https://developers.openai.com/blog/eval-skills). A small run with one CLI and its current default model is evidence about those fixtures, not a guarantee across agents or projects. Worked examples remain illustrative; their application tests are not run by these fixtures.
