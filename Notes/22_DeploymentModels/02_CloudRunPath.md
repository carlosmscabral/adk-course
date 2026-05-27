---
module: 22_DeploymentModels
page: 02_CloudRunPath
title: Cloud Run path — Dockerfile, adk deploy, env vars
estimated_minutes: 25
prereqs: [22_DeploymentModels/01]
concepts: [Dockerfile, adk deploy cloud_run, $PORT, env vars, source-based deploy]
icon: ☁️
in_production: true
detours_suggested: [Cloud_Run]
---

[← Prev: 01_DeploymentLandscape](01_DeploymentLandscape.md)  [↑ Map](../../MAP.md)  [Next: 03_AgentEnginePath →](03_AgentEnginePath.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 02 Cloud Run

---

> 🧭 Both Cloud Run and Agent Engine have specific layout expectations (where `agent.py` sits relative to the Dockerfile, what `adk deploy cloud_run` discovers, how the `agents_dir` resolves). See [[3A_ProjectStructure/06_DeploymentExpectations]] before structuring your project — a few decisions made on day one save migration pain later.

## ☁️ The shortest path — `adk deploy cloud_run`

```bash
adk deploy cloud_run \
    --project=my-gcp-project \
    --region=us-central1 \
    --service_name=research-assistant \
    --app_name=research_assistant \
    --session_service_uri=sqlite:///./sessions.db \
    ./research_assistant
```

Behind the scenes, this:

1. Generates a minimal **Dockerfile** for your agent (`google-adk[cloudrun]` + your deps).
2. Builds the image with Cloud Build.
3. Pushes to Artifact Registry.
4. Deploys to Cloud Run with the flags you supplied.

For a hackathon → demo path that's enough. For prod, you write your own Dockerfile (next section) so you control the layers, base image, and CI.

## ☁️ The Dockerfile you actually want

```dockerfile
# Dockerfile — Work/22_DeploymentModels/research_assistant/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. System deps your tools need (psql client, curl, etc.) — keep minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Python deps first — better layer caching
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev --no-install-project

# 3. The agent code
COPY research_assistant/ ./research_assistant/
COPY server.py ./

# 4. Cloud Run injects PORT (default 8080). Listen on it; bind 0.0.0.0.
ENV PORT=8080
EXPOSE 8080

# 5. Single uvicorn process per container (see module 21 page 10 item #2)
CMD exec uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 1
```

And the `server.py`:

```python
# Work/22_DeploymentModels/research_assistant/server.py
import os
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,                                              # no dev UI in prod
    session_service_uri=os.environ["SESSION_SERVICE_URI"],  # required in prod
    artifact_service_uri=os.environ.get("ARTIFACT_SERVICE_URI"),
    allow_origins=os.environ.get("ALLOW_ORIGINS", "").split(","),
)
```

Three properties of this setup:

- **Build once, deploy anywhere.** The image runs locally (`docker run -p 8080:8080`) identically to Cloud Run.
- **Fail-fast on missing env.** `SESSION_SERVICE_URI` raises at boot if unset — you find out in the deployment log, not from a confused user.
- **One worker, scale horizontally.** Cloud Run gives you `--concurrency=80` requests per container; the container itself runs one Python process.

## ☁️ Deploying your own Dockerfile

Skip `adk deploy` — use plain `gcloud`:

```bash
# 1. Build and push
gcloud builds submit \
    --tag us-central1-docker.pkg.dev/$PROJECT/agents/research-assistant:$GIT_SHA \
    .

# 2. Deploy
gcloud run deploy research-assistant \
    --project=$PROJECT \
    --region=us-central1 \
    --image=us-central1-docker.pkg.dev/$PROJECT/agents/research-assistant:$GIT_SHA \
    --set-env-vars="SESSION_SERVICE_URI=postgresql+psycopg://...,GOOGLE_CLOUD_PROJECT=$PROJECT" \
    --service-account=research-assistant@$PROJECT.iam.gserviceaccount.com \
    --concurrency=20 \
    --cpu=2 --memory=2Gi \
    --min-instances=1 \
    --max-instances=10
```

`--min-instances=1` keeps one warm instance to avoid cold start. `--concurrency=20` lower than the default (80) because agents are long-lived per request.

## ☁️ Required env vars

| Var                          | Why                                                                |
|------------------------------|--------------------------------------------------------------------|
| `GOOGLE_CLOUD_PROJECT`       | Vertex AI project for `gemini-2.5-flash` model calls.             |
| `GOOGLE_GENAI_USE_VERTEXAI`  | `"True"` for Vertex (recommended in GCP) vs API key.              |
| `SESSION_SERVICE_URI`        | Persistence — Cloud SQL for Postgres recommended.                  |
| `ARTIFACT_SERVICE_URI`       | `gs://bucket` if your agent emits artifacts.                       |
| `ALLOW_ORIGINS`              | CORS allow-list for your frontend.                                 |
| `PORT`                       | Set by Cloud Run; do not hard-code.                                |

If you're using API-key models (Gemini API), add `GOOGLE_API_KEY` via Secret Manager — never in `--set-env-vars` directly. See page 08.

> 🛠 **Have the student run:** locally, `docker build -t agent-test . && docker run -p 8080:8080 -e SESSION_SERVICE_URI="sqlite:///./test.db" -e GOOGLE_API_KEY=... agent-test`, then `curl http://localhost:8080/health`. The exact same image deploys to Cloud Run.

## ⚠️ Gotcha — cold start with heavy imports

Agents that import heavy deps at module-load time (Vertex SDK warmup, BigQuery client, large embeddings) eat 3-8s of cold start. Mitigations:

- `--min-instances=1` keeps one warm (costs ~$10/month for 1 vCPU).
- **Lazy-import** the heavy stuff inside route handlers, not at module level.
- **CPU boost during startup**: Cloud Run defaults to throttling CPU outside requests. `--cpu-boost` doubles CPU during cold start. Free for first 180 invocations/month.

Page 05 covers cold-start mitigation across all three platforms.

## ⚠️ Gotcha — `adk deploy cloud_run --with_ui`

`--with_ui` ships the Angular dev UI to prod. **Don't.** The dev UI has no auth, no rate limiting, and exposes session histories. The flag exists for internal demos / staging environments behind a VPN — not the public internet.

## 🐍 Detour suggestion

If `gcloud run deploy`, Artifact Registry, and Cloud Build are still magic, take 30 min on [[Cloud_Run]] — it covers the platform primitives this page assumes.

## 🚀 In Production

> **🚀 In Production**
>
> Cloud Run does **not** retain in-memory state across container restarts. `InMemorySessionService` works fine until your container is replaced (autoscaling, deploy, OOM) and then every active session is gone. **Always** wire `SESSION_SERVICE_URI` to a real backend (Cloud SQL Postgres) before the first user touches the agent. The default is the wrong choice for prod.

> ❓ **Ask the student:** "Why does Cloud Run inject `PORT` instead of letting me hard-code 8080?" *(Container portability — Cloud Run may swap ports for routing; trusting the env var keeps the image deployable on Cloud Run, GKE, and local Docker unchanged.)*

---

[← Prev: 01_DeploymentLandscape](01_DeploymentLandscape.md)  [↑ Map](../../MAP.md)  [Next: 03_AgentEnginePath →](03_AgentEnginePath.md)
