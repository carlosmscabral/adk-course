---
module: Detours
page: FastAPI_for_ADK
title: FastAPI for ADK — wrapping and extending adk api_server
estimated_minutes: 30
icon: 🌐
prereqs: []
concepts: [adk_api_server, FastAPI_sub_app, middleware, custom_routes, Pydantic_models, dependency_injection, session_service_DI, lifespan]
---

[← Back to: 21_ADK_API_Surface]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ FastAPI for ADK

> 🧭 **Optional but recommended.** `adk api_server` ships a working FastAPI app, but the moment you need auth, a file-upload endpoint, or a health check that talks to your DB — you mount your own FastAPI around it. ~30 min.

---

## 🌐 1. The mental model — ADK is a FastAPI app

```
  your FastAPI app                       internals
  ├── /healthz       (yours)             │
  ├── /admin/reload  (yours)             │
  ├── /upload        (yours)             │
  └── /adk           ──► adk.get_fast_api_app()  ◄── owns:
                                          /run, /run_sse,
                                          /apps/{app}/users/{u}/sessions
                                          /apps/{app}/users/{u}/sessions/{s}/events
                                          /list-apps, /debug/*
```

`adk api_server` is just `uvicorn main:app` where `app` was built by `google.adk.cli.fast_api.get_fast_api_app(...)`. That function returns a regular FastAPI instance. You can:

1. **Use it directly** (the `adk api_server` path).
2. **Wrap it** — mount the ADK app as a sub-app of your own FastAPI, add routes/middleware around it.
3. **Compose it** — build your own FastAPI from scratch and call ADK's `Runner` directly in handlers.

Most teams land at #2. It gives you control where you want it and ADK's machinery where you don't.

---

## 🌐 2. The wrapper pattern

```python
# main.py — run with: uv run uvicorn main:app --port 8080
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# ADK's FastAPI app — knows your agents in ./agents/
adk_app = get_fast_api_app(
    agents_dir="./agents",
    session_service_uri="sqlite:///./sessions.db",  # or "agentengine://...", "postgres://..."
    web=False,                                       # set True to expose adk web UI
)

# Your wrapper
app = FastAPI(title="my-agent-platform")

# Your routes — add BEFORE mounting, so they're discoverable
@app.get("/healthz")
def healthz():
    return {"ok": True}

# Mount ADK at /adk; or "/" to overlay (collision-prone, prefer subpath)
app.mount("/adk", adk_app)
```

Now `curl localhost:8080/healthz` is yours, `curl localhost:8080/adk/run_sse ...` is ADK's.

---

## 🌐 3. Auth middleware — the most common addition

Add OAuth2 / API key checking once, applied to everything:

```python
# auth.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, valid_keys: set[str], skip_paths: set[str]):
        super().__init__(app)
        self.valid_keys = valid_keys
        self.skip_paths = skip_paths

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.skip_paths:
            return await call_next(request)
        key = request.headers.get("x-api-key", "")
        if key not in self.valid_keys:
            raise HTTPException(status_code=401, detail="invalid api key")
        return await call_next(request)

# main.py
import os
app.add_middleware(
    APIKeyMiddleware,
    valid_keys=set(os.environ["VALID_API_KEYS"].split(",")),
    skip_paths={"/healthz", "/docs", "/openapi.json"},
)
```

For real OAuth, swap to `fastapi.security.OAuth2AuthorizationCodeBearer` or `fastapi-users` and verify JWTs. The pattern stays identical — one middleware, applied before the ADK mount.

> **🚀 In Production**
>
> Don't authenticate inside ADK callbacks (`before_model_callback`) for the bearer-token check. By the time your callback runs, the request has already entered your event loop and consumed a session slot. Middleware rejects bad tokens at the HTTP boundary — cheaper and clearer.

---

## 🌐 4. Custom routes — file upload, health, admin

Mix Pydantic + standard FastAPI dependency injection with ADK's machinery.

**File upload to GCS, then hand off to the agent:**

