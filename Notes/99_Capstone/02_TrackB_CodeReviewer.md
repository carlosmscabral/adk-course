---
module: 99_Capstone
page: 02_TrackB_CodeReviewer
title: Track B — Code Reviewer
estimated_minutes: 30
prereqs: [99_Capstone/00]
concepts: [code-reviewer, sandboxed-execution, sub_agents]
icon: 🛠
in_production: true
---

[← Prev: 99_Capstone/01_TrackA_ResearchAssistant]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/03_TrackC_PersonalKnowledgeHub →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 02 Track B

# 🛠 Track B — Code Reviewer

See `_figures/track_b.txt` for the architecture diagram.

## The pitch

An agent that ingests a Git diff (PR-style), **runs the test suite in a sandbox**, and posts a structured code review across 3 dimensions: syntax, style, security. Exposed over A2A so a GitHub webhook can trigger it.

## The spec

### Agents (3 minimum — sub_agents pattern)

1. **`Coordinator`** (root `LlmAgent`)
   - Receives the diff in the user message.
   - `sub_agents=[syntax_agent, style_agent, security_agent]`.
   - Aggregates outputs into one review.

2. **`SyntaxAgent`** (`LlmAgent`)
   - Tool: `FunctionTool(run_tests)` — invokes pytest in a sandboxed code executor.
   - Tool: `FunctionTool(apply_diff_to_workspace)` — preps the workspace.
   - Output: pass/fail + list of failing tests.

3. **`StyleAgent`** (`LlmAgent`)
   - Tool: `FunctionTool(lint)` — runs `ruff` (or `pylint`, your call) on the diff.
   - Output: list of style issues with line numbers.

4. **`SecurityAgent`** (`LlmAgent`)
   - Tool: `MCPToolset` to a "security-rules" MCP server (yours; can be `bandit` wrapped).
   - Output: list of security findings.

### Tools (≥2)

- `FunctionTool(run_tests)` (Track B's headline tool — wraps `VertexAiCodeExecutor` or `ContainerCodeExecutor`).
- `FunctionTool(lint)`.
- `MCPToolset(...)` for security rules.

### Code execution sandbox (mandatory for this track)

`VertexAiCodeExecutor` for prod, `ContainerCodeExecutor` for local dev. **Never** `UnsafeLocalCodeExecutor` — the whole point of this track is to safely run user-supplied code.

### Persistent state

`DatabaseSessionService` — sessions keyed by `pr_id`. State carries the diff, the workspace path, and accumulated findings.

### Memory service

`VertexAiMemoryBankService` keyed on `repo_id` so the reviewer remembers per-repo style conventions across PRs (e.g., "this repo uses 2-space indent" / "this repo's tests are in `spec/`, not `tests/`").

### Eval cases (≥5)

- Trivial passing PR (1-line type-hint addition) — expect APPROVE.
- PR breaking a test — expect SyntaxAgent failure surfaced.
- PR with `eval(user_input)` — expect SecurityAgent block.
- PR with style violations but passing tests — expect APPROVE with style notes.
- PR with no tests at all — expect SyntaxAgent flag "no test coverage."

Use `RubricBasedEvaluator` for the structured review outputs.

### Plugins (≥1) and callbacks (≥2)

- `LoggingPlugin`.
- `ReflectAndRetryToolPlugin` (the test runner CAN flake — retry once).
- `before_tool_callback` on `run_tests`: validate the diff doesn't include `rm -rf /` patterns before letting the sandbox execute it.
- `after_agent_callback` on the Coordinator: POST the final review to GitHub's review API.

### A2A interface

`to_a2a(coordinator)`. GitHub webhook → tiny FastAPI shim → `RemoteA2aAgent.run(...)`.

### Observability

OpenTelemetry → Cloud Trace. The sandbox execution should be a span you can drill into.

### README

Architecture, run commands, eval results, plus a **"Safety" section** explaining what the sandbox prevents and what it doesn't.

## Suggested file layout

```
capstone-code-reviewer/
├── code_reviewer/
│   ├── agent.py              ← Coordinator
│   ├── sub_agents/
│   │   ├── syntax/agent.py
│   │   ├── style/agent.py
│   │   └── security/agent.py
│   ├── tools/
│   │   ├── run_tests.py
│   │   ├── lint.py
│   │   └── github.py
│   ├── plugins/
│   │   └── diff_safety.py
│   └── mcp_servers/
│       └── security_rules/   ← your MCP server
├── tests/
│   ├── fixtures/             ← sample diffs
│   └── eval_set.json
├── README.md
└── pyproject.toml
```

> 🚀 **In Production**
>
> Never run user-supplied code in a non-sandboxed environment. `VertexAiCodeExecutor` is the only `safe` choice for cloud; `ContainerCodeExecutor` is the only safe choice for self-hosted. Audit your `before_tool_callback` guard regularly — patches around shell metacharacters are a moving target.

> 🛠 **Have the student run:** `git diff HEAD~1` on this very course repo and paste the output as their first test fixture.

[← Prev: 99_Capstone/01_TrackA_ResearchAssistant]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/03_TrackC_PersonalKnowledgeHub →]
