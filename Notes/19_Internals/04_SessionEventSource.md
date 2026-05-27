---
module: 19_Internals
page: 04_SessionEventSource
title: Session and Event — the data model
estimated_minutes: 25
prereqs: [19_Internals/03]
concepts: [Session, Event, EventActions, pydantic]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/03_RunnerSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/05_ToolDispatch →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 04 Session & Event Source

# 🧠 Session and Event — the data model

Files:
- `/home/carloscabral/study/adk-python/src/google/adk/sessions/session.py`
- `/home/carloscabral/study/adk-python/src/google/adk/events/event.py`
- `/home/carloscabral/study/adk-python/src/google/adk/events/event_actions.py`

## `Session` (52 lines, all of it)

Open `sessions/session.py`. The **entire** definition fits on screen:

```python
class Session(BaseModel):
    id: str
    app_name: str
    user_id: str
    state: dict[str, Any] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)
    last_update_time: float = 0.0
    _storage_update_marker: str | None = PrivateAttr(default=None)
```

That's it. A session is **(metadata + a dict + an event log)**. Everything else — multi-agent transfers, tool calls, memory pulls — is _events_ that mutate that dict.

The `_storage_update_marker` is private; service impls use it to detect stale reads (optimistic concurrency).

## `Event` — `events/event.py:93`

Inherits from `LlmResponse` (so it can carry `content`, `partial`, etc.). Adds:

```python
invocation_id: str
author: str                      # 'user' or agent name
actions: EventActions            # state_delta, transfer_to_agent, …
output: Any | None               # workflow-node output
node_info: NodeInfo              # node path / run_id (for graph)
long_running_tool_ids: set | None
branch: str | None               # 'agent_1.agent_2' for isolation
isolation_scope: str | None      # INTERNAL — don't touch
id: str
timestamp: float
```

Two ergonomic conveniences in `__init__` (line 159):

- `Event(message=...)` → routes to `content` via `t_content`.
- `Event(state=...)` → routes to `actions.state_delta`.
- `Event(route=..., node_path=...)` → workflow shortcuts.

## `EventActions` — `events/event_actions.py:52`

```python
class EventActions(BaseModel):
    state_delta: dict[str, object] = {}      # ← the state mutation
    artifact_delta: dict[str, int] = {}
    transfer_to_agent: str | None = None     # multi-agent transfer
    escalate: bool | None = None             # LoopAgent exit
    skip_summarization: bool | None = None   # raw tool output
    requested_auth_configs: dict | None = None
    # ... and more (route, agent_state, end_of_agent, …)
```

**This** is the bus. Every state mutation, every transfer, every loop-exit — they're all just fields on an `EventActions` carried by an `Event`.

## `is_final_response` (line 220)

A subtle but load-bearing method:

```python
def is_final_response(self) -> bool:
    if self.actions.skip_summarization or self.long_running_tool_ids:
        return True
    return (
        not self.get_function_calls()
        and not self.get_function_responses()
        and not self.partial
        and not self.has_trailing_code_execution_result()
    )
```

This is how downstream consumers (the runner, an A2A server, the `adk web` UI) decide "the agent is done speaking, render the bubble." It's a **derived** property — there's no `final: bool` field.

> ⚠️ **Gotcha:** `partial=True` events are streamed deltas (token-by-token). They are NEVER final responses. If you're filtering events for "the answer," check `is_final_response()` and ignore partials.

> 🛠 **Have the student run:** open `event_actions.py` and list every field on `EventActions`. Match each to a feature they've used (e.g., `state_delta` → module 04, `transfer_to_agent` → module 05).

> ❓ **Ask the student:** "If `Session.state` is just a dict, what holds the `user:` / `app:` / `temp:` semantics?" *(Answer: `sessions/state.py` defines `State`, a dict subclass that interprets prefixes when read; the prefix split happens on append, in `_session_util.extract_state_delta`.)*

[← Prev: 19_Internals/03_RunnerSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/05_ToolDispatch →]
