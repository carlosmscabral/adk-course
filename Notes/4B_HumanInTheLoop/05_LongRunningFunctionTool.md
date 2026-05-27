---
module: 4B_HumanInTheLoop
page: 05_LongRunningFunctionTool
title: LongRunningFunctionTool — pause for an external system (which may be a human)
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/04, 03_Tools/06]
concepts: [LongRunningFunctionTool, external-completion, polling, webhook]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_RunnerResumeAndCancel](04_RunnerResumeAndCancel.md)  [↑ Map](../../MAP.md)  [Next: 06_RequestInputInGraphs →](06_RequestInputInGraphs.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 05 Long-Running Tool

# 🛠 `LongRunningFunctionTool` as a HITL primitive

`request_confirmation` is a tight pause: the runtime knows it's a pause, knows it has to surface a UI prompt, knows the resume payload is a `ToolConfirmation`. **`LongRunningFunctionTool` is a looser pause**: it says "this tool will *eventually* return, the result is going to come from somewhere outside the agent process — wake me when it lands."

That "somewhere outside" can be a Cloud Build run finishing, an OCR job completing — or **a human clicking approve in their own time**. Same primitive, more general.

## The shape

```python
from google.adk.tools import LongRunningFunctionTool


def submit_for_legal_review(doc_id: str) -> dict:
    """Submit `doc_id` to the legal queue. Returns a ticket id; the
    review verdict will arrive later as a separate function response."""
    ticket = legal_queue.enqueue(doc_id)
    return {"ticket": ticket, "status": "pending"}


review_tool = LongRunningFunctionTool(func=submit_for_legal_review)
```

When the agent calls `submit_for_legal_review`, the tool returns immediately with `{"status": "pending"}`. The LLM is told "this is a long-running tool; the real answer is not back yet." The invocation suspends.

Later — minutes, hours, days — your external system calls back into the runner with a `function_response` carrying the final verdict, using the same `(invocation_id, function_call_id)` pattern you learned in page 04.

## Why use this instead of `request_confirmation`?

The two have different mental models:

| Primitive | Who completes it | Payload shape | Best for |
|---|---|---|---|
| `ctx.request_confirmation` | A human, *via your UI* | `ToolConfirmation(confirmed: bool)` | Approve / reject of an agent-proposed action |
| `LongRunningFunctionTool` | An external system (which can be a human) | Any function return-value shape you define | Tickets, OCR jobs, build pipelines, legal review, anything async |

The `request_confirmation` flow is *opinionated* — the runtime knows it's an approval and renders accordingly in `adk web`. `LongRunningFunctionTool` is *unopinionated* — you decide what the eventual response means.

## Runnable scaffold

```python
# Work/4B_05_long_running.py — manually drive the resume with a fake "verdict".
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import LongRunningFunctionTool
from google.adk.apps.app import App
from google.adk.apps._configs import ResumabilityConfig
from google.genai import types


def submit_for_legal_review(doc_id: str) -> dict:
    """Submit `doc_id` to legal; result arrives later."""
    # In real life: enqueue to a queue, return a ticket id.
    return {"ticket": f"LEGAL-{doc_id}", "status": "pending"}


review_tool = LongRunningFunctionTool(func=submit_for_legal_review)

agent = LlmAgent(
    name="contract_filer", model="gemini-2.5-flash",
    instruction=(
        "When the user asks to file a contract, call submit_for_legal_review "
        "with the doc id. Tell the user it's pending."
    ),
    tools=[review_tool],
)
app = App(name="filer", root_agent=agent,
          resumability_config=ResumabilityConfig(is_resumable=True))


async def main():
    runner = InMemoryRunner(app=app)
    sess = await runner.session_service.create_session(app_name="filer", user_id="u1")

    pending_invocation_id, pending_fc_id = None, None
    async for event in runner.run_async(
        user_id="u1", session_id=sess.id,
        new_message=types.Content(role="user",
            parts=[types.Part(text="File contract DOC-42 for legal review.")]),
    ):
        for fc in (event.content.parts if event.content else []):
            if fc.function_call and fc.function_call.name == "submit_for_legal_review":
                pending_invocation_id = event.invocation_id
                pending_fc_id = fc.function_call.id
                print(f"submitted; ticket pending: invocation={pending_invocation_id}")

    # ... days pass; legal team approves; we resume with the verdict ...
    verdict_msg = types.Content(role="user", parts=[types.Part(
        function_response=types.FunctionResponse(
            id=pending_fc_id,
            name="submit_for_legal_review",
            response={"ticket": "LEGAL-DOC-42", "status": "approved",
                      "reviewer": "alice@legal.example"},
        )
    )])
    async for event in runner.run_async(
        user_id="u1", session_id=sess.id,
        invocation_id=pending_invocation_id,
        new_message=verdict_msg,
    ):
        for p in (event.content.parts if event.content else []):
            if p.text: print("AGENT:", p.text)


asyncio.run(main())
```

```
$ uv run python Work/4B_05_long_running.py
submitted; ticket pending: invocation=inv_...
AGENT: Legal review approved by alice@legal.example. Filing DOC-42.
```

> 🛠 **Have the student run:** the script, then modify the verdict to `{"status": "rejected", "reason": "missing signature"}`. Observe the agent's final-text changes accordingly — proving the verdict really does flow through.

## Composition with `request_confirmation`

You can use both in the same agent. A common pattern:
1. `request_confirmation` to approve **starting** a long job ("Run this $200 Vertex training? Yes / No.").
2. `LongRunningFunctionTool` to wait for the **job to finish**.

Two pauses, two different surfaces — both are HITL.

> ❓ **Ask the student:** "Could `request_confirmation` be built on top of `LongRunningFunctionTool`? Why does ADK ship both?" (Yes, in principle — but the approval flow is so common that ADK gives it the opinionated short-cut: `ToolConfirmation` payload type, `adk_request_confirmation` reserved name, frontend renderer in `adk web`. You're paying a few KB for ergonomics.)

## 🚀 In Production

> **🚀 In Production**
>
> Long-pauses run into **state-store TTLs**: if your session backend (Firestore, Postgres) prunes rows after N days, your pending invocation silently vanishes. Two mitigations: (1) raise the TTL on the table where ADK persists sessions; (2) implement an idle-job sweeper that reads pending invocations older than N hours and either re-notifies or abandons them (don't resume, append a terminal event — page 04 covers the pattern, since there is no `runner.cancel()`). See also [10_DurableExecutionIntegrations](10_DurableExecutionIntegrations.md) — for pauses measured in days, Temporal/Dapr usually win.

---

[← Prev: 04_RunnerResumeAndCancel](04_RunnerResumeAndCancel.md)  [↑ Map](../../MAP.md)  [Next: 06_RequestInputInGraphs →](06_RequestInputInGraphs.md)
