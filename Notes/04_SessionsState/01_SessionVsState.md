---
module: 04_SessionsState
page: 01_SessionVsState
title: Session vs. State
estimated_minutes: 15
prereqs: [04_SessionsState/00]
concepts: [Session, State, event-log]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 04_SessionsState/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/02_StateScopes →]

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 01 Session vs. State

# 🧠 Session vs. State

You met both names in Module 01. Here's the precise difference.

## 🧠 The Session is the conversation container

```
Session {
    id:        "s-abc123"
    app_name:  "myapp"
    user_id:   "carlos"
    events:    [Event, Event, Event, ...]      ← the conversation
    state:     {...}                            ← arbitrary KV
}
```

A `Session` is what `session_service.create_session(...)` returns. It owns:
* An ordered **event log** (every message, tool call, tool result, system note).
* A **state dict** (arbitrary key-value pairs).

The agent never touches a Session directly — it accesses both through the Runner and `ToolContext`.

## 🧠 State is the dict

```text
session.state == {'user:name': 'Carlos', 'last_query': 'whales'}
```

That's it. Just a dict. Keys are strings; values are JSON-serializable. There's no magic.

What's special: ADK *manages how the dict gets written*. You don't `session.state["x"] = y` from outside. Instead:
* Tools write via `tool_context.state["x"] = y` → captured as a `state_delta` on the tool-result event.
* Agents write via `output_key=` → the agent's text reply gets stored under that key (page 05).
* `create_session(..., state={"x": 1})` seeds initial state.

## 🧠 Why this design?

```
{{INCLUDE _figures/state_flow.txt}}
```

The big payoff: **every state change is in the event log.** You can:
* Audit who changed what when.
* Replay the conversation from any point and reconstruct state.
* Stream state changes to dashboards (Module 15).
* Persist Sessions in any backend (Module 04 page 06) — the state is just a fold of deltas.

## ❓ Compare: chat history vs. state

> ❓ **Ask the student:** "what's the difference between *chat history* and *state*?"
> *(Expected: chat history is the user-visible conversation — the messages and replies. State is structured data the agent and tools want to remember. They're stored in the same Session but used differently — chat history is shown to the LLM as messages; state is shown to the LLM as either a prompt template substitution* (`{var}`) *or via a tool reading it explicitly.)*

> 🛠 **Have the student run:**
> ```python
> # Work/04_session_seed.py — run with: uv run python Work/04_session_seed.py
> import asyncio
> from google.adk.sessions import InMemorySessionService
>
> async def main():
>     ss = InMemorySessionService()
>     s = await ss.create_session(
>         app_name="x", user_id="u", session_id="s",
>         state={"hello": "world"},
>     )
>     print(s.state)   # {'hello': 'world'}
>     print(s.events)  # []
>
> asyncio.run(main())
> ```
> Two attributes, both real. State seeded at creation time; events start empty.

> **🚀 In Production**
>
> The state dict isn't a database. Keep it small — kilobytes, not megabytes. For big blobs use **artifacts** (Module 11). For structured queryable data use **memory** (Module 11) or your own DB. State that grows unboundedly will eventually OOM your session backend.

---

[← Prev: 04_SessionsState/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/02_StateScopes →]
