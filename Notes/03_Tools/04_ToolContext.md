---
module: 03_Tools
page: 04_ToolContext
title: ToolContext — tools can see (and change) state
estimated_minutes: 20
prereqs: [03_Tools/03]
concepts: [ToolContext, state, escalate, artifact]
icon: 🛠
in_production: true
detours_suggested: [Detours/PY_contextvars]
---

[← Prev: 03_Tools/03_DocstringAsSchema](03_DocstringAsSchema.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/05_BuiltInTools →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 04 ToolContext

# 🛠 `ToolContext`

If your tool needs to read or write the **session state**, add an optional `tool_context: ToolContext` parameter. ADK injects the context at call time. **The LLM does not see it** — it's absent from the JSON schema.

> 🧭 Curious how ADK propagates context through async calls? Detour [[Detours/PY_contextvars]] explains the Python primitive — back in ~10 min.

```python
from google.adk.tools import ToolContext


def remember(name: str, tool_context: ToolContext) -> str:
    """Save the user's preferred name.

    Args:
        name: The name the user wants to be called by.
    """
    tool_context.state["user:name"] = name
    return f"Got it, {name}."
```

Notice:
* `name` IS in the schema (the LLM passes it).
* `tool_context` is NOT in the schema (ADK injects it).

## 🛠 What `tool_context` exposes

```python
def my_tool(query: str, tool_context: ToolContext) -> str:
    """..."""
    # read state
    cached = tool_context.state.get("temp:cache", {}).get(query)

    # write state — becomes a state_delta on this tool's result event
    tool_context.state["temp:last_query"] = query

    # signal early-exit of the agent loop (covered in Module 07)
    tool_context.actions.escalate = True

    # access artifact service (files/blobs — Module 11)
    # await tool_context.save_artifact(filename="...", artifact=...)

    return "..."
```

The big four are:
* `tool_context.state` — read/write the session's state dict.
* `tool_context.actions.escalate` — bubble up an early termination signal.
* `tool_context.actions.transfer_to_agent` — hand control to a sibling agent (Module 05).
* `tool_context.save_artifact(...)` — store a binary blob the agent can reference later (Module 11).

For Foundation Track you mostly use `tool_context.state`.

## 🛠 Read state from inside a tool

```python
# Work/04_whoami_tool.py — run with: uv run python Work/04_whoami_tool.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


def whoami(tool_context: ToolContext) -> str:
    """Return the user's saved name, or 'stranger' if unknown."""
    return tool_context.state.get("user:name", "stranger")


agent = LlmAgent(
    name="who", model="gemini-2.5-flash",
    instruction="When asked who the user is, call whoami() and report the result verbatim.",
    tools=[whoami],
)

async def main():
    ss = InMemorySessionService()
    session = await ss.create_session(
        app_name="x", user_id="u", session_id="s",
        state={"user:name": "Carlos"},          # pre-seed
    )
    runner = Runner(app_name="x", agent=agent, session_service=ss)
    async for event in runner.run_async(
        user_id="u", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text="Who am I?")]),
    ):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)

asyncio.run(main())
```

```text
Carlos
```

This tool takes NO arguments from the LLM — its only parameter is `tool_context`, which the LLM never sees. From the LLM's view, `whoami()` is a zero-argument tool that returns a string. Useful pattern for "read-only" tools.

## ⚠️ Mutations are deltas

When you write `tool_context.state["x"] = y`, the change is captured as a `state_delta` and attached to the **event** that wraps this tool's return. It's only visible to the agent on the *next* iteration of the loop. Don't expect a fresh read-back inside the same tool call to reflect changes mid-execution.

## ❓ Quiz

> ❓ **Ask the student:** Gemini's tool call has signature `remember(name="Carlos")`. Why doesn't the LLM pass `tool_context=…`?
> *(Expected: because `tool_context` is special — ADK detects the parameter type `ToolContext` and injects it server-side. The schema sent to Gemini omits it. The LLM never knows it exists.)*

> 🛠 **Have the student do this:** write a tiny `Work/state_peek.py` agent with one tool `peek()` that returns `repr(tool_context.state)`. Run it through a `Runner` and ask the agent "what's in state?" — they should see an empty dict (or whatever you pre-seeded). This reinforces that state is a real Python dict, accessible from tools.

> **🚀 In Production**
>
> Tools can mutate state. Tools can mutate state from inside a partial-failure handler. State changes ARE persisted in the event log. **Never use state for transient retry counters that should be reset between turns** — use `temp:` prefix (gone after this invocation) instead of bare keys (persisted to the end of the session). Foot-gun: forgetting the prefix and ending up with stale state outliving its purpose.

---

[← Prev: 03_Tools/03_DocstringAsSchema](03_DocstringAsSchema.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/05_BuiltInTools →]
