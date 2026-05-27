---
module: 4B_HumanInTheLoop
page: 02_RequestConfirmation
title: ctx.request_confirmation() — pausing inside a tool
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/01, 03_Tools/02]
concepts: [request_confirmation, ToolConfirmation, hint, payload, function_call_id]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 01_WhyHITL](01_WhyHITL.md)  [↑ Map](../../MAP.md)  [Next: 03_RequestedToolConfirmations →](03_RequestedToolConfirmations.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 02 Request Confirmation

# 🛠 `ctx.request_confirmation()`

One method on `Context` is the entire HITL primitive for tools.

## The primitive

```python
# inside any FunctionTool
def delete_file(path: str, ctx: Context) -> dict:
    if ctx.tool_confirmation is None or not ctx.tool_confirmation.confirmed:
        ctx.request_confirmation(
            hint=f"Delete {path}? This is permanent.",
            payload={"path": path},
        )
        return {}                          # the return value is ignored on this pass
    # confirmed branch:
    os.remove(path)
    return {"deleted": path}
```

Two halves of the same function:
- **First call**: `ctx.tool_confirmation is None`. The tool calls `ctx.request_confirmation(...)` and the runtime pauses.
- **Resumed call**: `ctx.tool_confirmation` is a `ToolConfirmation(confirmed=True, payload=...)` populated from the client's response. The side-effect runs.

The full lifecycle across processes — client, Runner, tool fn, user — with the session store as the only thing that survives the pause:

[See `_figures/hitl_lifecycle.txt`](_figures/hitl_lifecycle.txt) — annotated timeline of one full pause/resume cycle, plus the three invariants you must keep in mind (tool is called **twice**; pause survives a restart **only** with a durable session backend; resume identity = `invocation_id + function_call_id`, which means anyone holding those IDs can fake-approve unless you bind them to the authenticated user).

## A first, full, runnable example

```python
# Work/4B_02_request_confirmation.py — run with: uv run python Work/4B_02_request_confirmation.py
import asyncio, os, tempfile
from google.adk.agents import LlmAgent, Context
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.apps import ResumabilityConfig
from google.genai import types


def delete_file(path: str, ctx: Context) -> dict:
    """Delete a file at `path`. Asks the user first."""
    if ctx.tool_confirmation is None or not ctx.tool_confirmation.confirmed:
        ctx.request_confirmation(
            hint=f"Delete {path}? This is permanent.",
            payload={"path": path},
        )
        return {}
    if not ctx.tool_confirmation.confirmed:
        return {"deleted": False, "reason": "user rejected"}
    os.remove(path)
    return {"deleted": True, "path": path}


agent = LlmAgent(
    name="janitor",
    model="gemini-2.5-flash",
    instruction="Delete the file the user names. Use the delete_file tool.",
    tools=[delete_file],
)

app = App(
    name="janitor_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)


async def main():
    # Make a real file to (maybe) delete.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp.write(b"throwaway\n"); tmp.close()
    print(f"Created {tmp.name}")

    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name="janitor_app", user_id="u1"
    )

    first_msg = types.Content(role="user", parts=[types.Part(text=f"Delete {tmp.name}")])
    pending_confirmation_fc_id = None

    async for event in runner.run_async(
        user_id="u1", session_id=session.id, new_message=first_msg
    ):
        for fc_id, conf in event.actions.requested_tool_confirmations.items():
            print(f"PAUSED: function_call_id={fc_id} hint={conf.hint!r}")
            pending_confirmation_fc_id = fc_id
            print(f"        payload={conf.payload}")

    print(f"After first run: file still exists? {os.path.exists(tmp.name)}")
    # → True — the runtime paused before executing the side effect.


asyncio.run(main())
```

```
$ uv run python Work/4B_02_request_confirmation.py
Created /tmp/tmpXXXXXX.txt
PAUSED: function_call_id=fc_1 hint='Delete /tmp/tmpXXXXXX.txt? This is permanent.'
        payload={'path': '/tmp/tmpXXXXXX.txt'}
After first run: file still exists? True
```

The file survives. The agent paused. Page 03 explains the **event** we're reading off; page 04 shows how to *resume* it with an approval.

> 🛠 **Have the student run:** the snippet above. They should see "file still exists? True". If the file got deleted, `ctx.request_confirmation` is being skipped — most likely they forgot the `if ctx.tool_confirmation is None` guard.

## Anatomy of `ToolConfirmation`

```python
class ToolConfirmation(BaseModel):
    hint: str = ""              # human-readable: shown in the approval UI
    confirmed: bool = False     # client flips this to True/False on resume
    payload: Optional[Any] = None  # round-trip JSON the client may modify
```

Three fields, three uses:
- `hint` is for the **human** — render it in the UI.
- `confirmed` is for **your code** — branch on it.
- `payload` is the **carrier** — useful for two patterns:
  1. **Echo-back**: the tool sends the proposed args; the client returns them unchanged after approval. Simple audit story.
  2. **Edit-on-approve**: the client modifies the payload (e.g., user changes "$1200" to "$1000"); the tool reads the modified payload on resume.

## ⚠️ The function-call-id requirement

`ctx.request_confirmation()` raises `ValueError` if `ctx.function_call_id` is unset. Translation: **you can only call it from inside a tool**, not from `before_agent_callback`, not from a graph function node, not from an `LlmAgent.instruction`. For graph-node HITL, use `RequestInput` (page 06).

> ❓ **Ask the student:** "Why is the tool function called twice — once to pause, once to act?" (Because the same function body has to handle both halves; ADK does not split it for you. The `if ctx.tool_confirmation is None` branch is your "pause arm".)

## 🚀 In Production

> **🚀 In Production**
>
> Do **any** side-effect work in the pre-confirm branch and you have shipped a vulnerability — the user can trigger an unwanted action just by mentioning it, then refuse to approve. Audit rule: in the `ctx.tool_confirmation is None` branch, write only the `request_confirmation` call and a bare `return {}`. Reviewers should reject PRs that violate this.

---

[← Prev: 01_WhyHITL](01_WhyHITL.md)  [↑ Map](../../MAP.md)  [Next: 03_RequestedToolConfirmations →](03_RequestedToolConfirmations.md)
