---
module: 4B_HumanInTheLoop
page: 06_RequestInputInGraphs
title: RequestInput — pause the whole graph for a human
estimated_minutes: 20
prereqs: [4B_HumanInTheLoop/05, 06_GraphWorkflows/04]
concepts: [RequestInput, rerun_on_resume, workflow-pause, payload]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 05_LongRunningFunctionTool](05_LongRunningFunctionTool.md)  [↑ Map](../../MAP.md)  [Next: 07_AmbientAgents →](07_AmbientAgents.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 06 RequestInput in Graphs

# 🧠 The third pause primitive

Two primitives so far:
- **`ctx.request_confirmation`** — pause one tool call inside an `LlmAgent`.
- **`LongRunningFunctionTool`** — pause one tool call, response from anywhere.

The third — **`RequestInput`** — pauses an entire **graph workflow** at a *node*. Use it when the human needs to interject *between* steps, not approve a single tool action.

This page is a tight recap; the long teaching lives at [06_GraphWorkflows/04_HumanInTheLoop](../06_GraphWorkflows/04_HumanInTheLoop.md). Open both side by side.

## The shape

```python
from google.adk.events import RequestInput
from google.adk import Context, Workflow


async def ask_for_destination(ctx: Context):
    """Pause the workflow and ask the user for a city."""
    yield RequestInput(
        message="Which city should we plan for?",
        response_schema={"city": str},
    )
```

The node yields `RequestInput`; the workflow suspends; the user responds; on resume the response becomes the node's `node_input` and downstream nodes continue.

## Why three primitives, not one

Conceptually all three are "pause + checkpoint + resume." Mechanically:

| Primitive | Suspends... | Resume payload type | Where to teach |
|---|---|---|---|
| `ctx.request_confirmation` | one tool call inside an LlmAgent | `ToolConfirmation` (approve/reject + payload) | here (pages 02-04) |
| `LongRunningFunctionTool` | one tool call, generic | whatever your tool returns | here (page 05) |
| `RequestInput` | a workflow node | dict matching `response_schema` | [06 Graph Workflows/04](../06_GraphWorkflows/04_HumanInTheLoop.md) |

The split exists because the three live at different abstraction layers (tool → tool → graph node) and the runtime surfaces them on different fields (`event.actions.requested_tool_confirmations` for the first two flavors of tool pause; the `RequestInput` is a content event in its own right).

## Runnable — concierge workflow with `RequestInput`

The canonical sample is `workflows-HITL_concierge`. Boiled down:

```python
# Work/4B_06_request_input.py (sketch — see 06/04 for the full version)
from pydantic import BaseModel
from google.adk import Workflow, Context
from google.adk.events import RequestInput
from google.adk.agents.llm_agent import LlmAgent


class Itinerary(BaseModel):
    activities: list[str]


async def initial_prompt(ctx: Context):
    yield RequestInput(
        message="City + interests?",
        response_schema={"user": str},
    )


concierge = LlmAgent(
    name="concierge", model="gemini-2.5-flash",
    instruction="Plan from the user's {node_input}.",
    output_schema=Itinerary,
)


async def ask_feedback(node_input: Itinerary):
    yield RequestInput(
        message=f"How's this? {node_input.activities}\nApprove or revise.",
        payload=node_input.model_dump(),
        response_schema={"feedback": str},
    )


async def process(node_input: str):
    yield {"final_feedback": node_input}


root_agent = Workflow(
    name="concierge_workflow",
    rerun_on_resume=True,
    edges=[
        ("START", initial_prompt, concierge, ask_feedback, process),
        (process, concierge),                # cycle back if revision requested
    ],
)
```

Two `RequestInput` pauses in one workflow. The agent can loop back to itself based on the human's feedback, which is the property graphs give you that pure-tool HITL does not.

## When to pick which

**Tool confirmation** is right when the pause is *inside* an agent's decision: "before I call this tool, ask the user."

**`RequestInput`** is right when the pause is *between* agents or *between* deterministic steps: "after the planner finishes, before the executor starts, ask the user to pick from the plan."

> ❓ **Ask the student:** "An e-commerce agent needs the user to confirm a cart before checkout. Tool confirmation or `RequestInput`?" (Either works. `RequestInput` is cleaner if checkout is its own node downstream of cart-builder; `request_confirmation` is cleaner if checkout is a single `place_order` tool call. Trade-off: graph nodes are heavier but more reusable.)

> 🛠 **Have the student:** read [06_GraphWorkflows/04_HumanInTheLoop](../06_GraphWorkflows/04_HumanInTheLoop.md) end to end if they haven't yet — page 11's dissection sample uses both flavors and we'll need to know the difference cold.

## 🚀 In Production

> **🚀 In Production**
>
> `rerun_on_resume` exists at **two scopes** — verify in `src/google/adk/workflow/_workflow.py:157` (workflow, default `True`) and `_base_node.py:56` (node, default `False`). The workflow-level default says "rerun every node when resuming", which is the safe-by-default behaviour for graph correctness but is exactly what burns money on resume. Mark each expensive LLM node explicitly with `rerun_on_resume=False` at the node level — that opt-out wins over the workflow default, and the node completes immediately using the resume input as its output (per the node-level docstring). The 06 module's dissection sample has the explicit pattern.

---

[← Prev: 05_LongRunningFunctionTool](05_LongRunningFunctionTool.md)  [↑ Map](../../MAP.md)  [Next: 07_AmbientAgents →](07_AmbientAgents.md)
