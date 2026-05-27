---
module: 1A_AppAndRunner
page: 01_AppVsRunnerVsAgent
title: App vs Runner vs Agent — who owns what
estimated_minutes: 25
prereqs: [1A_AppAndRunner/00]
concepts: [App, Runner, LlmAgent, container, lifecycle]
icon: 🧠
in_production: true
detours_suggested: [PY_pydantic]
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_OnStartupShutdown →](02_OnStartupShutdown.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 01 App vs Runner vs Agent

# 🧠 `App` vs `Runner` vs `LlmAgent` — who owns what

The single biggest source of confusion in ADK 2.0 is *three objects* that look like they could each be "the top". They aren't peers. They are a stack.

## 🧠 The picture

```
{{INCLUDE _figures/app_hierarchy.txt}}
```

`App` is the **config truth** (a Pydantic model, no I/O). `Runner` is the **runtime executor** built from it (orchestrates one turn). `LlmAgent` is the **per-turn brain** (what the Runner calls).

| Object | Lifetime | Construction | What it owns |
|---|---|---|---|
| `LlmAgent` | The whole process. Reused per turn. | You write it. `LlmAgent(name=, model=, instruction=, tools=, sub_agents=)`. | Prompt, tools, sub-agent wiring. **No state.** |
| `App` | The whole process. One per agent app. | `App(name=, root_agent=agent, plugins=[...], events_compaction_config=..., context_cache_config=..., resumability_config=...)`. | Plugins, all cross-cutting config (cache, compaction, resumability), and the `app:`-state namespace. |
| `Runner` | The whole process. One per app. | `Runner(app=app, session_service=...)`. | Session service, memory service, artifact service, credential service. Drives `run_async`. |
| `Session` | Per `(app_name, user_id, session_id)` triple. | `await session_service.create_session(...)`. | Events log and state dict for one conversation. |

The key insight: **`App` is config; `Runner` is runtime.** You can build the App once at import time and reuse it forever. You can build the Runner once per process and reuse it forever. Only the Session is per-conversation.

## 🛠 By-hand example — wrap the agent in an App

```python
# Work/1A_app_basics.py — run with: uv run python Work/1A_app_basics.py
import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# 1. The agent — still just a config object, same as Module 02.
greeter = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="Reply in exactly one short sentence. Be friendly.",
    description="Greets the user.",
)

# 2. The App — the new 2.0 container. `name` is the app_name.
app = App(
    name="hello_app",
    root_agent=greeter,
)

# 3. The Runner — built from the App. No more `app_name=` here; it
#    comes from the App. No more `agent=` here either.
session_service = InMemorySessionService()
runner = Runner(app=app, session_service=session_service)


async def main() -> None:
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name="hello_app",      # must match app.name
        user_id="carlos",
        session_id=session_id,
    )

    msg = types.Content(role="user", parts=[types.Part(text="Say hi.")])

    async for event in runner.run_async(
        user_id="carlos",
        session_id=session_id,
        new_message=msg,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

```
$ uv run python Work/1A_app_basics.py
Hi there! How can I help you today?
```

## 🧠 What changed from Module 02?

| Module 02 (legacy still works) | Module 1A (2.0 modern) |
|---|---|
| `Runner(app_name="hello", agent=root, session_service=ss)` | `App(name="hello", root_agent=root)` then `Runner(app=app, session_service=ss)` |
| Plugins via deprecated `Runner(plugins=[...])` kwarg | `App(plugins=[...])` — single source of truth |
| No app-level cache/compaction/resumability config | All three live on the App, propagated to the Runner |
| Cross-cutting code had to be passed through Runner kwargs | Cross-cutting code lives on the App once |

The Module 02 form **still works** — `Runner(app_name=..., agent=...)` internally calls `App(name=app_name, root_agent=agent, plugins=plugins or [])` and proceeds. But every new feature 2.0 adds (resumability, caching, compaction, future things) goes on `App`, not on `Runner`. Writing the `App` explicitly is the forward-compatible shape.

> ❓ **Ask the student:** "If I have a plugin I want to share across two separate conversations for the same user, where does the plugin live — App or Session?"
> *(Expected: App. The Session is per-conversation and dies. The App is process-wide and the plugin list is shared across every Runner invocation against that App.)*

## 🧠 Why split `App` from `Runner`?

Three reasons:

1. **Config vs runtime separation.** `App` is a Pydantic model with `extra="forbid"` — it validates your config at construction. `Runner` is a runtime executor with mutable internal state (active invocations, plugin manager). Mixing them made Runner kwargs balloon as 2.0 added features.
2. **One Runner can be built from one App, but the App is the unit of identity.** `app_name` is part of the session primary key — sessions belong to apps, not to runners. The App is what *names* the agent application; the Runner is just one way to execute it (others: A2A serving, eval harness, ambient agent driver — all consume the same `App`).
3. **Cross-cutting features compose.** Resumability, context caching, context compaction, plugins — they all want one config object to attach to. Pre-2.0 each was a separate Runner kwarg; post-2.0 they all live on App.

> 🛠 **Have the student run:** `Work/1A_app_basics.py`. Then change `app = App(name="hello_app", ...)` to `app = App(name="hello-app", ...)` (hyphen — still valid per `validate_app_name`) and re-run. Confirm it still works. Then try `app = App(name="user", ...)` and watch it raise (the name `"user"` is reserved). The App is doing real validation at construction time.

## 🚀 In Production

> **🚀 In Production**
>
> Always construct the App **once at module scope** (or in a small `get_app()` factory cached with `functools.lru_cache`). The App holds plugin instances, model registries, possibly DB pool references — building a fresh `App(...)` per request defeats every cross-cutting feature it owns. Same rule as the cached Runner from [02 First Agent § 06 In Production](../02_FirstAgent/06_InProduction.md), one layer up.

> 🧭 **If the student looks stuck:** the App is a Pydantic model. If "why does this validate at construction?" is fuzzy, take detour [[PY_pydantic]] — 20 minutes covers Pydantic's `BaseModel`, `model_validator`, and `ConfigDict(extra="forbid")` which is exactly what `App` uses.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_OnStartupShutdown →](02_OnStartupShutdown.md)
