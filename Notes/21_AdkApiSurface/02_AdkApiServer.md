---
module: 21_AdkApiSurface
page: 02_AdkApiServer
title: adk api_server — the headless HTTP surface
estimated_minutes: 20
prereqs: [21_AdkApiSurface/01C]
concepts: [adk api_server, FastAPI, uvicorn, app_name, list-apps]
icon: 🌐
in_production: true
detours_suggested: [FastAPI_for_ADK]
---

[← Prev: 01C_FullCliFamily](01C_FullCliFamily.md)  [↑ Map](../../MAP.md)  [Next: 03_RestShapes →](03_RestShapes.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 02 adk api_server

---

## 🌐 What it is

`adk api_server` = `adk web` minus the Angular dev UI. Same FastAPI app, same routes, no static SPA mount. This is the **deployable surface**.

```
adk api_server <AGENTS_DIR> [--host 0.0.0.0] [--port 8000]
                            [--session_service_uri sqlite:///...]
                            [--artifact_service_uri gs://...]
                            [--allow_origins=https://my-frontend.example.com]
```

Under the hood it calls the same factory `adk web` calls, with `web=False`:

```python
# src/google/adk/cli/api_server.py — paraphrased
fast_api_app = get_fast_api_app(
    agents_dir=...,
    web=False,                       # <— the only difference from `adk web`
    session_service_uri=...,
    artifact_service_uri=...,
    allow_origins=...,
    lifespan=...,
)
uvicorn.run(fast_api_app, host=host, port=port)
```

## 🌐 What routes you get

The full set, mounted at the root of the FastAPI app. (See `src/google/adk/cli/api_server.py` for the live definitions.)

```
GET  /health
GET  /version
GET  /list-apps
GET  /apps/{app_name}/app-info

# Session CRUD (page 07)
GET    /apps/{app_name}/users/{user_id}/sessions/{session_id}
GET    /apps/{app_name}/users/{user_id}/sessions
POST   /apps/{app_name}/users/{user_id}/sessions/{session_id}
POST   /apps/{app_name}/users/{user_id}/sessions
DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}

# Artifacts (link to 04A Artifacts module)
GET/POST /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/...

# The three invocation surfaces
POST      /run          ← single-shot JSON, returns list[Event]   (page 03)
POST      /run_sse      ← streaming events over SSE              (page 04)
WEBSOCKET /run_live     ← bidi voice/video                        (page 05)
```

That's the entire wire surface. There is no separate "v1" prefix; the URLs above are it.

## 🌐 A first hit with `curl`

```python
# Work/21_AdkApiSurface/02_curl_run.sh — run with: bash Work/21_AdkApiSurface/02_curl_run.sh
# Pre-req: in another terminal run:  adk api_server Work/21_AdkApiSurface --port 8000

APP=research_assistant
USER=alice
SESSION=sess-001

# 1. Create the session
curl -sS -X POST \
  "http://localhost:8000/apps/${APP}/users/${USER}/sessions/${SESSION}" \
  -H "content-type: application/json" -d '{}'

# 2. Hit /run with one user turn
curl -sS -X POST "http://localhost:8000/run" \
  -H "content-type: application/json" \
  -d "{
    \"app_name\": \"${APP}\",
    \"user_id\": \"${USER}\",
    \"session_id\": \"${SESSION}\",
    \"new_message\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"What is the speed of light in m/s?\"}]
    }
  }" | jq '.[0].content.parts[0].text'
```

Expected output (something close to):

```
"The speed of light in a vacuum is approximately 299,792,458 m/s."
```

> 🛠 **Have the student run:** the script above with the agent from page 01. Have them inspect the **full** JSON without `jq` — count how many events came back, and which one had the actual text.

## ⚠️ Gotcha — `app_name` vs `agent.name`

In the URL, `{app_name}` is the **package directory name**, not the agent's `name=` constructor kwarg.

- Folder is `research_assistant/` → URL is `/apps/research_assistant/...`.
- Agent code says `name="research_assistant_v2"` → does NOT change the URL.

The `app_name` field in the JSON body of `/run` must match.

## 🌐 Health and discovery

| Route          | What it returns                                                  | Use                                  |
|----------------|------------------------------------------------------------------|--------------------------------------|
| `GET /health`  | `{"status": "ok"}`                                              | Cloud Run / k8s readiness probe.     |
| `GET /version` | ADK version + Python version                                     | Debug "which build is running".      |
| `GET /list-apps` | `["app_name_1", "app_name_2"]`                                | Service discovery for your frontend. |
| `GET /apps/{app_name}/app-info` | Per-app metadata (agent name, model, tools) | UI rendering or auth gate decisions. |

## 🚀 In Production

> **🚀 In Production**
>
> `adk api_server` is single-process. It scales horizontally (multiple replicas) but **not** within a process — uvicorn workers > 1 break ADK's in-process session caches. The standard prod recipe is: **1 worker per pod, N pods behind a load balancer, sticky sessions by `session_id`**. If you cannot do sticky routing, push session state to a real backend (`DatabaseSessionService` with Postgres, or `VertexAiSessionService`) so any pod can serve any request.

> ❓ **Ask the student:** "Why does ADK ship `adk api_server` *separately* from `adk web` when the only difference is `web=False`?" *(Smaller deployable image, no Angular static bundle, no Builder routes — surface-area minimization for prod.)*

---

[← Prev: 01C_FullCliFamily](01C_FullCliFamily.md)  [↑ Map](../../MAP.md)  [Next: 03_RestShapes →](03_RestShapes.md)
