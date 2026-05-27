---
module: 01_Foundations
page: 04_StateLivesOnSession
title: State lives on the session
estimated_minutes: 10
prereqs: [01_Foundations/02]
concepts: [session-state, state-delta, event-actions]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 01_Foundations/03_ToolsArePythonFunctions](03_ToolsArePythonFunctions.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/05_DissectingSample →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 04 State lives on the session

# 🧠 State lives on the session

Another **preview** — Module 04 is the deep dive. Goal: install the vocabulary before we use it.

## 🧠 Two things the Session holds

1. **Event log** — every message, tool call, tool result, system note. Append-only, ordered.
2. **State dict** — a `dict[str, Any]` of arbitrary data the agent or tools want to carry across turns.

State is what makes "remember the user's name from turn 1" possible. The LLM itself is stateless; the Session is what gives it memory inside a conversation.

## 🧠 State changes are **deltas attached to events**

You don't directly mutate the session's state from outside. Instead, tools and callbacks emit a *delta* and ADK applies it as part of the next Event:

```python
def remember_name(name: str, tool_context: ToolContext) -> str:
    """Save the user's name."""
    tool_context.state["user:name"] = name   # ← this becomes a state_delta
    return f"Got it, {name}."
```

The resulting Event has `actions.state_delta = {"user:name": "Carlos"}`. The Session's view of state is the *fold* of all state deltas from all events.

Why this design? Because:

* It's **auditable** — every state change is in the event log.
* It's **replayable** — you can rewind to event N and reconstruct state at that point.
* It works across **persisted backends** — Postgres-backed Sessions just store events; state is reconstructed on read.

## 🧠 State prefixes (preview)

You'll see four kinds of state keys, distinguished by prefix:

| Prefix | Scope | Example |
|---|---|---|
| (none) | This session only | `state["last_query"]` |
| `user:` | This user, across all their sessions | `state["user:name"]` |
| `app:` | All users of this app | `state["app:rate_limit"]` |
| `temp:` | This invocation only (one turn) | `state["temp:retry_count"]` |

Module 04 walks through each. For now, just know they exist and that the prefix is parsed by the framework — it's not just convention.

> ❓ **Ask the student:** if a user opens a *new* session tomorrow, which state survives? Which is gone?
> *(Expected: `user:` and `app:` survive — they outlive the session. No-prefix state is gone because it was scoped to the previous session. `temp:` was gone before the turn ended.)*

> **🚀 In Production**
>
> Saving secrets in state is a common foot-gun. State is logged in events, events are persisted, persisted events end up in observability dashboards. **Never store API keys, passwords, or PII in state** unless your platform encrypts session storage AND your dashboards redact it. (Module 16 covers this in depth.)

> 🛠 **Have the student do this on paper:** sketch what state keys a multi-turn shopping agent would need across one user session. (Maybe `cart`, `user:address`, `user:payment_method`, `temp:last_search_query`.) Notice how prefix choice maps directly to "should this survive into tomorrow's session?"

---

[← Prev: 01_Foundations/03_ToolsArePythonFunctions](03_ToolsArePythonFunctions.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/05_DissectingSample →]
