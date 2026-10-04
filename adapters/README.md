# Optional native reviewer examples

These files are optional examples outside Lite/Plan-first payloads. They register a bounded reader in a supported native runtime; they do not replace a task micro spec or install an okms workflow. Portable adoption never copies native configuration. Explicit [Hybrid Team setup](../README.md#choose-a-template) installs its own preserving roles, hooks, and skills.

| Tool | Example | Project destination |
| --- | --- | --- |
| Codex | [Reviewer](codex/okms-reviewer.toml) | `.codex/agents/okms-reviewer.toml` |
| Claude Code | [Reviewer](claude/okms-reviewer.md) | `.claude/agents/okms-reviewer.md` |

Inspect existing project/user agents before choosing a unique name and destination. Merge deliberately and preserve existing configuration. Each example follows the caller's referenced instructions and selected spec, reads its assigned scope, and returns evidence to the coordinator. No model override is supplied.

Codex uses a TOML configuration layer with name, description, and developer instructions. The example sets a read-only sandbox default; parent runtime overrides can affect effective permissions, so validate the actual session rather than treating the file as an absolute boundary. [Official OpenAI documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

Claude Code uses YAML metadata followed by a Markdown system prompt. The example exposes Read, Glob, and Grep; probes needing other tools return to the coordinator. [Anthropic documentation](https://code.claude.com/docs/en/sub-agents).

To use one, ask the main agent to delegate a bounded read to `okms-reviewer`, supplying the actual parent contract, instructions, revision, scope, required output, and return condition. The main agent writes shared records and runs required combined checks. Native discovery, tool availability, and context behavior need actual evaluation for the installed tool version.

The [v0.4 observations](../evals/review-report.md) establish named-role selection and returned results for Claude Code 2.1.284. Codex 0.159.0's captured stream does not establish custom-role loading or dispatch; its TOML example remains source-backed rather than runtime-verified. See [pilot instructions](../evals/README.md); copying a definition alone is not proof that the role was loaded.
