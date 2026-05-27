---
module: 15_Observability
page: 05_Metrics
title: The four metrics every agent needs
estimated_minutes: 20
prereqs: [15_Observability/04]
concepts: [metrics, cost, latency, error rate, cardinality]
icon: 📊
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/04_TracingAnAgentRun](04_TracingAnAgentRun.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/06_BigQueryAsSink →](06_BigQueryAsSink.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 05 Metrics

---

## 📊 The four

Traces let you debug *one* request. Metrics let you watch *all* requests over time. The four agents care about:

1. **Tokens per turn** — distribution of `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens`. Watch the tail. A turn jumping from 2k to 50k tokens is a context-bloat regression.
2. **Latency per tool** — p50/p95/p99 per `gen_ai.tool.name`. Your slow user complaint is almost always one tool.
3. **Error rate per tool** — `errors / total` per `gen_ai.tool.name`. A tool silently failing is the second most common bug.
4. **Cost per model** — `(input_tokens * price_in + output_tokens * price_out)` rolled up by `gen_ai.request.model`. Finance will ask.

(The `gen_ai.*` attribute names follow the OpenTelemetry GenAI semantic conventions — see `google/adk/telemetry/tracing.py:44-58`.)

## 🛠 Emitting metrics via OTel

ADK emits the underlying *spans*. For aggregate metrics you have two paths:

**Path A — derive from spans.** Most backends (Cloud Trace + Cloud Monitoring, Honeycomb, Datadog) can build histograms from span attributes. No extra code in the agent.

**Path B — emit metrics directly.** Use the OTel metrics SDK from a callback:

```python
from opentelemetry import metrics
meter = metrics.get_meter("adk.agent")
tokens_hist = meter.create_histogram("agent.tokens.per_turn")

def after_model_callback(callback_context, llm_response):
    usage = llm_response.usage_metadata  # if available
    if usage:
        tokens_hist.record(
            usage.total_token_count,
            attributes={"model": llm_response.model},
        )
```

Path A is cheaper and recommended unless you need a metric the spans don't expose.

## ⚠️ Gotcha — cardinality kills

Metric labels are *aggregated* in the backend. Putting `gcp.vertex.agent.session_id` as a label = one timeseries per session = bill explosion + index collapse.

Allowed as labels: `gen_ai.request.model`, `gen_ai.tool.name`, `gen_ai.agent.name`, `tenant_id` (if low cardinality).
**Never** as labels: `gcp.vertex.agent.session_id`, `gcp.vertex.agent.invocation_id`, `user.id`, `request.id`, `trace.id`.

Those high-cardinality IDs belong on *spans* (where they help you jump from a metric anomaly into a specific trace).

> 🛠 **Have the student run:** pick the busiest tool in their M4 auditor. Predict p50/p95 latency. Then run the agent 10× with varied prompts and inspect the trace timing. Was the prediction right?

> 🚀 **In Production**
>
> Set up a **cost-per-session** dashboard before launch. Surprise: a small percentage of users (long sessions, runaway loops) drive >50% of token cost. You cannot tune what you do not measure.

---

[← Prev: 15_Observability/04_TracingAnAgentRun](04_TracingAnAgentRun.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/06_BigQueryAsSink →](06_BigQueryAsSink.md)
