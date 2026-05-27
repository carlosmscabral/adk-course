---
module: 13_Plugins
page: 09_InProduction
title: Plugins in production
estimated_minutes: 20
prereqs: [13_Plugins/08]
concepts: [ordering, latency, silent swallowing, async telemetry]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 13_Plugins/08_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/10_KnowledgeCheck →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 09 In Production

# 🚀 The four plugin gotchas nobody mentions in the docs

## 1. Order is part of the API

Plugins fire in the order you pass them. Same hook, different plugins: the first one runs first. If two plugins mutate the same field (`ContextFilter` and a custom redactor, for example), the order changes the output.

**Mitigation.** Document the order in code:

```python
plugins=[
    # 1. Redact PII before the LLM sees it. Run BEFORE all other plugins
    #    so logs see redacted content too.
    PiiRedactorPlugin(),
    # 2. Trim history.
    ContextFilterPlugin(...),
    # 3. Log what we're sending.
    LoggingPlugin(),
    # 4. Telemetry to BQ.
    BigQueryAgentAnalyticsPlugin(...),
]
```

Don't rely on lexicographic or registration order — be explicit.

## 2. A slow plugin slows every event

Plugins are on the hot path. If a plugin makes a synchronous network call to an external service in `before_model_callback`, you've added that latency to every model call.

**Mitigation.**

- Network calls in plugins must be `async` and either non-blocking (fire-and-forget) or budgeted with a tight timeout.
- For telemetry plugins, batch writes (`BigQueryAgentAnalyticsPlugin` supports it — configure it).
- Measure: add a latency histogram per plugin hook in dev before shipping.

## 3. Silent error swallowing

A plugin that does `try/except Exception: pass` inside a hook turns failures into ghosts — the runner reports success, but the side effect (log, redact, write) never happened. PII leaks, audit logs are missing rows, you're flying blind.

**Mitigation.**

- Re-raise after logging the error to a metric ("plugin_failure_total" labeled by plugin name + hook).
- Decide explicitly for each plugin whether a failure should be fatal or surfaced-and-continue. Both are valid; the silent default is not.

## 4. Telemetry plugins must be async / batched

`BigQueryAgentAnalyticsPlugin` is the canonical example. The default may be synchronous-on-write. At any real volume, that costs you wall-clock time per event.

**Mitigation.** Configure for batched async writes; use a background flush. Tune batch size to match BQ ingestion sweet spot (a few hundred to a few thousand rows per batch).

## Checklist before launch

- [ ] Plugin order documented inline with reasoning.
- [ ] No synchronous network calls on hot-path hooks.
- [ ] Every plugin defines what "failure" means (re-raise vs surface-as-metric).
- [ ] Telemetry plugins write async/batched.
- [ ] A latency histogram per plugin in your dashboard.
- [ ] If you have a "policy" plugin (safety, refusal, redaction), it's first in the list.

## Plugin vs callback — final word

Use a **callback** when:

- The concern is genuinely per-agent.
- You need access to `CallbackContext` specifics that aren't in plugin hook signatures.

Use a **plugin** when:

- The concern is cross-cutting.
- You'd otherwise add the same callback to every agent.
- You want runtime-toggleable policy (compose at `Runner(plugins=...)`).

> 🤖 **Tutor:** This page is the "graduation" page for the module. The student should be able to take their M1 agent, identify three potential cross-cutting concerns (logging, retry, redaction), and add them via plugins without changing the agent code.

---

[← Prev: 13_Plugins/08_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/10_KnowledgeCheck →]
