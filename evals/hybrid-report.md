# Hybrid Team: observed v0.1 CLI operation

The three selected acceptance cases pass: Codex coordinates mixed workers and hands off to Claude Code; Claude Code coordinates the same pair and hands off to Codex; an unavailable required gate prevents application and completion. Both successful projects pass all 15 independent root behavior cases, preserve the original HEAD and index bytes, and complete only after actual combined/root checks. [Measurements](hybrid-results.json) retain every criterion, exact native session ID, source fingerprint, and selected artifact hash.

Eight projects were executed on October 4, 2026: three pass, four retain failed criteria, and one was interrupted with partial evidence. These projects contain 14 root CLI invocations and 32 worker turns. Two separate component probes add one genuine CLI invocation each. This controlled Linux CLI evaluation measures selected operational behavior.

## Selected acceptance cases

| Frozen run and coordinator | Result | Observed evidence |
| --- | --- | --- |
| v5 / Codex | Pass, 13 criteria | Two returned providers; parallel starts; acknowledged peer request/reply; exact-session resume; verified integration; handoff to Claude; two completed rows; 15/15 independent behavior cases. |
| v4 / Claude Code | Pass, 13 criteria | The same operational evidence, with handoff to Codex; two completed rows; 15/15 independent behavior cases. |
| v4 / unavailable gate | Pass, 10 criteria | Two returned candidates and successful assigned checks; mandatory combined gate exits 34; application remains unchanged; both rows stay blocked. |

The label and duration workers own separate modules and share one dirty-code baseline. Both start before either returns. The label worker asks its Claude peer to confirm the saved contract, yields `waiting_input`, and resumes with its recorded Codex session ID after the peer replies. Both messages are acknowledged. A worker result remains a candidate until the coordinator reviews diffs, checks the combined worktree, applies it, and checks the actual root.

In each successful selected case, Codex also yields a second waiting turn because the draft's generic instruction to use a named Read tool is unsuitable for Codex. The coordinator supplies source/tool guidance and resumes the same session. These cases establish recoverable communication and integration; they do not establish autonomous source reading under that draft. The final provider-specific correction has separate component evidence below.

The failed-gate case deliberately leaves the root feature unimplemented: its root oracle reports 0/15 while the combined candidate's ordinary check passes. The required unavailable gate remains configured and fails before application. That combination supports truthful incomplete state; passing worker checks cannot replace the gate.

## Method and native activation

Observed versions are `codex-cli 0.159.0` and Claude Code `2.1.284`, using existing logins with no model override. Claude's stream reports `claude-opus-5-5`; Codex's captured JSONL does not identify its effective model. Source snapshots freeze the profile, checker, and runner separately for each run. Raw prompts, streams, invocation arrays, runtime state, messages, check logs, revisions, baseline/final files, and grades remain in ignored local run directories. Published hashes identify those artifacts but do not embed or distribute them.

The harness explicitly joins each real root using its streamed native ID and supplies its identity-file pointer. Claude root and worker hook receipts are observed. No Codex hook receipts are observed, and the harness does not activate untrusted hooks. Automatic Codex startup and SessionEnd handling therefore remain unverified; native review through `/hooks` is a prerequisite described in the [Codex hook documentation](https://learn.chatgpt.com/docs/hooks). With hooks inactive, the runtime can retain a departed root until explicit recovery.

Codex roots preserve existing user configuration, which here permits unrestricted sandbox access and no approval prompts. Workers use workspace-write plus the shared runtime state directory. Final Claude roots use acceptEdits and explicitly allowed local read/edit/Bash tools in the disposable fixtures. Claude workers retain a narrower runtime-command Bash rule. No permission-bypass flag is used; native deny rules remain effective. The initial stricter root fixture policy caused genuine denials and was revised explicitly, without changing worker scope or the grading criteria. Native/parent restrictions may prevent the same startup elsewhere.

## Retained failures and diagnosed changes

| Earlier case | Failed criteria retained |
| --- | --- |
| v1 / Codex | Root timeout/native permission denials; changed index bytes from optional Git stat-cache refresh. |
| v2 / Claude Code | Native root permission denials, despite successful feature and operational checks. |
| v2 / unavailable gate | Native root permission denials; required-gate/incomplete-state criteria pass. |
| v3 / Codex | Native denials, index-cache refresh, and unfinished receiving-coordinator completion. |
| v3 / Claude Code | Operator interruption after diagnosed shell-approval/handoff problems; native-root and final-completion criteria remain failed. |

The interrupted case preserves its stop reason and partial observations; v3's blocked case was never executed. Reruns use new directories after concrete implementation or fixture-policy changes. Earlier failures remain failures, including cases whose feature behavior already passes.

Initial Claude workers received a schema while their explicit tool list excluded StructuredOutput. Some returned prose or invalid field types and correctly failed the result contract. The adapter and native role now retain StructuredOutput, the prompt states the exact five-field schema, and strict validation remains. The [Claude structured-output documentation](https://code.claude.com/docs/en/agent-sdk/structured-outputs) describes the tool-backed result flow. Shell guidance also avoids compound calls, pipelines, loops, and heredocs under the narrow worker rule; native Read handles Claude file/log reads.

Handoff previously rotated the former coordinator's token without refreshing its identity file, exposed when Codex hooks were inactive. The runtime now writes a standby identity for the former owner and a coordinator identity for the receiver; cached old credentials remain rejected. A regression verifies both standby messaging and privileged-operation fencing.

Index-byte failures did not represent lost staged content, but still fail the original strict preservation criterion. The final fixture roots set `GIT_OPTIONAL_LOCKS=0` to suppress optional stat-cache refresh. This follows [Git's documented background-refresh behavior](https://git-scm.com/docs/git-status#_background_refresh), while preserving the same byte comparison.

## Final component observations and limits

The read-only Claude transport probe returns the exact schema through StructuredOutput, with exit zero and no permission denial. It performs no application implementation or verification. Its raw copied configuration and trace are retained; this preliminary probe did not save a complete source fingerprint.

After the mixed matrix, worker guidance was corrected separately for Codex: ordinary source reads and shell/file tools remain available within its sandbox. One actual Codex worker then reads source, edits only `labels.py`, passes its assigned check and seven independent behavior cases, and returns `result_ready` with zero coordinator input requests. That probe has a scripted owner, rather than another native coordinator session. Its source fingerprint matches the final distributed payload and runner. The full mixed matrix was not rerun after this correction or the runner's partial-execution restart guard.

All 69 repository tests pass, including ownership/recovery, denied operations, dirty snapshots, late-message wakeup, exact resume, mandatory gates, stale-owner integration fencing, adoption preservation, and a guard against silently restarting interrupted native work. Both skills validate. These ordinary checks use fake worker transports and do not create provider task sessions.

Claude's named external worker and available tool surface are observed; native Codex custom-role discovery/selection, native reader dispatch, and independent native skill activation are not established by this matrix. Only the installed Linux CLIs and controlled projects were observed. macOS/WSL, desktop/IDE, remote workers, other models, and trusted-hook automatic startup need separate evidence. Cooperative local identity/scope checks and worktree isolation do not establish an adversarial OS security boundary. Worked examples remain illustrative.
