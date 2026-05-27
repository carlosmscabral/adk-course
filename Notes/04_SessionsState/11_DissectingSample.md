---
module: 04_SessionsState
page: 11_DissectingSample
title: Dissecting llm-auditor — critic → reviser state flow
estimated_minutes: 20
prereqs: [04_SessionsState/10]
concepts: [SequentialAgent, output_key, sub-agent-chain]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 04_SessionsState/10_PersistentSessions](10_PersistentSessions.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/12_InProduction →](12_InProduction.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 11 Dissecting llm-auditor

# 🧠 Dissecting `llm-auditor`

Open [`adk-samples/python/agents/llm-auditor/llm_auditor/agent.py`](../../../adk-samples/python/agents/llm-auditor/llm_auditor/agent.py).

```python
from google.adk.agents import SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent

llm_auditor = SequentialAgent(
    name="llm_auditor",
    description="Evaluates LLM-generated answers, verifies accuracy, refines.",
    sub_agents=[critic_agent, reviser_agent],
)

root_agent = llm_auditor
```

A `SequentialAgent` runs its sub-agents in order. The reply from one is **automatically appended to the conversation** that the next sub-agent sees — so the reviser sees the critic's findings without any explicit wiring.

## 🧠 The implicit pipeline

```
user message
     │
     ▼
┌──────────────┐
│ critic_agent │  ← reads user msg + does fact-checking with google_search
└──────┬───────┘
       │ (reply appended to conversation)
       ▼
┌──────────────┐
│reviser_agent │  ← reads user msg + critic's findings + revises the answer
└──────┬───────┘
       │ (final reply to user)
       ▼
    output
```

This works because **all sub-agents share the same Session**. The critic's reply event is just another row in the event log; when the reviser runs, it sees the whole log.

## 🧠 What `output_key` would add

The as-shipped sample doesn't use `output_key`. The reviser reads the critic's reply because it's the most recent agent message in the conversation. **If** you wanted the critic's findings stored under a named state key for downstream agents *or* for prompt-template reuse, you'd add:

```python
# in critic_agent.py
critic_agent = Agent(
    ...,
    output_key="criticism",       # ← reply text → state["criticism"]
)

# in reviser_agent.py
reviser_agent = Agent(
    ...,
    instruction=(
        "You revise answers based on a critic's findings.\n\n"
        "Findings:\n{criticism}\n\n"
        "Apply the corrections minimally."
    ),
)
```

Now the reviser's prompt always reads the critic's last reply by name from state — independent of conversation order.

## 🧠 Why both patterns exist

| Pattern | When to use |
|---|---|
| Implicit (chained conversation) | Linear pipelines, sub-agents trust each other to read history |
| Explicit `output_key` + `{var}` | When the downstream prompt needs a named, addressable handle to the previous output |
| Explicit + non-default prefix (`user:`, `app:`) | When the value must survive beyond this invocation |

`llm-auditor` uses implicit because it's simple. `academic-research` uses explicit `output_key` because its coordinator's prompt has multiple `{var}` slots from multiple sub-agents.

## 🧠 Where state lives in this sample

* **Session**: shared by `llm_auditor`, `critic_agent`, `reviser_agent`. One conversation, three authors.
* **State**: largely empty in this sample. Could be enriched by adding `output_key=` on each sub-agent.
* **Event author**: tells you which sub-agent emitted what. The reviser sees events authored by `critic_agent` in its incoming context.

## ❓ Pop check

> ❓ **Ask the student:** if you swap `SequentialAgent` for `ParallelAgent`, what changes about the state flow?
> *(Expected: with `ParallelAgent` the critic and reviser would run simultaneously and CANNOT see each other's outputs — there's no "first agent's reply appended before second runs." To convert a sequential pipeline to parallel, you need to redesign so the agents don't depend on each other's outputs. Module 05 walks this.)*

> 🛠 **Have the student do this:** open `llm_auditor/sub_agents/critic/agent.py` and `reviser/agent.py`. Note both have `Agent(...)` (alias for `LlmAgent`). Neither has `output_key=` in this sample. Then read `agent.py`'s `SequentialAgent(sub_agents=[critic_agent, reviser_agent])`. Trace the data flow on paper.

---

[← Prev: 04_SessionsState/10_PersistentSessions](10_PersistentSessions.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/12_InProduction →](12_InProduction.md)
