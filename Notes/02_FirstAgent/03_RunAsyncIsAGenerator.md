---
module: 02_FirstAgent
page: 03_RunAsyncIsAGenerator
title: run_async returns an async generator
estimated_minutes: 20
prereqs: [02_FirstAgent/02]
concepts: [run_async, async-generator, Event, is_final_response]
icon: 🛠
in_production: false
detours_suggested: [PY_async, PY_generators]
---

[← Prev: 02_FirstAgent/02_RunnerAndSession](02_RunnerAndSession.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/04_TheGeminiPayload →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 03 `run_async` is a generator

# 🛠 `runner.run_async(...)` returns an **async generator**

This is the heart of ADK. Once you understand this one line, everything else is shapes around it.

```python
async for event in runner.run_async(user_id=..., session_id=..., new_message=...):
    ...
```

## 🛠 First end-to-end run

Write this to `Work/first_run.py`:

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "hello"
USER_ID = "carlos"
SESSION_ID = "s1"


async def main() -> None:
    agent = LlmAgent(
        name="greeter",
        model="gemini-2.5-flash",
        instruction="Reply in exactly one sentence. Be friendly.",
        description="Greets the user.",
    )
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID,
    )
    runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

    user_msg = types.Content(role="user", parts=[types.Part(text="say hi")])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_msg,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

> 🛠 **Have the student run:**
> ```bash
> $ python Work/first_run.py
> Hi there — happy to chat!
> ```
> (Output varies — Gemini is non-deterministic. As long as text appears, the wiring works.)

## 🧠 What `run_async` yields

Each `event` is an `Event` object with at minimum:

* `event.author` — the agent name (`"greeter"`).
* `event.content` — a `types.Content` (or None for some bookkeeping events).
* `event.actions` — `state_delta`, `transfer_to_agent`, etc. Mostly empty in single-agent apps.
* `event.is_final_response()` — a helper that returns True when this event represents the agent's *final* reply for the current invocation.

For now, **filter on `event.is_final_response()` and grab the text**. We'll explore the other event types in Modules 04, 05, and 07.

## 🛠 Extracting text safely

```python
if event.is_final_response() and event.content and event.content.parts:
    text = event.content.parts[0].text
```

The guards (`event.content and event.content.parts`) are not paranoia — partial events legitimately have `content=None` or empty parts. **Always guard.** Module 18 (streaming) deepens this.

## ❓ Why an async generator instead of a list?

> ❓ **Ask the student:** why does `run_async` yield events as they arrive instead of returning a `list[Event]` at the end?
> *(Expected: streaming. Long tool calls or model thinking can take seconds — yielding lets the UI show intermediate progress. Also lets you cancel the loop early, e.g. when the user hits stop.)*

## 🧭 Detour pointer

If `async for` feels uncomfortable, take detour [[PY_async]] (~30 min) before continuing. ADK is async-first; you'll see this pattern in every module from here forward.

> **🚀 In Production**
>
> Always handle the case where `is_final_response()` never fires — e.g., the model errored, your `max_iterations` cap hit, or the connection dropped. Wrap the `async for` in a `try` with a timeout, and log when the loop exits without a final response. (Module 15 has the observability patterns.)

---

[← Prev: 02_FirstAgent/02_RunnerAndSession](02_RunnerAndSession.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/04_TheGeminiPayload →]
