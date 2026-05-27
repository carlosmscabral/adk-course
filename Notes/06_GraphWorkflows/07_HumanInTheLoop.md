---
module: 06_GraphWorkflows
page: 07_HumanInTheLoop
title: Human-in-the-loop — pause, resume, cancel
estimated_minutes: 25
prereqs: [06_GraphWorkflows/06]
concepts: [RequestInput, rerun_on_resume, resume-token, Resume, Cancel]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/06_RoutingEdges]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/08_DissectingWorkflowSample →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 07 HITL

## 🧠 The HITL primitive

A workflow node can yield a special event that **pauses the entire workflow** until a human responds:

```python
from google.adk.events import RequestInput

async def ask_for_city(ctx):
    yield RequestInput(
        message="Which city? (e.g., 'America/New_York')",
        response_schema={"city": str},
    )
```

The runtime suspends the workflow, persists the state, and returns control to whoever invoked the runner. The caller (your application) shows the message to the user, collects a response, then calls a **resume API** with the response payload.

## 🧠 The full pause-resume lifecycle

```
   app                    workflow                    user
    │                        │                          │
    │  run_async(input)     │                          │
    │──────────────────────▶│                          │
    │                        │   node A runs            │
    │                        │   node B yields          │
    │                        │   RequestInput(...)      │
    │   RequestInput event  │                          │
    │◀──────────────────────│  ← workflow suspended    │
    │                                                   │
    │   render "Which city?" ──────────────────────────▶│
    │                                                   │
    │   ← {"city": "Paris"} ────────────────────────────│
    │                                                   │
    │  resume(payload, token)│                          │
    │──────────────────────▶│                          │
    │                        │  payload becomes         │
    │                        │  node B's "node_input"   │
    │                        │  on the next run         │
    │                        │  (because rerun_on_resume│
    │                        │   = True)                │
```

See [`_figures/hitl_pause.txt`](_figures/hitl_pause.txt) for the diagram.

## 🛠 Pattern from `workflows-HITL_concierge`

```python
from google.adk.events import RequestInput
from google.adk.agents.context import Context
from google.adk.workflow import Workflow, START

async def initial_prompt(ctx: Context):
    """Ask the user for a city + optional details."""
    input_message = "...City (Required), Age, Hobby, Example attraction..."
    yield RequestInput(message=input_message, response_schema={"user response": str})


async def get_user_feedback(node_input):
    """Ask: which of these activities do you like?"""
    message = f"Here is your recommended base itinerary:\n{node_input}\n\nWhich appeal?"
    yield RequestInput(
        message=message,
        payload=node_input,
        response_schema={"user": "response"},
    )

root_agent = Workflow(
    name="root_agent",
    rerun_on_resume=True,                  # ← Workflow field; default is already True
    edges=[
        (START, initial_prompt, concierge_agent, get_user_feedback, process_feedback),
        (process_feedback, concierge_agent),    # cycle back if user wants changes
    ],
)
```

`Workflow.rerun_on_resume` defaults to `True` (see `_workflow.py:157`), so the outer workflow re-enters its scheduler loop on resume. The HITL node re-runs with the user's response as its input — prior LLM calls are *not* re-paid because their outputs are checkpointed in the session events. Per-node `rerun_on_resume` is set on individual `FunctionNode`s.

## 🧠 Resume tokens

When the runtime emits a `RequestInput`, the event carries an **invocation_id** identifying the paused invocation. Your application stores it (typically in your own database keyed by the user's session) and passes it back to `Runner.run_async` along with the user's response wrapped in a `Content` with a function response:

```python
# Resume — the SAME run_async entrypoint, with invocation_id + a function-response message.
async for event in runner.run_async(
    user_id="u1",
    session_id="s1",
    invocation_id=stored_invocation_id,   # pause point
    new_message=function_response_content, # the user's reply as a function response
):
    ...
```

There is no separate `runner.resume(...)` method — resume is the regular `run_async` call with `invocation_id` set. See [`1A_AppAndRunner/04_WiringResumability`](../1A_AppAndRunner/04_WiringResumability.md) for the wiring and `runners.py` (`_resolve_invocation_id`, `_extract_resume_inputs`) for the exact contract.

## 🧠 Cancel

To cancel a suspended workflow, the dual is to simply not resume — the session keeps the paused state until you either resume or garbage-collect the session. Programmatic cancellation is handled at the App / session-service layer (delete the session, or send a cancel signal that the consuming code translates into "skip this invocation"). The `Workflow._cleanup_all_tasks` path covers in-process cancellation when the orchestration loop exits.

## ⚠️ HITL gotchas

1. **Side-effecting nodes upstream of a HITL pause** — if they have `rerun_on_resume=True` they re-fire (paying API costs twice). Mark expensive nodes `rerun_on_resume=False`.
2. **Schema drift between pause and resume** — if you change `response_schema` between releases while a workflow is suspended, the resume can fail. Version your schemas.
3. **Long-lived suspensions** — workflows can be paused for days. Make sure your session store (module 04) is durable (`DatabaseSessionService` or `VertexAiSessionService`, not `InMemorySessionService`).

> 🚀 **In Production**
>
> Treat the resume token as **sensitive**. Anyone with the token can inject the next input into the workflow. Bind it to the user's session and verify identity on resume.

> **🧭 See also**: `workflows-HITL_concierge` is the smallest graph-HITL sample (linear stem with a `RequestInput` pause for itinerary feedback, cycles back if the user wants changes). Read `agent.py` end-to-end — it's ~80 lines. The fuller 4B coverage is at [[4B_HumanInTheLoop/06_RequestInputInGraphs]], which uses the same sample as its canonical anchor.

> ❓ **Ask the student:** what changes for a 24-hour HITL pause vs a 30-second one? (Session persistence. The `InMemorySessionService` loses everything on process restart — must use a durable backend.)

---

[← Prev: 06_GraphWorkflows/06_RoutingEdges]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/08_DissectingWorkflowSample →]
