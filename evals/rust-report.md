# Hybrid Team: observed Rust 0.2.0 CLI operation

All three final-payload cases pass on October 4, 2026. Codex and Claude Code each coordinate two real mixed-provider workers, receive an acknowledged peer exchange, resume the exact saved Codex session, integrate checked candidates, and hand off to the other provider. Each successful root passes 15 independently specified behavior cases. The unavailable-gate case retains failed verification and two blocked rows without applying the feature. [Measurements](rust-results.json) retain all criteria, exact native IDs, source fingerprints, and 90 selected artifact hashes.

Three disposable projects contain five native root CLI invocations and eight worker turns. This is a controlled Linux CLI observation, not a comparison of model performance. The earlier [Python report](hybrid-report.md) and [measurements](hybrid-results.json) retain their failed and partial attempts unchanged.

## Final matrix

| Coordinator case | Result | Root behavior | Plan outcome |
| --- | --- | --- | --- |
| Codex, handoff to Claude Code | All 13 criteria pass | 15/15 | Both rows done after combined/root checks and receiving-coordinator verification. |
| Claude Code, handoff to Codex | All 13 criteria pass | 15/15 | Both rows done after the same observed checks and explicit handoff. |
| Claude Code, required gate unavailable | All 10 criteria pass | 0/15, expected unchanged baseline | Both rows blocked; required gate exits 34 before root application. |

Each pair starts in parallel from one dirty-code snapshot and owns separate application modules. In both successful cases, the Codex label worker asks its Claude duration peer about the saved contract, yields waiting_input without edits, then resumes once with the same native ID after the response. Both request and response are acknowledged. Unlike the historical Python draft, these final Codex workers need no additional source-reading guidance or extra recovery turn. Returned candidates pass their actual assigned checks; the coordinator reviews scoped diffs, checks the combined worktree, applies it, and checks the actual root before recording completion.

Original root HEAD and index bytes, staged content, unstaged baseline edits, notes, check source, and agent instructions remain preserved in all three cases. The blocked candidates pass ordinary checks, but the configured external fixture gate remains unavailable. Its failure is retained; worker success does not replace the gate.

## Binary and source provenance

The observed executable is the Linux musl artifact downloaded from the successful four-platform [Actions rehearsal](https://github.com/tidusvn05/okms/actions/runs/37203104400), built at source commit e927ec404505dad084a6071f8f32550069587f84 with Rust 1.88.0. Its output is `okms 0.2.0`; file inspection identifies a stripped, statically linked x86_64 ELF executable. The runner copies that executable into its frozen source and each project.

- Executable SHA256: `9196bc504504882f70948439352bd391231aa6c8e5a4cc6bd88b5518c7773889`.
- Linux archive SHA256: `7682dbe0042df94fd8f104ecffd894e9cf98ffd0481a1c39856eedf5cf64a354`.
- Downloaded Linux artifact ZIP SHA256: `3d7e474617721f3504c054c10d42b35875f161eb2edf068e20f389b8180633f6`.
- Aggregate artifact ZIP SHA256: `91504058cf9e5428f910aad9b718c44f71432ccdc3376728349a5fbf920835ed`.

Both ZIP digests match GitHub artifact metadata. All six assembled release assets pass SHA256 checks. The 53 source fingerprints cover Rust/Cargo/build/license files, the embedded payload, checker, runner, and independent SQLite observer. Report-only changes do not alter these checked files. Actual public-download comparison and publication evidence are recorded in the [release plan](../docs/work/P014-rust-cli/plan.md).

## Method, maintenance evidence, and retained failures

Observed native versions are `codex-cli 0.159.0` and Claude Code `2.1.284`, with existing authentication and no model override. Claude streams identify `claude-opus-5-5`; captured Codex JSONL does not identify its effective model. Python executes the maintainer harness and fixture application checks only. The distributed CLI/runtime is Rust and requires no Python interpreter.

The harness joins each real root with its streamed native ID and supplies an identity-file pointer. Codex roots retain existing user settings, which allow unrestricted sandbox access and no approval prompts in this environment; workers use workspace-write with the shared state directory. Claude roots use acceptEdits and explicitly allowed local tools in disposable fixtures; workers retain the narrower runtime-command Bash rule and StructuredOutput. Native deny rules remain effective. No permission-bypass flag, credential change, hook-trust change, or model override is used.

All 36 final criteria pass without a failed or partial native case in this frozen run. Earlier Python failures remain in their original report. Rust controls separately reproduced concurrent SQLite initialization contention and a TERM-ignoring descendant surviving cancellation; both were repaired and retested. An independent grader control exposed the obsolete lexical-directory ordering assumption after Rust introduced UUID turn names. Ordering now uses actual invocation timestamps; incorrect native resume IDs still fail. Binary drift rejects reuse, and saved evidence remains gradable without executing a current binary.

All 121 maintainer tests and six Rust tests pass, with minimum-toolchain checking, formatting and clippy. [CI](https://github.com/tidusvn05/okms/actions/runs/37203068610) passes both toolchain/Python combinations. The rehearsal builds and smoke-tests Linux musl and macOS on x86_64 and arm64, then passes the full prepare checks against its Linux binary. The two reviewed PRs are merged: portable 0.4.1 namespaces page metadata and follows project documentation conventions. Actual strict MkDocs builds support the metadata fix; no agent adoption pilot is claimed for the new setup prose.

## Activation limits and retained artifacts

Claude hook receipts are observed. No Codex hook receipt is observed; the runner never enables untrusted hooks. Automatic Codex startup/end handling remains unverified until native hook trust is reviewed. Explicit join works in the observed cases, and an exited Codex root may remain registered until recovery when hooks are inactive.

Native Codex custom-role selection, native reader dispatch, and independent skill activation are not established. Four-platform binary smoke tests do not establish native-provider behavior on macOS, arm64, or WSL. Desktop/IDE, remote workers, other models, and different permission configurations require separate evidence. Cooperative local fencing, scope checks and worktrees do not establish an adversarial OS security boundary.

Raw streams, prompts, invocation arrays, identities, runtime databases, messages/events, revisions, checks, snapshots, and grades remain in ignored local run directories. Public measurements expose identifiers and hashes, not authentication tokens or raw traces. Worked examples remain illustrative and were not executed by this matrix.
