---
module: 19_Internals
page: 06_WorkflowSource
title: Workflow runtime — nodes, edges, scheduler
estimated_minutes: 30
prereqs: [19_Internals/05, 06_GraphWorkflows/02]
concepts: [Workflow, BaseNode, NodeRunner, scheduler]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/05_ToolDispatch]  [↑ Map](../../MAP.md)  [Next: 19_Internals/07_ModelRegistry →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 06 Workflow Source

# 🧠 Workflow runtime

The graph workflow is the **primary** orchestration primitive in ADK 2.0 (the Sequential/Parallel/Loop agents from earlier are now wrappers).

File layout in `/home/carloscabral/study/adk-python/src/google/adk/workflow/`:

```
_base_node.py          - BaseNode abstract: _run_impl + run_async wrapper
_node.py               - Node concrete (mostly a thin coordinator)
_workflow.py           - Workflow(BaseNode): the graph itself
_node_runner.py        - Executes a single node (event author, tracing)
_dynamic_node_scheduler.py - Schedules nodes whose edges depend on runtime data
_parallel_worker.py    - Parallel branch execution
_function_node.py      - Wraps a plain Python function as a node
_tool_node.py          - Wraps a tool as a node
_llm_agent_wrapper.py  - Adapts LlmAgent → node (so the runner can graph it)
_join_node.py          - Fan-in / synchronization point
_retry_config.py       - Per-node retry policy
_trigger.py            - Edge condition / trigger
_errors.py             - Workflow-specific exceptions
```

## `Workflow` — `_workflow.py:148`

```python
class Workflow(BaseNode):
    """A workflow is itself a node — so workflows nest."""
    # Holds: nodes, edges, entry, parallel branches, retry config.
```

Workflows are nodes too. This is what lets you embed a sub-workflow as one node inside a bigger graph — same pattern as functions calling functions.

## `_base_node.py`

The contract every node must satisfy:

```python
class BaseNode(BaseModel):
    name: str
    description: str

    async def _run_impl(
        self, *, ctx: Context, node_input: Any
    ) -> AsyncGenerator[Any, None]:
        ...
```

`run_async` (the public wrapper) handles tracing, retries, event-author stamping, and then delegates to `_run_impl`. Subclasses implement `_run_impl`.

## How an edge fires

1. A node finishes; its last yielded value is the **node output**.
2. The scheduler (`_dynamic_node_scheduler.py` or static `_workflow.py`) inspects outgoing edges from that node.
3. Each edge has a **trigger** (`_trigger.py`): a predicate over `(node_output, ctx)`. Edges whose trigger fires get their target queued.
4. Queued nodes go through `_node_runner.py::NodeRunner.run` — which builds a child `Context`, captures the node's events, stamps `event.author`, and yields them up.

## Parallel branches

`_parallel_worker.py` runs sibling branches concurrently via `asyncio.gather`. Each branch gets its own `branch` string on its events (`"root.branch_a"`, `"root.branch_b"`), which keeps their conversation isolation correct (see `Event.branch`).

## Dynamic scheduling

`_dynamic_node_scheduler.py` handles the case where the next node isn't known statically — e.g., a router node returns a string and only one of N possible next nodes runs. The `_LoopState` class in `_workflow.py:80` tracks loop iteration state.

## The `LlmAgent → node` bridge

`_llm_agent_wrapper.py` is the seam. When the runner sees an `LlmAgent` as the root, it calls `build_node(agent)` which produces a node whose `_run_impl` drives `agent._llm_flow`. This is why **everything** in 2.0 runs through the workflow scheduler — even single-agent apps.

> 🚀 **In Production**
>
> The graph runtime adds non-trivial overhead per node (tracing span, author stamp, branch tracking). For tight loops you don't need a `Workflow` — a single `LlmAgent` with `tools` is faster. Use graphs when you actually need fan-out/fan-in or explicit control flow.

> 🛠 **Have the student run:** `wc -l /home/carloscabral/study/adk-python/src/google/adk/workflow/*.py`. The whole runtime is ~3-4k lines — small enough to skim in an afternoon.

> ❓ **Ask the student:** "If the runner always wraps an LlmAgent in a node, why doesn't a hello-world script feel slow?" *(Answer: it's one node, no fan-out, no scheduler loops; the overhead is microseconds per turn.)*

[← Prev: 19_Internals/05_ToolDispatch]  [↑ Map](../../MAP.md)  [Next: 19_Internals/07_ModelRegistry →]
