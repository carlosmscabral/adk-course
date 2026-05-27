---
module: 19_Internals
page: 11_TracingOneStateMutation
title: Tracing one tool_context.state mutation
estimated_minutes: 25
prereqs: [19_Internals/10]
concepts: [state_delta, EventActions, append_event]
icon: 🛠
in_production: false
---

[← Prev: 19_Internals/10_TracingOneToolCall]  [↑ Map](../../MAP.md)  [Next: 19_Internals/12_InProduction →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 11 Tracing One State Mutation

# 🛠 Trace a `state['x'] = 1` from inside a tool

```python
def remember(value: str, tool_context: ToolContext) -> str:
    """Store value in session state."""
    tool_context.state["last_value"] = value
    return f"stored {value}"
```

What happens between the assignment and the next agent's view of `state["last_value"]`?

## Step 1 — the assignment is captured, not committed

`tool_context.state` is **not** the session's state dict. It's a `State` view (`sessions/state.py`) whose mutations accumulate in `tool_context.actions.state_delta`. So:

```python
tool_context.state["last_value"] = "hello"
# under the hood:
# tool_context.actions.state_delta["last_value"] = "hello"
```

The session's `state` dict is untouched. (This is by design: tools shouldn't be able to half-apply changes if they crash mid-way.)

## Step 2 — the tool returns; FunctionResponse event is built

In `_postprocess_handle_function_calls_async` (base_llm_flow.py:1130), after `tool.run_async` returns:

```python
event = Event(
    author=agent.name,
    content=Content(parts=[FunctionResponse(...)]),
    actions=EventActions(
        state_delta=tool_context.actions.state_delta,   # ← {"last_value": "hello"}
        artifact_delta=tool_context.actions.artifact_delta,
        ...
    ),
)
yield event
```

The delta hitched a ride on the event.

## Step 3 — Runner persists; state is applied

The runner's `async for event in agent.run_async(...)` loop hands the event to `session_service.append_event(session, event)`. In `sessions/base_session_service.py` around line **114**:

```python
def append_event(self, session, event):
    ...
    if event.actions.state_delta:
        # Split into app: / user: / temp: / session-scoped buckets.
        # _session_util.extract_state_delta(event.actions.state_delta)
        ...
        # Update the in-memory session.state dict
        for key, value in event.actions.state_delta.items():
            session.state[key] = value
    ...
    session.events.append(event)
```

Then in the impl (e.g., `in_memory_session_service.py:349`), the same delta is split by prefix and stored:

- `app:foo` → `self.app_state[app_name]["foo"]`
- `user:bar` → `self.user_state[user_id]["bar"]`
- `temp:baz` → discarded (not persisted across invocations)
- `unprefixed` → `storage_session.state["unprefixed"]`

## Step 4 — next invocation sees it

When the next `run_async` starts and `_get_or_create_session` fetches the session, the state dict is rebuilt by **merging** app + user + session scopes (and ignoring `temp:`). The tool's `tool_context.state["last_value"]` now reads `"hello"`.

## The big picture

```
inside tool:    state[x] = 1
                  ↓ captured in
              actions.state_delta
                  ↓ rides on
                Event
                  ↓ persisted via
            session_service.append_event
                  ↓ writes to
        in-memory or DB store
                  ↓ visible on next
            session.state[x]
```

**Three rules that fall out:**

1. **Inside the tool, you can read your own writes** (the State view reflects pending deltas).
2. **Other agents only see the change after the event is persisted** — i.e. after `yield event` returns control to the runner.
3. **If the tool raises after a mutation, the delta is dropped** (the event isn't built, isn't yielded, isn't persisted). State mutations are atomic per tool call.

> 🚀 **In Production**
>
> If you need cross-process visibility (e.g., a long-running tool writing progress for a UI to poll), persist outside the session — Cloud Storage, Firestore, a Pub/Sub topic. State deltas only land at the end of the tool call.

> 🛠 **Have the student run:** add a `print(session.state)` immediately after their tool's `state["x"] = 1` line. Then a `print(session.state)` in the next turn. The first one will NOT show the change; the second one will.

> ❓ **Ask the student:** "What scope is `state['x']` if I never use a prefix?" *(Answer: session-scoped — stays with the session id, doesn't leak across users/apps. See `04_SessionsState/02_StateScopes`.)*

[← Prev: 19_Internals/10_TracingOneToolCall]  [↑ Map](../../MAP.md)  [Next: 19_Internals/12_InProduction →]
