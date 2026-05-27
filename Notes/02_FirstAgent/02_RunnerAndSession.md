---
module: 02_FirstAgent
page: 02_RunnerAndSession
title: Runner and InMemorySessionService
estimated_minutes: 20
prereqs: [02_FirstAgent/01]
concepts: [Runner, InMemorySessionService, create_session, app_name, user_id]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 02_FirstAgent/01_LlmAgentByHand](01_LlmAgentByHand.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/03_RunAsyncIsAGenerator →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 02 Runner and Session

# 🛠 `Runner` and `InMemorySessionService`

Two more objects. Then we run.

## 🛠 Create a session service and a session

```python
# Work/02_session_and_runner.py — run with: uv run python Work/02_session_and_runner.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="Reply in exactly one sentence. Be friendly.",
)

async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="hello",
        user_id="carlos",
        session_id="s1",
    )
    print("session.id:", session.id)
    print("session.state:", session.state)

    runner = Runner(
        app_name="hello",
        agent=agent,
        session_service=session_service,
    )
    print("runner.agent.name:", runner.agent.name)

asyncio.run(main())
```

```text
session.id: s1
session.state: {}
runner.agent.name: greeter
```

Three things to notice:

1. `create_session` is **async** — that's the whole framework. We drive it from an `async def main(): ...` and a single top-level `asyncio.run(...)`. Page 03 will pump events through `runner.run_async(...)` from inside the same `main`.
2. The triple `(app_name, user_id, session_id)` is the primary key for a session. Never reuse `session_id` across users.
3. `session.state` is just an empty dict on creation. State gets written via event deltas (Module 04).

## 🛠 What the Runner owns

The Runner now owns:
* A reference to the agent (what to run).
* The session service (where to read/write history).
* Optional `memory_service`, `artifact_service`, `credential_service` (None for now — we'll add them in later modules).

`app_name` on the Runner **must match** the `app_name` you used on `create_session`. Mismatched names = "session not found" errors.

## 🧠 The "by hand" pattern

```
{{INCLUDE _figures/by_hand_vs_cli.txt}}
```

Compare the two columns. The CLI version *is* the by-hand version with `input()` around it. There's no extra framework runtime to learn — `adk run` is the framework.

> ❓ **Ask the student:** if you call `runner.run_async(user_id="carlos", session_id="DOES_NOT_EXIST", ...)`, what happens?
> *(Expected: a `ValueError` — the runner can't find the session. Unless you constructed the Runner with `auto_create_session=True`, in which case it creates one on the fly. Default is `False`.)*

## 🚀 In production: cache the Runner

```python
# top of module, once
_RUNNER = Runner(app_name="hello", agent=agent, session_service=session_service)

async def handle_request(user_id: str, session_id: str, text: str) -> str:
    # ... use _RUNNER, not a fresh Runner
```

Building a Runner per request costs ~200-800ms of cold-start (auth, model spec, plugin init). Build once, reuse forever.

> **🚀 In Production**
>
> `InMemorySessionService` loses everything on process restart. Fine for tests and dev. Anything resembling production gets `DatabaseSessionService(db_url="sqlite:///sessions.db")` at minimum (SQLite file). See [[04_SessionsState/10_PersistentSessions]].

> 🛠 **Have the student run:** the script above. Add two more prints inside `main`: `print(runner.app_name == "hello")` and `print(runner.session_service is session_service)`. Both should be `True` — that's the point. There's no hidden state.

---

[← Prev: 02_FirstAgent/01_LlmAgentByHand](01_LlmAgentByHand.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/03_RunAsyncIsAGenerator →]
