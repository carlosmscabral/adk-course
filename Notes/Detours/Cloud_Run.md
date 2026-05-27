---
module: Detours
page: Cloud_Run
title: Cloud Run — the container target for ADK deployments
estimated_minutes: 30
icon: 🌐
prereqs: []
concepts: [container, request_lifecycle, concurrency, cold_start, env_vars, secret_manager, custom_domain, IAP, gcloud_run_deploy, adk_deploy]
---

[← Back to: 22_DeploymentModels]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Cloud Run

> 🧭 **Optional.** Take this detour if Cloud Run is hand-wavy before you read `22_DeploymentModels/03_DeployCloudRun`. The module assumes you know what "concurrency=80" buys you and why background work breaks. ~30 min.

---

## 🌐 1. The mental model — one container, request-scoped lifetime

```
  request ──► load balancer ──► instance (container) ──► response
                                   │
                                   ├── ~0 instances when idle (scale-to-zero)
                                   ├── N parallel requests per instance (concurrency)
                                   └── instance dies when no traffic for ~15 min
```

Cloud Run runs **one container image**, started on demand, killed when idle. You hand it an image, it gives you an HTTPS URL. No nodes, no pods, no YAML — just `gcloud run deploy`.

The contract: your container must listen on `$PORT` (default 8080) and respond to HTTP. ADK's `adk api_server` and `adk web` both do this; `adk deploy cloud_run` is a thin wrapper that builds the image, pushes it to Artifact Registry, and calls `gcloud run deploy` for you.

---

## 🌐 2. Request lifecycle — and why background work fails silently

```
  T0   request arrives           ─► CPU allocated
  T1   handler returns response  ─► CPU may be throttled to ~0
  T2   no requests for 15 min    ─► container SIGTERM'd, instance gone
```

**The rule that bites everyone:** outside an active request, your container's CPU is throttled — sometimes to zero. A `asyncio.create_task(...)` that you fire-and-forget after returning the HTTP response *may run, may not, may run at 1% speed*. Same for background threads, schedulers, message pumps.

Mitigations:

- **Stay in-request** — finish the work before responding (acceptable for short tasks).
- **Always-allocated CPU** — `--cpu-boost` and `--cpu-always-allocated` flags keep CPU on. Costs more; needed for streaming/Live workloads.
- **Cloud Tasks / Pub/Sub** — push background work to a queue, a separate worker service picks it up.
- **Cloud Run Jobs** — sibling product for batch/cron, not request-driven.

For ADK: long-running tools, `LongRunningFunctionTool`, and Live sessions all need `--cpu-always-allocated` or they degrade weirdly.

> **🚀 In Production**
>
> If your agent has tools that take >30 s, set `--timeout=3600` (max 60 min) AND `--cpu-always-allocated`. Default timeout is 300 s; default CPU allocation throttles between requests. Most "my agent works locally but hangs in Cloud Run" bug reports are one of these two.

---

## 🌐 3. Concurrency — the knob that decides cost and contention

```
  concurrency=1     ─► one request per instance, max isolation, max cost
  concurrency=80    ─► default; up to 80 simultaneous requests per instance
  concurrency=1000  ─► max; only safe for I/O-bound, low-memory handlers
```

ADK agents are I/O-bound (waiting on Gemini, BigQuery, MCP servers). High concurrency is usually fine — *except* for in-memory state. If you use `InMemorySessionService`, two requests on the same instance share Python memory. Two requests on different instances don't. Result: sessions appear and disappear depending on which instance you land on.

**Fix:** swap to `DatabaseSessionService` or `VertexAiSessionService` for any deploy with concurrency > 1 across multiple instances. (Module `04_SessionsState/03_SessionServices` covers this.)

---

## 🌐 4. Cold start — what makes the first request slow

```
  cold start = image pull + container boot + app init + first handler
              (~500ms)    (~200ms)        (varies) (your code)
```

For ADK, "app init" is where the time goes — importing google.adk, building agents, connecting to Vertex. 2-5 s typical. Mitigations:

- **`--min-instances=1`** keeps one warm. Eliminates cold start at the cost of always-on billing (~$5-15/mo per instance).
- **`--cpu-boost`** doubles CPU for the first 10 s of cold start. Free, often halves init time.
- **Lazy imports** — defer heavy imports until first use, not module load. Helps for branchy code paths.
- **Smaller image** — slimmer base, fewer deps. `python:3.12-slim` over `python:3.12`.

For prod user-facing agents: `min-instances=1` is the standard. For internal tools tolerant of 3 s latency: scale-to-zero saves real money.

---

