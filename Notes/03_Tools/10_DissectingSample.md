---
module: 03_Tools
page: 10_DissectingSample
title: Dissecting currency-agent and academic-research tool use
estimated_minutes: 20
prereqs: [03_Tools/09]
concepts: [McpToolset, google_search, AgentTool, real-samples]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/09_LongRunningTool](09_LongRunningTool.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/11_InProduction →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 10 Dissecting tool use

# 🧠 Two samples, side by side

We've talked about tools abstractly. Now read how two real ADK samples wire them in.

## 🧠 Sample 1 — `currency-agent`

Open [`adk-samples/python/agents/currency-agent/currency_agent/agent.py`](../../../adk-samples/python/agents/currency-agent/currency_agent/agent.py).

Tool definition is in the MCP server (`mcp-server/` subdir). The agent receives it via `McpToolset`:

```python
tools=[
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
        )
    )
],
```

**Big point:** the agent doesn't `import` the tool function. It connects to a process that exposes one. `McpToolset` auto-discovers tools from the connected MCP server at startup. This decouples the *agent author* from the *tool author* — Module 08 unpacks this fully.

For our purposes today: the tool ends up looking, from Gemini's view, exactly like a `FunctionTool` would. Same JSON schema, same call mechanics, same return shape. The transport changed; the contract didn't.

## 🧠 Sample 2 — `academic-research`

Open [`adk-samples/python/agents/academic-research/academic_research/agent.py`](../../../adk-samples/python/agents/academic-research/academic_research/agent.py).

```python
academic_coordinator = LlmAgent(
    name="academic_coordinator",
    model=MODEL,
    description="...",
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    output_key="seminal_paper",
    tools=[
        AgentTool(agent=academic_websearch_agent),
        AgentTool(agent=academic_newresearch_agent),
    ],
)
```

Two sub-agents wrapped as tools. From the coordinator's LLM perspective, it has two tools to pick from. Each sub-agent itself uses **`google_search`** (built-in):

```python
# from sub_agents/academic_websearch/agent.py
academic_websearch_agent = Agent(
    model="gemini-2.5-pro",
    name="academic_websearch_agent",
    instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
    output_key="recent_citing_papers",
    tools=[google_search],
)
```

So a single user message triggers (potentially):
1. Coordinator LLM picks `AgentTool(academic_websearch_agent)`.
2. ADK runs `academic_websearch_agent` as a nested agent loop.
3. That sub-agent's LLM picks `google_search`.
4. Search returns; sub-agent summarizes; coordinator sees the summary as a tool result.
5. Coordinator either replies, or calls the other `AgentTool` for more context.

Three tools chained, two levels deep. **All built from the primitives in this module** (`FunctionTool`-equivalent + built-in + `AgentTool`).

## 🧠 Side-by-side

| Concept | `currency-agent` | `academic-research` |
|---|---|---|
| How tools enter the agent | `McpToolset` (remote, dynamic) | Built-in + `AgentTool` (in-process) |
| Tool count | Discovered from MCP server | 2 wrapped sub-agents (each with 1 tool) |
| Depth | 1 level (agent → tool) | 2 levels (coordinator → sub-agent → tool) |
| Module to deep-dive | 08 (MCP) | 05 (Multi-agent) |

## ❓ Pop check

> ❓ **Ask the student:** in `academic-research`, the coordinator has `tools=[AgentTool(...), AgentTool(...)]`. Does it ALSO have direct access to `google_search`?
> *(Expected: no — only the wrapped sub-agents do. The coordinator can only invoke `google_search` indirectly by calling one of its `AgentTool`s. That's intentional separation of concerns.)*

> 🛠 **Have the student do this:** sketch on paper the call tree for one user question to `academic-research`. Start with the coordinator at the top, draw arrows down to whichever sub-agent it delegates to, then to whichever tool *that* sub-agent calls. Notice how the "tools=[…]" list at each layer determines what's reachable.

---

[← Prev: 03_Tools/09_LongRunningTool](09_LongRunningTool.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/11_InProduction →]
