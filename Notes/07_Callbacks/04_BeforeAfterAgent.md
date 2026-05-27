---
module: 07_Callbacks
page: 04_BeforeAfterAgent
title: before/after_agent_callback — per-invocation setup and teardown
estimated_minutes: 20
prereqs: [07_Callbacks/03]
concepts: [before_agent_callback, after_agent_callback, CallbackContext, state, artifacts]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 07_Callbacks/03_BeforeAfterTool](03_BeforeAfterTool.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/05_CallbackContextAnatomy →](05_CallbackContextAnatomy.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 04 Before/After Agent

# 🛠 Bracketing the whole agent invocation

`before_agent_callback` runs once when the agent is entered (per invocation, including each entry into a sub-agent). `after_agent_callback` runs once when it exits — even if it errored.

```python
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def before_agent_callback(callback_context: CallbackContext) -> types.Content | None: ...

def after_agent_callback(callback_context: CallbackContext) -> types.Content | None: ...
```

- Return `None`: passthrough.
- Return a `types.Content` from `before_agent_callback`: **skip the agent entirely**, that Content becomes the response.
- Return a `types.Content` from `after_agent_callback`: replace the agent's final output.

## Use case 1 — preload state

```python
def preload_user_profile(callback_context):
    state = callback_context.state
    if "user:profile" not in state:
        state["user:profile"] = load_profile_from_db(state.get("user_id"))
    return None
```

The `user:` prefix puts this in user-scoped state (recap 04). Now every LLM turn in this agent can see the profile through state-templating.

## Use case 2 — auth gate

```python
def require_signed_in(callback_context):
    if not callback_context.state.get("user:auth_token"):
        return types.Content(
            role="model",
            parts=[types.Part(text="Please sign in before using this agent.")],
        )
    return None
```

Cheaper than letting the LLM and tools run and then failing on a 401.

## Use case 3 — persist an artifact on the way out

```python
async def save_summary_artifact(callback_context):
    summary = callback_context.state.get("temp:final_summary")
    if summary:
        await callback_context.save_artifact(
            "summary.md",
            types.Part(text=summary),
        )
    return None
```

`temp:` state is dropped at end of invocation (recap 04), so this is your last chance to materialize it.

## Wiring it up

```python
agent = Agent(
    model="gemini-2.5-flash",
    name="profile_aware",
    instruction="Help the user. Profile: {user:profile}.",
    before_agent_callback=preload_user_profile,
    after_agent_callback=save_summary_artifact,
)
```

## In a sub-agent tree

If `agent` has `sub_agents=[child_a, child_b]`, the `before_agent_callback` on `child_a` runs each time the parent transfers to it, not just once. Use this for **per-child setup** (e.g., load the child's specialized context).

> ❓ **Ask the student:** if you wanted to enforce a 30-second budget on the whole agent (parent + any sub-agents combined), which two callbacks would you wire and on which agent?

> 🚀 **In Production**
>
> `before_agent_callback` is the right place for **resource acquisition** (DB pool, MCP client). Always pair with `after_agent_callback` for cleanup, even on error. If acquisition can fail, return a graceful `Content` rather than letting the exception unwind into a runner crash.

[← Prev: 07_Callbacks/03_BeforeAfterTool](03_BeforeAfterTool.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/05_CallbackContextAnatomy →](05_CallbackContextAnatomy.md)
