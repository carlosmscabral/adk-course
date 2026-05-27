---
module: 02_FirstAgent
page: 06_InProduction
title: First-Agent production checklist
estimated_minutes: 10
prereqs: [02_FirstAgent/05]
concepts: [session-persistence, runner-caching, session-id-uniqueness]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 02_FirstAgent/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/07_KnowledgeCheck →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 06 In Production

# 🚀 Production checklist — First Agent

What you just built (Runner + InMemorySession + LlmAgent) is *the same shape* you ship to production. The only swap-outs:

## 🚀 1. Replace `InMemorySessionService` immediately

In-memory sessions vanish on process restart. Real deployments use one of:

| Backend | Use when |
|---|---|
| `DatabaseSessionService(db_url="sqlite:///sessions.db")` | Single instance, file-backed. Lowest friction. |
| `DatabaseSessionService(db_url="postgresql://...")` | Multi-instance, shared backend. Default for serious apps. |
| `VertexAiSessionService(...)` | Running on Agent Engine / Vertex AI. Managed by Google. |

Migrate by changing one line. The API is identical.

## 🚀 2. Cache the Runner at module scope

```python
# good
_RUNNER = Runner(app_name="x", agent=root_agent, session_service=ss)

async def handle(req): 
    async for ev in _RUNNER.run_async(...): ...
```

A fresh Runner pays for auth, model spec resolution, plugin init. Per-request runners cost 200-800ms each. **Build once, reuse forever.**

## 🚀 3. Make `session_id` a true UUID, not user-derived

```python
# DANGEROUS
session_id = f"user-{user_email}-chat"  # collisions across tabs, reuse leaks data

# CORRECT
import uuid
session_id = str(uuid.uuid4())
```

Sessions are scoped by `(app_name, user_id, session_id)`. If two users hit the same `session_id` by accident, they read each other's events.

## 🚀 4. Always set a timeout / iteration cap

Without it, a broken prompt + flaky tool can run the loop forever, burning quota. Two mechanisms:

* For chat-style agents: `runner.run_async(..., run_config=RunConfig(max_iterations=10))`.
* For workflow-style: `LoopAgent(max_iterations=N)`.
* Always: wrap `async for` in an `asyncio.wait_for(...)` with a wall-clock timeout.

## 🚀 5. Handle the no-final-response case

`is_final_response()` is **not guaranteed** to fire. Model errored, you cancelled, max-iterations hit — any of these end the generator without a final. Always:

```python
final_text = None
async for event in runner.run_async(...):
    if event.is_final_response() and event.content and event.content.parts:
        final_text = event.content.parts[0].text

if final_text is None:
    log.warning("no final response", extra={...})
    return "Sorry, I couldn't generate a reply."
```

## 🚀 6. Inject `app_name` from config, not hard-code

`app_name` is part of the session primary key. Hard-coded `"hello"` everywhere = horrible to rename later. Read it from your config / env once.

> ❓ **Ask the student:** of the six rules, which one would catch the bug "users report their conversations are reset every time we deploy"?
> *(Expected: rule 1 — they're using `InMemorySessionService`. Every deploy = fresh process = lost sessions.)*

> 🤖 **Tutor:** when you check the student's mini-drill solution (next page), look for these rules. The drill doesn't *require* all of them (it's a one-shot script), but you can point out where rule 1, 2, or 3 would change their code if it were a real service.

---

[← Prev: 02_FirstAgent/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/07_KnowledgeCheck →]
