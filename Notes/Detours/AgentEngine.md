---
module: Detours
page: AgentEngine
title: Vertex AI Agent Engine — the managed runtime for ADK
estimated_minutes: 30
icon: 🌐
prereqs: []
concepts: [agent_engine, managed_runtime, session_persistence, tracing_integration, eval_integration, agent_engine_app, deployment_lifecycle, regions]
---

[← Back to: 22_DeploymentModels]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Agent Engine

> 🧭 **Optional.** Take this if "managed agent hosting" sounds like marketing and you want the concrete trade-offs. Agent Engine is the path Google nudges you toward; Cloud Run is the path you take when you need control. ~30 min.

---

## ☁️ 1. What Agent Engine is

```
   your agent code         Agent Engine Runtime           Vertex AI
   (LlmAgent + tools)  ──► (managed container)       ──► (Gemini, sessions,
                            │                              memory, tracing)
                            ├── session persistence (Vertex Sessions)
                            ├── auto-scale + warm pool
                            ├── built-in tracing → Cloud Trace
                            ├── eval harness integration
                            └── one HTTPS endpoint, one IAM boundary
```

Agent Engine (formerly "Reasoning Engine", now "Agent Engine Runtime") is a **fully managed runtime for ADK agents**. You hand Vertex a packaged agent; Vertex hosts it, exposes a stable resource name, scales it, traces it, and wires it into the rest of Vertex AI (Sessions, Memory Bank, Eval, RAG).

Compare to [[Cloud_Run]]: same goal (host an agent over HTTPS), different stance. Cloud Run hands you a container slot; Agent Engine hands you an agent slot.

---

## ☁️ 2. What you give up

Agent Engine is opinionated. You **don't** get:

