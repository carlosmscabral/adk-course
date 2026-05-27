---
module: 10_A2A
page: 05_A2A_vs_MCP
title: A2A vs MCP (the comparison that confuses everyone)
estimated_minutes: 20
prereqs: [10_A2A/04, 08_MCP/00]
concepts: [A2A, MCP, granularity, discovery, streaming, composition]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 10_A2A/04_ConsumeWithRemoteA2aAgent](04_ConsumeWithRemoteA2aAgent.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/06_DissectingSample →](06_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 05 A2A vs MCP

# 🧠 A2A vs MCP

This is the comparison everyone gets wrong on the first try. Both protocols let two processes talk; the difference is **granularity** and **abstraction**.

## The picture

```
{{_figures/a2a_vs_mcp.txt}}
```

## The table

| Axis                  | MCP                              | A2A                                       |
| --------------------- | -------------------------------- | ----------------------------------------- |
| **Granularity**       | Per-tool (per function).         | Per-agent (whole agent).                  |
| **What it exposes**   | Tools, resources, prompts.       | An entire agent with skills + sub-agents. |
| **Caller is**         | Any LLM client.                  | Another agent (or app talking A2A).       |
| **Discovery**         | `list_tools` RPC.                | `/.well-known/agent-card.json` AgentCard. |
| **Statefulness**      | Stateless per call.              | Stateful via `context_id`.                |
| **Streaming**         | Yes (transport-dep).             | First-class (SSE + push notifications).   |
| **Auth model**        | Per-request headers.             | OpenAPI `SecurityScheme` in card.         |
| **Schema unit**       | JSON Schema per tool.            | AgentCard for the agent + AgentSkill[].   |
| **Multi-tenancy**     | Per-server.                      | Per-task/context_id per agent.            |
| **Composition**       | Server bundles tools.            | Agent bundles tools, skills, sub-agents.  |

## Rule of thumb

> "I want to call **a function** on another process" → **MCP**.
> "I want to delegate **a goal** to another agent" → **A2A**.

If the upstream has no LLM (just a function), it's MCP. If it does have an LLM and you'd rather let it figure out the steps, it's A2A.

## They compose

The currency-agent sample shows the canonical stack:

```
        ┌─────────────┐    A2A     ┌─────────────────┐   MCP    ┌─────────┐
        │   client    │  ──────►   │  ADK agent      │ ───────► │ FX MCP  │
        │  (anything) │   <──────  │  exposed as A2A │ <─────── │ server  │
        └─────────────┘            └─────────────────┘          └─────────┘
```

A2A in front (public-facing contract). MCP in back (private tools the agent uses). This is the production shape: external integrations talk A2A; internal capability extension talks MCP. We dissect this exact setup in the next page.

## Anti-patterns

- **A2A for everything.** If the downstream is just one Python function with no decision-making, MCP is lighter. (No agent runtime to spin up.)
- **MCP for whole agents.** Don't try to expose "a planning agent" as an MCP tool — you lose the agent loop, the sub-agent tree, the streaming.
- **Mixing them on the same endpoint.** One process, one protocol. Compose by linking two processes.

> ❓ **Ask the student:** they have a corporate ticket-classifier with 50 internal rules and several escalation paths. MCP or A2A? (A2A — it's an agent, not a function.)
> Follow-up: that classifier calls a "search Jira" function. MCP or A2A? (MCP — it's a function.)

> 🚀 **In Production**
>
> When you stack them: each protocol has its own retry/timeouts. The MCP timeout fires inside the A2A request — set them so the inner one fails first (typically MCP 5-10 s, A2A 30-60 s) so the agent has a chance to recover before the caller does.

[← Prev: 10_A2A/04_ConsumeWithRemoteA2aAgent](04_ConsumeWithRemoteA2aAgent.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/06_DissectingSample →](06_DissectingSample.md)
