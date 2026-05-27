---
module: 15_Observability
page: 03_OpenTelemetryBasics
title: OpenTelemetry — traces, spans, attributes
estimated_minutes: 20
prereqs: [15_Observability/02]
concepts: [OpenTelemetry, span, trace, attributes, exporter]
icon: 📡
in_production: true
detours_suggested: [OpenTelemetry]
---

[← Prev: 15_Observability/02_StructuredLogging](02_StructuredLogging.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/04_TracingAnAgentRun →](04_TracingAnAgentRun.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 03 OTel Basics

---

## 🧠 Vocabulary

| Term | One-liner |
|---|---|
| **Trace** | A single end-to-end transaction. Has a `trace_id`. |
| **Span** | One unit of work inside a trace. Has start/end timestamps and a parent. |
| **Attributes** | Key-value tags on a span. (`model="gemini-2.5-flash"`, `tokens.in=412`.) |
| **Exporter** | Where spans are shipped. (stdout, OTLP collector, Cloud Trace, Jaeger…) |

A trace is a tree of spans. Reading the tree top-down tells you *what called what*. Reading left-right (by timestamp) tells you *what was slow*.

## 🧠 ADK's built-in OTel hooks

ADK uses OpenTelemetry natively. When the OTel SDK is installed and a tracer provider is configured, ADK automatically emits spans for:

- Each `Runner.run_async()` invocation (the outer span).
- Each agent invocation (sub_agents nest as child spans).
- Each model call.
- Each tool call.

You do **not** instrument by hand. You only configure the exporter.

## 🛠 Minimal exporter setup (stdout, for dev)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, ConsoleSpanExporter,
)

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Now build & run the agent normally — spans print to stdout.
```

Run the agent once; you will see a JSON blob per span, ending with the parent runner span.

## 🛠 Minimal exporter setup (OTLP collector, for prod)

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317"))
)
```

Same shape, different exporter. The collector forwards to your backend (Cloud Trace, Jaeger, Honeycomb, Tempo…).

> 🧭 **If the student looks stuck on the OTel data model:** suggest the [[OpenTelemetry]] detour. The acronym soup (W3C TraceContext, OTLP, BSP, SDK vs API) is worth one careful read.

## 🧠 The mental flip

Logs answer *did this happen?* — one line, one fact.
Traces answer *what is the shape of this request?* — a tree of facts with causal links.

The same `tool_call` you logged in page 02 also becomes a span. The trace tells you it ran *between* model call #1 and model call #2, took 1.1s, and was a child of `agent.research_assistant`. The log doesn't.

> 🚀 **In Production**
>
> In Google Cloud the standard exporter is `CloudTraceSpanExporter`. The OTLP collector pattern is still recommended for buffering and to keep your app independent of the backend. See page 08.

---

[← Prev: 15_Observability/02_StructuredLogging](02_StructuredLogging.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/04_TracingAnAgentRun →](04_TracingAnAgentRun.md)
