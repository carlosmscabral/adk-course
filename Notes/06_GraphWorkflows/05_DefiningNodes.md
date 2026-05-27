---
module: 06_GraphWorkflows
page: 05_DefiningNodes
title: Defining nodes — agents, functions, list-yielding fan-out
estimated_minutes: 25
prereqs: [06_GraphWorkflows/04]
concepts: [FunctionNode, node-decorator, Event, async-generator, list-fan-out]
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

### 2. `FunctionNode` — wrap a sync/async function

```python
from google.adk.workflow import FunctionNode
from google.adk.events import Event
from google.genai.types import Content

async def start_research_node(node_input: Content):
    """Read user input, stash topic in state, fan out platforms."""
    topic = str(node_input.parts[0].text if node_input.parts else "")
    yield Event(state={"topic": topic})              # write to state
    yield ["X", "LinkedIn", "Reddit", "Medium"]      # fan out

start_node = FunctionNode(
    func=start_research_node,
    name="Start Research Node",
    rerun_on_resume=True,           # FunctionNode.__init__ kwarg
)
```

Three things the function can yield:

- **`Event(state={...})`** — write to session state.
- **`Event(route="X")`** — emit a route label for conditional edges (page 06).
- **A plain value (str, list, dict, `ModelContent`)** — passed as `node_input` to the next node.

If you yield a **list**, the runtime fans out: the next node runs *once per list element*. This is how parallel research stages work — yield `["X", "LinkedIn", "Reddit", "Medium"]` and the next node is invoked four times concurrently.

### 3. Decorator form — `@node`

```python
from google.adk.workflow import node

@node(name="Upper")
async def upper(node_input: str):
    yield node_input.upper()
```

`@node` is a thin sugar over `FunctionNode` — same kwargs, same yield semantics. Pick whichever reads better.

> ⚠️ **Don't import `_ParallelWorker`**. The class exists at `google.adk.workflow._parallel_worker` but is **private** (leading underscore, not in `__init__.py __all__`). The public way to fan out is to yield a list from a node — the framework handles the parallel dispatch internally.

## 🛠 The full pattern, in code

A research pipeline assembled from the public 2.0 primitives:

```python
from google.adk.workflow import Workflow, START

research_workflow = Workflow(
    name="research_workflow",
    edges=[
        (
            START,
            start_node,            # FunctionNode — yields list to fan out
            research_worker_agent, # LlmAgent — runs once per list element
            distill_agent,         # LlmAgent — synthesizes the merged Content
            save_node,             # FunctionNode — persists the report
        ),
    ],
)
```

One chain, three node kinds, dynamic fan-out via the list yield. This is the entire research pipeline. The framework auto-fans-in: `distill_agent` sees one combined `Content` with one part per parallel result.

## 🧠 The `rerun_on_resume` flag

`FunctionNode(..., rerun_on_resume=True)` controls behavior when a workflow is **resumed** after a pause (HITL — page 07) or a checkpoint restore. If `True`, the node re-executes; if `False`, the resuming input is treated as the node's output (no re-execution). Pick `True` for cheap pure functions and for any node that uses `auth_config` (auth nodes *must* rerun); pick `False` for nodes with side effects (DB writes, paid API calls).

> ⚠️ `rerun_on_resume` is a `BaseNode` field (defaults to `False`); on `FunctionNode` it is an `__init__` kwarg. The `Workflow` class also has a `rerun_on_resume` field that defaults to `True` — that controls whether the *outer workflow* re-enters on resume, distinct from the per-node setting.

## 🧠 Node naming matters for traces

`FunctionNode(func, name="Combine Reports")` — the `name` shows up in every trace, log, and visual graph view. Treat it like a span name. Default is the function's `__name__` which is usually fine.

## ⚠️ One `Event`, one import

```python
from google.adk.events import Event
```

There is **one** `Event` in 2.0 — the framework's event envelope (`google.adk.events.Event`). The 1.x samples have a separate `agents.workflow.events.event.Event`; that module no longer exists in 2.0. Use `google.adk.events.Event`.

## 🛠 Write a tiny FunctionNode

```python
from collections.abc import AsyncGenerator
from google.adk.events import Event
from google.adk.workflow import FunctionNode

async def upper_node(node_input: str) -> AsyncGenerator[str, None]:
    yield node_input.upper()

upper = FunctionNode(func=upper_node, name="Upper")
```

> 🧭 **If `async def` + `yield` feels unfamiliar** → detour [[PY_async]] then [[PY_generators]].

> 🚀 **In Production**
>
> Keep `FunctionNode` bodies thin and deterministic. Push heavy logic into a regular function the node calls — easier to unit test in isolation. The node should be your *adapter* into the graph.

---

[← Prev: 06_GraphWorkflows/04_GraphIntro]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/06_RoutingEdges →]
