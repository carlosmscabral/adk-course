---
module: 05_MultiAgent
page: 00_Overview
title: Composing agents — sub_agents, AgentTool, transfer_to_agent
estimated_minutes: 15
prereqs: [04_SessionsState/08]
concepts: [sub_agents, AgentTool, transfer_to_agent, SequentialAgent, output_key, shared-state]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/08_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/01_WhyComposeAgents →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 00 Overview

## 🧠 What you'll learn

How to split one bloated agent into a team that cooperates. ADK 2.0 gives you **three** composition primitives — and they are *not* interchangeable:

1. **`sub_agents=[...]`** — parent's LLM picks who to delegate to. Implicit, descriptor-driven.
2. **`AgentTool(agent=...)`** — wrap an agent as a tool. Explicit; LLM "calls" the specialist.
3. **`transfer_to_agent`** — built-in tool the LLM emits to hand control elsewhere in the tree.

Then we layer the **`SequentialAgent`** wrapper that forces fixed-order execution (no LLM voting).

> 🧠 **"Collaborative agents" — what the term actually means.** The 2.0 release notes call out *collaborative agents* as a "new" composition pattern. It is **not** a new class. There is no `CollaborativeAgent` in `google.adk.agents`. It is Google's umbrella name for the three primitives above (`sub_agents`, `AgentTool`, `transfer_to_agent`) plus the graph workflow in [[06_GraphWorkflows/00_Overview]]. If a doc or release note mentions "collaborative agents," it is pointing back at these pages — there is no separate API to learn.

## 🗺 Prereqs

- `04_SessionsState/04_OutputKey` — `output_key=` writes into state.
- `04_SessionsState/02_StateScopes` — `{var}` substitution in instructions.
- `03_Tools/03_AgentAsTool` (preview only — we go deep here).

## ⏱ Time budget

**3 days**, ~6 hours actual work. The dissection page alone is ~90 min.

## 📦 Sample anchors

Real samples we'll open:

- `adk-samples/python/agents/llm-auditor/` — the **canonical** `SequentialAgent([critic, reviser])` shape. Dissected end-to-end on page 07.
- `adk-samples/python/agents/academic-research/` — coordinator with `AgentTool`-wrapped specialists.
- `adk-samples/python/agents/financial-advisor/` — 4 specialist `AgentTool`s under one `LlmAgent`.

## 🎯 The recurring research-assistant grows up

In `02_FirstAgent` we built a single `LlmAgent`. In `03_Tools` we gave it a `google_search`. Here it becomes a **team**: a planner, one or more researchers, a writer, optionally a critic. Module 06 then re-implements that same team as a graph. Module 14 evaluates it. Module 99 ships it.

## 🛠 Pages in this module

| Page | Topic |
|------|-------|
| 01 | Why compose? Single-agent failure modes. |
| 02 | `sub_agents=[...]` — implicit LLM delegation. |
| 03 | `transfer_to_agent` — the built-in tool that *moves the cursor*. |
| 04 | `AgentTool(agent=...)` — explicit specialist invocation. |
| 05 | Sharing state across agents — `output_key` → `{key}` is the de-facto bus. |
| 06 | `SequentialAgent` — when fixed order beats LLM routing. |
| 07 | 🛠 Dissecting `llm-auditor`. |
| 08 | 🛠 Quick read of `financial-advisor` for the AgentTool contrast. |
| 08A | 🧠 `LangGraphAgent` — wrap a LangGraph workflow as an ADK agent. |
| 09 | 🚀 In production — gotchas, mitigations. |
| 10 | ❓ Knowledge check. |
| 11 | 🏋 Mini-drill: clone the auditor shape with summarizer + translator. |

> 🤖 **Tutor:** student should already have written one `LlmAgent` with a tool and verified `state['x']` survives across turns. If either feels shaky, bounce back to 04 first.

---

[← Prev: 04_SessionsState/08_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/01_WhyComposeAgents →]
