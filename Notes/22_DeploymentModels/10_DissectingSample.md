---
module: 22_DeploymentModels
page: 10_DissectingSample
title: Dissecting adk-ae-oauth — the same agent, two deployments
estimated_minutes: 40
prereqs: [22_DeploymentModels/09]
concepts: [AgentEngineApp, OAuth on Agent Engine, deploy wrapper, Cloud Run derivative path]
icon: 🔬
in_production: false
detours_suggested: [AgentEngine]
---

[← Prev: 09_CostModelComparison](09_CostModelComparison.md)  [↑ Map](../../MAP.md)  [Next: 11_InProduction →](11_InProduction.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 10 Dissecting Sample

---

## 🔬 The sample

`/home/carloscabral/study/adk-samples/python/agents/adk-ae-oauth/`

```
adk-ae-oauth/
├── Makefile                       ← deploy / register-oauth / register-gemini-enterprise
├── pyproject.toml
├── adk_ae_oauth/
│   ├── __init__.py
│   ├── agent.py                   ← LlmAgent + App
│   ├── agent_engine_app.py        ← AgentEngineApp(AdkApp)  ← THIS is the deployment artifact
│   ├── auths.py                   ← AUTH_CONFIG + SCOPES
│   ├── tools.py                   ← negotiate_creds() + read_drive_file()
│   └── app_utils/
│       ├── deploy.py              ← Python deployer (vertexai SDK)
│       ├── telemetry.py
│       └── typing.py              ← Feedback model
└── tools/
    └── register_oauth.py          ← Gemini Enterprise OAuth resource provisioning
```

**Why this sample for this module.** It's the only ADK sample that ships **a real, production-grade deployment artifact** (`agent_engine_app.py`) wrapped in a Makefile that also handles the OAuth resource provisioning Gemini Enterprise requires. Every page in this module concretises in this sample.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/adk-ae-oauth/adk_ae_oauth/` and then read `agent_engine_app.py` end-to-end (only 65 lines).

## 🔬 File 1 — `agent.py` (the agent, transport-agnostic)

The agent itself is the same shape as every other ADK agent. Two relevant lines:

```python
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="drive_reader",
    tools=[read_drive_file],
    ...
)

app = App(name="drive_reader", root_agent=root_agent)
```

Note: it exports an **`App`**, not just the agent. `AgentEngineApp` consumes the `App`. The transport surface is *not* in this file — same pattern as currency-agent in module 21.

## 🔬 File 2 — `agent_engine_app.py` (the deployment artifact)

This is the file Agent Engine actually loads. Cross-link to **page 03** for the full code; key points here:

### Constructor (lines 56-65)

```python
agent_engine = AgentEngineApp(
    app=adk_app,
    artifact_service_builder=lambda: (
        GcsArtifactService(bucket_name=logs_bucket_name)
        if logs_bucket_name
        else InMemoryArtifactService()
    ),
)
```

`AgentEngineApp` subclasses `vertexai.agent_engines.templates.adk.AdkApp`. The constructor takes:
- `app=adk_app` — the `App` from `agent.py`.
- `artifact_service_builder=` — a **callable** (Vertex needs to defer construction; calling `GcsArtifactService(...)` at module load would tie credentials to the wrong identity).

The `lambda` here is the canonical pattern: build the service inside Vertex's worker context.

### `set_up()` (lines 33-42)

```python
def set_up(self) -> None:
    vertexai.init()
    setup_telemetry()
    super().set_up()
    logging.basicConfig(level=logging.INFO)
    logging_client = google_cloud_logging.Client()
    self.logger = logging_client.logger(__name__)
    if gemini_location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = gemini_location
```

Three crucial things:

1. **`vertexai.init()` first** — without this, downstream Vertex calls fail with "default project not set."
2. **`setup_telemetry()` *before* `super().set_up()`** — same gotcha as page 07: the tracer provider must exist before the App is constructed, or ADK's spans go to a noop.
3. **`super().set_up()`** — initialises `AdkApp` internals (session service, runner). Skip it and nothing works.

### `register_feedback()` + `register_operations()` (lines 44-53)

This is how you add **custom RPC operations** to an Agent Engine deployment. By default, Agent Engine exposes `stream_query`, `query`, etc. Override `register_operations()` to add yours:

```python
def register_operations(self) -> dict[str, list[str]]:
    operations = super().register_operations()
    operations[""] = operations.get("", []) + ["register_feedback"]
    return operations
```

The empty string key `""` means "synchronous (non-streaming) RPCs." Now clients can call `engine.register_feedback({...})` over the Vertex SDK.

> ❓ **Ask the student:** "Why expose feedback as an RPC on the engine, instead of a separate Cloud Function?" *(Co-located with the agent → has the same SA permissions, same logging context, same trace. One deployment artifact, two surfaces.)*

## 🔬 File 3 — `tools.py` and the OAuth pattern

`negotiate_creds()` in `tools.py` is the **three-stage** credential resolution that lets the *same code* work locally (ADK web UI) and in production (Agent Engine + Gemini Enterprise):

```python
# Stage 1 — cached token
cached_token = tool_context.state.get(auths.TOKEN_CACHE_KEY)
if cached_token is None:
    cached_token = tool_context.state.get(f"temp:{auths.TOKEN_CACHE_KEY}")
# ^^^ Gemini Enterprise injects under "temp:<AUTH_ID>"

# Stage 2 — ADK OAuth flow response
if exchanged_creds := tool_context.get_auth_response(auths.AUTH_CONFIG):
    creds = Credentials(token=..., refresh_token=..., ...)
    tool_context.state[auths.TOKEN_CACHE_KEY] = json.loads(creds.to_json())
    return creds

# Stage 3 — request the user authenticate
tool_context.request_credential(auths.AUTH_CONFIG)
return {"pending": True, "message": "Awaiting user authentication"}
```

Stage 1 handles **both** environments. The `temp:` prefix is how Gemini Enterprise injects a fresh OAuth token per request (it manages the consent screen and refresh outside your agent). The non-prefixed key is what your local ADK dev environment caches across turns.

Same code, no `if production:` branches. Cross-link **18 Auth flows** and **page 06**.

## 🔬 File 4 — `Makefile` (the operator-facing surface)

```makefile
deploy:
    uv run -m adk_ae_oauth.app_utils.deploy \
        --source-packages=./adk_ae_oauth \
        --entrypoint-module=adk_ae_oauth.agent_engine_app \
        --entrypoint-object=agent_engine \
        --requirements-file=adk_ae_oauth/app_utils/.requirements.txt
```

`make deploy` runs a **Python deployer** (`app_utils/deploy.py`), not `adk deploy agent_engine`. Why a custom deployer?

- Lets you set `agent_identity`, `secrets`, network config, all from the Makefile flags.
- Generates `.requirements.txt` from `uv.lock` (Agent Engine needs a pip-style requirements file, not a `pyproject.toml`).
- The `entrypoint-object=agent_engine` points Vertex at the `agent_engine = AgentEngineApp(...)` instance on the bottom of `agent_engine_app.py`.

```makefile
register-oauth:
    uv run python tools/register_oauth.py
```

This is the **OAuth resource registration** with Gemini Enterprise — separate from the agent deployment. Run it once per project. Cross-link page 06 § Gemini Enterprise.

```makefile
register-gemini-enterprise:
    uvx agent-starter-pack@0.39.4 register-gemini-enterprise ...
```

This registers the deployed agent against Gemini Enterprise's agent catalogue, binding the OAuth resource ID to the agent ID. After this, end users can sign in to Gemini Enterprise, find the agent, and consent to OAuth.

## 🔬 The full operator flow

```
1. make install                          # uv sync
2. make playground                       # local dev — ADK web UI, uses ADK OAuth flow
3. make register-oauth                   # one-time GE OAuth resource
4. make deploy                           # → Agent Engine
5. make register-gemini-enterprise \     # bind agent to GE
     AUTH_ID_RESOURCE=... GE_APP_ID=...
6. (end users access via Gemini Enterprise)
```

This is the **production operator runbook** for an OAuth-enabled ADK agent. Read the Makefile and you have the whole shipping pipeline in one file.

## 🔬 Mapping to this module's pages

| Page | Where it shows up in this sample |
|------|----------------------------------|
| 01 Landscape | `agent_engine_app.py` chooses Agent Engine path; could equally have chosen Cloud Run with a different entrypoint |
| 02 Cloud Run | **Absent** — the sample is Agent-Engine-only. Building a Cloud Run version is the mini-drill on page 13 |
| 03 Agent Engine | `agent_engine_app.py` end to end |
| 03A GKE | **Absent** — not the right fit for this sample (OAuth + Gemini Enterprise are GCP-native) |
| 04 Session persistence | `super().set_up()` initialises Vertex-managed session storage; nothing to configure |
| 05 Scaling & cold start | `set_up()` is the cold-start hot path — minimise work there |
| 06 Auth & IAM | `negotiate_creds()` three-stage pattern is the canonical OAuth-on-AE example |
| 07 Observability | `setup_telemetry()` in `app_utils/telemetry.py` |
| 08 Secrets | `make deploy SECRETS="STRIPE_KEY=stripe-api-key,..."` flag passes through to the deployer |
| 09 Cost | Agent Engine row of the cost table — sessions included, observability included |

## 🔬 What's intentionally missing

The sample does **not** ship a Cloud Run path, a GKE Helm chart, or a multi-region setup. That's not because they're hard — it's because the sample's value is the **OAuth + Gemini Enterprise** flow, which Agent Engine + Gemini Enterprise handles natively. Other deployment shapes would muddy the lesson.

The mini-drill on **page 13** has you carry the same agent to **Cloud Run** so you feel the difference: write your own Dockerfile, your own session-storage choice, your own auth middleware. Agent Engine hides all of these; Cloud Run forces you to choose.

> 🤖 **Tutor:** if the student can read `agent_engine_app.py` and explain what each line does, they understand how `AdkApp` subclassing works. That's the prerequisite for the mini-drill.

---

[← Prev: 09_CostModelComparison](09_CostModelComparison.md)  [↑ Map](../../MAP.md)  [Next: 11_InProduction →](11_InProduction.md)
