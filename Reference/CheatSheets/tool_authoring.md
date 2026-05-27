# 📋 Cheat Sheet — Tool authoring

ADK turns plain Python functions into tools the LLM can call. The function's signature + docstring becomes the schema the LLM sees. Get the schema right and the LLM picks the tool reliably; get it wrong and it never gets called (or gets called with garbage args).

## The minimal `FunctionTool`

```python
from google.adk.tools import FunctionTool

def get_weather(city: str, units: str = "celsius") -> dict:
    """Get the current weather for a city.

    Args:
        city: The city name, e.g. "Berlin" or "São Paulo".
        units: Temperature units. One of "celsius" or "fahrenheit".

    Returns:
        A dict with keys `temp`, `units`, `conditions`.
    """
    return {"temp": 22, "units": units, "conditions": "sunny"}

# wrap explicitly:
weather_tool = FunctionTool(func=get_weather)

# or just pass the bare function to LlmAgent — auto-wrapped:
LlmAgent(name="...", model="...", tools=[get_weather])
```

## Schema rules (the LLM reads these)

| Rule | Why |
|---|---|
| **Type hints on every parameter** | Without them, the LLM cannot infer the schema; the tool may register with `Any` types and the LLM will hallucinate args. |
| **Docstring with `Args:` block** | The LLM reads it. Each arg description tells the LLM when to populate that arg. |
| **Top-of-docstring summary** | One sentence — the LLM reads it to decide *whether* to call the tool. |
| **Return JSON-serializable** | Tool results round-trip through the runtime as `Content.parts`. Pydantic models OK; opaque objects not. |
| **No `**kwargs`** | The schema generator cannot represent untyped kwargs. Use explicit named params. |
| **Defaults are honored** | `def f(x: int, y: int = 0)` — the LLM is told `y` is optional. |
| **`Optional[T]` / `T \| None` is fine** | Generates a nullable schema. |
| **`Literal["a", "b"]` becomes an enum** | Best for fixed choices like units, modes. |
| **Pydantic `BaseModel` params** | Become nested object schemas. Great for structured args. |

## With `ToolContext` — access state, actions, artifacts

```python
from google.adk.tools import ToolContext

def list_todos(tool_context: ToolContext) -> list[str]:
    """List the current user's todos."""
    return tool_context.state.get("user:todos", [])

def add_todo(item: str, tool_context: ToolContext) -> dict:
    """Add a todo item for the user."""
    todos = tool_context.state.get("user:todos", [])
    todos.append(item)
    tool_context.state["user:todos"] = todos
    return {"added": item, "total": len(todos)}
```

The `tool_context: ToolContext` parameter is **detected by name + type** — the LLM does NOT see it as an argument. The runtime injects it.

`ToolContext` exposes:
- `.state` — dict-like read/write on the active session state.
- `.actions` — `EventActions` you can mutate (see [event_actions cheat sheet](event_actions.md)).
- `.save_artifact(...)` / `.load_artifact(...)` — artifact I/O.
- `.user_content` — the user's original message for this turn.

## `LongRunningFunctionTool` — for tools that take ≥ a few seconds

```python
from google.adk.tools import LongRunningFunctionTool

def render_video(prompt: str) -> dict:
    """Render a 5-second video. Returns the rendered URL when done."""
    # ... slow work ...
    return {"url": "..."}

video_tool = LongRunningFunctionTool(func=render_video)
```

The runtime treats it specially so the agent can yield intermediate Events while the tool runs (instead of blocking). Pair with streaming (Module 18) for progress UI.

## `AgentTool` — wrap an agent as a tool

```python
from google.adk.tools import AgentTool
from google.adk.agents import LlmAgent

sub = LlmAgent(name="translator", model="gemini-2.5-flash",
               instruction="Translate text to French.")

translator_tool = AgentTool(agent=sub)

root = LlmAgent(name="root", model="gemini-2.5-flash",
                instruction="If asked for French, call `translator`.",
                tools=[translator_tool])
```

Different from `sub_agents=`: `AgentTool` is **explicitly invoked** by the parent LLM as a function call, returning a string. `sub_agents=` is **LLM-delegated** via `transfer_to_agent`.

## Common confusions

- **Docstring is part of the contract.** Edit the docstring → the schema changes → the LLM's behavior changes. Treat it like code.
- **Return type hint is informational, not enforced.** Returning a non-serializable object errors at runtime, not at schema-gen time.
- **`tool_context` must be typed `ToolContext`** — not `Any`, not omitted. The injection looks at the annotation.
- **Don't put secrets in tool args** — they get logged + persisted in Events. Pull secrets from env/Secret Manager inside the tool body.

## Where it's covered in the course

- Engine-first walk: [Notes/03_Tools/02_FunctionTool](../../Notes/03_Tools/02_FunctionTool.md)
- Built-in tools: [Notes/03_Tools/04_BuiltInTools](../../Notes/03_Tools/04_BuiltInTools.md)
- `AgentTool` vs `sub_agents=`: [Notes/05_MultiAgent/03_AgentAsTool](../../Notes/05_MultiAgent/03_AgentAsTool.md)
- `LongRunningFunctionTool` for streaming: [Notes/18_StreamingLive/05_StreamingTools](../../Notes/18_StreamingLive/05_StreamingTools.md)
- Type hints detour: [Notes/Detours/PY_typing.md](../../Notes/Detours/PY_typing.md)
- Pydantic for structured args: [Notes/Detours/PY_pydantic.md](../../Notes/Detours/PY_pydantic.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
