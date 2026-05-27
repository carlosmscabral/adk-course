---
module: 1A_AppAndRunner
page: 07_RunnerInsideTheApp
title: Runner is constructed from the App
estimated_minutes: 15
prereqs: [1A_AppAndRunner/06]
concepts: [Runner, App, _resolve_app, legacy-compat, plugins-deprecation]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 06_WiringContextCompaction](06_WiringContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 08_DissectingSample →](08_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 07 Runner Inside the App

# 🧠 Runner is constructed *from* the App

We have built the App three times now (pages 04, 05, 06). Each time we passed it to `Runner(app=app, session_service=...)` and moved on. This page is the one-page deep-dive on what that line actually does — because every legacy-compat path in 2.0 routes through it.

## 🧠 The three Runner constructions ADK 2.0 accepts

```python
# 1. Modern (recommended). The App carries everything.
runner = Runner(
    app=App(name="x", root_agent=agent, plugins=[...]),
    session_service=ss,
)

# 2. Legacy (still works). The Runner builds an App for you.
runner = Runner(
    app_name="x",
    agent=agent,
    session_service=ss,
    plugins=[...],          # DeprecationWarning
)

# 3. Node-based (graph workflow, Module 06). One of `app | agent | node` required.
runner = Runner(
    node=root_node,
    session_service=ss,
)
```

Exactly **one** of `app`, `agent`, or `node` must be provided; providing more than one raises `ValueError`. Internally `_resolve_app(...)` (see [adk-python/src/google/adk/runners.py](file:///home/carloscabral/study/adk-python/src/google/adk/runners.py) ~line 261) normalizes all three into a single `App` instance:

```python
# Excerpt: how legacy `agent=` gets wrapped
if agent is not None:
    if not app_name:
        raise ValueError("app_name is required when agent is provided without app.")
    return App(name=app_name, root_agent=agent, plugins=plugins or [])
```

The legacy form is just sugar — the Runner *always* operates on an `App`. After construction:

```python
self.app = app
self.app_name = app_name or app.name
self.agent = app.root_agent
self.context_cache_config = app.context_cache_config
self.resumability_config  = app.resumability_config
self.plugin_manager = PluginManager(plugins=app.plugins, ...)
```

Every cross-cutting field on the App ends up on the Runner. The Runner is, structurally, **a live view onto a frozen App config**.

## 🛠 Watch the legacy form auto-wrap

```python
# Work/1A_legacy_wrap.py — run with: uv run python Work/1A_legacy_wrap.py
import warnings

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

load_dotenv()

agent = LlmAgent(name="greeter", model="gemini-2.5-flash", instruction="Hi.")
session_service = InMemorySessionService()

# Legacy: pass agent + app_name. Runner wraps in App internally.
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    runner = Runner(
        agent=agent,
        app_name="hello",
        session_service=session_service,
        plugins=[],     # ← passing the deprecated kwarg to see the warning
    )

# The deprecation warning fires only if `plugins=` was passed alongside no `app=`.
print("captured warnings:", [str(w.message) for w in caught])

# The Runner's `app` attribute is now a real App, auto-built from your args.
print("runner.app:", type(runner.app).__name__, runner.app)
print("runner.app.name:", runner.app.name)
print("runner.app.root_agent.name:", runner.app.root_agent.name)
```

```
$ uv run python Work/1A_legacy_wrap.py
captured warnings: ['The `plugins` argument is deprecated. Please use the `app` argument to provide plugins instead.']
runner.app: App name='hello' root_agent=LlmAgent(name='greeter', ...) plugins=[] events_compaction_config=None context_cache_config=None resumability_config=None
runner.app.name: hello
runner.app.root_agent.name: greeter
```

Two things to confirm from that output:

1. `runner.app` exists and is a real `App`, even though we never typed `App(...)` ourselves.
2. The deprecation warning specifically calls out that **plugins** should move onto the App — that is the one Runner-kwarg that has been actively shrunk in 2.0.

## 🧠 Rules for the modern form

| Rule | Why |
|---|---|
| Provide exactly one of `app=`, `agent=`, `node=`. | Mutual exclusivity is checked; providing two raises. |
| If you pass `app=`, do not pass `plugins=`. | Plugins belong on the App. Passing both raises `ValueError`. |
| `app_name=` is optional when `app=` is given; it overrides `app.name` if both are set. | Same-process reuse of an App under different `app_name` is occasionally useful — eval harnesses do this. |
| `auto_create_session=True` opts into "create the session on the fly if missing". | Default `False` — you usually want the explicit `create_session(...)` call so collision bugs surface early. |

## 🧠 What you can still customize on Runner kwargs

Even with `app=`, these stay on Runner:

- `session_service` — required.
- `memory_service`, `artifact_service`, `credential_service` — optional services that are *runtime-scoped*, not config-scoped. (A `MemoryService` may hold an open DB connection that is per-process, not per-App.)
- `plugin_close_timeout` — operational tuning for shutdown.
- `auto_create_session` — operational tuning for missing sessions.

The split: **App = declarative truth. Runner = the per-process services that drive it.** Modules 11 (Memory) and 04A (Artifacts) live on Runner kwargs because their services are runtime concerns.

> ❓ **Ask the student:** "Why is `session_service` a Runner kwarg and not an App field?"
> *(Expected: a session service holds an open backend connection (DB pool, gRPC channel to Vertex). That is a per-process resource, not a piece of config you serialize. The App is a Pydantic model that should be serializable; the session service is not. Same logic applies to memory_service, artifact_service, credential_service — they live on the Runner because they are live resources.)*

## 🚀 In Production

> **🚀 In Production**
>
> When you onboard a teammate, show them the **modern form** (`Runner(app=App(...), session_service=...)`) on day one. The legacy form (`Runner(app_name=..., agent=..., plugins=...)`) is fine in older sample code, but every new feature 2.0 ships will land on `App` — your teammate writing 2026 code in the 2024 shape is acquiring tech debt. The migration cost from legacy → modern is one line; do it now.

> 🛠 **Have the student do:** open one sample from `adk-samples/python/agents/` and check whether it constructs `App(...)` or uses the legacy `Runner(app_name=..., agent=...)` form. Most ADK 2.0-aligned samples now use `App(...)` — count how many do, and how many haven't migrated. That gives them a real sense of how recent this pattern is.

---

[← Prev: 06_WiringContextCompaction](06_WiringContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 08_DissectingSample →](08_DissectingSample.md)
