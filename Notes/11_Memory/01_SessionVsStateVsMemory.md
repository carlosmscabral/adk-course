---
module: 11_Memory
page: 01_SessionVsStateVsMemory
title: Session vs State vs Memory — three lifetimes
estimated_minutes: 20
prereqs: [04_SessionsState/02]
concepts: [session, state, memory, lifetime, scope]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 11_Memory/00_Overview]  [↑ Map](../../MAP.md)  [Next: 11_Memory/02_InMemoryMemoryService →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 01 Session vs State vs Memory

# 🧠 The three lifetimes

ADK has three things that all sound like "remember stuff." They are not the same.

| Thing | Lifetime | Scope | Lives in | Survives session end? |
|-------|----------|-------|----------|----------------------|
| **Session** | one conversation | one user × one app × one session id | `SessionService` | — (it IS the session) |
| **State** | depends on prefix | per-session / per-user / per-app / per-turn | `session.state` dict | depends on prefix |
| **Memory** | forever (or TTL) | per-user (typically) | `MemoryService` | ✅ yes |

The state prefixes (recap from `04_SessionsState/02_StateScopes.md`):

```
state["scratch_pad"]       → session-scoped   (dies with session)
state["temp:reasoning"]    → invocation-only  (dies at turn end)
state["user:name"]         → user-scoped      (across sessions, this user)
state["app:rate_limit"]    → app-scoped       (across all users, this app)
```

🗺 Visualize:

```
$ cat _figures/memory_lifetimes.txt
```

## So when do I actually need Memory?

Use **memory** (not state) when:

- The fact must survive past the session — and `user:`-prefixed state isn't enough because you need *semantic retrieval* across past conversations, not key lookup.
- You want the system to *distill* what to remember (Memory Bank).
- You have a RAG corpus and want past chats to be retrievable like documents (Rag-backed memory).

Use **state** (not memory) when:

- The value is a known key (preferences, counters, IDs).
- You're inside a single conversation and the value is structured (working draft, current step, partial form).

> ⚠️ **Gotcha.** `user:`-prefixed state IS cross-session. So it overlaps with memory. Rule of thumb: if you'd reach for a `dict.get(key)`, use state. If you'd reach for a vector search, use memory.

> ❓ **Ask the student:** "Where do you store the user's favorite color: a movie they mentioned in passing 3 months ago: and the system's global error count?" *(Expected: state with `user:` prefix; memory; state with `app:` prefix.)*

> 🤖 **Tutor:** If the student answers all three the same way, replay this page. The taxonomy is the entire module.

---

[← Prev: 11_Memory/00_Overview]  [↑ Map](../../MAP.md)  [Next: 11_Memory/02_InMemoryMemoryService →]
