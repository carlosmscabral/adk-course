---
module: 19_Internals
page: 10_TracingOneToolCall
title: Tracing one tool invocation end-to-end
estimated_minutes: 30
prereqs: [19_Internals/09]
concepts: [function-call, tool-dispatch, FunctionResponse]
icon: 🛠
in_production: false
---

[← Prev: 19_Internals/09_DissectingOneCall]  [↑ Map](../../MAP.md)  [Next: 19_Internals/11_TracingOneStateMutation →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 10 Tracing One Tool Call

# 🛠 Trace one tool invocation

We follow a tool-using turn:

```python
def add(a: int, b: int) -> int:
    """Return a + b."""
    return a + b

agent = Agent(model="gemini-2.5-flash", instruction="use add", tools=[add])
# LLM responds with: function_call(name="add", args={"a":3, "b":4})
```

## The call stack — entering on the LLM response

```
_postprocess_async (base_llm_flow.py:952)
  └─ for processor in self.response_processors: ...
  └─ _postprocess_handle_function_calls_async (base_llm_flow.py:1130)
        └─ for each FunctionCall part in response.content.parts:
              ├─ find tool by name → FunctionTool wrapping `add`
              ├─ coerce args:
              │     {"a": 3, "b": 4}  →  match against FunctionDeclaration → typed kwargs
              ├─ build ToolContext (tools/tool_context.py)
              │     • state: live State view (session-scoped)
              │     • actions: empty EventActions to accumulate
              │     • artifacts: bridge to artifact_service
              │     • invocation_id, function_call_id
              ├─ run before_tool_callback (if any)        agents/llm_agent.py callbacks
              ├─ await tool.run_async(args=..., tool_context=ctx)
              │     ├─ FunctionTool.run_async (tools/function_tool.py)
              │     ├─ calls fn(**args)   → add(3, 4) → 7
              │     └─ returns 7
              ├─ run after_tool_callback (if any)
              ├─ build FunctionResponse Part:
              │     name="add", response={"result": 7}, id=fc_id
              └─ yield Event(
                       author=agent.name,
                       content=Content(parts=[FunctionResponse(...)]),
                       actions=EventActions(state_delta=ctx.actions.state_delta, ...)
                  )
```

## The outer loop kicks in

After the function-response event is yielded, `_run_one_step_async` returns. The outer `run_async` (line 818) loops: it builds a **new** `LlmRequest` whose contents now include the function response, and asks the LLM again. The LLM now produces text ("3 + 4 is 7") which goes through the partial+final path and ends the turn.

## What goes into the event

```
Event(
  invocation_id="inv-...",
  author="my_agent",
  content=Content(
    role="tool",
    parts=[Part(function_response=FunctionResponse(
      name="add", response={"result": 7}, id="fc-..."
    ))]
  ),
  actions=EventActions(
    state_delta={},          # tool didn't mutate state
    artifact_delta={},
  ),
  partial=False,
)
```

## Error path

If `add` raised `TypeError`:

```
tool.run_async  →  raises TypeError
  └─ caught in functions._invoke_tool / _run_and_handle_error
        ├─ on_tool_error_callback (if registered)
        │   └─ if returns a dict → use as the response
        └─ otherwise build FunctionResponse with error:
              {"error": "TypeError", "message": "...", "args": {...}}
```

The LLM sees the error and decides what to do (retry, apologize, escalate).

## Where to grep for the dispatch

The real dispatch lives in `flows/llm_flows/functions.py`. Useful symbols:

- `find_matching_function_call`
- `find_event_by_function_call_id`
- Helper builders for `FunctionResponse`

`base_llm_flow.py:1130` (`_postprocess_handle_function_calls_async`) is the orchestrator that calls into `functions.py` per call.

> ⚠️ **Gotcha:** the LLM can request multiple function calls in one response. `_postprocess_handle_function_calls_async` iterates over all of them; they're invoked **sequentially by default**. Parallel invocation requires the model emitting independent calls AND the agent configuration allowing it (see `run_config.py`).

> 🛠 **Have the student run:** add a `print` in their tool function. They'll see the print fire **before** the next LLM call — confirming the LLM doesn't see the result until the loop comes back around.

> ❓ **Ask the student:** "If `before_tool_callback` returns a dict, what happens to the actual tool function?" *(Answer: skipped. The dict becomes the FunctionResponse directly. This is the override seam for stubbing/mocking in tests.)*

[← Prev: 19_Internals/09_DissectingOneCall]  [↑ Map](../../MAP.md)  [Next: 19_Internals/11_TracingOneStateMutation →]
