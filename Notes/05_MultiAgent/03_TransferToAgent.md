---
module: 05_MultiAgent
page: 03_TransferToAgent
title: transfer_to_agent — the routing mechanism
estimated_minutes: 20
prereqs: [05_MultiAgent/02]
concepts: [transfer_to_agent, built-in-tool, agent-tree, escalate]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/02_SubAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/04_AgentAsTool →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 03 transfer_to_agent

## 🧠 The hidden tool

When you set `sub_agents=[...]`, ADK silently injects a built-in tool into the parent agent:

```
transfer_to_agent(agent_name: str)
```

The parent's LLM, when reading the user prompt, can choose to **call this tool** instead of (or in addition to) responding directly. Calling it switches the "active agent cursor" to the named target.

## 🛠 What the event stream looks like

If you watch `runner.run_async()` you'll see an event like this when the parent delegates:

```python
Event(
    author="triage",
    content=...,                     # maybe a thought
    actions=EventActions(
        transfer_to_agent="billing_agent",  # ← this is the handoff
    ),
)
```

The runner reads `actions.transfer_to_agent`, looks up `billing_agent` in the tree, and routes the **next** turn to it. The user sees one fluid conversation; under the hood the cursor moved.

## 🧠 The tree, drawn

```
                                      ┌──────────────────────────┐
                  active cursor ●────▶│ root: LlmAgent(triage)   │
                                      │ sub_agents=[             │
                                      │   billing_agent,         │
                                      │   tech_support_agent,    │
                                      │   sales_agent,           │
                                      │ ]                        │
                                      └──────────────────────────┘
                                                     │
                                  transfer_to_agent("billing_agent")
                                                     │
                                                     ▼
                                      ┌──────────────────────────┐
                                      │ billing_agent (now ●)    │
                                      └──────────────────────────┘
```

See [`_figures/subagent_vs_agenttool.txt`](_figures/subagent_vs_agenttool.txt) for the contrast figure.

## 🧠 transfer_to_agent vs escalate

`actions.escalate=True` is the *opposite*: hand control **back up** to the parent. A sub-agent uses it when it can't handle the request — the parent then re-routes (often to a different specialist).

```python
# inside a tool, via ToolContext:
def out_of_scope(question: str, tool_context):
    tool_context.actions.escalate = True
    return "I don't handle this — escalating."
```

## ⚠️ Two-way is not free

`transfer_to_agent` is **one-shot** per turn. If `billing_agent` then transfers to `tech_support_agent`, that's two transfers and the user is now talking to tech support without a visible breadcrumb. Mitigations:

- Use `SequentialAgent` (page 06) when the path is known.
- Cap delegation depth via `max_iterations` on the runner.
- Log every `actions.transfer_to_agent` in your observability layer (module 15).

## 🛠 Can I call it manually?

Yes — `transfer_to_agent` is just a built-in tool. Import:

```python
from google.adk.tools import transfer_to_agent
```

You almost never call it manually; the runner wires it automatically when `sub_agents=` is set. But knowing it exists demystifies the magic.

> 🚀 **In Production**
>
> Always log `actions.transfer_to_agent` and `actions.escalate`. Without this you cannot debug "why did the agent give a billing answer to a tech question?" — the answer is almost always "the triage routed wrong because its description-bank was sloppy."

> ❓ **Ask the student:** what's the difference between `transfer_to_agent` and just calling `AgentTool(agent=billing_agent)`? (We answer on the next page.)

---

[← Prev: 05_MultiAgent/02_SubAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/04_AgentAsTool →]
