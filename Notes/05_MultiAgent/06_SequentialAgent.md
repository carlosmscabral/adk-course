---
module: 05_MultiAgent
page: 06_SequentialAgent
title: SequentialAgent — when order is fixed
estimated_minutes: 15
prereqs: [05_MultiAgent/05]
concepts: [SequentialAgent, fixed-order-pipeline, deterministic-flow]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/05_SharingStateAcrossAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/07_DissectingLlmAuditor →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 06 SequentialAgent

## 🧠 The pitch

`sub_agents=` lets the LLM decide who runs next. Sometimes you don't want that — the pipeline is fixed (critic always runs before reviser). For that, ADK ships a workflow template:

```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="critique_then_revise",
    description="Score a draft, then improve it.",
    sub_agents=[critic, reviser],   # runs in this order, no LLM voting
)
```

`SequentialAgent` is not an `LlmAgent` — it has no model, no prompt, no temperature. It is a **deterministic orchestrator**. On invocation it runs `critic` to completion, then `reviser`, then returns the final agent's output to the user.

## 🧠 State plumbing still works

Each child still writes `output_key` and reads `{key}`. `SequentialAgent` does not add or remove any handoff machinery — it only enforces order.

```
                user input
                    │
                    ▼
            ┌────────────────────┐
            │ SequentialAgent    │
            │  ┌──────────────┐  │
            │  │   critic     │  │  output_key="criticism"
            │  └──────┬───────┘  │
            │         ▼          │
            │  ┌──────────────┐  │
            │  │   reviser    │  │  reads {criticism}, output_key="final"
            │  └──────────────┘  │
            └────────┬───────────┘
                     ▼
              user sees revised text
```

See [`_figures/auditor_graph.txt`](_figures/auditor_graph.txt).

## 🧠 Family: Sequential, Parallel, Loop

Three legacy workflow templates from ADK 1.x, still fully supported:

| Template | What it does |
|---|---|
| `SequentialAgent` | Run children one after the other. |
| `ParallelAgent` | Run all children concurrently; merge state at the end. |
| `LoopAgent` | Run children in a loop until `exit_loop` is called or `max_iterations=` is hit. |

We use all three at light depth in module 06 (graph workflows). For now, `SequentialAgent` is enough — it's the spine of the `llm-auditor` sample we dissect next.

## ⚠️ SequentialAgent is *not* recursive control flow

It can't branch on output. It can't skip. It can't loop. Need any of that → use a `LoopAgent` (for repeats with exit), a parent `LlmAgent` with `sub_agents=` (for branching by description), or a `WorkflowAgent` (module 06).

## 🛠 Quick example

```python
from google.adk.agents import LlmAgent, SequentialAgent

translator = LlmAgent(
    name="translator", model="gemini-2.5-flash",
    instruction="Translate to French.",
    output_key="french",
)
summarizer = LlmAgent(
    name="summarizer", model="gemini-2.5-flash",
    instruction="Summarize this French text in one sentence: {french}",
    output_key="summary",
)

pipeline = SequentialAgent(
    name="translate_then_summarize",
    sub_agents=[translator, summarizer],
)
```

Feed it English, get a French one-sentence summary. Each agent does one job.

> 🚀 **In Production**
>
> Prefer `SequentialAgent` over a single mega-`LlmAgent` with "first do X, then do Y" in the instruction. The mega-prompt drifts; the pipeline doesn't.

> ❓ **Ask the student:** in the pipeline above, what's in `session.state` after one run? (Both `french` and `summary`.) Confirm by inspection.

---

[← Prev: 05_MultiAgent/05_SharingStateAcrossAgents]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/07_DissectingLlmAuditor →]
