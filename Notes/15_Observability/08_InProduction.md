---
module: 15_Observability
page: 08_InProduction
title: Observability in production — the hardening checklist
estimated_minutes: 20
prereqs: [15_Observability/07]
concepts: [sampling, PII, cardinality, collector resilience, correlation IDs]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/07_DissectingSample](07_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/09_KnowledgeCheck →](09_KnowledgeCheck.yml)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 08 In Production

---

## 🚀 The checklist

Consolidates the `🚀 In Production` callouts from this module plus the gotchas you can only see at scale.

### 1. Sample, don't trace every request

At 10 RPS, full tracing = 864k traces/day. Most are duplicates of each other.

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
provider = TracerProvider(sampler=TraceIdRatioBased(0.05))  # 5%
```

Sample by trace-id (not per-span) so a sampled trace is *complete*. Always log errors at 100% (the `ParentBased` sampler covers this).

### 2. PII in spans — sanitize or omit

Span attributes default to the raw value. A `prompt="my email is alice@x.com"` attribute = PII leak in your tracing backend.

Mitigations:

- Use a `before_model_callback` to redact the prompt before it becomes a span attribute (see [[16_ProductionSecurity/05_GuardrailsCookbook]] § PII redaction).
- Or, omit `prompt`/`completion` attributes entirely; record only metadata (token counts, model name).

### 3. Span attribute cardinality limits

OTel backends index attributes. Unique-per-request values destroy the index.

- ✅ `model.name`, `tool.name`, `agent.name`, `tenant_id`, `model.region`.
- ❌ `session.id`, `user.id`, `prompt_text`, `trace.id` — *as metric labels*. As span IDs (lookup-only) they are fine.

### 4. The OTel collector is a single point of failure

The agent → collector hop is over the network. If the collector is down, **the agent must not block on telemetry**.

- Use `BatchSpanProcessor` (it buffers and retries) — never the simple processor in prod.
- Run the collector as a sidecar (per-pod) or DaemonSet (per-node), not as a remote service.
- Cap buffer size; on overflow, drop telemetry, *never* the user request.

### 5. Correlate trace IDs with user-visible request IDs

When support gets *"the agent did something weird"*, you need the trace.

- Surface a `request_id` to the user (footer of the response, ticket number, header).
- Stamp `request.id` on the root span as an attribute.
- Index by `request.id` in your tracing backend.

Without this link you will spend hours grepping logs and still not find it.

### 6. Cost guardrails on the analytics sink

The BigQuery sink fills up. Without governance:

- A `SELECT *` against the events table over 90 days can scan TBs → hundreds of dollars per query.
- A runaway agent (loop bug) can write GBs of events per hour.

Mitigations:
- Partition the BQ table by `event_ts` (day).
- Set a project-level BQ scan-byte cap.
- Add an alert on event-write QPS — a sudden spike is a loop-bug signature.
- Auto-expire old partitions (`time_partitioning.expiration_ms`).

### 7. Don't store secrets in events

Tool args may include API keys, OAuth tokens, ad-hoc passwords. The plugin will happily write them to BigQuery.

- Sanitize in `before_tool_callback`. Replace sensitive arg values with `"<redacted>"` before they enter the trace/log/BQ pipeline.
- Cross-link to [[16_ProductionSecurity/04_SecretsHandling]].

### 8. Match retention to compliance

- Traces — 7-30 days (debugging horizon).
- BQ analytics — 90-365 days (trend analysis).
- Audit log of *guardrail decisions* — whatever your regulator requires (often years).

Set partition expiration *before* the data piles up. Retrofitting deletion at TB scale is painful.

> 🤖 **Tutor:** ask the student which of these eight items their M4 auditor currently violates. Most will fail 4-6 of them on a fresh build — and that's fine for an exercise. The mini-drill on page 10 fixes one (correlation IDs via stdout exporter).

---

[← Prev: 15_Observability/07_DissectingSample](07_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/09_KnowledgeCheck →](09_KnowledgeCheck.yml)
