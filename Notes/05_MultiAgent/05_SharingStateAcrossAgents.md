---
module: 05_MultiAgent
page: 05_SharingStateAcrossAgents
title: Sharing state across agents — output_key is the bus
estimated_minutes: 20
prereqs: [05_MultiAgent/04, 04_SessionsState/04, 04_SessionsState/02]
concepts: [output_key, instruction-substitution, shared-session, handoff-bus]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/04_AgentAsTool]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/06_SequentialAgent →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 05 Sharing State

## 🧠 All agents in the tree see the same Session

This is the foundational fact. Whether you compose via `sub_agents=`, `AgentTool`, or `SequentialAgent`, every agent in the tree reads from and writes to **one** `Session` object with **one** `state` dict. Sub-agents inherit nothing else automatically (instructions are independent, tools are independent) — but state is shared.

## 🧠 The de-facto handoff pattern: output_key → {key}

We saw `output_key=` in [`04_SessionsState/04_OutputKey`](../04_SessionsState/09_OutputKeyShortcut.md). Recap:

```python
critic = LlmAgent(
    name="critic",
    instruction="Score the draft.",
    output_key="critique",          # writes its final response into state['critique']
)
```

In a downstream agent, **brace-substitute** the key in the instruction:

```python
reviser = LlmAgent(
    name="reviser",
    instruction="Improve the draft using this critique:\n\n{critique}",
)
```

At runtime ADK interpolates `state['critique']` into the prompt before the LLM call. That's the entire handoff mechanism. No queues, no callbacks, no tool calls — just `output_key` upstream and `{key}` downstream.

## 🛠 The pattern, drawn

```
  ┌──────────┐
  │  critic  │  output_key="critique"
  └────┬─────┘
       │ writes state['critique'] = "score: 7/10, weak intro"
       │
       ▼  same Session
  ┌──────────┐
  │ reviser  │  instruction: "...using this critique:\n{critique}"
  └──────────┘    LLM sees: "...using this critique:\nscore: 7/10, weak intro"
```

## 🧠 What about multiple state vars?

Any number. Each agent can write its own `output_key`, downstream agents pull whichever they need:

```python
planner = LlmAgent(name="planner",   output_key="plan")
research = LlmAgent(name="research", output_key="findings", instruction="Plan: {plan}\nFind ...")
writer = LlmAgent(name="writer",
                  instruction="Plan: {plan}\nFindings: {findings}\nWrite an article.")
```

## ⚠️ Brace-substitution is literal

`{plan}` interpolates `state['plan']` as a string. If `state['plan']` doesn't exist, you get an error or the literal `{plan}` (depends on ADK version — verify). Guard upstream agents *always* set the key, or wrap the downstream instruction defensively.

## 🧠 State scopes refresher

Recall from [`04_SessionsState/02_StateScopes`](../04_SessionsState/02_StateScopes.md):

- no-prefix — `session` scope (this conversation only)
- `user:` — across sessions for one user
- `app:` — across all users
- `temp:` — only for this turn

For agent-to-agent handoffs within one invocation, no-prefix is correct. Cross-session memory is module 11.

## 🛠 What writes besides `output_key`?

Three other paths:

1. **A `FunctionTool` that takes `tool_context`** can call `tool_context.actions.state_delta` or write `tool_context.state['x'] = y`.
2. **A `before/after_*_callback`** receives a `CallbackContext` with `.state` writes.
3. **The runner itself** seeds state at session creation.

`output_key` is the simplest and the one you'll use 90% of the time for handoffs.

> 🚀 **In Production**
>
> State is your dependency graph. Document which agent reads/writes which keys *in the agent's docstring*. Future-you debugging "why is `{findings}` empty?" will thank present-you. A naming convention helps: prefix outputs with the producer agent (`planner_plan`, `critic_critique`).

> 🛠 **Have the student run:** wire two trivial agents with `output_key="x"` and `instruction="...{x}..."`, run, print `session.state` after — confirm `x` is there.

---

[← Prev: 05_MultiAgent/04_AgentAsTool]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/06_SequentialAgent →]
