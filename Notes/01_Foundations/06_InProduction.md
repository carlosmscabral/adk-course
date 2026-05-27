---
module: 01_Foundations
page: 06_InProduction
title: Foundations — production checklist
estimated_minutes: 10
prereqs: [01_Foundations/05]
concepts: [model-tier, loop-bound, cold-start, session-backend]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 01_Foundations/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/07_KnowledgeCheck →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 06 In Production

# 🚀 Production checklist — Foundations

You haven't shipped anything yet, but the architecture decisions you make in Modules 02-04 will lock in based on what you absorb now.

## 🚀 1. Pick the right model tier per agent

Flash for tool-routing and short replies (cheap, fast). Pro for synthesis and long reasoning. In a multi-agent app each sub-agent picks its own tier — coordinator on Pro, leaf workers on Flash. **Default to Flash, promote with evidence.**

## 🚀 2. Cap the loop

There is nothing in the agent loop that prevents the LLM from calling tools forever. Two cap mechanisms:

* For workflow-style flows: `LoopAgent(max_iterations=N)`.
* For chat-style flows: pass a `RunConfig(max_iterations=N)` to `runner.run_async(...)`.

Without a cap, a bad-prompt + flaky-tool combination can run up your bill before anyone notices.

## 🚀 3. Cold-start matters

The first call to a fresh `Runner` instantiates auth clients, loads the model spec, and warms the session backend. In serverless deploys (Cloud Run, Agent Engine) this happens per container. Cache the Runner at module scope, not per-request:

```python
# good — built once per process
RUNNER = Runner(...)

def handle(req):
    async for event in RUNNER.run_async(...):
        ...
```

```python
# bad — built per request, adds 200-800ms per call
def handle(req):
    runner = Runner(...)
    async for event in runner.run_async(...):
        ...
```

## 🚀 4. Don't share sessions across users

`session_id` must be unique per *conversation*. **Never** reuse a `session_id` across users — events are written into the session by anyone with the ID, so cross-user reuse means data leaks. The `user_id` parameter is your safety net (Sessions are scoped by `(app_name, user_id, session_id)`), but don't rely on it; pick UUIDs.

## 🚀 5. Pick a session backend that matches your topology

| Topology | Backend |
|---|---|
| One process, dev/test | `InMemorySessionService` |
| One machine, persistent | `DatabaseSessionService(db_url="sqlite:///...")` |
| Multi-instance, self-hosted | `DatabaseSessionService(db_url="postgresql://...")` |
| Google-managed | `VertexAiSessionService` |

Migrating from in-memory to persistent after launch means losing live conversations. **Default to `DatabaseSessionService` with a SQLite URL even in dev** — same API, real persistence, swap URL when you go multi-instance.

## 🚀 6. Plan for observability now, not later

Even at the Foundations stage, get familiar with the `Event` schema. Module 15 (Observability) shows how plugins tap the event stream to write traces — but you can already preview it by `print`-ing events in your dev loop. The discipline of "every interesting moment is an event" pays dividends.

> ❓ **Ask the student:** of the six rules above, which would have caught the bug in [a hypothetical] postmortem where "users in the same Slack channel started seeing each other's chat histories"?
> *(Expected: rule 4 — somebody reused `session_id` across users. Production agents pick a UUID per conversation.)*

---

[← Prev: 01_Foundations/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/07_KnowledgeCheck →]
