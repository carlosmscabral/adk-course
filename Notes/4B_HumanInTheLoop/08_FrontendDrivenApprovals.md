---
module: 4B_HumanInTheLoop
page: 08_FrontendDrivenApprovals
title: Frontend-driven approvals — the client owns the approval UI
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/04]
concepts: [client-driven-resume, REST-shape, approval-queue, UI-rendering]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 07_AmbientAgents](07_AmbientAgents.md)  [↑ Map](../../MAP.md)  [Next: 09_ChatPlatformApprovals →](09_ChatPlatformApprovals.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 08 Frontend-Driven Approvals

# 🛠 Frontend-driven approvals

The pattern: your **client** (web UI, mobile app, Slack) sees the `requested_tool_confirmations` event, renders the prompt, collects the user's decision, and calls back into `runner.run_async` with the resume payload. The Runner does no UI work; it only honors the resume request.

This page focuses on the **shape of the client-side contract**. The UI implementation details live in [23 Frontend Integration](../23_FrontendIntegration/) — this page is the back-end side of that handshake.

## The three-step contract

```
1. POST /run                                   →  Runner
     body: { user_id, session_id, message }
   ← events streamed back (SSE / WebSocket)
   ← among them: event with actions.requested_tool_confirmations

2. (client renders UI)
   user clicks approve / reject

3. POST /run                                   →  Runner
     body: {
       user_id, session_id,
       invocation_id: <from event>,
       message: {
         role: "user",
         parts: [{
           function_response: {
             id: <function_call_id from event>,
             name: "adk_request_confirmation",
             response: { hint: "...", confirmed: true, payload: {...} }
           }
         }]
       }
     }
   ← events streamed back — resume proceeds
```

Three POSTs are the entire contract: start, render-in-between, resume. The Runner doesn't care that step 2 took 7 seconds or 7 days.

## A runnable client (Python, no UI — just the shape)

```python
# Work/4B_08_client.py — drives a HITL agent end-to-end via an in-process Runner.
import asyncio
from google.adk.agents import LlmAgent, Context
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.apps._configs import ResumabilityConfig
from google.adk.tools.tool_confirmation import ToolConfirmation
from google.adk.flows.llm_flows.functions import REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
from google.genai import types


def transfer_funds(amount: float, to: str, ctx: Context) -> dict:
    if ctx.tool_confirmation is None:
        ctx.request_confirmation(
            hint=f"Transfer ${amount:.2f} to {to}?",
            payload={"amount": amount, "to": to},
        )
        return {}
    if not ctx.tool_confirmation.confirmed:
        return {"status": "rejected"}
    # In real life: bank.transfer(...). Here: pretend.
    final = ctx.tool_confirmation.payload  # client may have edited amount
    return {"status": "transferred", **final}


agent = LlmAgent(
    name="banker", model="gemini-2.5-flash",
    instruction="Transfer the named amount to the named recipient.",
    tools=[transfer_funds],
)
app = App(name="bank", root_agent=agent,
          resumability_config=ResumabilityConfig(is_resumable=True))


async def fake_ui(hint, payload):
    """In a real UI: render `hint`, let user click approve/reject + edit `payload`."""
    print(f"\n  ┌─ APPROVAL ─────────────────────────")
    print(f"  │ {hint}")
    print(f"  │ payload={payload}")
    print(f"  └─ [a]pprove / [r]eject (auto-approving for demo)")
    return ToolConfirmation(confirmed=True, payload=payload)


async def main():
    runner = InMemoryRunner(app=app)
    sess = await runner.session_service.create_session(app_name="bank", user_id="u1")

    msg = types.Content(role="user",
                        parts=[types.Part(text="Transfer $250 to alice@x.com")])

    # Loop until no more pauses surface in a run.
    invocation_id, fc_id, tc = None, None, None
    while True:
        async for event in runner.run_async(
            user_id="u1", session_id=sess.id, new_message=msg,
            invocation_id=invocation_id,
        ):
            for k, v in event.actions.requested_tool_confirmations.items():
                invocation_id = event.invocation_id; fc_id = k; tc = v
            for part in (event.content.parts if event.content else []):
                if part.text: print("AGENT:", part.text)
        if fc_id is None: break        # no pause this iteration → done
        approval = await fake_ui(tc.hint, tc.payload)
        msg = types.Content(role="user", parts=[types.Part(
            function_response=types.FunctionResponse(
                id=fc_id, name=REQUEST_CONFIRMATION_FUNCTION_CALL_NAME,
                response=approval.model_dump(by_alias=True),
            )
        )])
        fc_id = None                    # reset; will be set again if another pause

asyncio.run(main())
```

```
$ uv run python Work/4B_08_client.py

  ┌─ APPROVAL ─────────────────────────
  │ Transfer $250.00 to alice@x.com?
  │ payload={'amount': 250.0, 'to': 'alice@x.com'}
  └─ [a]pprove / [r]eject (auto-approving for demo)
AGENT: Transferred $250.00 to alice@x.com.
```

> 🛠 **Have the student:** swap the auto-approve in `fake_ui` for an `input("a/r? ")` prompt. They now have a CLI HITL loop in ~80 lines. The mini-drill (page 14) builds exactly this.

## REST mapping (what the HTTP layer looks like)

When you front the Runner with the built-in FastAPI app, the same flow over HTTP is:

```
# Start
POST /apps/bank/users/u1/sessions/{sid}/run
  body: { "new_message": { "role": "user", "parts": [{"text": "..."}] } }

# Resume
POST /apps/bank/users/u1/sessions/{sid}/run
  body: {
    "invocation_id": "<from event>",
    "new_message": {
      "role": "user",
      "parts": [{
        "function_response": {
          "id": "<fc_id>",
          "name": "adk_request_confirmation",
          "response": { "hint": "...", "confirmed": true, "payload": {...} }
        }
      }]
    }
  }
```

Most front-ends wrap this in a tiny client SDK so the UI code looks like `await client.approve(approvalId)`. The wire is what you see above.

## Storing pending approvals

The Runner persists the *checkpoint* but **does not** keep an "approval queue" — that's your application's job. Typical schema:

```sql
CREATE TABLE pending_approvals (
  id              UUID PRIMARY KEY,
  app_name        TEXT,
  user_id         TEXT,            -- approver
  session_id      TEXT,
  invocation_id   TEXT,
  function_call_id TEXT,
  hint            TEXT,
  payload         JSONB,
  created_at      TIMESTAMP,
  expires_at      TIMESTAMP,       -- TTL for the audit story
  decided_at      TIMESTAMP NULL,
  decision        TEXT NULL        -- "approved" | "rejected" | "timeout"
);
```

You read this table to render the approval queue UI; on click, you mark `decision` and call `runner.run_async()` with the resume payload above; on `expires_at < now()` a sweeper calls `runner.cancel()` and sets `decision="timeout"`. Page 12 has the full production checklist for this table.

> ❓ **Ask the student:** "Why does the Runner not own the pending-approvals table?" (Because the table is also your audit log, also feeds your monitoring dashboard, also drives your "Slack manager X about expense Y" notification — those are *your* concerns, not the runtime's. The Runner gives you the events; you decide how to queue them.)

## 🚀 In Production

> **🚀 In Production**
>
> The #1 production bug for client-driven approvals: **the UI re-renders the same pending event twice** (once from initial fetch, once from a polling refresh) and the user clicks approve twice — generating two resume calls for the same `(invocation_id, function_call_id)`. The framework will run the tool body twice in the worst case (at-least-once semantics — page 04). Mitigation: dedupe on the client *and* make tools idempotent. Belt + suspenders.

---

[← Prev: 07_AmbientAgents](07_AmbientAgents.md)  [↑ Map](../../MAP.md)  [Next: 09_ChatPlatformApprovals →](09_ChatPlatformApprovals.md)
