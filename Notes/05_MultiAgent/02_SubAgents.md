---
module: 05_MultiAgent
page: 02_SubAgents
title: sub_agents — implicit LLM delegation
estimated_minutes: 25
prereqs: [05_MultiAgent/01, 04_SessionsState/04]
concepts: [sub_agents, description-as-routing-prompt, delegation, LlmAgent]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/01_WhyComposeAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/03_TransferToAgent →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 02 sub_agents

## 🧠 The shape

```python
from google.adk.agents import LlmAgent

triage = LlmAgent(
    name="triage",
    model="gemini-2.5-flash",
    instruction="Read the user's message. Decide which specialist is best.",
    sub_agents=[billing_agent, tech_support_agent, sales_agent],
)
```

That's it. No routing function, no `if/else`. The parent's LLM **reads each sub-agent's `description=` field** and picks the one to delegate to.

## 🧠 description = routing prompt

Stop and reread that. The `description` you pass to each sub-agent is **literally inlined into the parent's system prompt** as a router prompt. Sloppy description → sloppy routing.

Compare:

```python
# 💀 Vague — the parent will pick wrong constantly.
billing_agent = LlmAgent(
    name="billing_agent",
    description="Handles money stuff.",
    ...
)

# ✅ Specific — the parent knows exactly when to pick this.
billing_agent = LlmAgent(
    name="billing_agent",
    description=(
        "Answers questions about invoices, refunds, payment methods, "
        "and subscription tier changes. Cannot diagnose product bugs."
    ),
    ...
)
```

> 🛠 **Have the student run:** swap a working `description` for a vague one and see routing accuracy drop. This is the single highest-leverage fix in production multi-agent systems.

## 🧠 The flow, drawn

```
user: "my invoice double-charged me"
        │
        ▼
   ┌─────────┐  reads each sub-agent's description,
   │ triage  │  decides: "billing_agent"
   └────┬────┘
        │ delegates
        ▼
  ┌──────────────┐
  │ billing_agent│ ← runs with the SAME session + state
  └──────────────┘
```

Note the **same session + state** — the sub-agent inherits everything from the parent's `Session`. Anything `triage` wrote via `output_key=` is visible.

## 🧠 What "delegate" means

Under the hood, the parent's LLM emits the `transfer_to_agent` built-in tool call with `agent_name="billing_agent"`. The runner intercepts that tool call and switches the active agent. We unpack that mechanism on the next page.

## ⚠️ Common pitfalls

1. **Duplicate names.** Two sub-agents with `name="researcher"` — the transfer tool silently picks one. Always give unique names.
2. **Circular delegation.** `a → b → a → b...` if both descriptions claim "I handle X." Set `max_iterations` on the outer runner or wrap with `SequentialAgent` (page 06).
3. **No fallback.** What if none of the descriptions match? The parent will either answer itself (often wrong) or pick the closest. Always include "a generalist" sub-agent or tighten the parent's instruction to say "if no specialist applies, ask a clarifying question."

> 🚀 **In Production**
>
> Test each `description` with adversarial inputs: send 20 borderline queries, log which sub-agent was picked, fix the descriptions until accuracy ≥ 90%. This is the multi-agent equivalent of writing good docstrings for FunctionTools.

> ❓ **Ask the student:** write descriptions for three specialists — one for arithmetic, one for definitions, one for translations. We'll test them in the mini-drill.

---

[← Prev: 05_MultiAgent/01_WhyComposeAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/03_TransferToAgent →]
