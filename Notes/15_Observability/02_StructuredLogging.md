---
module: 15_Observability
page: 02_StructuredLogging
title: Structured logging with LoggingPlugin
estimated_minutes: 20
prereqs: [13_Plugins/03, 15_Observability/01]
concepts: [LoggingPlugin, ANSI stdout, structlog, log levels, correlation]
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

Run the agent and **stdout** shows ANSI-grey, human-readable lines (one per lifecycle event):

```text
[LoggingPlugin] 🚀 USER MESSAGE
   Session: sess_abc | Invocation: inv_001
   Content: "what's the latest ADK release?"
[LoggingPlugin] 🤖 MODEL REQUEST
   Agent: research_assistant
   Model: gemini-2.5-flash
[LoggingPlugin] 🔧 TOOL CALL
   Tool Name: google_search
   Agent: research_assistant
   Arguments: {"q": "ADK 2.0 release date"}
[LoggingPlugin] ✅ TOOL RESPONSE
   Tool Name: google_search
```

Three things to notice:

1. **Human-readable lines, not JSON.** Great for tailing in a dev terminal, **bad** as input to a log aggregator (no fields to grep by, ANSI escapes get in the way).
2. **Session + invocation IDs** appear at the top of each user-message line — that is your correlation key.
3. **Emoji + indentation** are the format; the plugin uses `print()` with `\033[90m...\033[0m` wrappers (see `google/adk/plugins/logging_plugin.py:284-288`).

> ⚠️ **Format reality check**
> `LoggingPlugin` writes ANSI-colored, human-readable lines to stdout — useful for local dev, but **not** what you want piped into a log aggregator. For structured JSON, wire `structlog` via `logging.dictConfig` or write a custom plugin (see page 13_Plugins/03). The plugin does **not** emit JSON, even at INFO/DEBUG levels.

## 🐍 Detour suggestion

If `logging.getLogger(__name__)`, handlers, and the Python log hierarchy feel hand-wavy, take 20 min on [[PY_logging]] before page 03. Note: despite the name, `LoggingPlugin` itself does **not** route through the stdlib `logging` module — it calls `print()` directly. A custom plugin that calls `logger.info(...)` (with a `structlog` JSON formatter wired via `dictConfig`) is what gets you real structured logs.

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
