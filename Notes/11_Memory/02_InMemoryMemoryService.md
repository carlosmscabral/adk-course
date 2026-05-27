---
module: 11_Memory
page: 02_InMemoryMemoryService
title: InMemoryMemoryService — the dev-only backend
estimated_minutes: 15
prereqs: [11_Memory/01]
concepts: [InMemoryMemoryService, MemoryService, Runner wiring]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/01_SessionVsStateVsMemory]  [↑ Map](../../MAP.md)  [Next: 11_Memory/03_VertexAIMemoryBank →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 02 InMemoryMemoryService

# 🛠 The simplest possible MemoryService

Like `InMemorySessionService`, this is a dict in your Python process. Restart → gone. **Dev only.**

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.agents import LlmAgent

memory_service = InMemoryMemoryService()

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="remember_me",
    instruction=(
        "If asked what we have discussed, call the load_memory tool. "
        "Otherwise answer normally."
    ),
)

runner = Runner(
    app_name="dev",
    agent=agent,
    memory_service=memory_service,    # <— wire it here
)
```

The Runner now exposes `memory_service` to every callback and to the `load_memory` built-in tool (see `05_LoadMemoryTool.md`).

## Writing to memory

Memory writing is **never automatic** at the runtime level. You write in a callback:

```python
from google.adk.agents.callback_context import CallbackContext

async def remember_after_turn(ctx: CallbackContext):
    # ship the whole session's events to memory
    await ctx.add_session_to_memory()
    return None

agent = LlmAgent(
    ...,
    after_agent_callback=remember_after_turn,
)
```

`add_session_to_memory()` is the high-level "snapshot this conversation." For incremental processing, use `ctx.add_events_to_memory(events=[...])` and pick just the events worth remembering.

> ⚠️ **Gotcha.** With `InMemoryMemoryService`, "memory" is a literal Python dict keyed by `(app_name, user_id)`. Two runners in two processes do not share it. Cross-process testing requires a real backend (Vertex services or your own).

> 🛠 **Have the student run:** Start a session, say "my favorite ice cream is mango", end the session, start a new one with the same `user_id`, and ask "what flavor did I like?" If the agent doesn't recall: did the callback fire? Did the new turn invoke `load_memory`? (We'll cover both in 05.)

> **🚀 In Production**
>
> `InMemoryMemoryService` is dev-only. Swap to `VertexAiMemoryBankService` (managed, summarized) or `VertexAiRagMemoryService` (your Vector Search index) before deploying. See `07_InProduction.md` for the choice matrix.

---

[← Prev: 11_Memory/01_SessionVsStateVsMemory]  [↑ Map](../../MAP.md)  [Next: 11_Memory/03_VertexAIMemoryBank →]
