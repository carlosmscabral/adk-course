---
module: 06_GraphWorkflows
page: 05_DefiningNodes
title: Defining nodes — agents, functions, parallel workers
estimated_minutes: 25
prereqs: [06_GraphWorkflows/04]
concepts: [FunctionNode, ParallelWorker, Event, async-generator]
icon: 🛠
in_production: true
detours_suggested: [PY_async, PY_generators]
---

[← Prev: 06_GraphWorkflows/04_GraphIntro]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/06_RoutingEdges →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 05 Defining Nodes

## 🧠 Three node kinds you'll use 90% of the time

### 1. Agent nodes — pass an `LlmAgent` directly

```python
edges=[(START, my_llm_agent, next_thing)]
```

No wrapper required. The runtime invokes the agent and uses its final response as the node's output.

### 2. `FunctionNode` — wrap an async function

```python
from google.adk.agents.workflow.function_node import FunctionNode
from google.adk.agents.workflow.events.event import Event
from google.genai.types import Content

async def start_research_node(node_input: Content):
    """Read user input, stash topic in state, fan out platforms."""
    topic = str(node_input.parts[0].text if node_input.parts else "")
    yield Event(state={"topic": topic})              # write to state
    yield ["X", "LinkedIn", "Reddit", "Medium"]      # fan out

start_node = FunctionNode(
    start_research_node,
    name="Start Research Node",
    rerun_on_resume=True,
)
```

Three things the function can yield:

- **`Event(state={...})`** — write to session state.
- **`Event(route="X")`** — emit a route label for conditional edges (page 06).
- **A plain value (str, list, dict, `ModelContent`)** — passed as `node_input` to the next node.

If you yield a **list**, the runtime fans out: the next node runs *once per list element* (parallel). This is the pattern in `workflow-concurrent_research_writer`'s research stage — the start node yields `["X", "LinkedIn", "Reddit", "Medium"]` and the next node (a `ParallelWorker`) runs 4x concurrently.

### 3. `ParallelWorker` — wrap an agent for fan-out

```python
from google.adk.agents.workflow.parallel_worker import ParallelWorker

research_worker = ParallelWorker(_research_worker_llm_agent)
```

Place a `ParallelWorker` after a node that yields a list — it gets one input per list element and runs the wrapped agent in parallel for each. The framework auto-fans-in: downstream nodes see one combined `Content` with all parts.

## 🛠 The full pattern, in code

From `workflow-concurrent_research_writer/agent.py`:

```python
research_workflow = WorkflowAgent(
    name="research_workflow",
    edges=[
        (
            START,
            start_node,                              # FunctionNode
            ParallelWorker(research_worker_agent),   # fan-out
            distill_agent,                           # LlmAgent — synthesize
            save_node,                               # FunctionNode — persist
        ),
    ],
)
```

One chain, four node kinds, dynamic fan-out. This is the entire research pipeline.

## 🧠 The `rerun_on_resume` flag

`FunctionNode(..., rerun_on_resume=True)` controls behavior when a workflow is **resumed** after a pause (HITL — page 07) or a checkpoint restore. If `True`, the node re-executes; if `False`, the recorded output is replayed without re-running. Pick `True` for cheap pure functions, `False` for nodes with side effects (DB writes, paid API calls).

## 🧠 Node naming matters for traces

`FunctionNode(func, name="Combine Reports")` — the `name` shows up in every trace, log, and visual graph view. Treat it like a span name. Default is the function's `__name__` which is usually fine.

## ⚠️ Don't forget to import the right `Event`

```python
from google.adk.agents.workflow.events.event import Event
```

This is **NOT** the same as `google.adk.events.Event` (the runtime/turn-level Event). The workflow `Event` is a node-yield envelope. Easy mistake; the type checker will catch it.

## 🛠 Write a tiny FunctionNode

```python
from collections.abc import AsyncGenerator
from google.adk.agents.workflow.events.event import Event
from google.adk.agents.workflow.function_node import FunctionNode

async def upper_node(node_input: str) -> AsyncGenerator[str, None]:
    yield node_input.upper()

upper = FunctionNode(upper_node, name="Upper")
```

> 🧭 **If `async def` + `yield` feels unfamiliar** → detour [[PY_async]] then [[PY_generators]].

> 🚀 **In Production**
>
> Keep `FunctionNode` bodies thin and deterministic. Push heavy logic into a regular function the node calls — easier to unit test in isolation. The node should be your *adapter* into the graph.

---

[← Prev: 06_GraphWorkflows/04_GraphIntro]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/06_RoutingEdges →]
