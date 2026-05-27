---
module: Detours
page: OpenTelemetry
title: OpenTelemetry — traces, spans, metrics for agents
estimated_minutes: 35
icon: 📊
prereqs: []
concepts: [trace, span, attribute, metric, exporter, otlp, collector, sampling]
---

[← Back to Map](../../MAP.md)

Triggered from: `15_Observability` (the whole module sits on top of OTel).

> Take this detour before module 15 if "trace vs span vs metric" is fuzzy, or if you've never run an OTLP exporter. ~35 min — long for a detour, but observability is load-bearing for prod agents.

---

## 📊 1. The mental model — traces are trees of spans

```
  trace_id = abc...                    one request, one trace
  ├── span: HTTP /chat       [0ms → 850ms]
  │   ├── span: agent.run    [10ms → 800ms]
  │   │   ├── span: llm.call.gemini   [20ms → 600ms]
  │   │   └── span: tool.get_weather  [610ms → 780ms]
  │   │       └── span: http.get      [615ms → 770ms]
  │   └── span: serialize    [810ms → 845ms]
```

Concepts in three sentences:

- A **trace** = one logical operation, identified by a `trace_id`.
- A **span** = one unit of work inside that operation; has `start_time`, `end_time`, `attributes`, optional `events`, optional `links` to other traces.
- Spans nest. The tree shape is the call graph.

That's the whole data model. Everything else is plumbing.

---

## 📊 2. Three signal types — pick the right one

| signal     | shape                | answers                                   |
|------------|----------------------|-------------------------------------------|
| **Traces** | per-request tree     | "what happened on *this* request, where did time go?" |
| **Metrics**| aggregates over time | "p99 latency this week? error rate by tool?" |
| **Logs**   | timestamped messages | "what did the code print at 14:32:01?"    |

Rule:
- Per-request causality → trace.
- Dashboards and alerts → metric.
- Free-text debugging → log.

Metric flavors:
- **Counter** — monotonic up (requests served, tokens used).
- **Histogram** — distribution (latency, payload size).
- **Gauge** — instantaneous value (queue depth, in-flight requests).

---

## 📊 3. Exporters and the Collector

The SDK produces data; an **exporter** ships it somewhere:

```
  your app  ──OTLP──►  OTel Collector  ──►  Cloud Trace
                          │           ──►  Cloud Monitoring
                          │           ──►  Jaeger (dev)
                          └─── filter, sample, batch, redact
```

Common exporters:
- **OTLP** (gRPC or HTTP) — the standard wire format. Almost always what you want.
- **Console** — print to stdout. Great for dev / learning.
- **Cloud Trace / Cloud Monitoring** — GCP-native, fewer hops, but ties you to GCP.
- **Jaeger / Zipkin** — open-source UIs for local exploration.

The **OTel Collector** is a separate process that receives OTLP, runs **processors** (batching, sampling, attribute redaction, tail-based filtering), and forwards to one or more backends. It's the buffer between your app and the storage system. In prod, always have one — your app should never block on the backend being up.

---

## 📊 4. The 6-line Python instrumentation

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter, BatchSpanProcessor,
)

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("parent") as parent:
    parent.set_attribute("agent.name", "researcher")
    with tracer.start_as_current_span("llm.call"):
        ...
    with tracer.start_as_current_span("tool.call"):
        ...
```

Output (trimmed):

```
{ "name": "llm.call",  "trace_id": "abc...", "parent_id": "1...", "duration": 0.4s }
{ "name": "tool.call", "trace_id": "abc...", "parent_id": "1...", "duration": 0.1s }
{ "name": "parent",    "trace_id": "abc...", "parent_id": null,   "duration": 0.5s }
```

Children carry the same `trace_id` and reference `parent_id`. That's the tree.

---

## 📊 5. ADK ships with this wired

ADK emits OTel traces for every agent run, LLM call, and tool call out of the box — you don't write the spans, you just set a provider:

```python
# Anywhere before runner.run_async
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
    # or: OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
)
trace.set_tracer_provider(provider)
```

Run an agent → spans flow to your Collector (port 4317 is OTLP/gRPC's default). On GCP, the `CloudTraceSpanExporter` skips the Collector and posts directly to Cloud Trace. Module `15_Observability` walks the full setup including metrics.

> ⚠️ **Gotcha.** Without the `http://` scheme (or `insecure=True`), the exporter assumes TLS and your local collector connection will fail with an SSL handshake error — a common first-run trap.

> 📦 **Install note.** `opentelemetry-sdk` ships only the SDK plus the console exporter. The OTLP exporter (`opentelemetry.exporter.otlp.proto.grpc.trace_exporter` above) lives in a **separate** package: `pip install opentelemetry-exporter-otlp` (which pulls in both the gRPC and HTTP variants), or `opentelemetry-exporter-otlp-proto-grpc` / `opentelemetry-exporter-otlp-proto-http` for just one transport. Cloud Trace, Jaeger, Zipkin exporters are all separate packages too. Stack-trace `ModuleNotFoundError: No module named 'opentelemetry.exporter.otlp'` always means "you didn't install the exporter package."

---

## 📊 6. Pitfalls

⚠️ **High-cardinality attributes.** Don't put user IDs, session IDs, or trace IDs in attribute *keys*. (Values are fine.) Cardinality explosion = your metrics backend bills you a fortune and queries time out.

⚠️ **Sampling decisions.** In prod, 100% trace export is usually wasteful. **Head-based sampling** (sample at request start) is cheap; **tail-based** (decide after the trace finishes, so you always keep errors) needs the Collector. 1-5% head sampling is a reasonable default for high-traffic services.

⚠️ **Span leaks.** A span that never closes (forgot the `with` block, exception path) shows up as a missing leaf. Always use `start_as_current_span` as a context manager — `start_span` is a footgun.

⚠️ **PII in attributes.** Anything you `.set_attribute()` ends up in your tracing backend, indefinitely. Don't put user messages, API keys, or PII directly in attributes — redact at the Collector with `attributes` processor.

⚠️ **Sync vs async context propagation.** OTel auto-propagates context across `await` boundaries — but only if you use `start_as_current_span`. Manually-managed spans across `await` will lose the parent link.

> **🚀 In Production**
>
> Run an OTel Collector sidecar (or DaemonSet on GKE). Your app exports to `localhost:4317`; the Collector batches, samples, and forwards. This means: backend outages don't kill your app, redaction happens centrally, and switching backends (Jaeger → Cloud Trace) is a Collector config change with zero app deploys.

---

## 🛠 Have the student try

Write the smallest possible trace and watch it print to the console:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer("demo")

with tracer.start_as_current_span("parent") as p:
    p.set_attribute("kind", "demo")
    with tracer.start_as_current_span("child-a"):
        pass
    with tracer.start_as_current_span("child-b") as cb:
        cb.add_event("midway")
```

Run it, look at the JSON. Verify:

1. All three spans share the same `trace_id`.
2. `parent`'s `parent_id` is `null`; the children's points at `parent`'s span_id.
3. `child-b` has an `events` array with one `midway` entry.

Now swap `ConsoleSpanExporter` for `OTLPSpanExporter(endpoint="http://localhost:4317")` (or `OTLPSpanExporter(endpoint="localhost:4317", insecure=True)`), run `docker run -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one`, open `http://localhost:16686`, and find your trace.

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — almost certainly `15_Observability/01_TracingBasics`.
