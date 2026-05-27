---
module: 15_Observability
page: 04_TracingAnAgentRun
title: One Runner.run_async() = one trace
estimated_minutes: 20
prereqs: [15_Observability/03]
concepts: [trace, span hierarchy, sub_agent nesting]
icon: 🧵
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/03_OpenTelemetryBasics](03_OpenTelemetryBasics.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/05_Metrics →](05_Metrics.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 04 Tracing An Agent Run

---

## 🧠 The unit of work

One call to `runner.run_async(...)` produces **one trace** — one `trace_id` — containing many spans:

- 1 outer span for the runner.
- 1 span per agent invocation. (sub_agents nest as children.)
- 1 span per model call.
- 1 span per tool call.

A loop with 3 turns and 2 tool calls per turn = ~13 spans in one trace.

## 🧵 ASCII timeline

```
{{ _figures/trace_timeline.txt }}
```

(Open `_figures/trace_timeline.txt` for the full view.)

The point: you see *what happened*, *in what order*, *for how long*, all under one `trace_id`.

## 🧠 Span attributes you will rely on

| Attribute | Where | Why it matters |
|---|---|---|
| `model.name` | LLM span | Per-model cost rollups. |
| `tokens.in` / `tokens.out` | LLM span | Cost and prompt-bloat detection. |
| `tool.name` | Tool span | Slowest-tool rollups. |
| `tool.status` | Tool span | Error-rate per tool. |
| `session.id` | Runner span | Correlate with the user's complaint. |
| `agent.name` | Agent span | Which sub_agent did what. |

These attributes are emitted automatically by ADK. You can add custom attributes from a callback via `tool_context` / `callback_context` — useful for tagging traces with `request_id`, `user_tier`, etc.

> 🛠 **Have the student run:** with the ConsoleSpanExporter from page 03, send a prompt that needs 2 tool calls (e.g., the research_assistant looking up something then summarizing). Have them count the spans and identify the parent of each.

## ⚠️ Gotcha — span cardinality

`agent.name`, `tool.name`, `model.name` are *low* cardinality (a handful of values). Backend indices love them.

`session.id`, `user.id`, `request.id` are *high* cardinality (one per request). They are *useful* as span IDs / labels but should **not** be used as metric labels — see page 05.

> 🚀 **In Production**
>
> When a customer reports "my agent did something weird at 3:42pm" you will need the trace_id. Build your UI / chat surface so it logs the trace_id back to the user (e.g., as a request reference). Without that link, you are grep-ing logs blind. See [[15_Observability/08_InProduction]].

---

[← Prev: 15_Observability/03_OpenTelemetryBasics](03_OpenTelemetryBasics.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/05_Metrics →](05_Metrics.md)