- **Custom HTTP routes.** No `/admin/reload-config`, no file-upload endpoint, no health probe of your choosing. The endpoints exposed are fixed: `streamQuery`, `query`, session CRUD. If you need custom routes → Cloud Run.
- **Custom middleware.** No FastAPI auth layer, no rate-limiting middleware. Auth is via Vertex IAM (the caller's SA must have `aiplatform.user` on the engine). Fine for service-to-service, awkward for end-user logins → put Cloud Run + IAP in front, or front it with API Gateway.
- **A persistent filesystem.** Read-only at runtime; use GCS for artifacts.
- **Process control.** No `--cpu-always-allocated` knob. The runtime decides.
- **Local debugging parity.** Vertex-only deploys; no local Agent Engine emulator (you debug with `InMemoryRunner` and trust integration tests).

---

## ☁️ 3. What you gain

- **Session persistence** for free. `VertexAiSessionService` is the default; sessions survive restarts, replicas, region failovers (within a multi-region deploy).
- **Tracing integration** out of the box. Spans flow to Cloud Trace with no exporter setup.
- **Memory Bank** wiring. `VertexAiMemoryBankService` plugs in via config, no separate infra.
- **Eval integration.** The Vertex AI Eval service can target your engine by resource name — no copy-paste of the deployed code.
- **One IAM boundary.** "Who can call this agent?" = one IAM policy. With Cloud Run you'd manage IAP + ingress + LB + auth code.
- **No Dockerfile.** You ship a Python package; Vertex builds the image.

The trade is: lose flexibility, gain "the rest of Vertex AI integrates by default."

---

## ☁️ 4. The `agent_engine_app.py` shape

The contract Vertex looks for. Minimal:

```python
# agent_engine_app.py
from google.adk.agents import Agent
from vertexai import agent_engines

root_agent = Agent(
    model="gemini-2.5-flash",
    name="research_agent",
    instruction="Help the user research topics. Cite sources.",
)

# This object is what Vertex deploys.
app = agent_engines.AdkApp(agent=root_agent)
```

`AdkApp` is the Vertex adapter — it knows how to translate Agent Engine's HTTP surface into ADK `Runner` calls. Most teams keep `agent_engine_app.py` thin and put real agent definition in `agent.py`, importing it here.

> Three import paths float around: `from vertexai.agent_engines.templates.adk import AdkApp` (e.g., RAG sample), `from vertexai.preview.reasoning_engines import AdkApp` (llm-auditor, customer-service, academic-research), and `vertexai.agent_engines.AdkApp` (used here). All resolve to the same class.

For collaborative or sub-agent setups, you still only register the **root**; sub-agents come along for the ride.

---

## ☁️ 5. Deployment lifecycle

```
  package ──► upload to GCS ──► Vertex builds image ──► engine_resource_name
   (Python)    (staging bucket)   (~3-7 min first time)   projects/.../reasoningEngines/123
```

Three commands cover 95% of usage:

```bash
# 1. Deploy (or update — same command, new revision under the hood)
#    NOTE: `--staging_bucket` is deprecated in ADK 2.0 (see cli_tools_click.py:2256-2261,
#    callback _deprecate_staging_bucket at 1559-1568). Just leave it out — Agent Engine
#    provisions and manages its own staging now.
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  ./my_agent_package

# 2. List
gcloud ai reasoning-engines list --region=us-central1

# 3. Delete
gcloud ai reasoning-engines delete RESOURCE_ID --region=us-central1
```

The resource name (e.g., `projects/123/locations/us-central1/reasoningEngines/8765`) is **stable across redeploys** — clients pin to it, you redeploy without breaking integrations.

Programmatic equivalent:

```python
# Programmatic equivalent — exact shape moves with the vertexai SDK.
# Newer adk-python (see cli_deploy.py:1169) drives the deploy via:
#     client.agent_engines.create(config=agent_config)
# where agent_config has entrypoint_module / entrypoint_object / source_packages.
# Older snippets used `agent_engines.create(agent_engine=app, requirements=[...])`.
# Verify against the installed `vertexai` SDK before pinning. The high-level
# concept is the same: hand Vertex a packaged ADK app + its requirements.
from vertexai import agent_engines
import vertexai

vertexai.init(project="my-proj", location="us-central1")

remote = agent_engines.create(
    agent_engine=app,
    requirements=["google-adk>=2.0.0", "google-cloud-bigquery"],
)
print(remote.resource_name)
```

`requirements=` is your `pyproject` deps; Vertex resolves and installs them in the built image. Heavy native deps work but slow the build.

---

## ☁️ 6. Calling a deployed engine

```python
from vertexai import agent_engines

remote = agent_engines.get(
    "projects/123/locations/us-central1/reasoningEngines/8765"
)

# One-shot
result = remote.query(input="What is the capital of France?")
print(result["output"])

# Streaming (yields events like local ADK)
for event in remote.stream_query(
    user_id="u1",
    session_id="s1",
    message="research the Mars 2026 mission",
):
    print(event)
```

Authentication is ADC — same as any Vertex client. The caller's identity must hold `roles/aiplatform.user`.

---

## ☁️ 7. Regions and quotas

Agent Engine is regional. Pick the region where Gemini, your sessions, and your data live — cross-region calls add latency and egress.

Common regions (2026 GA): `us-central1`, `us-east1`, `us-west1`, `europe-west1`, `europe-west4`, `asia-southeast1`. Check the live availability matrix; rolling out continuously.

Quota items to watch:
- **Reasoning Engines per project** — usually 100, raise via support.
- **Concurrent queries per engine** — auto-scales; cap is a project-level Vertex AI quota.
- **Gemini token quota** — this is the real bottleneck. Per-region. Distinct from the engine quota.

---

## ☁️ 8. When to pick Agent Engine vs Cloud Run

| concern                          | Agent Engine                  | Cloud Run                    |
|----------------------------------|-------------------------------|------------------------------|
| time to first deploy             | ~5 min                        | ~10-30 min (Dockerfile etc.) |
| custom HTTP routes               | no                            | yes                          |
| auth model                       | Vertex IAM                    | anything (IAP, OAuth, keys)  |
| session persistence              | built-in                      | bring your own (DB)          |
| tracing                          | built-in to Cloud Trace       | OTel exporter you wire       |
| eval harness                     | first-class                   | run locally or DIY           |
| WebSockets / Live streaming      | limited (bidi via SDK)        | full                         |
| price model                      | per-request + tokens          | per-instance-second + tokens |
| vendor lock-in                   | high (Vertex resource name)   | low (it's just a container)  |

Rule of thumb: **prototype on Agent Engine** to get the agent + sessions + tracing wired in days, not weeks. **Graduate to Cloud Run** when you need custom auth, custom routes, WebSockets, or multi-cloud.

> **🚀 In Production**
>
> Agent Engine handles session and memory persistence, but you still pay the egress / token cost on every redeploy if you don't checkpoint. To roll back a session that hit a bad invocation, use `runner.rewind_async` (`runners.py:1114-1121`) — it appends a rewind Event with the inverse state-delta, so the session reads as if the bad invocation never happened. The real signature takes `user_id` + `session_id`, not a session object:
>
> ```python
> await runner.rewind_async(
>     user_id=...,
>     session_id=...,
>     rewind_before_invocation_id=...,
> )
> ```
>
> Keeps users moving while you debug the new revision.

---

## 🛠 Have the student try

Deploy the same hello-agent from [[Cloud_Run]] section 8, but to Agent Engine:

```python
# agent_engine_app.py
from google.adk.agents import Agent
from vertexai import agent_engines

root_agent = Agent(
    model="gemini-2.5-flash",
    name="hello_agent",
    instruction="Greet the user warmly in one sentence.",
)

app = agent_engines.AdkApp(agent=root_agent)
```

```bash
# `--staging_bucket` is deprecated — leave it out.
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  .
```

Then call it from Python:

```python
from vertexai import agent_engines
remote = agent_engines.get("projects/.../reasoningEngines/...")
for event in remote.stream_query(user_id="u1", session_id="s1", message="hi"):
    print(event)
```

Now hit Cloud Trace in the GCP console → you should see one trace per call, with spans for `agent.run` and `llm.call.gemini`, with zero exporter setup on your side.

---

[← Back to: 22_DeploymentModels/04_AgentEngineDeploy](../22_DeploymentModels/03_AgentEnginePath.md)  [↑ Map](../../MAP.md)

**When you're done:** return to module 22. The `05_ChoosingTarget` page maps real workloads to the right runtime using the trade-off table from section 8 above.
