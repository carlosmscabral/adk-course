---
module: 04_SessionsState
page: 02_StateScopes
title: State scopes — the four prefixes
estimated_minutes: 20
prereqs: [04_SessionsState/01]
concepts: [state-prefix, user-state, app-state, temp-state, session-state]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/01_SessionVsState](01_SessionVsState.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/03_ReadingStateInPrompts →]

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 02 State scopes

# 🧠 The four state prefixes

State keys are strings. ADK parses the prefix on each key to decide where the value lives. **The prefixes are not convention — the framework reads them.**

## 🧠 The table

| Prefix | Scope | Survives | Use for |
|---|---|---|---|
| *(none)* | This session | only this conversation | turn-to-turn chat context (`last_query`, `pending_action`) |
| `user:` | This user (across all their sessions) | every future session of this user | preferences, names, account IDs |
| `app:` | This app (all users) | every session of every user | global config, feature flags |
| `temp:` | This invocation (one user turn) | nothing — dropped after this `run_async()` | retry counters, scratch values |

## 🧠 Concrete examples

```python
# In a tool:
tool_context.state["last_query"]   = "whales"       # this session only
tool_context.state["user:name"]    = "Carlos"       # carries across Carlos's sessions
tool_context.state["app:rate"]     = 100            # visible to ALL users
tool_context.state["temp:retries"] = 2              # gone after this turn
```

After this tool returns:
* Reading `state["last_query"]` next turn → `"whales"`. Reading it from a *different* session of the same user → `KeyError`.
* Reading `state["user:name"]` from any future session of Carlos → `"Carlos"`.
* Reading `state["app:rate"]` from a session of a totally different user → `100`.
* Reading `state["temp:retries"]` even one more time in this same turn → fine. Next turn → gone.

## 🧠 Reading is just `state[key]`

The prefix is parsed at **write** time. Reads are uniform:

```python
state["user:name"]    # reads from user-scoped store
state["app:rate"]     # reads from app-scoped store
state["last_query"]   # reads from this session's state
state["temp:foo"]     # reads from per-invocation scratch
```

When the Runner builds the state view for the next LLM call, it merges all four scopes into a single dict keyed by the full prefixed names. From your tool's perspective, it's a flat dict.

## ⚠️ The #1 bug

Forgetting the `user:` prefix when you mean to remember something across sessions:

```python
# WRONG — name forgotten when this session ends
tool_context.state["name"] = "Carlos"

# RIGHT — name remembered across Carlos's future sessions
tool_context.state["user:name"] = "Carlos"
```

Symptoms: agent works great in a single conversation, then "forgets" the user the next day. Fix: audit your state writes and add `user:` where appropriate.

## ⚠️ The #2 bug

Forgetting the `temp:` prefix for scratch values:

```python
# WRONG — pollutes the session forever with stale retry counters
tool_context.state["retry_count"] = 3

# RIGHT — gone at end of this turn
tool_context.state["temp:retry_count"] = 3
```

Symptoms: state dict grows monotonically; eventually you store hundreds of stale keys.

## ❓ Self-check

> ❓ **Ask the student:** for each scenario, name the right prefix:
> 1. The user's preferred timezone.
> 2. Whether the experimental "v3 prompt" is enabled for all users today.
> 3. A counter of how many times this tool retried in the current turn.
> 4. The list of items in the user's current shopping cart (cart resets per session).
>
> *(Expected: 1. `user:`. 2. `app:`. 3. `temp:`. 4. no prefix — session-scoped.)*

> 🛠 **Have the student do this:** sketch the state dict a multi-day, multi-user shopping assistant would carry. Mark each entry's prefix. Then ask: "what happens if I forget the `user:` prefix on `name`?" *(The agent re-asks the user's name every session.)*

> **🚀 In Production**
>
> Prefixes are also **the boundary for cross-user data leaks**. A bug that writes a user's PII into `app:` makes it visible to every other user. Always code-review state writes for the right prefix; consider a linter or a state-write callback (Module 07) that rejects unknown keys.

---

[← Prev: 04_SessionsState/01_SessionVsState](01_SessionVsState.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/03_ReadingStateInPrompts →]
