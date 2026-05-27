---
module: 06_GraphWorkflows
page: 04_GraphIntro
title: Workflow, nodes, edges
estimated_minutes: 25
prereqs: [06_GraphWorkflows/03]
concepts: [Workflow, START, edges-tuple, node-chaining]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/03_WhyGraphWorkflows]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/05_DefiningNodes →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 04 Graph Intro

## 🧠 The minimum-viable graph

```python
from google.adk.workflow import Workflow, START

root_agent = Workflow(
    name="root_agent",
    edges=[
        (START, city_generator_agent, lookup_time_function, city_report_agent),
    ],
)
```

This is the entire shape of the minimum-viable graph. Three observations:

1. **`Workflow`** is the new orchestrator. Like `SequentialAgent`, it has no model — it's a runtime (a `BaseNode` subclass whose `_run_impl` IS the scheduler loop).
2. **`edges`** is a list of tuples. Each tuple is a **chain**: read it as "from START, go to A, then to B, then to C."
3. **`START`** is a sentinel `BaseNode` constant. Every graph begins there.

## 🧠 The edges API in one breath

An edge tuple is `(source, target1, target2, ..., targetN)`. The runtime treats this as a chain — `source → target1 → target2 → ... → targetN`. Multiple chains in one `edges=` list overlay into one graph.

```python
edges=[
    (START, A, B),          # START → A → B
    (B, C, D),              # B → C → D
    (A, E),                 # A → E (parallel branch from A)
]
```

The graph that builds:

```
            START
              │
              ▼
              A ─────▶ E
              │
              ▼
              B
              │
              ▼
              C
              │
              ▼
              D
```

A is followed by both B and E (two outgoing edges), B branches to C, C to D.

## 🧠 What goes in a node slot?

Any of:

- An **`LlmAgent`** — the runtime invokes it like a turn.
- A **`FunctionNode`** — wraps a sync/async function or generator (we'll see this on page 05).
- A **`Workflow`** — graphs nest inside graphs. `Workflow` is itself a `BaseNode`, so a whole workflow can serve as a node in a bigger one.
- A **`@node`-decorated function** — decorator-style equivalent of `FunctionNode` (page 05).

Heterogeneous nodes are normal. Fan-out (parallel execution) is achieved by **yielding a list** from one node — the framework dispatches the next node once per element. There is no public `ParallelWorker` class in 2.0.

## 🧠 The 3-node graph, drawn

```
                  START
                    │
                    ▼
        ┌────────────────────────┐
        │  city_generator_agent  │   (LlmAgent — picks a city)
        │  output_key="city"      │
        └─────────┬──────────────┘
                  │
                  ▼
        ┌────────────────────────┐
        │  lookup_time_function   │   (plain function turned into a node)
        │  yields Event(data=...) │
        └─────────┬──────────────┘
                  │
                  ▼
        ┌────────────────────────┐
        │   city_report_agent    │   (LlmAgent — formats the sentence)
        └────────────────────────┘
```

See [`_figures/graph_workflow.txt`](_figures/graph_workflow.txt).

## 🧠 What's not in the basic shape

You can't yet route conditionally (page 06), pause for input (page 07), or fan-out (page 05). The 3-node linear graph above is the simplest meaningful workflow — your "hello world" graph.

## 🛠 Run it

```bash
adk run adk-samples/python/agents/workflows-sequential
```

Watch each node fire in order. The output is `"It is HH:MM:SS in CITY right now."`

> ❓ **Ask the student:** what's the difference between this graph and `SequentialAgent([city_generator_agent, lookup_time_function, city_report_agent])`?
>
> (Answer: functionally identical for this case! The graph wins only when you add routing, parallelism, or HITL. Always pick the simpler tool when you can.)

> ⚠️ **API surface note**: the framework 2.0 API lives at `google.adk.workflow`. Public exports (see `google/adk/workflow/__init__.py`) are `Workflow`, `BaseNode`, `START`, `FunctionNode`, `Edge`, `node`, `JoinNode`, `RetryConfig`, `NodeTimeoutError`, `DEFAULT_ROUTE`. The 1.x-era samples (`workflow-concurrent_research_writer`, `workflows-HITL_concierge`) still import from `google.adk.agents.workflow.*` — those `pyproject.toml` files pin `google-adk<2.0.0`. On 2.0, use `from google.adk.workflow import Workflow, START, FunctionNode` and ignore the old paths.

---

[← Prev: 06_GraphWorkflows/03_WhyGraphWorkflows]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/05_DefiningNodes →]
