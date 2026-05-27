---
module: 22_DeploymentModels
page: 07_ObservabilityWiring
title: Observability wiring per platform
estimated_minutes: 20
prereqs: [22_DeploymentModels/06, 15_Observability/08]
concepts: [OTel exporter, Cloud Trace, Cloud Logging, BigQuery sink, per-platform wiring]
icon: 📊
in_production: true
detours_suggested: [OpenTelemetry]
---

[← Prev: 06_AuthAndIAM](06_AuthAndIAM.md)  [↑ Map](../../MAP.md)  [Next: 08_SecretsAcrossPlatforms →](08_SecretsAcrossPlatforms.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 07 Observability wiring

---

## 📊 The signal stack across platforms

| Signal       | Cloud Run                                | Agent Engine                    | GKE                                                |
|--------------|------------------------------------------|---------------------------------|----------------------------------------------------|
| **Logs**     | stdout → Cloud Logging (auto)            | stdout → Cloud Logging (auto)   | stdout → Cloud Logging (via Fluentbit sidecar)     |
| **Traces**   | You wire OTel exporter                   | **Wired to Cloud Trace by default** | You wire OTel exporter                         |
| **Metrics**  | Cloud Monitoring (basic) + custom OTel   | Vertex-managed                  | Cloud Monitoring + Prometheus + custom OTel        |
| **BigQuery sink** | You wire `BigQueryAgentAnalyticsPlugin` (module 15) | You wire it       | You wire it                                        |

The pattern across platforms: **logs are free, traces require setup, metrics need custom work**. Agent Engine compresses the trace+logs setup to ~0.

## 📊 Cloud Run / GKE — wire OTel to Cloud Trace

```python
# Work/22_DeploymentModels/research_assistant/telemetry.py
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

def setup_telemetry():
    resource = Resource.create({
        SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "research-assistant"),
    })
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(CloudTraceSpanExporter())
    )
    trace.set_tracer_provider(provider)
```

Then in your `server.py`:

```python
# Work/22_DeploymentModels/research_assistant/server.py — augmented
from research_assistant.telemetry import setup_telemetry

setup_telemetry()  # MUST come before get_fast_api_app(...)

from google.adk.cli.fast_api import get_fast_api_app
app = get_fast_api_app(agents_dir=..., web=False, ...)
```

**Order matters** (module 15 page 03 § gotcha): `set_tracer_provider` before constructing the App, otherwise ADK's spans go to a noop provider.

## 📊 Agent Engine — telemetry pattern in `agent_engine_app.py`

The `adk-ae-oauth` sample puts telemetry in `set_up()`:

```python
class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        vertexai.init()
        setup_telemetry()       # <-- BEFORE super().set_up()
        super().set_up()
```

Vertex injects the Cloud Trace exporter automatically when you call `vertexai.init()`. Your `setup_telemetry()` only needs to handle anything custom — extra exporters, custom resource attributes.

## 📊 BigQuery analytics sink — same code, three platforms

`BigQueryAgentAnalyticsPlugin` (module 15 page 06) is wired on the `App`, not the platform:

```python
# Work/22_DeploymentModels/research_assistant/agent.py
from google.adk.apps import App
from google.adk.plugins.analytics.bigquery import BigQueryAgentAnalyticsPlugin

bq_logging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id="adk_agent_analytics",
    table_id="agent_events",
    location="us-east1",
)

app = App(
    name="research_assistant",
    root_agent=root_agent,
    plugins=[bq_logging],
)
```

Because the wiring is in the App, the same `agent.py` ships to Cloud Run, Agent Engine, or GKE unchanged. Only the **environment vars** (PROJECT_ID etc.) differ per platform.

The dataset must be **provisioned out of band** (cross-link: module 15 page 07 § `prepare_dataset.py`). The plugin auto-creates the table.

## 📊 Per-platform gotchas

### Cloud Run
- Cold-started instances might not flush the BatchSpanProcessor before shutdown. Lower `schedule_delay_millis` to 1000 (default 5000) to flush more aggressively, or use a `SimpleSpanProcessor` for last-minute spans (with cost overhead).
- `gcloud run logs tail` is easier than the Cloud Logging UI for live debugging.

### Agent Engine
- Cannot run a sidecar OTel collector. The Vertex-injected exporter is your only path.
- Custom attributes via `tracer.start_as_current_span("X", attributes={"my.attr": "v"})` work — they end up in Cloud Trace as span attributes.

### GKE
- Run the **OTel Collector as a DaemonSet** (one per node). Pods send to `localhost:4317` via OTLP. The collector handles batching, retries, fan-out to multiple backends (Cloud Trace + Honeycomb + Datadog).
- Workload Identity must include `roles/cloudtrace.agent` on the GSA bound to the pod, otherwise spans 403.

## 📊 Logs — structured everywhere

Use JSON, not free text:

```python
import logging, json, sys
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
            "trace_id": ...,  # pull from active OTel span if available
        })

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)
```

Cloud Logging auto-parses stdout JSON into structured log entries. The `severity`, `trace`, and `httpRequest` fields are auto-mapped if you use the conventional names. Cross-link: module 15 page 02 § `LoggingPlugin`.

## ⚠️ Gotcha — trace context propagation through tool calls

When a tool calls another service (BigQuery, HTTP API), the trace context must propagate so the downstream span is parented correctly. ADK's `LoggingPlugin` and OTel auto-instrumentation handle this for HTTP libraries that respect `traceparent`. For custom clients, inject explicitly:

```python
from opentelemetry import propagate
headers = {}
propagate.inject(headers)  # adds 'traceparent' header
httpx.get(url, headers=headers)
```

Without this, your trace will look like a flat tree of disconnected spans.

## 🚀 In Production

> **🚀 In Production**
>
> **Traces are the most expensive observability signal**. At 100 RPS with full tracing you can spend $500+/month on Cloud Trace alone. Sample (module 15 page 08 item #1) and budget. Conversely, the **BigQueryAgentAnalyticsPlugin** is the cheapest long-horizon signal — analytics queries cost cents, the storage is cheap, retention is your call. Many teams sample traces 1-5% but log to BigQuery 100% for the audit trail.

> 🧭 **If the student looks stuck:** suggest [[OpenTelemetry]] detour — it covers OTLP, BatchSpanProcessor, the trace-context spec the rest of this page assumes.

---

[← Prev: 06_AuthAndIAM](06_AuthAndIAM.md)  [↑ Map](../../MAP.md)  [Next: 08_SecretsAcrossPlatforms →](08_SecretsAcrossPlatforms.md)
