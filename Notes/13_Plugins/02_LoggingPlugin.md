---
module: 13_Plugins
page: 02_LoggingPlugin
title: LoggingPlugin
estimated_minutes: 15
prereqs: [13_Plugins/01]
concepts: [LoggingPlugin, ANSI stdout, dev observability]
icon: 🛠
in_production: true
detours_suggested: []
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

You now get human-readable log lines for:

- Every user message in.
- Every model request out, response in (with model name, latency).
- Every tool call (name, args) and response (or error).
- Every agent transfer.
- Every event the runner yields.

In dev, this is enough to debug "why didn't my agent call that tool" without writing a single print.

## How it actually writes (important)

`LoggingPlugin` does **not** use Python's `logging` module. Its `_log` method (`google/adk/plugins/logging_plugin.py:284-288`) wraps each message with ANSI grey color codes and calls `print()` directly:

```python
# from logging_plugin.py
def _log(self, message: str) -> None:
    formatted_message: str = f"\033[90m[{self.name}] {message}\033[0m"
    print(formatted_message)
```

Consequences you need to know:

- `logging.basicConfig(...)` has **zero effect** on this output. There is no logger, no handler, no level filter.
- Output goes to **stdout**, not stderr. Capture it with `python script.py > run.log` (or `2>&1 | cat` if you're piping into a log aggregator that mangles the ANSI escape codes).
- It's noisy. Every event prints a multi-line block. Fine for one-off dev runs, not for prod tailing.
- It doesn't redact. PII flows through verbatim.

## What it does NOT do

- Doesn't persist anywhere durable.
- Doesn't sample. Every event gets printed.
- Doesn't emit structured JSON. If you need parseable output, use `DebugLoggingPlugin` (`google/adk/plugins/debug_logging_plugin.py`), which writes YAML/JSON-shaped entries to a file, or write your own plugin that calls `logging.getLogger(...)` with a JSON formatter.

## Dev usage

```python
from google.adk.runners import Runner
from google.adk.plugins import LoggingPlugin

runner = Runner(app_name="dev", agent=root_agent, plugins=[LoggingPlugin()])
```

That's it. Run the agent, watch stdout. If the grey ANSI is unreadable in your terminal, redirect (`> run.log`) and `cat` the file — most pagers strip the escape codes cleanly enough.

## Prod usage

You almost never want `LoggingPlugin` *only* in prod. Either:

- Use `DebugLoggingPlugin` for structured file output, OR
- Write a custom plugin that emits JSON via `logging` to your real sink (Cloud Logging / your SIEM), AND
- Add `BigQueryAgentAnalyticsPlugin` (page 06) for queryable, long-lived event records.

`LoggingPlugin` is for the *human* in dev; `BigQueryAgentAnalyticsPlugin` is for the *machine* in prod.

> 🛠 **Have the student run:** Take any working agent (e.g. from M1), wire `LoggingPlugin`, run one turn, paste a slice of the stdout output. The student should be able to point at the lines for: user message, model request, tool call, tool response, model response, final event.

> **🚀 In Production**
>
> `LoggingPlugin` alone is not a production observability strategy — it's `print()` with color codes. For structured output prefer `DebugLoggingPlugin` or a custom plugin that ships JSON through `logging` to Cloud Logging / your SIEM; for queryable history use `BigQueryAgentAnalyticsPlugin`. See `15_Observability` for the full pattern.

---

[← Prev: 13_Plugins/01_WhatIsAPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/03_ReflectAndRetryToolPlugin →]
