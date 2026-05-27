---
module: 24_ChannelIntegrations
page: 10_DissectingSample
title: Dissecting ambient-expense-agent — Pub/Sub channel + HITL
estimated_minutes: 45
prereqs: [24_ChannelIntegrations/09]
concepts: [ambient_expense, pubsub_trigger, graph_workflow, request_input, hitl, structured_logging]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 09_HandlingMultimedia](09_HandlingMultimedia.md)  [↑ Map](../../MAP.md)  [Next: 11_InProduction →](11_InProduction.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 10 Dissecting Sample

# 🔬 Dissecting `ambient-expense-agent`

> 🤖 **Tutor:** open the sample in the student's editor. Walk paths and lines; don't paste.

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/`

## Why this sample

It is the canonical ADK 2.0 ambient sample. Pub/Sub is the "channel" — no user typed a message; an event fires, an agent reviews, low-value auto-approves, high-value pauses for human approval via `RequestInput` (HITL). It exercises:

- Pub/Sub trigger via `get_fast_api_app(trigger_sources=["pubsub"])` (page 07's exact pattern).
- A `Workflow` graph with conditional routing (mixed function nodes + LLM agent + HITL node).
- A frontend that queries `GET /apps/.../sessions` to surface pending approvals.
- Structured logging to drive log-based metrics and alert emails (a third "channel" — email out).

## What we'll trace

By the end the student should be able to:

- Point at the line that registers the Pub/Sub trigger endpoint.
- Point at the line that normalizes the subscription resource path → short name.
- Point at the `Workflow` definition and explain each edge.
- Point at the `RequestInput` that pauses the workflow for human approval.
- Explain how the frontend discovers pending approvals.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/` and confirm `expense_agent/`, `frontend/`, `Dockerfile`, `Makefile`, `terraform/`.

## File-by-file walkthrough

### `expense_agent/fast_api_app.py` — the channel doorway

This is the universal-adapter-as-code from pages 01 and 07. Two interesting things:

```python
app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,
    trigger_sources=["pubsub"],
)
```

That single call registers `POST /trigger/pubsub`. ADK does the webhook→Runner mapping; you don't write it.

```python
@app.middleware("http")
async def normalize_pubsub_subscription(request, call_next):
    if request.url.path.endswith("/trigger/pubsub") and request.method == "POST":
        body = await request.body()
        data = json.loads(body)
        sub = data.get("subscription", "")
        if "/" in sub:
            data["subscription"] = sub.rsplit("/", 1)[-1]
            request._body = json.dumps(data).encode()
    return await call_next(request)
```

The middleware turns `projects/my-proj/subscriptions/review-sub` into `review-sub`. Why: ADK uses `subscription` as the `user_id`. Without normalization the user_id would be the full resource path — ugly, leaky, and breaks frontend session listings.

> ❓ **Ask the student:** "Why does the sample even need a custom middleware? Could you just set the trigger's user_id elsewhere?"
>
> (Answer: ADK's built-in trigger handler reads `subscription` verbatim. The sample owns the HTTP path; the cleanest fix is to rewrite the body before ADK sees it. A future ADK release may make this a config option.)

### `expense_agent/agent.py` — the graph

This is the agent. Walk it top to bottom with the student:

1. **Pydantic schema** (`ExpenseData`) — typed flow between nodes.
2. **Function nodes** (`parse_expense_email`, `route_by_amount`, `auto_approve`, `request_approval`, `process_decision`) — pure Python, no LLM.
3. **One LLM agent** (`review_agent`) with one tool (`emit_expense_alert`).
4. **`Workflow`** with edges:

```python
root_agent = Workflow(
    name="expense_processor",
    edges=[
        ("START", parse_expense_email, route_by_amount),
        (route_by_amount, {
            "AUTO_APPROVE": auto_approve,
            "NEEDS_REVIEW": review_agent,
        }),
        (review_agent, request_approval, process_decision),
    ],
)
```

Trace:

```
START → parse_expense_email → route_by_amount
                              ├── AUTO_APPROVE → auto_approve → END
                              └── NEEDS_REVIEW → review_agent → request_approval (HITL pause)
                                                            ↓
                                                  human approves/rejects
                                                            ↓
                                                  process_decision → END
```

### The HITL twist — `request_approval`

```python
def request_approval(node_input, ctx):
    expense = ctx.state.get("expense_data", {})
    yield RequestInput(
        message="Expense requires manager approval. Approve or reject.",
        payload=expense,
    )
```

This is where the workflow **pauses**. ADK persists session state, returns from the Pub/Sub webhook (which has already ACK'd long ago), and waits. Some frontend (the `frontend/` folder) discovers this pending session by querying `GET /apps/.../sessions` and shows an approval card. When a human POSTs the decision, the workflow resumes with the decision as `node_input` to `process_decision`.

> ❓ **Ask the student:** "How is this different from a standard chat bot, in terms of session lifecycle?"
>
> (Answer: a chat bot's session lives only during a user-typed turn. An ambient agent's session can span days — created by a Pub/Sub event, paused at HITL, resumed when a human approves. The persistent session service is non-negotiable here.)

### `expense_agent/config.py` — review threshold

Trivial; pulls `review_threshold` (defaults $100). Worth noting because the threshold is the *only* business rule that hand-tuned humans care about; the rest is policy and risk-scoring inside the LLM agent's instruction.

### `frontend/main.py` — the approval UI

This is where pages 03-05's "frontend speaks ADK" patterns from module 23 show up. The frontend polls `GET /apps/expense_agent/users/{subscription_name}/sessions` to find sessions paused on `RequestInput`. Each pending session renders as an approval card with Approve/Reject buttons. Click → POST `/run` with the decision.

This is exactly the **HITL frontend pattern** from [23/10 OptimisticUI](../23_FrontendIntegration/10_OptimisticUI.md).

### `terraform/` — the deployment

For the student already in the deployment headspace: this folder shows the full prod wiring — Cloud Run service, Pub/Sub topic + subscription pointing at the service's `/trigger/pubsub` URL, IAM bindings, secrets. Module 22 (Deployment) is where this lives in depth.

## Trace one expense

```
1. Finance system publishes to Pub/Sub topic "expense-reports":
   {"amount": 450, "submitter": "alice@co", "category": "travel",
    "description": "client dinner", "date": "2026-05-25"}

2. Pub/Sub push delivery hits POST /trigger/pubsub
   Middleware normalizes subscription path → "review"
   ADK constructs session: user_id="review", session_id=<auto>
   ADK invokes root_agent (the Workflow)

3. parse_expense_email: pulls amount=450 etc.
4. route_by_amount: 450 >= 100 → routes NEEDS_REVIEW; stashes data in state
5. review_agent (LLM): inspects, calls emit_expense_alert
   → structured log lands in Cloud Logging
   → log-based metric fires → alert email sent (FOURTH channel!)
6. request_approval: yields RequestInput
   → workflow PAUSES
   → webhook returns 200 to Pub/Sub long ago
   → session sits in DB with status="awaiting_input"

7. (Hours later) Manager visits frontend
   → frontend GETs /apps/expense_agent/users/review/sessions
   → finds the paused session, renders approval card
   → manager clicks "Approve"
   → frontend POSTs /run with {"decision": "approve"}

8. process_decision: logs the verdict
9. Workflow ENDs; session marked complete.
```

Three to four channels touched in one flow:

- **In**: Pub/Sub.
- **Out**: structured log → Cloud Logging → email alert.
- **In**: frontend (approval click).
- **Out**: structured log → status report.

## Module concepts present in this sample

| Module concept | Where in the sample |
|---|---|
| Pub/Sub trigger (page 07) | `fast_api_app.py:42-46` (`trigger_sources=["pubsub"]`) |
| Subscription name normalization (page 07) | `fast_api_app.py:48-67` (middleware) |
| Ambient agent → posting to "another channel" (page 07) | `agent.py:129-162` (`emit_expense_alert` → Cloud Logging) |
| HITL pause/resume + frontend discovery (page 08, cross-ref to 23/10) | `agent.py:197-209` (`RequestInput`) + `frontend/main.py` |
| Per-channel `user_id` (page 08) | The subscription-name-as-user_id pattern (`fast_api_app.py` middleware) |
| Long-running ack (page 02 implicit) | Pub/Sub ack happens *before* the workflow pauses — same idea |

## What it doesn't have

- **Direct Slack/Chat/Discord integration** — the alerts go to *email* via log-based metrics. To send to Slack instead, replace `emit_expense_alert` with `post_to_slack` (page 03 pattern). Trivial swap.
- **Multimedia** — expense reports are JSON. If finance attached PDF receipts, you'd add page 09's `fetch_and_attach` pattern.

> 🛠 **Have the student run:** `cd ~/study/adk-samples/python/agents/ambient-expense-agent && make dev` (or follow README). Publish a test message: `gcloud pubsub topics publish ...`. Watch the agent fire. Then watch the frontend reveal a pending approval.

[← Prev: 09_HandlingMultimedia](09_HandlingMultimedia.md)  [↑ Map](../../MAP.md)  [Next: 11_InProduction →](11_InProduction.md)
