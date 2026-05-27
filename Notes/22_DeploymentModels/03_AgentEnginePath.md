---
module: 22_DeploymentModels
page: 03_AgentEnginePath
title: Agent Engine path — managed Runtime, AgentEngineApp, session persistence
estimated_minutes: 30
prereqs: [22_DeploymentModels/02]
concepts: [AgentEngineApp, AdkApp, agent_engine_app.py, register_operations, VertexAiSessionService]
icon: ☁️
in_production: true
detours_suggested: [AgentEngine]
---

[← Prev: 02_CloudRunPath](02_CloudRunPath.md)  [↑ Map](../../MAP.md)  [Next: 03A_GKE →](03A_GKE.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 03 Agent Engine

---

> 🧭 Both Cloud Run and Agent Engine have specific layout expectations (Agent Engine wants an `agent_engine_app.py` next to your agent package, with the `AdkApp` subclass exposed at module level). See [[3A_ProjectStructure/06_DeploymentExpectations]] before structuring your project — a few decisions made on day one save migration pain later.

## ☁️ What Agent Engine is

**Vertex AI Agent Engine** (a.k.a. Agent Runtime) is a managed compute target where Google runs your agent. You don't ship a container — you ship an **`AdkApp` subclass** that the platform instantiates.

What's managed for you:

- **Compute**: scaling, cold-start mitigation, region distribution.
- **Sessions**: `VertexAiSessionService` is the default — durable, queryable, no DB to operate.
- **Memory**: `VertexAiMemoryBankService` available out of the box.
- **Observability**: OTel traces wired to Cloud Trace; logs to Cloud Logging.
- **Safety**: Google's safety classifiers run by default on model I/O.
- **Auth integration**: works natively with Gemini Enterprise OAuth flows.

What you give up:

- **Container customization**: no sidecars, no apt-installed binaries.
- **Wire-level customization**: limited custom routes (you can register operations, but you don't own the FastAPI app).
- **Velocity on bleeding edge**: Agent Engine lags ADK releases by 2-6 weeks.
- **Region flexibility**: limited to Agent Engine regions (page 01).

## ☁️ The `agent_engine_app.py` shape

The canonical file pattern, distilled from `adk-ae-oauth`:

```python
# Work/22_DeploymentModels/research_assistant/agent_engine_app.py
import logging
import os
from typing import Any

import vertexai
from dotenv import load_dotenv
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.cloud import logging as google_cloud_logging
from vertexai.agent_engines.templates.adk import AdkApp

from research_assistant.agent import app as adk_app
from research_assistant.app_utils.telemetry import setup_telemetry
from research_assistant.app_utils.typing import Feedback

load_dotenv()


class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        """Initialize the agent engine app with logging and telemetry."""
        vertexai.init()
        setup_telemetry()
        super().set_up()
        logging.basicConfig(level=logging.INFO)
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback — exposed as a custom operation."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Register custom operations on top of ADK's standard ones."""
        operations = super().register_operations()
        operations[""] = operations.get("", []) + ["register_feedback"]
        return operations


logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

agent_engine = AgentEngineApp(
    app=adk_app,
    artifact_service_builder=lambda: (
        GcsArtifactService(bucket_name=logs_bucket_name)
        if logs_bucket_name
        else InMemoryArtifactService()
    ),
)
```

Three things to notice:

1. **`AdkApp` is the base class.** Vertex's template for ADK agents. It already knows how to call `runner.run_async()` and translate the I/O to the Vertex SDK.
2. **`set_up()` runs once per Vertex worker boot.** Put one-time wiring here (telemetry, logging client). Avoid heavy startup — it adds cold-start time.
3. **`register_operations()` is how you add custom HTTP-shaped ops.** Vertex exposes them as RPCs alongside the standard chat ops (`async_query`, `stream_query`, etc.).

## ☁️ Deploying it

```bash
adk deploy agent_engine \
    --project=$PROJECT \
    --region=us-central1 \
    --staging_bucket=gs://my-staging \
    --display_name="research-assistant" \
    ./research_assistant
```

> **⚠️ Deprecation — `--staging_bucket`**
>
> `--staging_bucket` is still accepted but emits a deprecation warning ("This argument is no longer required or used" — see `adk-python/src/google/adk/cli/cli_tools_click.py:2256` + the `_deprecate_staging_bucket` callback at L1559). The modern shape in the Python SDK is `client.agent_engines.create(config=...)` — Vertex now manages staging internally. Drop the flag when you can; new scripts shouldn't include it.

What this does:

1. Packages your project into a zip.
2. Uploads to `gs://my-staging`.
3. Calls Vertex's `agent_engines.create(...)` with `agent_engine_app:agent_engine` as the entrypoint.
4. Vertex builds an isolated runtime, installs deps, instantiates `AgentEngineApp`.
5. Returns an **Agent Engine Resource ID** (e.g., `projects/123/locations/us-central1/reasoningEngines/456`).

That ID is now your public handle. To call the deployed agent:

```python
# Work/22_DeploymentModels/03_call_agent_engine.py
from vertexai import agent_engines

ae = agent_engines.get("projects/123/locations/us-central1/reasoningEngines/456")
for event in ae.stream_query(
    user_id="alice",
    session_id="sess-001",
    message="What is the speed of light in m/s?",
):
    print(event)
```

The Vertex SDK abstracts away the HTTP entirely — you call methods on a Python proxy.

## ☁️ Sessions — managed by default

Agent Engine wires `VertexAiSessionService` automatically. Sessions persist across container restarts, scale-out events, region failover. You don't provision a DB.

```python
# from Vertex's side — agent_engine_app.py does NOT explicitly wire this
adk_app.session_service  # → VertexAiSessionService (auto-injected by the runtime)
```

Trade-off: you cannot query sessions via SQL. You go through the Vertex API or the AE-aware Python SDK.

## ☁️ Custom operations — when ADK routes are not enough

The standard ADK ops are `query`, `async_query`, `stream_query`, `register_feedback` (if you register it). If you need other endpoints — e.g., bulk inference, evaluation triggers, admin actions — register them via `register_operations`:

```python
def my_custom_op(self, args: dict) -> dict:
    """An operation Vertex exposes as a callable RPC."""
    ...
    return {"result": ...}

def register_operations(self) -> dict[str, list[str]]:
    ops = super().register_operations()
    ops[""] = ops.get("", []) + ["my_custom_op"]
    return ops
```

Operation arg types are inferred via Pydantic. Return types must be JSON-serializable.

## ☁️ Gemini Enterprise registration (briefly)

If you want your agent to show up in **Gemini Enterprise** (Google's productized agent surface), you register the Agent Engine resource through Discovery Engine API. The `adk-ae-oauth` sample shows the full dance (`tools/register_oauth.py` + `make register-gemini-enterprise`). Page 06 covers the IAM side.

## ⚠️ Gotcha — `set_up()` runs once per worker, not once globally

If you log "AgentEngineApp ready" in `set_up`, you'll see it log multiple times — once per Vertex worker boot, once per cold start, possibly more. Don't put one-time global side effects (DB schema migrations) there.

## ⚠️ Gotcha — local development with `AdkApp`

`adk web` does NOT load `agent_engine_app.py` — it loads `agent.py` directly. Your `set_up()` telemetry will not run locally. Either:

- Replicate the `set_up()` wiring in a `local_dev.py` you run instead of `adk web`.
- Accept the gap and test telemetry only after deploy.

The `adk-ae-oauth` sample's Makefile has both `make playground` (no telemetry) and `make deploy-and-test` (telemetry-on).

## 🐍 Detour suggestion

If `AdkApp`, Vertex resource IDs, and Pydantic-typed operations are still moving parts, take 25 min on [[AgentEngine]]. It covers the platform primitives this page composes.

## 🚀 In Production

> **🚀 In Production**
>
> Agent Engine **silently absorbs the session persistence layer**. That's a feature (no DB to operate) and a trap (you don't see the schema, can't `SELECT * FROM sessions WHERE user_id = ...`). Plan how you'll observe sessions in prod: the Vertex API has `list_sessions` + `get_session`, but no SQL. If your support team needs to grep through user history, build a small Cloud Function that exports session JSON to BigQuery on a cron — Vertex does not do that for you.

> ❓ **Ask the student:** "If you need a sidecar that translates a proprietary protocol before the agent sees the request, which path?" *(Not Agent Engine — it doesn't do sidecars. GKE, or Cloud Run with the translator in front.)*

---

[← Prev: 02_CloudRunPath](02_CloudRunPath.md)  [↑ Map](../../MAP.md)  [Next: 03A_GKE →](03A_GKE.md)
