---
module: 10_A2A
page: 01_WhatIsA2A
title: What is A2A (the protocol, in one page)
estimated_minutes: 15
prereqs: [10_A2A/00]
concepts: [A2A, AgentCard, JSON-RPC, task, context_id]
icon: 📡
in_production: false
detours_suggested: []
---

[← Prev: 10_A2A/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/02_AgentCard →](02_AgentCard.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 01 What Is A2A

# 📡 Agent-to-Agent — the wire-level model

**A2A** is an open protocol for agent interoperability. It is a community spec (`a2aproject/A2A`) with a Python SDK (`a2a-sdk`) that ADK builds on. The spec's deal:

- Every A2A agent **publishes an AgentCard** at a well-known URL (`/.well-known/agent.json`).
- Callers send messages over **JSON-RPC** (single-shot) and receive **task** objects back.
- Long-running work uses **streaming events** (Server-Sent Events / WebSockets).
- Multi-turn conversations carry a **context_id** so the agent can keep state.

## The picture

```
{{_figures/a2a_topology.txt}}
```

(See `_figures/a2a_topology.txt` for the full ASCII.)

## The discovery flow

1. Caller fetches `GET https://your-agent.example.com/.well-known/agent.json`.
2. Server returns the AgentCard (we cover its shape on the next page).
3. Caller now knows the RPC URL, the agent's skills, the auth, the input/output modes.
4. Caller sends `POST https://your-agent.example.com/` with a JSON-RPC `message/send` body.
5. Server returns a `Task` with status (`completed`, `input_required`, `failed`, ...).
6. If `input_required`, the caller can continue by including the `context_id` in the next message.

## What A2A is NOT

- **Not MCP.** MCP exposes tools (function-grained). A2A exposes an agent (goal-grained). They compose: an A2A agent can have MCP tools internally. The dedicated comparison is page 05.
- **Not a transport.** A2A is a protocol; transports are HTTP, SSE, WebSocket. ADK's `to_a2a()` builds an HTTP+SSE Starlette app.
- **Not framework-locked.** Any framework that implements the A2A spec can talk to your ADK agent. That's the point.

## Why this matters

Before A2A, "calling another agent" meant gluing two frameworks together at the Python level. Now it's an HTTP call with a stable contract. Three consequences:

- **Polyglot agent systems.** ADK calling LangChain calling AutoGen — all over A2A.
- **Independent deploys.** Each agent ships at its own cadence.
- **Service-mesh-friendly.** Load balancers, auth proxies, observability all work because it's just HTTP.

> ❓ **Ask the student:** in their stack, what's currently glued together at the Python level that could become A2A endpoints instead?

> 🚀 **In Production**
>
> A2A is the public contract. The AgentCard is the API surface. **Version it like an API.** A naive change to your agent's `description` field can change how callers' LLMs decide to call you. We cover the versioning play in `07_InProduction.md`.

[← Prev: 10_A2A/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/02_AgentCard →](02_AgentCard.md)
