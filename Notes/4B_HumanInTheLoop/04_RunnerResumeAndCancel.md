---
module: 4B_HumanInTheLoop
page: 04_RunnerResumeAndCancel
title: Resume and cancel — runner.run_async(invocation_id=...) and the dual
estimated_minutes: 30
prereqs: [4B_HumanInTheLoop/03, 1A_AppAndRunner/02]
concepts: [resume, invocation_id, ResumabilityConfig, function_response, cancel, at-least-once]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 03_RequestedToolConfirmations](03_RequestedToolConfirmations.md)  [↑ Map](../../MAP.md)  [Next: 05_LongRunningFunctionTool →](05_LongRunningFunctionTool.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 04 Resume & Cancel

# 🛠 Resume an invocation

A paused invocation isn't a new method — it's the same `runner.run_async()` you already call, with two changes:

1. Pass `invocation_id=<the id from the pause event>`.
2. Pass `new_message=<function_response>` instead of a user content.

## The resume call, end to end

```python
# Work/4B_04_resume.py — uses the same `agent`/`app` from page 02
import asyncio, json, os, tempfile
from google.adk.agents import LlmAgent, Context
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.apps._configs import ResumabilityConfig
from google.adk.tools.tool_confirmation import ToolConfirmation
from google.adk.flows.llm_flows.functions import REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
from google.genai import types


def delete_file(path: str, ctx: Context) -> dict:
    if ctx.tool_confirmation is None or not ctx.tool_confirmation.confirmed:
        ctx.request_confirmation(hint=f"Delete {path}?", payload={"path": path})
        return {}
    os.remove(path); return {"deleted": True, "path": path}


agent = LlmAgent(
    name="janitor", model="gemini-2.5-flash",
    instruction="Delete the file the user names.", tools=[delete_file])
app = App(name="janitor", root_agent=agent,
          resumability_config=ResumabilityConfig(is_resumable=True))


async def main():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp.write(b"x"); tmp.close()

    runner = InMemoryRunner(app=app)
    sess = await runner.session_service.create_session(app_name="janitor", user_id="u1")

    # --- Turn 1: pause -----------------------------------------------------
    pending_invocation_id, pending_fc_id = None, None
    async for event in runner.run_async(
        user_id="u1", session_id=sess.id,
        new_message=types.Content(role="user",
                                  parts=[types.Part(text=f"Delete {tmp.name}")]),
    ):
        for fc_id in event.actions.requested_tool_confirmations:
            pending_invocation_id = event.invocation_id
            pending_fc_id = fc_id

    assert os.path.exists(tmp.name), "file should still exist — paused, not yet deleted"

    # --- Build the resume message: a function_response with the approval ---
    approval = ToolConfirmation(confirmed=True, payload={"path": tmp.name})
    resume_msg = types.Content(role="user", parts=[types.Part(
        function_response=types.FunctionResponse(
            id=pending_fc_id,
            name=REQUEST_CONFIRMATION_FUNCTION_CALL_NAME,   # "adk_request_confirmation"
            response=approval.model_dump(by_alias=True),
        )
    )])

    # --- Turn 2: resume ----------------------------------------------------
    async for event in runner.run_async(
        user_id="u1", session_id=sess.id,
        invocation_id=pending_invocation_id,
        new_message=resume_msg,
    ):
        for part in (event.content.parts if event.content else []):
            if part.text: print("AGENT:", part.text)

    assert not os.path.exists(tmp.name), "file should be gone after approval"
    print("DELETED.")


asyncio.run(main())
```

Three load-bearing details:

1. `invocation_id=` is **not optional** on resume. Drop it and the runtime starts a fresh invocation instead.
2. The `function_response.name` must be exactly `adk_request_confirmation` (imported from `google.adk.flows.llm_flows.functions` as `REQUEST_CONFIRMATION_FUNCTION_CALL_NAME`). The runtime keys off this name to route the response to the paused tool.
3. The `function_response.id` is the same `function_call_id` the pause event handed you. Different id → the runtime can't match the response back.

> 🛠 **Have the student run:** the script. They should see "DELETED." and the temp file should be gone. If "DELETED." prints but the file is still there, the resume didn't reach the confirmed branch — usually a typo in `name=...`.

## The reject path

To reject, pass `ToolConfirmation(confirmed=False, ...)`. The tool body will run with `ctx.tool_confirmation.confirmed == False`. Return a polite "not done" object; the LLM summarizes it back to the user.

## `App.resumability_config` is the gate

```python
App(name="...", root_agent=..., resumability_config=ResumabilityConfig(is_resumable=True))
```

Without `is_resumable=True`, the runtime won't store the checkpoint and `invocation_id=` on resume raises. This is wired in the **App container** ([1A_AppAndRunner/04_ResumabilityConfig](../1A_AppAndRunner/04_ResumabilityConfig.md)) — we re-state it here so the surface is in one place.

## Cancel

`runner.cancel(invocation_id)` is the dual: it tears down a paused invocation without resuming it. Use it for:
- **Timeout**: an approval queued 7 days ago that no one acted on.
- **User abandon**: chat session closed, no approver still online.
- **Admin override**: ops needs to drain the queue before a deploy.

```python
await runner.cancel(invocation_id=pending_invocation_id)
```

A cancelled invocation cannot be resumed — the checkpoint is removed. The session itself survives.

## ⚠️ Semantics — at-least-once on resume

From the framework's `ResumabilityConfig` docstring:

> ADK resumes the invocation in a best-effort manner:
> 1. Tool calls to resume need to be **idempotent** — we only guarantee at-least-once.
> 2. Any temporary / in-memory state will be lost upon resumption.

Translation: a tool can resume twice if the first resume crashes after the side effect but before the runtime persists the function-response event. Idempotency keys (UUIDs in `payload`) are how you defend.

> ❓ **Ask the student:** "If `delete_file` runs twice, what happens?" (Second `os.remove` raises `FileNotFoundError`. Idempotency = `if os.path.exists(path): os.remove(path)`. The lazy fix; the right fix is a per-action idempotency token in `payload`.)

## 🚀 In Production

> **🚀 In Production**
>
> Three guardrails: **(1)** `App.resumability_config.is_resumable = True` *and* a durable `SessionService` (Database / Sqlite / VertexAi — not `InMemorySessionService`). **(2)** Every side-effecting tool that can be resumed must be idempotent — assume it can run twice. **(3)** Wire a TTL on the pending-confirmation queue and a scheduled `runner.cancel()` job to clean up abandoned approvals. Page 12 has the consolidated checklist.

---

[← Prev: 03_RequestedToolConfirmations](03_RequestedToolConfirmations.md)  [↑ Map](../../MAP.md)  [Next: 05_LongRunningFunctionTool →](05_LongRunningFunctionTool.md)
