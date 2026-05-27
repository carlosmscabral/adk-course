---
module: 10_A2A
page: 00_Overview
title: Module 10 — A2A (expose agents as services, consume remote agents)
estimated_minutes: 10
prereqs: [02_FirstAgent/00, 05_MultiAgent/00]
concepts: [A2A, AgentCard, to_a2a, RemoteA2aAgent, agent_as_a_service]
icon: 🗺
in_production: true
detours_suggested: [a2UI]
---

[← Prev: 09_Skills](../09_Skills/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 10_A2A/01_WhatIsA2A →](01_WhatIsA2A.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 00 Overview

# 🗺 Module 10 — A2A (Agent-to-Agent)

You have a great ADK agent. Other teams want to use it. They run different frameworks. They don't want your Python; they want a URL. **A2A is that URL.**

A2A is an open protocol — and an ecosystem of SDKs — for **agent-to-agent communication**. ADK 2.0 ships first-class support both directions: `to_a2a(root_agent)` turns any ADK agent into an A2A server, and `RemoteA2aAgent` lets you embed someone else's A2A endpoint as a sub-agent.

## 🎯 What you'll walk away knowing

- The A2A wire model: AgentCard manifest, JSON-RPC messages, task lifecycle, capability discovery.
- `to_a2a(root_agent)` — minimal "agent as a service" in one line.
- `RemoteA2aAgent(agent_card=URL)` — consume a remote agent as if it were local.
- A2A vs MCP — the comparison every student gets wrong once.
- The auto-built AgentCard vs a hand-crafted one.

## 🧰 Prereqs

- 02 (LlmAgent), 05 (sub-agents — RemoteA2aAgent slots in as a sub-agent).
- Helpful: 08 (MCP — the A2A vs MCP page leans on it heavily).

## ⏱ Time

~3 days. The shape is small, but two-process debugging is its own skill.

## 📦 Sample anchors

- `adk-samples/python/agents/currency-agent/` — exposes A2A via `to_a2a(...)` at the bottom of `currency_agent/agent.py`. Ships a test client (`currency_agent/test_client.py`) that hits the AgentCard endpoint and sends messages.
- The same sample also consumes an MCP server. Stacked A2A-in-front + MCP-in-back is the canonical production shape.

## 🗺 Map of this module

```
00 Overview            ← you are here
01 What Is A2A
02 AgentCard
03 Serve with to_a2a
04 Consume with RemoteA2aAgent
05 A2A vs MCP
06 Dissecting Sample (currency-agent)
07 In Production
08 Knowledge Check
09 Mini Drill
```

> 🤖 **Tutor:** A2A is where the student's tower of toys (Modules 02-09) becomes shippable. Reinforce that this is the production endpoint pattern.

[← Prev: 09_Skills](../09_Skills/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 10_A2A/01_WhatIsA2A →](01_WhatIsA2A.md)
