# 📋 Cheat Sheet — `EventActions` fields

`Event.actions` is an `EventActions` object that carries **side effects** the runner must apply: state mutations, artifact writes, control-flow directives. This is how an agent or tool talks to the runtime.

```python
from google.adk.events import EventActions
```

## The fields

| Field | Type | Semantics |
|---|---|---|
| `state_delta` | `dict[str, Any]` | Key→value pairs to merge into `session.state`. The runner applies these in-order and persists via the session service. Keys can use any of the four prefixes (`user:`, `app:`, `temp:`, none). Setting a value to `None` stores `None` — it does not delete the key. |
| `artifact_delta` | `dict[str, int]` | Map of artifact name → version. The runner records that the artifact was written. Used in conjunction with `ArtifactService` to track outputs (files, images). |
| `transfer_to_agent` | `str \| None` | Name of the agent to transfer control to. The runner halts the current agent's turn and routes the next user-equivalent input to the named agent. Used by the `transfer_to_agent` built-in tool. |
| `escalate` | `bool` | When `True`, signals "I cannot handle this — escalate up the agent tree." Often surfaces to a parent agent or to a human-in-the-loop. |
| `skip_summarization` | `bool` | When `True` on a tool result Event, prevents the LLM from summarizing — the raw tool output flows straight through. Useful for tools that already return user-facing text. |
| `requested_auth_configs` | `dict[str, AuthConfig]` | Lists auth configs the tool needs the user to satisfy before it can proceed. The runner surfaces these to the client. |
| `requested_tool_confirmations` | `dict[str, ToolConfirmation]` | Tool confirmations requested by this event, keyed by function call id. Used by tools that require user confirmation before running. |
| `end_of_agent` | `Optional[bool]` | When `True`, signals the current agent has finished its run. May fire multiple times within one invocation for loops. Set only by ADK workflow primitives. |

## How they're set

### From a callback

```python
from google.adk.events import EventActions

def after_tool_callback(tool, args, tool_context, tool_response):
    tool_context.actions.state_delta["temp:last_tool_ran"] = tool.name
    tool_context.actions.skip_summarization = True
    return None  # passthrough
```

### From a tool

```python
def my_tool(query: str, tool_context: ToolContext) -> dict:
    tool_context.actions.state_delta["search_query"] = query
    return {"results": [...]}
```

### From a custom `BaseAgent` subclass

```python
class MyAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        yield Event(
            author=self.name,
            content=types.Content(role="model", parts=[...]),
            actions=EventActions(
                state_delta={"step": "done"},
                transfer_to_agent="next_agent",
            ),
        )
```

## How they're applied

The runner inspects every yielded `Event`:

```
for event in async for ...:
    # 1. apply state_delta to session.state
    session.state.update(event.actions.state_delta)
    # 2. record artifact_delta to ArtifactService
    # 3. if transfer_to_agent: switch active agent for next turn
    # 4. if escalate: bubble up
    # 5. persist session via session_service
```

`State.update(...)` preserves dict insertion order (CPython 3.7+), so keys land in the order you set them.

## Common confusions

- **`state_delta` is staged, not immediate.** Setting `tool_context.actions.state_delta["x"] = 1` does NOT update `session.state["x"]` until the runner applies the Event. If your tool later reads `tool_context.state["x"]`, it sees the staged value (the runtime composes a view) — but other concurrent reads do not.
- **`skip_summarization=True` is for tools whose output is already prose** — e.g., a summarization tool. Most tools should leave it `False` so the LLM can frame the answer.
- **`transfer_to_agent` does not stop the current Event** — the Event still flows. The transfer takes effect on the *next* delegation point.
- **`escalate` is advisory** — the parent agent (or runtime) decides what to do. There is no automatic "abort the whole tree."

## Where it's covered in the course

- Event anatomy: [Notes/02_FirstAgent/03_RunAsyncAndEvents](../../Notes/02_FirstAgent/03_RunAsyncAndEvents.md)
- State deltas: [Notes/04_SessionsState/03_EventDeltas](../../Notes/04_SessionsState/03_EventDeltas.md)
- `transfer_to_agent`: [Notes/05_MultiAgent/02_Transfer](../../Notes/05_MultiAgent/02_Transfer.md)
- `escalate` + human-in-the-loop: [Notes/06_GraphWorkflows/04_HumanInTheLoop](../../Notes/06_GraphWorkflows/04_HumanInTheLoop.md)
- `skip_summarization` use case: [Notes/03_Tools/02_FunctionTool](../../Notes/03_Tools/02_FunctionTool.md)
- Internals trace through `actions`: [Notes/19_Internals/03_SessionMutation](../../Notes/19_Internals/03_SessionMutation.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
