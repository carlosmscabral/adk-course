---
module: 21_AdkApiSurface
page: 01B_AdkWebUnderTheHood
title: adk web under the hood — the dev UI and its ASGI mount
estimated_minutes: 25
prereqs: [21_AdkApiSurface/01A]
concepts: [adk web, get_fast_api_app, Angular dev UI, hot reload, mount]
icon: 🔬
in_production: false
detours_suggested: [FastAPI_for_ADK]
---

[← Prev: 01A_AdkRunUnderTheHood](01A_AdkRunUnderTheHood.md)  [↑ Map](../../MAP.md)  [Next: 01C_FullCliFamily →](01C_FullCliFamily.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 01B adk web internals

---

## 🔬 What `adk web` actually is

`adk web` = `adk api_server` + a **pre-built Angular dev UI** served from the same FastAPI app.

```
src/google/adk/cli/cli_tools_click.py
  @main.command("web")  def cli_web(...)
        │ resolves AGENTS_DIR (positional, default ".")
        │ resolves --port (default 8501), --host (default 127.0.0.1)
        │
        ▼
src/google/adk/cli/api_server.py
  get_fast_api_app(
      agents_dir=...,
      web=True,                      ← THIS is the difference vs api_server
      session_service_uri=...,
      artifact_service_uri=...,
      allow_origins=[...],
      lifespan=...,
  ) -> FastAPI
        │
        ▼
  uvicorn.run(app, host=..., port=...)
```

The Angular bundle ships inside the wheel at `cli/browser/` and is mounted at `/`. The same FastAPI process serves:

- `/` → the Angular SPA
- `/dev-ui/config` → JSON config the SPA reads on boot
- `/list-apps` → enumerates packages under `agents_dir`
- `/apps/{app}/users/{user}/sessions/...` → REST CRUD (page 07)
- `/run`, `/run_sse`, `/run_live` → the three invocation surfaces (pages 03-05)

## 🔬 Where the dev UI gets its app list

When the SPA opens, it calls `GET /list-apps`. The handler walks `agents_dir`, treating every subdirectory with an `__init__.py` (or `agent.py`) as a candidate. That is why dropping a new folder into your `agents_dir` makes it show up in the dev UI's dropdown without restart.

```
agents_dir/
├── research_assistant/      ← shows up
│   └── agent.py
├── currency_agent/          ← shows up
│   └── agent.py
└── scratch.py               ← does NOT show up (not a package)
```

## 🔬 Hot reload — what's actually live and what isn't

This trips everyone. Two pieces of state, two reload behaviors:

| State                         | Reload behavior                                                          |
|-------------------------------|--------------------------------------------------------------------------|
| The Angular **bundle**        | Cached by the browser. Hard-refresh to update.                            |
| The **list of apps**          | Re-read on every `/list-apps` call — drop in a new dir, refresh, it's there. |
| The **agent code itself**     | **Loaded once per process.** Edit `agent.py` → restart `adk web`.        |
| The **session state**         | In-memory by default — wiped on restart. Pass `--session_db_url sqlite:///x.db` to persist across restarts. |

So the dev loop is: edit code → Ctrl+C → `adk web` again. There is no `--reload` flag wired to uvicorn (the framework intentionally avoids it because agent boot can have heavy side effects).

> 🛠 **Have the student run:** start `adk web`, leave it running, edit `agent.py` to change the instruction, refresh the browser. The behavior does **not** change. Then restart `adk web` — now it changes.

## 🔬 The port and the auth defaults

`adk web` defaults are aggressively local:

- **Port**: `8501`.
- **Host**: `127.0.0.1` (not `0.0.0.0`).
- **Auth**: none. The dev UI assumes the only user is you.
- **CORS**: configurable via `--allow_origins`, default empty.

Bind to `0.0.0.0` only over a tunnel (`ngrok`, `gcloud compute start-iap-tunnel`) or on a dev box behind a corp VPN — never on the public internet.

## 🔬 The Visual Builder, briefly

If you launch with the Builder mode enabled, `cli/fast_api.py::_register_builder_endpoints` adds `/builder/*` routes for save/load of `AgentConfig`-style YAML. The Builder is *opt-in* in 2.0 GA and not on the default `adk web` surface yet. Cross-link: [[VisualBuilder]] detour.

## ⚠️ Gotcha — "the UI shows my agent but `/run` 404s"

Means: `agents_dir` was scanned successfully (SPA lit up) but the URL you POSTed used the wrong `app_name`. The `app_name` in the URL **must be the package name** (the directory name), not the agent's `name=` kwarg. Page 03 has the exact shape.

## 🚀 In Production

> **🚀 In Production**
>
> Never expose `adk web` to end users. The Angular bundle is a **dev tool** — no rate limiting, no auth, no CSRF protection on the builder endpoints, and it ships the full session history to the browser unfiltered. For end users you want either (a) your own SPA against the JSON API (module **23 Frontend Integration**) or (b) Agent Engine's managed UI surface (module **22 Deployment Models**).

> 🧭 **If the student looks stuck:** suggest the [[FastAPI_for_ADK]] detour — it covers `get_fast_api_app(...)` as a primitive so this page reads naturally.

---

[← Prev: 01A_AdkRunUnderTheHood](01A_AdkRunUnderTheHood.md)  [↑ Map](../../MAP.md)  [Next: 01C_FullCliFamily →](01C_FullCliFamily.md)
