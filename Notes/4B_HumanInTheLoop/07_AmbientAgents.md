---
module: 4B_HumanInTheLoop
page: 07_AmbientAgents
title: Ambient Agents — event-triggered runs that occasionally pause for a human
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/06]
concepts: [ambient-agents, Pub/Sub-trigger, GCS-trigger, Scheduler-trigger, 10-minute-cap]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 06_RequestInputInGraphs](06_RequestInputInGraphs.md)  [↑ Map](../../MAP.md)  [Next: 08_FrontendDrivenApprovals →](08_FrontendDrivenApprovals.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 07 Ambient Agents

# ☁️ Ambient Agents

> 🤖 **Tutor:** the word "ambient" is overloaded — in product copy it means "always on, no UI". For ADK, narrow it to: **the agent is triggered by an external event, not a user message.**

Every agent we've built so far runs because **the user typed.** Ambient agents flip that: they run because **something happened** — a Pub/Sub message arrived, a file landed in GCS, Cloud Scheduler fired a cron — and a turn begins with no human in the loop. They're a 2.0 surface; the canonical reference is `ambient-expense-agent`.

```
  classic chat agent           ambient agent
  ───────────────              ─────────────
  user types  ▶  agent runs    Pub/Sub  ▶  agent runs
  agent replies  ◀  user reads (no user yet)
                               agent eventually
                               needs a human?
                                  ▶  pauses with
                                     RequestInput,
                                     emails the human
                                     via a side channel
```

## Where the human enters

In a chat agent, the human is *implicit* — there is always a user on the other end. In an ambient agent, the human is *opt-in*: they only join when the workflow chooses to pause. So ambient + HITL is not redundant; it's the **standard composition** for ambient flows that need a gate.

`ambient-expense-agent` is the model:
- **Triggered** by a Pub/Sub message ("expense submitted: $X").
- **Auto-decides** for low-value expenses (under $100) — never bothers a human.
- **Pauses with `RequestInput`** for high-value expenses, emails the manager, waits.
- **Resumes** when the manager clicks approve/reject in a separate UI.

## Triggers ADK supports

ADK 2.0 ships with built-in trigger endpoints for three sources:

| Trigger | Where the event comes from | Typical pattern |
|---|---|---|
| **Pub/Sub** | Cloud Pub/Sub topic push subscription | Expense submission, order placed, alert from monitoring |
| **GCS** | Object created/deleted notification | New file uploaded, document to process |
| **Scheduler** | Cloud Scheduler cron job | Nightly summary, daily cleanup |

These are exposed by ADK's FastAPI app (the same surface that exposes `/run`) at endpoints like `/triggers/pubsub`, `/triggers/gcs`, `/triggers/scheduler`. Your deploy wires them to the relevant GCP source.

## The 10-minute cap

Pub/Sub push delivery has a **10-minute ack deadline** (technically up to 600s for the longest configurable maxAckDeadlineSeconds). If your ambient agent runs longer than that without acking, Pub/Sub redelivers, your agent runs again, and you end up with duplicate work.

The implication for ambient + HITL: **the agent must pause and ack within 10 minutes**. A `RequestInput` is the right pattern — the workflow suspends, the FastAPI endpoint returns 200 to ack the message, and the resume happens **as a separate request** when the human responds. If you held the Pub/Sub message open until the human approved, you'd lose it (or process the expense twice).

This is the difference between **"long-running tool"** and **"pause-then-resume"**: the former blocks the trigger HTTP call; the latter ends the HTTP call and waits for a *new* call to drive the resume. **Always pause-then-resume for ambient.**

## A skeleton

```python
# expense_agent/agent.py — derived from ambient-expense-agent
from google.adk import Agent, Context, Event, Workflow
from google.adk.events import RequestInput


def parse_pubsub(node_input: str) -> Event:
    # ... decode base64, extract amount ...
    return Event(output=parsed)


def route_by_amount(node_input: dict, ctx: Context) -> Event:
    ctx.state["expense_data"] = node_input
    if node_input["amount"] >= 100:
        return Event(route="NEEDS_REVIEW", output=node_input)
    return Event(route="AUTO_APPROVE", output=node_input)


def auto_approve(node_input: dict) -> Event:
    # log + return — sub-10-minute hot path, no human involved
    return Event(output={"status": "approved", **node_input})


review_agent = Agent(
    name="review_agent", model="gemini-2.5-flash",
    instruction="...analyze risk, call emit_expense_alert tool...",
    tools=[emit_expense_alert],
)


def request_approval(node_input, ctx: Context):
    yield RequestInput(
        message="Expense requires manager approval.",
        payload=ctx.state.get("expense_data", {}),
    )


root_agent = Workflow(
    name="expense_processor",
    edges=[
        ("START", parse_pubsub, route_by_amount),
        (route_by_amount, {"AUTO_APPROVE": auto_approve, "NEEDS_REVIEW": review_agent}),
        (review_agent, request_approval, process_decision),
    ],
)
```

Two paths from one graph. The auto-approve path stays sub-10-minutes; the review path pauses and is resumed by a *different* HTTP request (the manager clicking approve).

## Production architecture

```
  Pub/Sub  ─▶  Cloud Run (ADK backend)
                  │
              ┌───┴────┐
              │ ack    │  (sub-10-min — workflow suspended)
              ▼        │
        emit log ◀─────┘  (Cloud Monitoring picks up, emails manager)
                  ▲
                  │ (manager clicks approve in a separate UI)
  Cloud Run (approval frontend, IAP-protected)
                  │
                  ▼
              POST /run (with function_response payload + invocation_id)
                  │
                  ▼
           Cloud Run (ADK backend, same one) — resume
```

The frontend is a second Cloud Run service in front of the same ADK backend. Identity-Aware Proxy (IAP) handles auth on the approval UI. See `/home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/terraform/` for the deploy.

> 🛠 **Have the student:** `cat /home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/expense_agent/agent.py` and identify the four kinds of nodes (function, LLM agent, HITL-pause, decision). The graph **mixes** them — that's the ambient + HITL pattern in one file.

## When ambient is wrong

Not every "background" thing should be an ambient agent. If the workflow:
- Runs for **more than ~30 minutes total** (auto + manual) — you want durable execution ([10_DurableExecutionIntegrations](10_DurableExecutionIntegrations.md)).
- Has **complex retry policies** (exponential backoff with jitter, dead-letter after N attempts) — durable execution wins again.
- Is genuinely **batch** (process 10k rows, emit one report) — that's Cloud Run Jobs / Dataflow / Composer, not an ambient agent.

The ambient agent shines in the middle: event-driven, latency budget of minutes-to-an-hour, occasional human gate.

> ❓ **Ask the student:** "What forces a Pub/Sub-triggered ambient agent to pause-then-resume instead of waiting inline for a human?" (The 10-minute ack deadline. Holding the request open will get the message redelivered.)

## 🚀 In Production

> **🚀 In Production**
>
> Ambient agents must be **idempotent at the trigger level** — Pub/Sub guarantees at-least-once. The standard mitigation: parse a unique id off the message (Pub/Sub `messageId`, GCS `eventId`, your own `expense_id`) on the first node and short-circuit if you've already processed it. Store the dedup set in the session store, not in process memory.

---

[← Prev: 06_RequestInputInGraphs](06_RequestInputInGraphs.md)  [↑ Map](../../MAP.md)  [Next: 08_FrontendDrivenApprovals →](08_FrontendDrivenApprovals.md)
