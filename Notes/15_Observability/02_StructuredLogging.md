---
module: 15_Observability
page: 02_StructuredLogging
title: Structured logging with LoggingPlugin
estimated_minutes: 20
prereqs: [13_Plugins/03, 15_Observability/01]
concepts: [LoggingPlugin, JSON logs, log levels, correlation]
icon: 🪵
in_production: true
detours_suggested: [PY_logging]
---

[← Prev: 15_Observability/01_WhyObservability](01_WhyObservability.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/03_OpenTelemetryBasics →](03_OpenTelemetryBasics.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 02 Structured Logging

---

## 🧠 The plugin

`LoggingPlugin` is the simplest observability primitive in ADK. It hooks every lifecycle callback (model in, model out, tool in, tool out, agent enter, agent exit) and emits a log line for each.

```python
from google.adk.apps import App
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.agents import Agent

root_agent = Agent(model="gemini-2.5-flash", name="research_assistant", ...)

app = App(
    name="research_assistant",
    root_agent=root_agent,
    plugins=[LoggingPlugin()],
)
```

That's the entire wiring. The plugin is registered at the `App` level so it sees every agent in the graph.

## 🛠 What you get

Run the agent and `stderr` shows:

```json
{"ts": "2026-05-27T14:02:11Z", "level": "INFO", "event": "model_request",
 "agent": "research_assistant", "session": "sess_abc",
 "model": "gemini-2.5-flash", "tokens_in": 412}
{"ts": "2026-05-27T14:02:12Z", "level": "INFO", "event": "tool_call",
 "agent": "research_assistant", "tool": "google_search",
 "args": {"q": "ADK 2.0 release date"}}
{"ts": "2026-05-27T14:02:13Z", "level": "INFO", "event": "tool_result",
 "tool": "google_search", "status": "ok", "latency_ms": 980}
```

Three things to notice:

1. **JSON, not free text.** Grep-able and ship-able to a log aggregator.
2. **`session` field.** Correlates lines from one user conversation.
3. **`latency_ms` on `tool_result`.** First-class duration.

## 🐍 Detour suggestion

If `logging.getLogger(__name__)`, handlers, and the Python log hierarchy feel hand-wavy, take 20 min on [[PY_logging]] before page 03. The plugin sits on top of the stdlib `logging` module.

> 🛠 **Have the student run:** add `LoggingPlugin()` to the M4 auditor's `App`, then `adk run` it with one prompt. Have them paste the first 5 log lines. Ask which line answered *which* of the three questions from page 01.

## ⚠️ Gotcha — log volume

`LoggingPlugin` defaults to INFO. A long-tool-call run can be 30+ lines. Multiply by traffic and you have a bill.

Knobs to turn:

- **Log level**: drop to WARN in prod to keep only errors.
- **Sampling**: log 1-of-N requests (page 08).
- **Sink choice**: stdout in dev, Cloud Logging in prod (router takes care of cost).

> 🚀 **In Production**
>
> Never log the raw model prompt or tool args verbatim — they may contain PII or secrets. Either *sanitize* in a `before_*_callback` (see [[16_ProductionSecurity/05_GuardrailsCookbook]]) or scope the field with an allow-list.

---

[← Prev: 15_Observability/01_WhyObservability](01_WhyObservability.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/03_OpenTelemetryBasics →](03_OpenTelemetryBasics.md)
