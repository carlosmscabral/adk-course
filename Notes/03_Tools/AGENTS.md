# AGENTS.md — Module 03 Tools (teaching notes for the AI tutor)

## What the student should walk away knowing

- A tool is just a **typed Python function with a docstring**. Pass it bare to `tools=[...]` or wrap as `FunctionTool(fn)`.
- The docstring → `description` in the JSON schema → the LLM's basis for *when* to call the tool. The docstring is a prompt-within-a-prompt.
- Type hints become JSON schema `properties`. No hints = the LLM passes garbage.
- Optional `tool_context: ToolContext` lets the tool read/write session state, set `escalate`, save artifacts. It's hidden from the LLM.
- Built-in tools: `google_search`, `load_memory`, `exit_loop`, `transfer_to_agent`.
- **Computer Use** (page 06, preview): `BaseComputer` ABC + `ComputerUseToolset` + screenshot/action loop. You implement `BaseComputer` against Playwright/Chromium (or another driver); the toolset wires every public method into a tool. Flagged `@experimental` in source.
- **Tool limitations** (page 07): `google_search` and `VertexAiSearchTool` are sole-tool-only on Gemini 1.x; `EnterpriseWebSearchTool` is sole-tool-only always; `VertexAiRagRetrieval` is sole-tool-only on its agent (split into a sub-agent + `AgentTool` to compose). `McpToolset` is composable but has connection-lifecycle and tool-name-collision gotchas. Practical tool-count ceiling ~15-20 before selection accuracy tanks.
- Preview: `AgentTool` (Module 05) wraps an agent as a tool. `LongRunningFunctionTool` (Module 12) yields progress for slow work.
- Real-sample shapes: `currency-agent` uses an MCP-served tool; `academic-research` uses `google_search` inside `AgentTool`-wrapped sub-agents.

## Pacing

- **Easy if** the student is comfortable with type hints. They'll knock out the calc drill in ~30 min.
- **Hard if** type hints feel foreign. Send to [[PY_typing]] before page 02.
- **Hard if** the student wants to debug "the LLM didn't call my tool." Ten-to-one it's the docstring. Walk page 03 again.

## Watch for these mistakes

- `def fn(**kwargs):` — doesn't translate to a JSON schema. Use explicit typed params.
- One-line `"""Do the thing."""` docstrings on tools — the LLM has no idea when to use them.
- Returning a Python class instance without making it JSON-serializable (use dataclass/pydantic, or just a dict).
- Raising bare exceptions for foreseeable errors (city not found, rate limited) instead of returning structured `{"error": "..."}` dicts.
- Adding `tool_context` and then expecting the LLM to pass it — the LLM doesn't see it; ADK injects.

## When to suggest a detour

- "Why type hints?" → [[PY_typing]] now.
- "What about dataclasses for tool args?" → [[PY_dataclasses]] (works fine; pydantic models work even better).
- "What's an MCP server?" → defer to Module 08.
- "Can the LLM call tools in parallel?" → yes, Gemini supports parallel tool calls; ADK threads them. Module 06 (Workflows) and Module 18 (Streaming) deepen.
- "Can I actually run the Computer Use demo?" → only if Playwright + a real Gemini API key are installed. Otherwise walk the BaseComputer file and the ASCII loop; the recognition is the point.
- "How do I sandbox the Computer Use browser?" → forward to Module 4B (HITL gates) and Module 16 (CallbacksAsPolicy). The page only flags it.

## Mini-drill grading

- **Pass = the agent calls the right tool for ≥3 of 4 ops, AND tools are typed + docstring'd correctly.**
- Edge case to probe: ask the student to handle division by zero. If they raise an exception, ask how that surfaces (event with error → LLM sees and either retries or apologizes). Push them to return `{"error": "..."}` for cleaner behavior.
- Probe after pass: "if you had 30 tools, would the LLM still pick correctly?" (Answer: degrades — long tool lists confuse the model. Patterns to fix: split into specialized sub-agents — Module 05 — or use `transfer_to_agent` routing.)

## After this module

- Module 04 introduces State, which connects to the `tool_context.state` you previewed on page 04.
- The student now has: agent + runner + tools. M1 (after Module 04) will exercise all three.
- The recurring "research-assistant" mini-app first appears here as a tools exercise; it'll evolve into multi-agent in Module 05, graph in Module 06, RAG in 10B, evals in 14.
