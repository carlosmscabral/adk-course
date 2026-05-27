---
module: 21_AdkApiSurface
page: 06_WrappingInFastAPI
title: Wrapping ADK in your own FastAPI process
estimated_minutes: 25
prereqs: [21_AdkApiSurface/05]
concepts: [get_fast_api_app, custom routes, middleware, lifespan, mount]
icon: 🌐
in_production: true
detours_suggested: [FastAPI_for_ADK]
---

[← Prev: 05_WebSocketsForLive](05_WebSocketsForLive.md)  [↑ Map](../../MAP.md)  [Next: 07_SessionAndEventResources →](07_SessionAndEventResources.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 06 Wrapping in FastAPI

---

## 🌐 Why wrap

`adk api_server` gives you ADK's routes and nothing else. Real services need:

- A `/healthz` that checks downstream deps (BigQuery, Redis).
- A custom `/feedback` route for the UI's thumbs-up/down.
- Auth middleware that decodes a Firebase JWT into `user_id`.
- Static asset mounts for a custom dev tool.
- Metrics middleware for Prometheus scrapes.

For all of that, drop `adk api_server` and build a FastAPI app that **includes** ADK as a sub-mount or composes with its router.

## 🌐 The factory

`google.adk.cli.fast_api.get_fast_api_app(...)` is the public function. Same factory `adk web` and `adk api_server` both call.

```python
# Work/21_AdkApiSurface/06_wrap_fastapi.py — run with: uv run python Work/21_AdkApiSurface/06_wrap_fastapi.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Build ADK's FastAPI app (this IS a FastAPI instance)
adk_app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,                                  # no dev UI
    session_service_uri="sqlite:///./sessions.db",
    allow_origins=["http://localhost:3000"],    # your SPA
)

# 2. Add your custom routes on the SAME app
@adk_app.get("/healthz")
async def healthz():
    return {"status": "ok", "deps": ["sqlite"]}

@adk_app.post("/feedback")
async def feedback(req: Request):
    body = await req.json()
    # write to BigQuery, emit metric, etc.
    return JSONResponse({"ok": True, "received": body})

# 3. Add middleware
@adk_app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(adk_app, host="0.0.0.0", port=8000)
```

```
$ uv run python Work/21_AdkApiSurface/06_wrap_fastapi.py
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Now `/healthz`, `/feedback`, **and** all of ADK's routes (`/run`, `/run_sse`, `/apps/.../sessions/...`) are on the same FastAPI app.

## 🌐 Two composition patterns

### Pattern A: extend (above)

`get_fast_api_app(...)` returns a `FastAPI`. You add routes, middleware, mounts to it. Simplest; recommended for most services.

### Pattern B: sub-mount

Run ADK at a sub-path so your own app owns `/`:

```python
# Work/21_AdkApiSurface/06_submount.py
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

app = FastAPI(title="my-service")

adk_app = get_fast_api_app(agents_dir="./agents", web=False)
app.mount("/agent", adk_app)

@app.get("/")
async def home():
    return {"message": "homepage; agent is at /agent"}
```

Clients then hit `POST /agent/run`, `POST /agent/apps/.../sessions/...`, etc. Useful when you're adding agents to an existing service.

## 🌐 Lifespan — provisioning shared resources

ADK uses FastAPI's `lifespan` hook for service warmup (loading the agent loader, connecting to the session DB). If you need your own warmup, **chain** lifespans:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def my_lifespan(app):
    # warmup: open BigQuery client, prime caches
    app.state.bq = make_bq_client()
    yield
    # teardown: close client
    app.state.bq.close()

adk_app = get_fast_api_app(
    agents_dir="./agents",
    web=False,
    lifespan=my_lifespan,  # ADK wraps your lifespan around its own
)
```

The factory accepts a `lifespan=` kwarg and composes it with its internal lifespan — your `yield` happens *inside* the ADK lifespan window.

## ⚠️ Gotcha — route name collisions

Your custom routes share the URL space with ADK's. If you define `GET /health` and ADK already defines `GET /health`, FastAPI uses **the first registered handler**. Either:

- Use distinct names (`/healthz`, `/livez`) for your routes.
- Or sub-mount (Pattern B) so ADK lives under a prefix.

## ⚠️ Gotcha — CORS twice

`get_fast_api_app(allow_origins=[...])` adds a CORS middleware. If you also add `app.add_middleware(CORSMiddleware, ...)`, you'll have *two* CORS layers. Symptom: duplicate `Access-Control-Allow-Origin` headers, browser console errors. Pick one place to configure CORS.

## 🐍 Detour suggestion

If `FastAPI`, `middleware`, `lifespan`, and `mount` are still moving parts in your head, take 30 min on [[FastAPI_for_ADK]]. It covers the FastAPI primitives ADK actually relies on, in the order this page assumes you know them.

## 🚀 In Production

> **🚀 In Production**
>
> When you wrap ADK in your own FastAPI app, **you own the deployment**. The CLI's `adk deploy cloud_run` will not build your custom routes — you write the Dockerfile yourself. The standard recipe: a 30-line Dockerfile that `COPY`s your project, installs deps, and `CMD`s `uvicorn your_module:adk_app`. Module **22 page 02** has the exact Dockerfile shape.

---

[← Prev: 05_WebSocketsForLive](05_WebSocketsForLive.md)  [↑ Map](../../MAP.md)  [Next: 07_SessionAndEventResources →](07_SessionAndEventResources.md)
