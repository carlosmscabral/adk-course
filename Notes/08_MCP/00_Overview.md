---
module: 08_MCP
page: 00_Overview
title: Module 08 — MCP (consume external servers, expose your own tools)
estimated_minutes: 10
prereqs: [03_Tools/00, 07_Callbacks/00]
concepts: [MCP, MCPToolset, stdio, sse, streamable_http, FastMCP]
icon: 🗺
in_production: true
detours_suggested: [FastMCP, PY_async]
---

[← Prev: 07_Callbacks](../07_Callbacks/09_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 08_MCP/01_WhatIsMCP →](01_WhatIsMCP.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 00 Overview

# 🗺 Module 08 — MCP (Model Context Protocol)

You can write Python functions and turn them into ADK tools (Module 03). That's great until you need to share those tools across many agents, or integrate with someone else's catalog (Google Maps tools, Stripe tools, a corporate knowledge base).

**MCP** is the standard that solves both. It is a JSON-RPC-over-transports protocol for tool / resource / prompt exposure. ADK ships an `MCPToolset` to consume *any* MCP server as if its tools were native. And `FastMCP` lets you publish your own.

## 🎯 What you'll walk away knowing

- The MCP wire model: tools, resources, prompts, transports.
- How to consume an MCP server from an ADK agent with `MCPToolset`.
- The 3 transports: stdio (local subprocess), HTTP-SSE, Streamable-HTTP.
- How to serve your own tools with `FastMCP`.
- Lifecycle management (the cleanup pattern that catches everyone).
- Where MCP belongs vs A2A (preview for Module 10).

## 🧰 Prereqs

- 03 (FunctionTool & how the LLM sees tools).
- 07 (callbacks — for wrapping MCP calls with retry / auth).
- Helpful: [[PY_async]] (MCP is `async`-first).
- Optional deep dive: [[FastMCP]] for the server framework.

## ⏱ Time

~3 days. Two for consumer + transports; one for serving + lifecycle.

## 📦 Sample anchors

- `adk-samples/python/agents/antom-payment/antom-payemnt-agent/agent.py` — minimal stdio consumer (`uvx ant-intl-antom-mcp`).
- `adk-samples/python/agents/travel-planner-google-maps-mcp/travel_planner_agent/agent.py` — Streamable-HTTP consumer + skills + callbacks all wired together.
- `adk-samples/python/agents/currency-agent/currency_agent/agent.py` + `mcp-server/server.py` — agent consumes its own MCP server. We dissect both ends.

## 🗺 Map of this module

```
00 Overview            ← you are here
01 What Is MCP
02 MCPToolset
03 Transports
04 Lifecycle Management
05 Serving via FastMCP
06 Dissecting Sample (currency-agent + antom-payment)
07 In Production
08 Knowledge Check
09 Mini Drill
```

> 🤖 **Tutor:** if the student already used `FunctionTool` in Module 03, lead with "MCP is the same idea, but over the network and with a standard contract." That's the engineering hook.

[← Prev: 07_Callbacks](../07_Callbacks/09_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 08_MCP/01_WhatIsMCP →](01_WhatIsMCP.md)
