---
module: 08_MCP
page: 02_MCPToolset
title: MCPToolset — the consumer side
estimated_minutes: 25
prereqs: [08_MCP/01]
concepts: [MCPToolset, connection_params, BaseToolset, LlmAgent.tools]
icon: 🛠
in_production: true
detours_suggested: [PY_async]
---

[← Prev: 08_MCP/01_WhatIsMCP](01_WhatIsMCP.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/03_Transports →](03_Transports.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 02 MCPToolset

# 🛠 Consuming an MCP server with `MCPToolset`

`MCPToolset` is a `BaseToolset`. From the agent's perspective, it behaves exactly like a list of `FunctionTool`s — but those tools live in an external MCP server.

```python
from google.adk import Agent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

agent = Agent(
    model="gemini-2.5-flash",
    name="currency_agent",
    instruction="Use the exchange-rate tool to answer FX questions.",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://localhost:8080/mcp",
            )
        )
    ],
)
```

That's the whole thing. On the first turn that needs tools, ADK opens a session to the MCP server, lists tools, exposes their schemas to the LLM, and routes function-call invocations through.

> 🛠 **Have the student run:** start with the snippet above. Don't actually start a server yet — just observe that the agent boots without raising. The connection is lazy; it opens on first call.

## What's in the box

When `MCPToolset` connects, the server tells it:

```json
[
  {"name": "get_exchange_rate", "description": "...", "input_schema": {...}},
  {"name": "list_currencies",   "description": "...", "input_schema": {...}}
]
```

Each entry becomes a tool the LLM sees, with the description as the tool's docstring and the schema as the parameter shape. **The LLM does not know it's MCP.** It sees tools.

## Filtering the tool list

A server can expose 30 tools and you only want 3. Use the `tool_filter` arg:

```python
MCPToolset(
    connection_params=...,
    tool_filter=["get_exchange_rate", "list_currencies"],  # only these
)
```

Useful for keeping prompts lean (every tool schema eats context tokens).

## Two name imports, same class

The framework exports both `MCPToolset` and `McpToolset`. Same class, alias. Pick the one your eyes prefer; samples use both.

```python
from google.adk.tools.mcp_tool import MCPToolset  # uppercase MCP
from google.adk.tools.mcp_tool import McpToolset  # camel-style
```

## Where the LLM call ends up

```
LLM  ──function_call──►  MCPToolset  ──JSON-RPC──►  MCP server  ──fn──►  external API
        ◄──result─────              ◄──result──             ◄────────
```

A normal `before_tool_callback` / `after_tool_callback` fires around the MCPToolset call — meaning every guardrail you learned in Module 07 applies unchanged here.

> ⚠️ **Gotcha** — when the MCP server is down or unreachable, the failure surfaces as a tool error. Combine with `on_tool_error_callback` (Module 07) for graceful degradation.

> 🚀 **In Production**
>
> MCP tool calls go through the network. Treat them like any other dependency: timeouts, retries, circuit breakers. The standard ADK pattern is `before_tool_callback` for the retry policy + `on_tool_error_callback` for the fallback. We give you a snippet in `07_InProduction.md`.

[← Prev: 08_MCP/01_WhatIsMCP](01_WhatIsMCP.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/03_Transports →](03_Transports.md)
