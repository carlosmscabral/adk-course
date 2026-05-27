---
module: 4B_HumanInTheLoop
page: 03_RequestedToolConfirmations
title: EventActions.requested_tool_confirmations — the pause event on the wire
estimated_minutes: 20
prereqs: [4B_HumanInTheLoop/02]
concepts: [EventActions, requested_tool_confirmations, function_call_id, adk_request_confirmation]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 02_RequestConfirmation](02_RequestConfirmation.md)  [↑ Map](../../MAP.md)  [Next: 04_RunnerResumeAndCancel →](04_RunnerResumeAndCancel.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 03 Requested Tool Confirmations

# 🧠 The pause event

When the tool calls `ctx.request_confirmation(...)`, the runtime turns it into an **event** with a populated `actions.requested_tool_confirmations` dict. This is the interface every client (web UI, Slack bot, CLI) reads.

## The shape

```python
class EventActions(BaseModel):
    requested_tool_confirmations: dict[str, ToolConfirmation] = {}
    # ... other fields (state_delta, transfer_to_agent, escalate, ...)
```

- **Key**: the `function_call_id` (a string the runtime generates per tool call — `fc_1`, `fc_2`, ...).
- **Value**: the `ToolConfirmation(hint=..., payload=..., confirmed=False)` you constructed in the tool.

## Reading it

```python
async for event in runner.run_async(user_id="u1", session_id=sess_id, new_message=msg):
    pending = event.actions.requested_tool_confirmations
    if pending:
        for fc_id, tc in pending.items():
            print(f"[PAUSE {fc_id}] hint={tc.hint!r}  payload={tc.payload!r}")
            # → persist (event.invocation_id, fc_id, tc) somewhere
            #   so your UI / Slack / approval queue can present it.
```

You always get the dict — empty when nothing is pending. The presence of one or more entries is your signal **"the workflow is suspended; do not assume there will be more events."**

## What's actually on the wire

Internally the runtime represents the pause as a *function call* with the reserved name `adk_request_confirmation`. The framework's `request_confirmation` LLM-flow processor (`google.adk.flows.llm_flows.request_confirmation`) inspects incoming function responses, finds the ones named `adk_request_confirmation`, parses out the `ToolConfirmation` payload, and *re-runs the original tool* with `ctx.tool_confirmation` populated.

You normally don't see this — `event.actions.requested_tool_confirmations` is the friendly façade — but it explains the shape of the resume payload in page 04. If you're debugging in `adk web` and see a `function_call` named `adk_request_confirmation`, that's the pause marker; it's not user-facing.

## A second runnable — multiple pending confirmations in one turn

The LLM can request several confirmed tools in parallel:

```python
# Work/4B_03_multi_pause.py
import asyncio
from google.adk.agents import LlmAgent, Context
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.apps import ResumabilityConfig
from google.genai import types


def send_email(to: str, ctx: Context) -> dict:
    """Send an email to `to`. Asks for confirmation first."""
    if ctx.tool_confirmation is None:
        ctx.request_confirmation(hint=f"Email {to}?", payload={"to": to})
        return {}
    return {"sent_to": to}


agent = LlmAgent(
    name="bulk_mailer",
    model="gemini-2.5-flash",
    instruction=(
        "When asked to email a list, call send_email once per recipient. "
        "Do NOT batch."
    ),
    tools=[send_email],
)
app = App(
    name="bulk", root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)


async def main():
    runner = InMemoryRunner(app=app)
    sess = await runner.session_service.create_session(app_name="bulk", user_id="u1")
    msg = types.Content(role="user", parts=[
        types.Part(text="Email alice@x.com, bob@x.com, carol@x.com")])
    async for event in runner.run_async(
        user_id="u1", session_id=sess.id, new_message=msg
    ):
        for fc_id, tc in event.actions.requested_tool_confirmations.items():
            print(f"PENDING {fc_id}: {tc.hint}")


asyncio.run(main())
```

```
$ uv run python Work/4B_03_multi_pause.py
PENDING fc_1: Email alice@x.com?
PENDING fc_2: Email bob@x.com?
PENDING fc_3: Email carol@x.com?
```

Three pending confirmations from one turn. Your UI must render all three and let the user approve them **independently** — see page 08.

> 🛠 **Have the student:** modify the script so the agent emails one address. Confirm only one entry comes back. Then four, then ten — the runtime imposes no upper bound.

## The rule

**`event.actions.requested_tool_confirmations` is your one-stop event surface for pending HITL.** Every client integration in this module reads this dict; they only differ in how they render it and how they collect the response.

> ❓ **Ask the student:** "If two confirmations are pending and the user approves one and rejects the other, what's the shape of the resume payload?" (Two function responses, one with `confirmed=True`, one with `confirmed=False`. Page 04 shows the wire.)

## 🚀 In Production

> **🚀 In Production**
>
> Persist *both* the `invocation_id` (from the event) and the `function_call_id` (from the dict key) when you queue an approval. Anyone presenting both gets to drive the resume. **Bind them to the authenticated user** in your approval store — otherwise a leaked URL trivially impersonates the approver.

---

[← Prev: 02_RequestConfirmation](02_RequestConfirmation.md)  [↑ Map](../../MAP.md)  [Next: 04_RunnerResumeAndCancel →](04_RunnerResumeAndCancel.md)
