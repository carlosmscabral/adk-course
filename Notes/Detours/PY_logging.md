---
module: Detours
page: PY_logging
title: logging — stdlib basics and the structlog upgrade
estimated_minutes: 20
icon: 🐍
prereqs: []
concepts: [logging, levels, handlers, structlog, JSON_logs, library_pitfall]
---

[← Back to Map](../../MAP.md)

Triggered from: `13_Plugins` (`LoggingPlugin`), `15_Observability`.

> Take this detour if you've been `print`-debugging your agent and want to graduate to something a real ops team will accept. ~20 min.

---

## 🐍 1. The five levels, the one rule

```
DEBUG     - dev firehose, off by default
INFO      - normal milestones ("agent started", "tool called")
WARNING   - something looks off, processing continues
ERROR     - operation failed but app survives
CRITICAL  - the app cannot continue
```

The rule: set the level threshold per **environment**, not per `print`. Dev: DEBUG. Prod: INFO. Disaster recovery: drop to DEBUG temporarily.

```python
>>> import logging
>>> logging.basicConfig(level=logging.INFO)
>>> logger = logging.getLogger(__name__)
>>> logger.debug("noisy")            # not shown
>>> logger.info("agent started")
INFO:__main__:agent started
>>> logger.error("tool blew up")
ERROR:__main__:tool blew up
```

`__name__` as the logger name lets you filter by module: `logging.getLogger("myapp.tools").setLevel(logging.DEBUG)` enables debug only there.

---

## 🐍 2. `basicConfig` is fine for scripts — wrong for libraries

For a CLI / one-off script, `logging.basicConfig(level=..., format=...)` at startup is the right move. For a **library** (anything imported by other code), do **not** call `basicConfig` or attach handlers to the root logger. You'll stomp on whatever the importing app set up.

Library-friendly pattern:

```python
# my_library/__init__.py
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())   # opt-in: app must configure
```

The app that imports you decides where logs go. The library only emits.

> ⚠️ ADK follows this — it doesn't auto-configure logging. If you see "nothing's being logged", that's why. Call `logging.basicConfig(level=logging.INFO)` in your entry point.

---

## 🐍 3. Formatters and handlers

The default format (`LEVEL:logger:message`) is rough. A useful one:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("agent").info("hello")
# 14:23:01 INFO     agent: hello
```

Handlers route records: `StreamHandler` (stderr, default), `FileHandler`, `RotatingFileHandler`, `SMTPHandler`, etc. You can attach multiple — INFO to console, ERROR+ to file:

```python
console = logging.StreamHandler();         console.setLevel(logging.INFO)
errfile = logging.FileHandler("err.log");  errfile.setLevel(logging.ERROR)
logging.basicConfig(handlers=[console, errfile], level=logging.INFO)
```

---

## 🐍 4. Why structured logging — `structlog` and JSON

Once logs leave your laptop, a log aggregator (Cloud Logging, Datadog, Loki) wants **JSON**, not a sentence. Compare:

```
INFO 14:23:01 tool_call: weather city=Paris latency_ms=412
```

vs

```json
{"ts":"14:23:01","level":"info","event":"tool_call","tool":"weather","city":"Paris","latency_ms":412}
```

The JSON version is queryable: `latency_ms > 1000 AND tool="weather"`. The sentence version is grep-fodder.

```python
>>> import structlog
>>> log = structlog.get_logger()
>>> log.info("tool_call", tool="weather", city="Paris", latency_ms=412)
2026-05-27T14:23:01 [info] tool_call city=Paris latency_ms=412 tool=weather
```

Configure structlog to emit JSON in prod and pretty key=value in dev — same call site.

---

## 🐍 5. Don't log secrets — and tame third-party noise

Two final habits:

**Redact**: never log full prompts to user messages without filtering. PII and secrets leak fast.

```python
def safe_msg(m: str) -> str:
    return m[:50] + "..." if len(m) > 50 else m
logger.info("user_msg=%s", safe_msg(user_input))
```

**Mute the firehose**: SDKs love DEBUG-level chatter. Crank specific loggers down:

```python
logging.getLogger("google.adk").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
```

> ⚠️ **In ADK**: `LoggingPlugin` (module 13) wires structured logs through every callback automatically. Use it; don't hand-roll.

---

## 🛠 Have the student try

Convert a script from `print` to `logger.info` and see the difference:

```python
# before:
print("starting")
print("got result", 42)

# after:
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)
log.info("starting")
log.info("got result %s", 42)         # use %-formatting, not f-strings
```

Then flip `level=logging.WARNING` and re-run. Notice the INFO lines vanish without touching the call sites — that's the win you can't get from `print`.

> Why `%s` instead of f-strings? Lazy formatting: if the level filters the message out, the interpolation never happens. Cheap, but it adds up in hot loops.

---

Back to: whichever page triggered this — likely `13_Plugins/02_LoggingPlugin` or `15_Observability/01_Logging`.

[← Back to Map](../../MAP.md)