## 🌐 5. Env vars vs Secret Manager mounts

Two ways to get secrets in:

```bash
# Env var (visible in console, fine for non-secrets)
gcloud run deploy my-agent \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=my-proj,LOG_LEVEL=info

# Secret Manager (encrypted at rest, audit-logged, rotatable)
gcloud run deploy my-agent \
  --set-secrets=API_KEY=my-api-key:latest,DB_PASSWORD=db-pass:2
```

`--set-secrets` mounts the secret as an env var inside the container at startup. The version (`:latest`, `:2`) pins which secret version to use. **`:latest` re-reads on each deploy, not on each request** — rotating the secret doesn't auto-roll your service.

Rule:
- Project IDs, region, log levels → env vars.
- API keys, DB passwords, OAuth client secrets → Secret Manager.
- Service account credentials → don't mount; use the runtime SA (next section).

---

## 🌐 6. Identity — the runtime service account

Cloud Run runs as a service account. By default: the Compute Engine default SA, which is overprivileged. Always set explicit:

```bash
gcloud iam service-accounts create my-agent-sa
gcloud projects add-iam-policy-binding my-proj \
  --member=serviceAccount:my-agent-sa@my-proj.iam.gserviceaccount.com \
  --role=roles/aiplatform.user

gcloud run deploy my-agent \
  --service-account=my-agent-sa@my-proj.iam.gserviceaccount.com
```

Inside the container, **no creds file needed** — ADC (Application Default Credentials) picks up the runtime SA automatically. `google-cloud-aiplatform`, `google.cloud.bigquery`, ADK's Vertex calls all just work.

---

## 🌐 7. Custom domain + IAP

Two-step:

```bash
# Map custom domain (requires domain ownership verification first)
gcloud run domain-mappings create \
  --service=my-agent --domain=agent.example.com --region=us-central1

# Put behind Identity-Aware Proxy (zero-trust auth)
gcloud run services update my-agent \
  --ingress=internal-and-cloud-load-balancing
# then attach a load balancer + IAP per Cloud docs
```

IAP gives you "only users in `agents-team@company.com` group can hit this URL," enforced at Google's edge — no auth code in your container. The standard pattern for internal-only agent UIs.

For public agents: skip IAP, but put `--no-allow-unauthenticated` and let the agent do its own auth (OAuth, API keys) inside the handler.

---

## 🌐 8. `gcloud run deploy` vs `adk deploy cloud_run`

```bash
# Manual — full control, you own the Dockerfile
gcloud run deploy my-agent \
  --source=. --region=us-central1 --allow-unauthenticated

# ADK helper — generates the Dockerfile + entrypoint, calls gcloud under the hood
adk deploy cloud_run \
  --project=my-proj --region=us-central1 \
  --service_name=my-agent \
  --agent_engine_app=agent_engine_app.py \
  ./my_agent_package
```

`adk deploy cloud_run` is great for the first deploy — it knows to expose `/run`, `/run_sse`, `/apps/{app}/users/{u}/sessions`, etc. After that, most teams switch to a hand-written Dockerfile + their own CI, because they want:

- Custom middleware (auth, rate limiting) → see [[FastAPI_for_ADK]].
- Multi-stage builds for smaller images.
- Pinned deps via `uv pip compile`.
- Their CI/CD pipeline (Cloud Build, GitHub Actions).

The ADK helper is a starting point, not a destination.

---

## 🛠 Have the student try

Deploy the tiniest possible ADK agent to Cloud Run and hit it:

```python
# Work/cloud_run_agent/agent.py
from google.adk.agents import Agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="hello_agent",
    instruction="Greet the user warmly in one sentence.",
)
```

```bash
# from Work/cloud_run_agent/
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  --service_name=hello-agent \
  .

# Grab the URL it prints, then:
curl -X POST "$URL/run_sse" \
  -H "Content-Type: application/json" \
  -d '{"app_name":"hello_agent","user_id":"u1","session_id":"s1",
       "new_message":{"role":"user","parts":[{"text":"hi"}]}}'
```

You should see SSE events stream back. Now:

1. `gcloud run services describe hello-agent` — note the URL, region, concurrency, CPU allocation.
2. `gcloud logging read 'resource.type=cloud_run_revision'` — find your request.
3. Redeploy with `--min-instances=1` and compare cold-start times.

---

[← Back to: 22_DeploymentModels/03_DeployCloudRun](../22_DeploymentModels/03_DeployCloudRun.md)  [↑ Map](../../MAP.md)

**When you're done:** head back to `22_DeploymentModels`. The `04_AgentEngineDeploy` page builds the contrast — same agent, managed runtime.
