---
module: 13_Plugins
page: 02_LoggingPlugin
title: LoggingPlugin
estimated_minutes: 15
prereqs: [13_Plugins/01]
concepts: [LoggingPlugin, structured logs, dev observability]
icon: 🛠
in_production: true
detours_suggested: [PY_logging]
---

[← Prev: 13_Plugins/01_WhatIsAPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/03_ReflectAndRetryToolPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 02 LoggingPlugin

# 🛠 LoggingPlugin: the easiest plugin you'll ever use

```python
from google.adk.runners import Runner
from google.adk.plugins import LoggingPlugin

runner = Runner(
    app_name="dev",
    agent=root_agent,
    plugins=[LoggingPlugin()],
)
```

You now get structured log lines for:

- Every user message in.
- Every model request out, response in (with model name, latency).
- Every tool call (name, args) and response (or error).
- Every agent transfer.
- Every event the runner yields.

In dev, this is enough to debug "why didn't my agent call that tool" without writing a single print.

## What it does NOT do

- Doesn't persist anywhere durable — it writes to Python's `logging` module. Where those logs go is your stdlib config (see `[[PY_logging]]`).
- Doesn't sample. Every event gets a log line. Noisy for prod.
- Doesn't redact. PII flows through verbatim.

## Dev usage

Pair with `logging.basicConfig(level=logging.INFO)` and you have a debuggable agent without leaving Python:

```python
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

runner = Runner(..., plugins=[LoggingPlugin()])
```

## Prod usage

You almost never want `LoggingPlugin` *only* in prod. Either:

- Configure structured JSON sinks (handlers that write to Cloud Logging / your SIEM), AND
- Add `BigQueryAgentAnalyticsPlugin` (page 06) for queryable, long-lived event records.

`LoggingPlugin` is for the *human* in dev; `BigQueryAgentAnalyticsPlugin` is for the *machine* in prod.

> ⚠️ **Gotcha.** `LoggingPlugin` logs at INFO. If your root logger filters INFO out, you'll see nothing and assume the plugin didn't load.

> 🛠 **Have the student run:** Take any working agent (e.g. from M1), wire `LoggingPlugin`, run one turn, paste a slice of the log output. The student should be able to point at the lines for: user message, model request, tool call, tool response, model response, final event.

> 🧭 **If the student looks stuck on Python logging config:** suggest detour [[PY_logging]].

> **🚀 In Production**
>
> `LoggingPlugin` alone is not a production observability strategy. It's a dev convenience. Pair with structured JSON formatting and ship to a real backend (Cloud Logging, etc.); for queryable history use `BigQueryAgentAnalyticsPlugin`. See `15_Observability` for the full pattern.

---

[← Prev: 13_Plugins/01_WhatIsAPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/03_ReflectAndRetryToolPlugin →]
