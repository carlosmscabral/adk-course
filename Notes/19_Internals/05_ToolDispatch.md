---
module: 19_Internals
page: 05_ToolDispatch
title: Tool dispatch — schema, args, errors
estimated_minutes: 30
prereqs: [19_Internals/04]
concepts: [BaseTool, FunctionTool, FunctionDeclaration, dispatch]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/04_SessionEventSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/06_WorkflowSource →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 05 Tool Dispatch

# 🧠 Tool dispatch — the BaseTool contract

File: `/home/carloscabral/study/adk-python/src/google/adk/tools/base_tool.py`
Class: `BaseTool` — line **47**.

## The contract — 3 methods

```python
class BaseTool(ABC):
    name: str
    description: str
    is_long_running: bool = False
    custom_metadata: Optional[dict[str, Any]] = None

    def _get_declaration(self) -> Optional[types.FunctionDeclaration]: ...
    async def run_async(self, *, args, tool_context) -> Any: ...
    async def process_llm_request(self, *, tool_context, llm_request) -> None:
        llm_request.append_tools([self])      # default
```

That's the entire tool API.

- **`_get_declaration`** — return the schema the LLM sees (Gemini `FunctionDeclaration` / OpenAI tool schema). `None` for built-ins that are model-native (e.g. `google_search` for Gemini).
- **`run_async`** — the actual work.
- **`process_llm_request`** — hook to mutate the outgoing request (default: just register the tool).

## Schema generation — `FunctionTool`

`tools/function_tool.py` is the wrapper for plain Python functions. It uses `_function_parameter_parse_util.py` and `_automatic_function_calling_util.py` to:

1. Inspect signature → param names + type hints.
2. Parse docstring (Google / Sphinx / NumPy style) → param descriptions.
3. Build a `types.FunctionDeclaration(name=fn.__name__, description=docstring, parameters=…)`.

**This is why your tool needs typed params and a docstring.** No types → no schema → LLM can't call it reliably. (We saw this back in `03_Tools/02_FunctionTool`.)

## Dispatch — where it actually happens

When the LLM responds with a `function_call`, the dispatch is **not** in `base_tool.py`. It's in:

`/home/carloscabral/study/adk-python/src/google/adk/flows/llm_flows/functions.py`

The high-level dance (paraphrased):

```
1. _postprocess_handle_function_calls_async (base_llm_flow.py:1130)
     extracts each FunctionCall from the model response.
2. For each call:
     a. Look up the tool by name in the agent's resolved tool list.
     b. Coerce JSON args → Python types using the FunctionDeclaration schema.
     c. Build a ToolContext (state, actions, artifact bridge, …).
     d. Run before_tool_callback if present.
     e. await tool.run_async(args=coerced, tool_context=ctx)
     f. Wrap the return value in a FunctionResponse Part.
     g. Run after_tool_callback if present.
     h. Emit an Event(content=Content(parts=[FunctionResponse(...)]),
                        author=agent_name,
                        actions=EventActions(state_delta=ctx.state_delta, ...))
```

## Error wrapping

If `tool.run_async` raises:

1. `on_tool_error_callback` is invoked (if registered).
2. If the callback returns a replacement result, that's used.
3. Otherwise, the exception is converted into a `FunctionResponse` with an error payload (`{"error": "...", "message": "..."}`).
4. The LLM sees the error in the next turn and decides whether to retry, apologize, or escalate.

This is why a raised `ZeroDivisionError` in a calculator tool doesn't crash the agent — it becomes an event the LLM can reason about.

## `custom_metadata`

A free-form dict on every tool. **JSON-serializable required.** Used by features like skills (to tag tools with manifest data), evals (to tag tools for trajectory scoring), and your own analytics.

> ⚠️ **Gotcha:** if your tool returns a non-JSON-serializable object (a `pandas.DataFrame`, a `numpy.array`), the `FunctionResponse` build will fail. Wrap with `.to_dict()` or stringify before returning.

> 🛠 **Have the student run:** open `tools/function_tool.py` and find where `_get_declaration` builds the `FunctionDeclaration`. Trace one call: `FunctionTool(my_fn)._get_declaration()` should produce a schema with `my_fn`'s param names.

> ❓ **Ask the student:** "Where would you add a metric that times every tool invocation?" *(Answer: either a `before/after_tool_callback`, or a custom `Plugin` with `on_tool_*` hooks — module 13.)*

[← Prev: 19_Internals/04_SessionEventSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/06_WorkflowSource →]
