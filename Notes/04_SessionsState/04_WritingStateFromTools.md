---
module: 04_SessionsState
page: 04_WritingStateFromTools
title: Writing state from a tool
estimated_minutes: 15
prereqs: [04_SessionsState/03]
concepts: [tool_context, state_delta, event-actions]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/03_ReadingStateInPrompts](03_ReadingStateInPrompts.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/05_ContextCaching →](05_ContextCaching.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 04 Writing state from tools

# 🛠 Writing state from a tool

You met `ToolContext` on Module 03 page 04. Here's how the writes flow into the session.

```python
from google.adk.tools import ToolContext


def remember_name(name: str, tool_context: ToolContext) -> str:
    """Save the user's preferred name for future sessions.

    Args:
        name: The name the user wants to be called.
    """
    tool_context.state["user:name"] = name
    return f"Got it — I'll call you {name} from now on."
```

## 🧠 What ADK does on that assignment

It does NOT directly mutate the Session's state dict. Instead:

1. The assignment is **recorded** on the `tool_context` object.
2. When the tool returns, ADK packages the tool result as an `Event(content=function_response, actions=EventActions(state_delta={"user:name": "Carlos"}))`.
3. The Runner appends this Event to the Session and applies the delta to the appropriate scope (here: `user_state`, because of the `user:` prefix).
4. Next iteration's LLM call sees the new value when ADK rebuilds the state view.

```
{{INCLUDE _figures/state_flow.txt}}
```

## 🛠 Trace it

```python
# Work/04_state_from_tool.py — run with: uv run python Work/04_state_from_tool.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


def remember_name(name: str, tool_context: ToolContext) -> str:
    """Save the user's preferred name for future sessions.

    Args:
        name: The name the user wants to be called.
    """
    tool_context.state["user:name"] = name
    return f"Got it — I'll call you {name} from now on."


agent = LlmAgent(
    name="memory", model="gemini-2.5-flash",
    instruction="If the user gives you their name, call remember_name.",
    tools=[remember_name],
)

async def main():
    ss = InMemorySessionService()
    session = await ss.create_session(app_name="x", user_id="u", session_id="s")
    runner = Runner(app_name="x", agent=agent, session_service=ss)
    async for event in runner.run_async(
        user_id="u", session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Call me Carlos.")],
        ),
    ):
        if event.actions and event.actions.state_delta:
            print("STATE_DELTA:", event.actions.state_delta)
        if event.is_final_response() and event.content:
            print("REPLY:", event.content.parts[0].text)

asyncio.run(main())
```

```text
STATE_DELTA: {'user:name': 'Carlos'}
REPLY: Got it — I'll call you Carlos from now on.
```

Every state mutation is visible in the event stream. That's why observability is cheap (Module 15) — you don't have to instrument writes; they're already events.

## ⚠️ Single-tool-call atomicity

State deltas land **after** the tool returns. If your tool reads, computes, and writes, that's fine — but if you read again *later in the same tool call* you're reading the pre-write value. Within one Python function, normal local variables work as you'd expect; we're talking about the Session's state, which is "as of the last applied delta."

## ⚠️ Mutating containers

```python
# WRONG — mutates in place, but ADK's delta tracking may miss it
tool_context.state["cart"].append({"sku": "abc"})

# RIGHT — reassign the whole list
cart = list(tool_context.state.get("cart", []))
cart.append({"sku": "abc"})
tool_context.state["cart"] = cart
```

Treat state values as immutable. **Read, modify a copy, write the copy back.**

## ❓ Quiz

> ❓ **Ask the student:** in the trace above, why does the `STATE_DELTA` event appear BEFORE the `REPLY` event?
> *(Expected: the state write happens in the tool's result event, which the Runner emits before the agent's follow-up text reply. Two separate events; state-delta is on the tool-result one, the agent's reply is a subsequent event.)*

> 🛠 **Have the student run:** the script above with their own tool that writes `state["user:name"]`. Confirm they see the `state_delta` event. Then call `runner.run_async` a SECOND time inside the same `main()` (same session) with a different question, and confirm the new state is visible via a `{user:name}` prompt template (page 03).

> **🚀 In Production**
>
> Tools that fail partway through can leave state in an inconsistent place. If your tool writes multiple keys, do all writes at the END after all computation succeeded — or wrap with a try/except and explicitly roll back. ADK doesn't transactionally roll back state on tool errors; the deltas applied so far stick.

---

[← Prev: 04_SessionsState/03_ReadingStateInPrompts](03_ReadingStateInPrompts.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/05_ContextCaching →](05_ContextCaching.md)
