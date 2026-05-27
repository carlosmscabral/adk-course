---
module: 1A_AppAndRunner
page: 02_OnStartupShutdown
title: App lifecycle — on_startup and on_shutdown hooks
estimated_minutes: 20
prereqs: [1A_AppAndRunner/01]
concepts: [lifecycle, startup, shutdown, McpToolset, connection-pool, warm-up]
icon: 🛠
in_production: true
detours_suggested: [PY_async, FastAPI_for_ADK]
---

[← Prev: 01_AppVsRunnerVsAgent](01_AppVsRunnerVsAgent.md)  [↑ Map](../../MAP.md)  [Next: 03_AppStateBoundary →](03_AppStateBoundary.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 02 On Startup / Shutdown

# 🛠 App lifecycle — startup and shutdown hooks

The `App` Pydantic model itself does not (today) expose `on_startup=` / `on_shutdown=` kwargs. **Lifecycle is provided by the runtime that hosts the App** — `adk api_server`, your own FastAPI wrapper, or your own asyncio main. This page shows the canonical wrapping patterns.

> 🤖 **Tutor:** if the student googles "ADK on_startup" and gets confused, this page is the answer. The App is config; the lifecycle hooks live on whatever you wrap the App with. The pattern is borrowed straight from FastAPI / Starlette.

## 🧠 What needs a startup hook?

| Resource | Why it needs startup | Why putting it in `LlmAgent(...)` at import time is wrong |
|---|---|---|
| **MCP server child process** | `McpToolset(stdio_params=...)` spawns a subprocess; you do not want one per request. | Spawning at import time blocks import. Spawning per-request adds ~200ms latency. |
| **Database connection pool** | Opening a pool is async I/O. | Cannot `await` at import time without `asyncio.run` hacks. |
| **Vertex AI client warm-up** | First API call after process start pays ~500ms TLS + auth. | Better to pay it once before the first user request lands. |
| **Loading a large local model** | `LiteLlm(model="gemma-2-9b")` may pull weights. | Should happen before serving begins, not on the hot path. |

The App owns the agent that *uses* these resources. But *initializing* them is a process-lifecycle concern.

## 🛠 Pattern 1 — bare asyncio script

```python
# Work/1A_lifecycle_bare.py — run with: uv run python Work/1A_lifecycle_bare.py
import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


async def on_startup() -> tuple[Runner, InMemorySessionService]:
    """Build the App, open expensive resources, return the live Runner."""
    print("[startup] building agent...")
    agent = LlmAgent(
        name="greeter",
        model="gemini-2.5-flash",
        instruction="Reply in one short sentence.",
    )

    print("[startup] building App...")
    app = App(name="hello_app", root_agent=agent)

    print("[startup] opening session service...")
    session_service = InMemorySessionService()

    print("[startup] building Runner (this pays auth + model spec cost)...")
    runner = Runner(app=app, session_service=session_service)

    print("[startup] ready.")
    return runner, session_service


async def on_shutdown(runner: Runner) -> None:
    """Close pooled resources via the Runner's lifecycle hook.

    `runner.close()` is the public shutdown path (runners.py:2135-2150). It
    closes toolsets, then plugins, then flushes the session_service — i.e.
    the full set of long-lived resources the Runner owns. Prefer it over
    poking individual subsystems like `runner.plugin_manager.close()`.
    """
    print("[shutdown] closing runner (toolsets + plugins + session flush)...")
    await runner.close()
    print("[shutdown] done.")


async def main() -> None:
    runner, session_service = await on_startup()
    try:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name="hello_app", user_id="carlos", session_id=session_id,
        )
        msg = types.Content(role="user", parts=[types.Part(text="hi")])
        async for ev in runner.run_async(
            user_id="carlos", session_id=session_id, new_message=msg,
        ):
            if ev.is_final_response() and ev.content and ev.content.parts:
                print(ev.content.parts[0].text)
    finally:
        await on_shutdown(runner)


if __name__ == "__main__":
    asyncio.run(main())
```

```
$ uv run python Work/1A_lifecycle_bare.py
[startup] building agent...
[startup] building App...
[startup] opening session service...
[startup] building Runner (this pays auth + model spec cost)...
[startup] ready.
Hi! How can I help you today?
[shutdown] closing plugins...
[shutdown] done.
```

The `try`/`finally` is the lifecycle. `on_startup()` is just "what runs before the first user request." `on_shutdown()` is "what runs after the last." Nothing magic.

## 🛠 Pattern 2 — FastAPI lifespan

In a real service you host with FastAPI. The framework gives you `@asynccontextmanager`-shaped lifespan.

```python
# Work/1A_lifecycle_fastapi.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

_RUNNER: Runner | None = None
_SESSION_SERVICE: InMemorySessionService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _RUNNER, _SESSION_SERVICE
    # ── startup ──
    agent = LlmAgent(name="greeter", model="gemini-2.5-flash", instruction="Be brief.")
    _SESSION_SERVICE = InMemorySessionService()
    _RUNNER = Runner(
        app=App(name="hello_app", root_agent=agent),
        session_service=_SESSION_SERVICE,
    )
    yield                          # ← server runs here
    # ── shutdown ──
    # Prefer the full Runner shutdown (closes toolsets, plugins, flushes
    # session_service). `plugin_manager.close()` is the plugin-only subset.
    await _RUNNER.close()


api = FastAPI(lifespan=lifespan)


@api.post("/chat")
async def chat(req: dict) -> dict:
    # use _RUNNER and _SESSION_SERVICE here
    return {"ok": True}
```

The `lifespan` runs the App-construction work **before** the first request. The framework guarantees `on_shutdown` even on SIGTERM (Cloud Run, Agent Engine, GKE — all honor it). This is the production shape.

## 🛠 Pattern 3 — `adk api_server` does this for you

```bash
$ adk api_server my_agent/
```

… discovers `my_agent/agent.py`, imports `root_agent` or `app`, builds the Runner, opens lifespan. You get pattern 2 for free. See [Module 21 ADK API Surface](../21_AdkApiSurface/) for the full picture.

> ❓ **Ask the student:** "We have an `McpToolset(stdio_params=...)` that spawns a Python subprocess on import. Why is that subprocess a startup-hook concern instead of just `agent = LlmAgent(tools=[McpToolset(...)])` at module scope?"
> *(Expected: import-time subprocess spawning blocks Python's import machinery, can race against testing, and offers no clean shutdown path. The pattern is: declare the toolset config at module scope, but `await toolset.connect()` inside the startup hook so it owns the subprocess lifetime.)*

## 🚀 In Production

> **🚀 In Production**
>
> The single most common bug: **forgetting to call the Runner's shutdown hook**. Prefer `await runner.close()` (runners.py:2135-2150) — it closes toolsets, then plugins, then flushes `session_service`. `await runner.plugin_manager.close()` is the plugin-only subset and is fine if that is genuinely all you wired, but `runner.close()` is the safer default. Plugins, toolsets, and session stores may hold open MCP subprocesses, file handles, and gRPC channels; without close, Cloud Run will SIGKILL them (plugins after `plugin_close_timeout`, default 5s) and you leak file descriptors across redeploys. Always wire shutdown — even if "the plugin list is empty today" — because future-you will add a plugin or a stateful session backend without remembering this rule.

> 🧭 **If the student looks stuck on async lifespan:** detour [[PY_async]] § "async context managers" — 10 min recap of `@asynccontextmanager` and why FastAPI's lifespan uses it.

---

[← Prev: 01_AppVsRunnerVsAgent](01_AppVsRunnerVsAgent.md)  [↑ Map](../../MAP.md)  [Next: 03_AppStateBoundary →](03_AppStateBoundary.md)
