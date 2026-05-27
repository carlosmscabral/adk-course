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
from google.adk.agents.workflow.events.request_input import RequestInput

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
from google.adk.agents.workflow.events.request_input import RequestInput
from google.adk.agents.workflow.workflow_context import Context

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

root_agent = WorkflowAgent(
    name="root_agent",
    rerun_on_resume=True,                  # ← critical for HITL nodes
    edges=[
        ("START", initial_prompt, concierge_agent, get_user_feedback, process_feedback),
        (process_feedback, concierge_agent),    # cycle back if user wants changes
    ],
)
```

Notice `rerun_on_resume=True` on the workflow itself. When the workflow resumes, the HITL node re-runs with the user's response as its input — the prior LLM calls upstream are *not* re-paid because their outputs are checkpointed.

## 🧠 Resume tokens

When the runtime emits a `RequestInput`, it also produces a **resume token** identifying the suspension point. Your application stores the token (typically in your own database keyed by the user's session) and presents it to the resume API later:

```python
# pseudo
await runner.resume(
    invocation_id=stored_token,
    user_input={"user response": "Paris, age 28, hiking"},
)
```

The exact API for `resume()` lives on the `Runner` in ADK 2.0; consult the latest docs and the `workflows-HITL_concierge` sample for the up-to-date signature.

## 🧠 Cancel

`runner.cancel(invocation_id)` is the dual — it tears down a suspended workflow cleanly. Use it for timeouts, user-abandons-chat scenarios, or admin overrides.

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
