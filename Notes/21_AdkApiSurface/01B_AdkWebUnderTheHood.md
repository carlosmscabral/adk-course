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
        │ resolves --port (default 8000), --host (default 127.0.0.1)
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
| The **agent code itself**     | Loaded once per process **by default**. Toggle with `--reload_agents` (see below). |
| The **session state**         | In-memory by default — wiped on restart. Pass `--session_service_uri sqlite:///x.db` to persist across restarts. |

There are **two distinct reload flags** on `adk web`, and they do different things:

- `--reload/--no-reload` (default **`True`**) — wired straight into `uvicorn.Config(..., reload=reload)` at `cli/cli_tools_click.py:1839`. This is **uvicorn's process-level watcher**: any `.py` file change anywhere uvicorn is watching triggers a full server restart. Disabled on Windows automatically (`_check_windows_reload`).
- `--reload_agents` (default **`False`**) — passed to `get_fast_api_app(..., reload_agents=...)` (`cli/fast_api.py:396`). This is the **agent-cache live reload**: the loader re-imports the agent package on each invocation instead of caching it in-process. No server restart.

So the caveat on the table above: "agent code: loaded once per process" is only true when `--reload_agents` is **False** (the default). With `--reload_agents`, the loader re-imports per call. The two flags compose: `--no-reload --reload_agents` keeps the uvicorn process stable but still re-imports the agent each time.

> 🛠 **Have the student run:** start `adk web` with all defaults, leave it running, edit `agent.py` to change the instruction. Because `--reload=True` is the default, **uvicorn will restart the process** and the change *will* land on next request. Now restart with `adk web --no-reload --no-reload_agents path/to/agents` and try the same edit — behavior does **not** change until manual Ctrl+C and restart. Finally try `adk web --no-reload --reload_agents` — agent edits land without restarting the server.

## 🔬 The port and the auth defaults

`adk web` defaults are aggressively local:

- **Port**: `8000`.
- **Host**: `127.0.0.1` (not `0.0.0.0`).
- **Auth**: none. The dev UI assumes the only user is you.
- **CORS**: configurable via `--allow_origins`, default empty.

Bind to `0.0.0.0` only over a tunnel (`ngrok`, `gcloud compute start-iap-tunnel`) or on a dev box behind a corp VPN — never on the public internet.

## 🔬 The Visual Builder, briefly

Builder endpoints (`/builder/*` — save/load of `AgentConfig`-style YAML) are wired conditionally inside `cli/fast_api.py`: the registration runs only when `adk web` is the launcher (i.e. `web=True`) **and** the optional `python-multipart` dependency is installed. If multipart is missing, the loader emits a warning and the routes are silently skipped — `adk api_server` never registers them at all. The Builder is *opt-in* in 2.0 GA and gated behind that extra dep. Cross-link: [[VisualBuilder]] detour.

## ⚠️ Gotcha — "the UI shows my agent but `/run` 404s"

Means: `agents_dir` was scanned successfully (SPA lit up) but the URL you POSTed used the wrong `app_name`. The `app_name` in the URL **must be the package name** (the directory name), not the agent's `name=` kwarg. Page 03 has the exact shape.

## 🚀 In Production

> **🚀 In Production**
>
> Never expose `adk web` to end users. The Angular bundle is a **dev tool** — no rate limiting, no auth, no CSRF protection on the builder endpoints, and it ships the full session history to the browser unfiltered. For end users you want either (a) your own SPA against the JSON API (module **23 Frontend Integration**) or (b) Agent Engine's managed UI surface (module **22 Deployment Models**).

> 🧭 **If the student looks stuck:** suggest the [[FastAPI_for_ADK]] detour — it covers `get_fast_api_app(...)` as a primitive so this page reads naturally.

---

[← Prev: 01A_AdkRunUnderTheHood](01A_AdkRunUnderTheHood.md)  [↑ Map](../../MAP.md)  [Next: 01C_FullCliFamily →](01C_FullCliFamily.md)
