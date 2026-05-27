---
module: 07_Callbacks
page: 05_CallbackContextAnatomy
title: CallbackContext anatomy — what's there, what isn't, common gotchas
estimated_minutes: 20
prereqs: [07_Callbacks/04]
concepts: [CallbackContext, ToolContext, state, invocation_id, agent_name, save_artifact]
icon: 🧠
in_production: true
detours_suggested: [Detours/PY_contextvars]
---

[← Prev: 07_Callbacks/04_BeforeAfterAgent](04_BeforeAfterAgent.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/06_CallbackRecipeCookbook →](06_CallbackRecipeCookbook.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 05 CallbackContext anatomy

# 🧠 What's actually in `CallbackContext`?

Every callback (except `*_tool_*` which use `ToolContext`) receives one. You've used `.state` extensively. Here's the full surface, what's mutable, and what isn't.

## 🧠 The fields you'll use most

```python
# Work/05_cbctx_probe.py — run with: uv run python Work/05_cbctx_probe.py
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio


def probe(ctx: CallbackContext):
    print(f"  invocation_id={ctx.invocation_id}")
    print(f"  agent_name={ctx.agent_name}")
    print(f"  user_id={ctx.user_id}")
    print(f"  session_id={ctx.session.id}")   # access the id via ctx.session — there is no shortcut attribute on ctx itself
    print(f"  state keys={list(ctx.state.keys())}")
    return None


agent = Agent(
    name="probe_agent", model="gemini-2.5-flash",
    instruction="Say hi.",
    before_agent_callback=probe,
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="probe_app")
    sess = await runner.session_service.create_session(
        app_name="probe_app", user_id="u-42", state={"seed": 1},
    )
    async for _ in runner.run_async(
        user_id="u-42", session_id=sess.id,
        new_message=types.Content(role="user", parts=[types.Part(text="hi")]),
    ):
        pass


asyncio.run(main())
```

```
$ uv run python Work/05_cbctx_probe.py
  invocation_id=e-…       # a uuid4
  agent_name=probe_agent
  user_id=u-42
  session_id=…             # ctx.session.id — also a uuid4
  state keys=['seed']
```

## 🧠 The complete surface

| Attribute | Read | Mutate | Notes |
|---|---|---|---|
| `state` | ✅ | ✅ via assignment | The state dict — same view your tools see. Writes become `state_delta` events. |
| `user_id` | ✅ | ❌ | Owner of this conversation. Stable across the session. |
| `session` | ✅ | ❌ | The `Session` object — `ctx.session.id` for the session id, `ctx.session.events` for history (read-only). There is **no** top-level shortcut attribute; always go through `.session`. |
| `invocation_id` | ✅ | ❌ | One per `run_async()` call. New invocation = new id even for the same session. |
| `agent_name` | ✅ | ❌ | The agent currently executing — important in sub-agent trees. |
| `_invocation_context` | ✅ | ❌ (private) | Deeper handle for advanced patterns; use sparingly. |
| `save_artifact(name, part)` | — | `async` call | Persist a binary or text Part. Returns version int. |
| `load_artifact(name, version=None)` | — | `async` call | Read back. |
| `list_artifacts()` | — | `async` call | List names in scope. |

## ⚠️ What is NOT here

* **No direct access to `events`.** You can't read the conversation history through `CallbackContext`. If you need it, the surface is on `_invocation_context.session.events` (private; expect breakage).
* **No `tool` reference.** That's `ToolContext`'s job (page 03).
* **No `LlmRequest` / `LlmResponse`.** Those are passed as separate args to the model callbacks.
* **No write to `user_id` or `session.id`** — these identify the conversation; mutating them is meaningless.

## 🧠 `ToolContext` and `CallbackContext` are the SAME class

```python
from google.adk.tools.tool_context import ToolContext

def my_tool_cb(tool, args, tool_context: ToolContext):
    # exact same surface as CallbackContext — they are aliases of one class:
    print(tool_context.function_call_id)   # the LLM's call id for this tool invocation
    print(tool_context.actions)            # mutable EventActions for this turn
    return None
```

`ToolContext` is **not** a subclass of `CallbackContext` — both names are aliases for `google.adk.agents.context.Context` (`tools/tool_context.py:29` says `ToolContext = Context`; `agents/callback_context.py:22` says `CallbackContext = Context`). The names exist for self-documenting parameter types; the surface is identical. That means `function_call_id` and `actions` are technically present on every `CallbackContext` too — they're just only populated/meaningful inside a tool callback.

> 🧭 Curious how ADK propagates context through async calls? Detour [[Detours/PY_contextvars]] explains the Python primitive — back in ~10 min.

## ⚠️ Mutation gotchas (the four that keep biting people)

1. **Reassign, don't mutate.** `ctx.state["cart"].append(x)` may be missed by the delta tracker. Read, copy, modify the copy, write the copy back.
2. **`temp:` is dropped at end of invocation.** Don't `ctx.state["temp:budget"] = 100` in `before_agent_callback` of a parent and expect a sub-agent's later invocation to see it. `temp:` is per-invocation; sub-agent entries are fresh invocations in the callback sense.
3. **Writes from `before_model_callback` are queued.** The state change shows up on the next event, not synchronously inside the callback. If you read back `ctx.state["x"]` after writing it in the same callback, you'll see the new value (it's in the local dict) — but **other concurrent observers** won't until the event lands.
4. **Artifact calls are `async`.** `await ctx.save_artifact(...)` — forgetting `await` returns a coroutine, not a version int. Lint your callbacks with `mypy --strict` or you'll ship this bug.

## 🧠 The `invocation_id` is your tracing key

If you log one thing per callback, log `invocation_id`. It is the only id that joins:

- the LLM call's request/response,
- every tool call within the loop,
- the agent's events,
- the trace spans your OpenTelemetry plugin (Module 15) emits.

A single user turn = a single invocation_id. Log it; you'll thank yourself.

## ❓ Quiz

> ❓ **Ask the student:** in a parent → child sub-agent tree, the parent's `before_agent_callback` writes `ctx.state["temp:flag"] = True`. The child's `before_agent_callback` reads `ctx.state.get("temp:flag")`. What does it see?
> *(Expected: `None`. `temp:` state is scoped to the invocation. The child's entry is a new invocation in the callback sense — the `temp:` keys don't carry over. Use no-prefix or `app:` state if you want it to survive the sub-agent hop.)*

> 🛠 **Have the student run:** the probe script above, then add `before_model_callback` and `after_tool_callback` that also print `ctx.invocation_id` and confirm the id is the same across all three for one user turn.

> **🚀 In Production**
>
> Treat `_invocation_context` as private. If you reach into `_invocation_context.session.events`, your code will break on a minor ADK upgrade. If you need history, register a `before_model_callback` that captures `llm_request.contents` instead — that's the supported surface.

[← Prev: 07_Callbacks/04_BeforeAfterAgent](04_BeforeAfterAgent.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/06_CallbackRecipeCookbook →](06_CallbackRecipeCookbook.md)
