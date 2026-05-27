---
module: 05_MultiAgent
page: 04_AgentAsTool
title: AgentTool — wrap an agent as a tool
estimated_minutes: 25
prereqs: [05_MultiAgent/03, 03_Tools/03]
concepts: [AgentTool, explicit-invocation, tool-vs-delegation]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/03_TransferToAgent]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/05_SharingStateAcrossAgents →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 04 AgentTool

## 🧠 The other composition primitive

We previewed `AgentTool` in [`03_Tools/03_AgentAsTool`](../03_Tools/08_AgentToolPreview.md). Here is the full story.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-pro",
    instruction="Solve the user's request. You have specialists available.",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)
```

The specialists are wrapped as **tools** — they appear in the coordinator's tool list just like a `FunctionTool` would. The coordinator's LLM calls them the way it calls any other tool: it picks a name, supplies arguments, and gets back a string result.

## 🧠 sub_agents vs AgentTool — the mental model

| | `sub_agents=[...]` | `AgentTool(agent=...)` |
|---|---|---|
| **Invocation** | Implicit — parent's LLM delegates via `transfer_to_agent` | Explicit — parent's LLM calls it like a function |
| **Cursor** | Moves to the sub-agent for the rest of the turn | Stays on the parent; the tool returns and the parent continues |
| **Conversation** | Sub-agent sees the user; user sees the sub-agent's reply | Sub-agent sees only the args; user only sees the parent's synthesis |
| **Use when** | Whole-conversation handoff (triage, intake) | One-shot specialist call inside a larger response |

```
sub_agents:                        AgentTool:

  user ──▶ parent                    user ──▶ parent
              │ transfer                        │ tool_call(specialist, args)
              ▼                                 ▼
           sub-agent                         specialist
              │                                 │ returns string
              ▼                                 ▼
            user                            parent ──▶ user
```

## 🛠 Real sample — `financial-advisor`

Open `adk-samples/python/agents/financial-advisor/financial_advisor/agent.py`. The coordinator does **not** use `sub_agents=`. It uses:

```python
financial_coordinator = LlmAgent(
    name="financial_coordinator",
    model="gemini-2.5-pro",
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=trading_analyst_agent),
        AgentTool(agent=execution_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)
```

Why? Because the financial coordinator wants to **orchestrate** — pull data, then call the trading analyst with that data, then ask the risk analyst about the result, then write a unified plan. Each specialist returns a string; the coordinator weaves them together. With `sub_agents=` the cursor would jump to `data_analyst` and never return.

## 🧠 The wrapping behavior

`AgentTool` synthesizes a tool name from `agent.name`, a description from `agent.description`, and an argument schema (typically `{request: str}`). So **description quality still matters** — same lesson as page 02.

## ⚠️ Don't double-compose the same agent

If `specialist_x` appears in `sub_agents=[specialist_x]` *and* `tools=[AgentTool(agent=specialist_x)]` of the same parent — you'll trigger duplicate-name errors or strange routing. Pick one mode per relationship.

> 🚀 **In Production**
>
> Pattern: high-level orchestration → `AgentTool`. User-facing triage → `sub_agents`. Mixing them inside one parent only when the design *truly* needs both behaviors (rare). When in doubt, default to `AgentTool` — it keeps the conversation on a single agent and is easier to observe.

> ❓ **Ask the student:** in `financial-advisor`, why would changing `data_analyst` from `AgentTool` to `sub_agents=` break the orchestration?

---

[← Prev: 05_MultiAgent/03_TransferToAgent]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/05_SharingStateAcrossAgents →]
