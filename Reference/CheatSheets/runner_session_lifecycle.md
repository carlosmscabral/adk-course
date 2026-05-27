# 📋 Cheat Sheet — Runner & Session lifecycle

How one turn flows from `runner.run_async(...)` to a final `Event`. Print this and tape it above your monitor for the Foundation Track.

## ASCII timeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   1. CONSTRUCT once                                                        │
│   ───────────────                                                          │
│                                                                            │
│      session_service = InMemorySessionService()                            │
│      agent = LlmAgent(name=..., model=..., instruction=..., tools=[...])   │
│      runner = Runner(                                                      │
│          app_name="my_app",                                                │
│          agent=agent,                                                      │
│          session_service=session_service,                                  │
│      )                                                                     │
│                                                                            │
│                                                                            │
│   2. CREATE A SESSION (once per user conversation)                         │
│   ─────────────────────────────────────────────                            │
│                                                                            │
│      session = await session_service.create_session(                       │
│          app_name="my_app",                                                │
│          user_id="alice",                                                  │
│          state={"user:name": "Alice"},  # optional seed                    │
│      )                                                                     │
│                                                                            │
│      session.id  → "abc123…"     ← stable for the conversation             │
│      session.state → {"user:name": "Alice"}                                │
│      session.events → []                                                   │
│                                                                            │
│                                                                            │
│   3. ONE TURN — runner.run_async(...) yields Events                        │
│   ─────────────────────────────────────────────────                        │
│                                                                            │
│      user_msg = types.Content(role="user",                                 │
│                               parts=[types.Part(text="Hello")])            │
│                                                                            │
│      async for event in runner.run_async(                                  │
│          user_id="alice",                                                  │
│          session_id=session.id,                                            │
│          new_message=user_msg,    # Optional[types.Content]                │
│          # invocation_id=None,    # set to resume an interrupted run       │
│          # state_delta=None, run_config=None, yield_user_message=False,    │
│      ):                                                                    │
│                                                                            │
│          # Each Event has:                                                 │
│          #   event.author      → "user" | <agent name> | tool name         │
│          #   event.content     → types.Content with parts                  │
│          #   event.actions     → EventActions (state_delta, transfer, …)   │
│          #   event.is_final_response() → True for the last event           │
│                                                                            │
│          if event.is_final_response():                                     │
│              text = event.content.parts[0].text                            │
│                                                                            │
│                                                                            │
│   4. STATE MUTATION (happens inside run_async)                             │
│   ────────────────────────────────────────────                             │
│                                                                            │
│      For each event the runner emits:                                      │
│        – if event.actions.state_delta is non-empty                         │
│        – the runner APPLIES the delta to session.state                     │
│        – and PERSISTS via session_service                                  │
│                                                                            │
│      So by the time the loop exits, session.state is up to date and        │
│      session.events has the full transcript appended.                      │
│                                                                            │
│                                                                            │
│   5. NEXT TURN — reuse the same session.id                                 │
│   ─────────────────────────────────────────                                │
│                                                                            │
│      Just call run_async again with the same session_id. The runner        │
│      loads the session, includes prior events in the LLM context (unless   │
│      include_contents="none" on the agent), and the cycle repeats.         │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Minimal end-to-end (the bare-metal pattern)

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    session_service = InMemorySessionService()
    agent = LlmAgent(name="hello", model="gemini-2.5-flash",
                     instruction="Greet the user.")
    # Modern: pass an App object via `app=` (recommended path per runners.py:209).
    # Legacy (still supported): pass app_name=/agent= separately, as below.
    runner = Runner(app_name="demo", agent=agent,
                    session_service=session_service)

    session = await session_service.create_session(
        app_name="demo", user_id="u1",
    )

    try:
        async for event in runner.run_async(
            user_id="u1",
            session_id=session.id,
            new_message=types.Content(role="user",
                                      parts=[types.Part(text="hi")]),
            # Optional kwargs (defaults shown):
            # invocation_id=None,   # set to resume an interrupted invocation
            # state_delta=None,     # extra state to merge before this turn
            # run_config=None,      # RunConfig overrides
            # yield_user_message=False,
        ):
            if event.is_final_response():
                print(event.content.parts[0].text)
    finally:
        # Walks the agent tree and closes MCP toolsets via _cleanup_toolsets
        # (runners.py:2094-2144). Always wrap run_async in try/finally.
        await runner.close()

asyncio.run(main())
```

## Common confusions

- **`run_async` is an async generator, not a coroutine.** You `async for` it; you do not `await` it once.
- **One call to `run_async` = one user turn**, but emits *many* Events (model-thought, tool-call, tool-result, final). Only the last has `is_final_response() == True`.
- **State writes happen inside the loop**, not after. By the time you exit the `async for`, the session is already updated and persisted.
- **`session_id` must be passed back** on every subsequent call. The Runner does not remember which session you are on between calls — it is stateless across calls.
- **`new_message` is `types.Content`**, not a bare string. `role="user"`, `parts=[types.Part(text=...)]`. See [GeminiPayload detour](../../Notes/Detours/GeminiPayload.md).

## Where it's covered in the course

- Engine-first walk: [Notes/02_FirstAgent/02_RunnerAndSession](../../Notes/02_FirstAgent/02_RunnerAndSession.md), [Notes/02_FirstAgent/03_RunAsyncAndEvents](../../Notes/02_FirstAgent/03_RunAsyncIsAGenerator.md)
- Session services: [Notes/04_SessionsState/01_SessionLifecycle](../../Notes/04_SessionsState/01_SessionVsState.md)
- Event deltas: [Notes/04_SessionsState/03_EventDeltas](../../Notes/04_SessionsState/04_WritingStateFromTools.md)
- Internals trace: [Notes/19_Internals/01_TracingRunAsync](../../Notes/19_Internals/09_DissectingOneCall.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
