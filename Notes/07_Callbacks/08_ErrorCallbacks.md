---
module: 07_Callbacks
page: 08_ErrorCallbacks
title: on_model_error / on_tool_error — recover from exceptions
estimated_minutes: 20
prereqs: [07_Callbacks/07]
concepts: [on_model_error_callback, on_tool_error_callback, retry, recovery]
icon: 🛠
in_production: true
detours_suggested: [PY_logging]
---

[← Prev: 07_Callbacks/07_CallbacksVsPlugins](07_CallbacksVsPlugins.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/09_DissectingSample →](09_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 08 Error Callbacks

# 🛠 When things blow up

Two hooks intercept exceptions thrown from the LLM call or tool call:

```python
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

def on_model_error_callback(
    callback_context, llm_request: LlmRequest, error: Exception,
) -> LlmResponse | None: ...

def on_tool_error_callback(
    tool: BaseTool, args: dict, tool_context: ToolContext, error: Exception,
) -> dict | None: ...
```

Return `None`: let the exception propagate (the runner will surface it as an error event).
Return a recovery value: **the exception is swallowed and the recovery value is used as if the call had succeeded.**

## Recover from a model error (retry-as-mock)

```python
def heal_with_fallback(callback_context, llm_request, error):
    log.warning("Model failed: %s — returning fallback", error)
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=(
                "I'm having trouble reaching the model right now. "
                "Try again in a moment."
            ))],
        )
    )
```

Now a transient 503 turns into a graceful message instead of a stack trace.

## Recover from a tool error

```python
def tolerate_search_outage(tool, args, tool_context, error):
    if tool.name == "google_search":
        return {"results": [], "error": "search_unavailable"}
    return None  # other tools: let it propagate
```

The agent loop continues; the LLM sees an empty result and can decide whether to give up or try another approach.

## The infinite-loop trap

```python
# DON'T DO THIS
def bad_handler(callback_context, llm_request, error):
    return call_the_model_again(llm_request)  # what if THIS fails too?
```

If your error callback itself raises, ADK invokes it again. Set a flag (`tool_context.state["temp:retry_count"]`) and refuse after N attempts.

```python
def bounded_retry(callback_context, llm_request, error):
    n = callback_context.state.get("temp:model_retries", 0)
    if n >= 2:
        return LlmResponse(content=types.Content(
            role="model",
            parts=[types.Part(text="Service unavailable.")],
        ))
    callback_context.state["temp:model_retries"] = n + 1
    return None  # propagate this one, but the next failure will be caught
```

## Wiring it up

```python
agent = Agent(
    model="gemini-2.5-flash",
    name="resilient",
    tools=[google_search],
    on_model_error_callback=bounded_retry,
    on_tool_error_callback=tolerate_search_outage,
)
```

> 🛠 **Have the student run:** wire a tool that always raises `RuntimeError("boom")` and an `on_tool_error_callback` that returns `{"status": "ok", "note": "mocked"}`. Confirm the agent never sees the exception.

> 🚀 **In Production**
>
> Always log inside error callbacks before returning a recovery value — silent recovery is the worst kind of production bug ([[PY_logging]]). The standard pattern is: log, increment a metric ([[15_Observability/00_Overview]]), then return the fallback. Pair with circuit-breakers via a small `temp:`-state counter to avoid hammering a downed service.

[← Prev: 07_Callbacks/07_CallbacksVsPlugins](07_CallbacksVsPlugins.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/09_DissectingSample →](09_DissectingSample.md)
