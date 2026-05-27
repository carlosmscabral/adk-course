---
module: 4B_HumanInTheLoop
page: 11_DissectingSample
title: Dissecting ambient-expense-agent — ambient + HITL composed end to end
estimated_minutes: 45
prereqs: [4B_HumanInTheLoop/10]
concepts: [ambient-expense-agent, RequestInput, route-by-amount, manager-approval]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 10_DurableExecutionIntegrations](10_DurableExecutionIntegrations.md)  [↑ Map](../../MAP.md)  [Next: 12_InProduction →](12_InProduction.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 11 Dissecting Sample

# 🔬 Dissecting `ambient-expense-agent`

> 🤖 **Tutor:** open the sample directory side-by-side with this page. The student should be reading along, not listening to you paraphrase. Point at line numbers; the page does too.

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/`

## Why this sample

It's the only canonical sample that **composes every HITL surface this module taught**: ambient trigger (Pub/Sub), conditional routing (cheap path skips HITL entirely), LLM review on the expensive path, `RequestInput` pause for human approval, frontend-driven resume from an IAP-protected Cloud Run service. One file (`expense_agent/agent.py`) holds the workflow; another two (`config.py`, `fast_api_app.py`) wire the runtime; a Terraform tree deploys the lot.

`workflows-HITL_concierge` is the smaller alternative — it's good for understanding the pure `RequestInput` shape, but it doesn't show ambient triggering or the production deployment. We use that sample on page 06 (`RequestInput` recap). Here we go bigger.

## What we will trace

By the end of this read-through the student should be able to:
- Point at the line where the Pub/Sub event is parsed into structured expense data.
- Point at the line where the $100 threshold splits the cheap from the expensive path.
- Point at the line where the workflow **pauses with `RequestInput`** for human approval.
- Point at the line where the workflow **resumes** (the resume happens *outside* this file — but they should be able to name the route).
- Describe how the manager finds out a pending approval exists (Cloud Monitoring email).

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/` and confirm the layout (`expense_agent/`, `frontend/`, `terraform/`, `tests/`).

## File-by-file walkthrough

### `expense_agent/agent.py` — the workflow

This is the heart of the sample. It defines a `Workflow` with five nodes:

```
START → parse_expense_email → route_by_amount → { AUTO_APPROVE: auto_approve,
                                                  NEEDS_REVIEW: review_agent
                                                    → request_approval
                                                    → process_decision }
```

#### `parse_expense_email` (line ~59)

A pure function node. Takes the raw Pub/Sub message string, base64-decodes the inner data field, returns an `Event(output={"amount": ..., "submitter": ..., "category": ...})`. Note the defensive `try/except` — Pub/Sub can deliver malformed messages.

> ❓ **Ask the student:** "Why is parsing a separate node from routing?" (Single-responsibility — and if you ever want to swap Pub/Sub for SQS, only one node changes. Routing stays the same.)

#### `route_by_amount` (line ~90)

The conditional. Writes `node_input` into `ctx.state["expense_data"]` so the HITL node can use it later. Returns `Event(route="NEEDS_REVIEW", ...)` or `Event(route="AUTO_APPROVE", ...)`. The graph's edges (line ~262) consume the route string.

#### `auto_approve` (line ~107)

The cheap path. Emits a structured log line (Cloud Logging picks it up as JSON) and returns `Event(output={"status": "approved", ...})`. No LLM, no human — this branch finishes in ms.

#### `review_agent` (line ~165) — the LLM step

An `Agent` (single-turn) with `input_schema=ExpenseData`. Instructions tell it to evaluate risk, call `emit_expense_alert` (which emits a Cloud Monitoring log that triggers the manager's email), and return a structured review. Note: this is the **expensive** part of the workflow. We'll talk about marking it `rerun_on_resume=False` in the "tracing" section below.

#### `request_approval` (line ~197) — the HITL pause

The page-06 pattern, applied:

```python
def request_approval(node_input, ctx: Context):
    expense = ctx.state.get("expense_data", {})
    yield RequestInput(
        message="Expense requires manager approval. Approve or reject.",
        payload=expense,
    )
```

The workflow suspends here. The Pub/Sub HTTP call returns 200; Cloud Run is free to scale this instance down. The pending invocation lives in the session store until someone resumes it.

> ❓ **Ask the student:** "Why does `request_approval` re-read `expense_data` from `ctx.state` instead of just using `node_input`?" (Because `node_input` here is the **review_agent's structured review** — it doesn't have the raw amount/submitter the UI wants to show. The original expense was stashed in state by `route_by_amount` precisely for this purpose.)

#### `process_decision` (line ~212) — the post-resume node

Runs after the human resumes the workflow with `{"decision": "approve"}` or `{"decision": "reject"}`. Reads `node_input` (the resume payload), branches, emits a final log line, returns the user-facing message.

### `expense_agent/config.py` — the knobs

Three settings:
- `model` — the LLM for `review_agent` (defaults to a Gemini model).
- `review_threshold` — the $100 cut-off. Lives in code, not in the prompt, on purpose: business rules deserve unit tests.
- `app_name` — the ADK app name for the Runner.

### `expense_agent/fast_api_app.py` — the trigger wiring

This module exposes the FastAPI app that Cloud Run runs. The interesting line is the `App` construction with `resumability_config=ResumabilityConfig(is_resumable=True)` (or its equivalent — varies slightly between samples; the student should confirm by reading the file). Without that, the `RequestInput` pause has nowhere to checkpoint to.

### `frontend/` — the approval UI

A small web app. It calls a backend endpoint that lists pending approvals (queries the session store for invocations with pending `RequestInput`) and POSTs the resume back. IAP fronts it for auth. The student does not need to read every JS file — just understand the contract from page 08 is the contract this frontend implements.

### `terraform/` — the deploy

Two Cloud Run services (backend + frontend), one Pub/Sub topic + push subscription, one Cloud Monitoring email channel, one IAP config. If the student is GCP-curious, this is a good detour — otherwise skim.

## Trace one turn

End-to-end on paper (high-value expense path):

```
Pub/Sub message {"amount": 250, "submitter": "alice@x.com", ...}
  → HTTP POST → ADK trigger endpoint
  → parse_expense_email yields Event(output={"amount": 250, ...})
  → route_by_amount writes ctx.state["expense_data"], yields Event(route="NEEDS_REVIEW")
  → review_agent (LlmAgent) runs:
      → reads input as ExpenseData
      → calls emit_expense_alert tool (structured log to Cloud Logging)
      → returns structured review
  → request_approval yields RequestInput(message="...", payload=expense)
  → workflow SUSPENDS — checkpoint persisted to session store
  → HTTP call returns 200 — Pub/Sub message acked
  → Cloud Monitoring sees the alert log, emails the manager
  ─────────── time passes ───────────
  → manager opens approval UI (IAP)
  → manager clicks "Approve"
  → frontend POSTs to ADK backend with resume payload
  → workflow RESUMES at request_approval node
  → process_decision runs with {"decision": "approve"}
  → final log line, final event
```

> 🛠 **Have the student run** (locally, or by reading the README): the sample's local-test mode. It bypasses Pub/Sub by accepting a JSON expense via a regular HTTP POST. Drive a low-value expense (auto-approves) and a high-value expense (pauses). Confirm both traces.

## Module concepts present in this sample

| Module concept | Where in the sample |
|---|---|
| HITL — pause-then-resume | `expense_agent/agent.py:197` (`request_approval` yields `RequestInput`) |
| `App.resumability_config` | `expense_agent/fast_api_app.py` (and recap [Module 1A](../1A_AppAndRunner/04_ResumabilityConfig.md)) |
| Ambient trigger (Pub/Sub) | `terraform/` Pub/Sub push to Cloud Run + ADK trigger endpoint |
| Frontend-driven resume | `frontend/` posts to backend; backend calls `runner.run_async(invocation_id=...)` |
| In-state stash for HITL payload | `expense_agent/agent.py:100` (`route_by_amount` writes `ctx.state["expense_data"]`) |
| 10-minute ack deadline avoidance | The whole "suspend, ack, resume separately" design (page 07) |

---

[← Prev: 10_DurableExecutionIntegrations](10_DurableExecutionIntegrations.md)  [↑ Map](../../MAP.md)  [Next: 12_InProduction →](12_InProduction.md)