```python
# routes/upload.py
from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel
from google.cloud import storage

router = APIRouter(prefix="/files")
bucket = storage.Client().bucket("my-agent-uploads")

class UploadResponse(BaseModel):
    gcs_uri: str
    size_bytes: int

@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile) -> UploadResponse:
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(413, "file too large (50 MB cap)")
    blob = bucket.blob(f"uploads/{file.filename}")
    blob.upload_from_file(file.file, content_type=file.content_type)
    return UploadResponse(gcs_uri=f"gs://{bucket.name}/{blob.name}",
                          size_bytes=blob.size or 0)

# main.py
from routes import upload
app.include_router(upload.router)
```

The agent can then receive `gs://...` URIs (e.g., via a `process_uploaded_file` tool) and read them directly.

**Health that actually checks something:**

```python
@app.get("/healthz")
async def healthz(session_svc = Depends(get_session_service)):
    # liveness: process is up
    # readiness: session store is reachable
    try:
        await session_svc.list_sessions(app_name="hello_agent", user_id="_probe")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(503, f"session store unreachable: {e}")
```

K8s/Cloud Run can hit this and pull a bad replica out of rotation.

---

## 🌐 5. Pydantic models for request/response

`Runner.run_async` consumes `google.genai.types.Content`. If you want a cleaner external API, define your own Pydantic shapes and translate:

```python
from pydantic import BaseModel
from google.genai import types as gtypes

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class ChatChunk(BaseModel):
    author: str
    text: str | None = None
    tool_calls: list[dict] = []

def to_genai(req: ChatRequest) -> gtypes.Content:
    return gtypes.Content(role="user", parts=[gtypes.Part(text=req.message)])
```

Now your OpenAPI schema is clean (auto-generated `/docs`), clients aren't coupled to `google.genai` internals, and you have one obvious spot to validate inputs.

---

## 🌐 6. Dependency injection for session services

ADK exposes the session service it built internally, but if you also use it in your own handlers, DI gives you one source of truth:

```python
# deps.py
from functools import lru_cache
from google.adk.sessions import DatabaseSessionService

@lru_cache(maxsize=1)
def get_session_service() -> DatabaseSessionService:
    return DatabaseSessionService(db_url="sqlite:///./sessions.db")

# main.py
from fastapi import Depends
from deps import get_session_service

# Pass the SAME instance into the ADK app
adk_app = get_fast_api_app(
    agents_dir="./agents",
    session_service=get_session_service(),  # not the URI form — the instance
)

# And use it in your own routes
@app.get("/sessions/{user_id}")
async def my_list(user_id: str, svc = Depends(get_session_service)):
    return await svc.list_sessions(app_name="hello_agent", user_id=user_id)
```

One process, one connection pool, one session store. The alternative — letting ADK and your handlers each construct their own — leads to schema mismatches and double-locked SQLite files.

---

## 🌐 7. Lifespan — startup and shutdown

FastAPI's lifespan context lets you do expensive init once:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.bq_client = bigquery.Client()
    print("warmed up")
    yield
    # shutdown
    app.state.bq_client.close()

app = FastAPI(lifespan=lifespan)
```

Useful for: prewarming BigQuery / Vertex clients, opening MCP connections, loading a vector index. ADK's `get_fast_api_app` accepts lifecycle hooks too — for things owned solely by ADK (the runner, session service), let it manage them; for ambient infra, use FastAPI's lifespan.

---

## 🛠 Have the student try

Take any agent from earlier modules and wrap it:

```python
# Work/wrapped_server.py — run with:
#   uv run uvicorn Work.wrapped_server:app --port 8080
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

adk_app = get_fast_api_app(agents_dir="./agents", web=False)

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"adk_app": "0.1.0", "build": "local-dev"}

app.mount("/adk", adk_app)
```

Verify:

1. `curl localhost:8080/healthz` → `{"status":"ok"}`
2. `curl localhost:8080/version` → version info
3. `curl localhost:8080/adk/list-apps` → list of agents in `./agents/`
4. `curl -N localhost:8080/adk/run_sse -d '...'` → SSE event stream (ADK's, untouched)

Now add a 1-line auth middleware that requires `X-API-Key: secret` on `/adk/*` only — confirm `/healthz` still works without the header.

---

[← Back to: 21_ADK_API_Surface/04_CustomizingTheServer](../21_ADK_API_Surface/04_CustomizingTheServer.md)  [↑ Map](../../MAP.md)

**When you're done:** head back to module 21. The In-Production page (`06_InProduction.md`) revisits middleware ordering and the "where to put auth" question with the deployment context from [[Cloud_Run]].
