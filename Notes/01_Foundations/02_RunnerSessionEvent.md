---
module: 01_Foundations
page: 02_RunnerSessionEvent
title: Runner, Session, Event — the three runtime primitives
estimated_minutes: 20
prereqs: [01_Foundations/01]
concepts: [Runner, Session, Event, runtime-plumbing]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 01_Foundations/01_WhatIsAnAgent](01_WhatIsAnAgent.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/03_ToolsArePythonFunctions →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 02 Runner, Session, Event

# 🧠 Runner, Session, Event

The agent itself (`LlmAgent(...)`) is **stateless and reusable** — it's a config object. To make a conversation *happen*, ADK introduces three runtime primitives.

## 🧠 The three boxes

| Box | What it is | What it owns |
|---|---|---|
| **Runner** | The orchestrator. Owns the agent loop. | Reference to the agent, the session service, optional memory/artifact services. |
| **Session** | The conversation container. One per user-conversation pair. | The event log (chat history) and the state dict. |
| **Event** | One row in the log. Append-only. | Author (which agent), content (text/tool-call/tool-result), optional `state_delta`. |

A useful metaphor: if the agent is the *recipe*, the Runner is the *cook*, the Session is the *plate as it's being built*, and each Event is the *cook narrating the next action* ("added garlic", "deglazed pan").

## 🧠 Timeline of one turn

```
{{INCLUDE _figures/runtime_timeline.txt}}
```

What that ASCII timeline shows:

1. The caller hands the Runner a new user message.
2. The Runner fetches the Session (history + state) and POSTs everything to Gemini.
3. Gemini streams back a reply. The Runner wraps each chunk as an **Event**, yields it to the caller, and appends it to the Session.
4. If the reply was a tool call, the Runner executes the tool, wraps the result as another Event, and posts again. Loop until text reply.

The caller drives iteration by `async for event in runner.run_async(...)`. The generator finishes when the agent's done.

## 🧠 Why split it into three?

Because each piece can swap independently in production:

* **Runner** stays the same; you'll rarely subclass it.
* **Session** has multiple implementations:
  * `InMemorySessionService` — lost on process restart, perfect for dev.
  * `DatabaseSessionService(db_url="sqlite:///...")` — local SQLite file, great for single-machine deployments.
  * `DatabaseSessionService(db_url="postgresql://...")` — Postgres-backed, multi-instance ready.
  * `VertexAiSessionService` — Google-managed, integrated with Agent Engine.
* **Event** is a uniform schema; the same `Event` type flows from any agent through any plugin (Module 13). Plugins can observe or transform events without knowing about the agent's internals.

> ❓ **Ask the student:** the agent (`LlmAgent(...)`) is stateless. Where, then, does "the conversation so far" live?
> *(Expected: in the Session, as a list of Events. The Runner re-reads it on every turn and stuffs it into the next LLM call.)*

## 🧠 What "events stream" actually means

`runner.run_async(...)` returns an **async generator** of Events. You iterate with `async for`. Each iteration may be:

* A partial-text chunk (Gemini streaming a reply token-by-token).
* A complete tool-call event.
* A tool-result event.
* A final reply event with `event.is_final_response() == True`.

You're not obligated to do anything with intermediate events — you can ignore everything except the final response. But observability platforms (Module 15) want them all.

> **🚀 In Production**
>
> Always pick the right `SessionService` early. Swapping from `InMemorySessionService` to `DatabaseSessionService` after launch means migrating live conversations or losing them. The cheap-and-cheerful play: use `DatabaseSessionService(db_url="sqlite:///sessions.db")` from day one — same API, persists to a file, no infra. Switch the URL to Postgres when you go multi-instance.

> 🛠 **Have the student do this on paper:** label each box in the timeline figure with which framework class it corresponds to (`Runner`, `Session`, `InMemorySessionService`, `LlmAgent`, `Event`). Then circle which boxes will swap in production.

---

[← Prev: 01_Foundations/01_WhatIsAnAgent](01_WhatIsAnAgent.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/03_ToolsArePythonFunctions →]
