---
module: 08_MCP
page: 01_WhatIsMCP
title: What is MCP (and why ADK speaks it natively)
estimated_minutes: 15
prereqs: [08_MCP/00]
concepts: [MCP, JSON-RPC, tools, resources, prompts, transports, interop]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 08_MCP/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/02_McpToolset →](02_McpToolset.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 01 What Is MCP

# 🧠 The Model Context Protocol

**MCP is an open standard for exposing capabilities to LLM agents.** It's tooling-shaped (think: "OpenAPI for agent tools") but covers three things:

| Primitive   | What it is                                                       | ADK consumer surface       |
| ----------- | ---------------------------------------------------------------- | -------------------------- |
| **Tool**    | A callable function the agent can invoke.                       | `McpToolset` lists & calls. |
| **Resource**| A read-only blob (file, document, page) the agent can fetch.    | Surfaced as tool-callable. |
| **Prompt**  | A pre-canned prompt template the agent can request and fill in. | Surfaced as a tool.        |

The protocol is **JSON-RPC** under the hood, and it's **transport-agnostic** — same messages flow over stdio, HTTP-SSE, or Streamable-HTTP.

## The architecture in one picture

```
{{_figures/mcp_topology.txt}}
```

(Open `_figures/mcp_topology.txt` for the full ASCII.)

## Why it exists

Before MCP, every agent framework reinvented "how to expose tools" — OpenAI plugins, custom HTTP schemas, RPC bridges. The MCP spec converged on one wire format so a tool server written for one framework runs in any framework. ADK 2.0 ships first-class MCP support both directions:

- **Consume:** `from google.adk.tools.mcp_tool import McpToolset` — drop an MCP server into your agent's `tools=[...]` list.
- **Serve:** ADK does not bundle a server framework; the community standard is **FastMCP** (a single-file decorator API). We use it in 05.

## What MCP is NOT

It's not A2A. MCP exposes **tools**, A2A exposes **whole agents**. Granularity is the difference. We unpack the comparison in [[10_A2A/05_A2A_vs_MCP]].

It's not a service mesh. Discovery is per-server-URL today; if you need a registry, you build one on top.

It's not magic. The LLM still needs to be told what tools exist (the toolset returns schemas) — same flow you saw with `FunctionTool` in Module 03, just with the server hop added.

> ❓ **Ask the student:** if you've already written `FunctionTool`s in Module 03, what does MCP add that a local function doesn't? (Answer they should land on: cross-process, language-agnostic, reusable across agents, standard auth surface.)

> 🚀 **In Production**
>
> MCP servers are real network endpoints with real failure modes. Plan for: (1) network timeouts, (2) version skew (the server's tool signatures change), (3) auth token rotation. We cover each in `07_InProduction.md`.

[← Prev: 08_MCP/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/02_McpToolset →](02_McpToolset.md)
