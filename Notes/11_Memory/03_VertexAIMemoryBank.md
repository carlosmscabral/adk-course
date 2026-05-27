---
module: 11_Memory
page: 03_VertexAIMemoryBank
title: VertexAiMemoryBankService — managed, auto-summarized
estimated_minutes: 25
prereqs: [11_Memory/02]
concepts: [VertexAiMemoryBankService, Agent Engine, summarization, Memory Bank]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/02_InMemoryMemoryService]  [↑ Map](../../MAP.md)  [Next: 11_Memory/04_VertexAIRagMemoryService →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 03 VertexAI Memory Bank

# ☁️ Managed memory: let Google decide what to remember

`VertexAiMemoryBankService` is a managed service that lives inside **Agent Engine**. You hand it a session's events; it summarizes them into long-lived "memory items" (facts, preferences) keyed per user, and serves them back on retrieval. You do not chunk, embed, or index — that's the trade.

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.runners import Runner

memory_service = VertexAiMemoryBankService(
    project="your-gcp-project",
    location="us-central1",
    agent_engine_id="456",  # bare numeric ID, NOT the full resource path
    # If you only have the full path "projects/.../reasoningEngines/456",
    # extract the ID: id_ = agent_engine.api_resource.name.split('/')[-1]
)

runner = Runner(
    app_name="prod-app",
    agent=agent,
    memory_service=memory_service,
)
```

The `agent_engine_id` is the Reasoning Engine resource that hosts the memory bank for *this* deployed agent. Each Agent Engine resource gets its own memory bank.

> 🪧 **Pass the bare ID, not the full path.** The constructor expects just the ID segment (e.g. `"456"`), not `"projects/.../reasoningEngines/456"`. If you pass the full path, the service logs a warning and the request will end up double-prefixed (`reasoningEngines/projects/...`) and fail at call time. See `vertex_ai_memory_bank_service.py:220-226` (warning) and `:346` / `:424` / `:481` (the `'reasoningEngines/' + self._agent_engine_id` concatenation that breaks). Extract with `agent_engine.api_resource.name.split('/')[-1]`.

## What gets stored

When you call `ctx.add_session_to_memory()`, Memory Bank:

1. Inspects the conversation's events.
2. Extracts user-relevant facts ("user prefers vegan recipes", "user lives in São Paulo").
3. Persists those as discrete memory items.
4. On retrieval (via `load_memory` or `PreloadMemoryTool`), returns the items matching a query.

You do not control the extraction prompt directly in this surface. If you want that control, use `VertexAiRagMemoryService` instead (next page).

## The Memory Bank pattern (from the `memory-bank` sample)

```python
# from adk-samples/python/agents/memory-bank/app/agent.py
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

async def generate_memories_callback(ctx: CallbackContext):
    await ctx.add_session_to_memory()
    return None

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="...you remember user preferences across sessions...",
    tools=[get_weather, get_current_time, PreloadMemoryTool()],
    after_agent_callback=generate_memories_callback,
)
```

Two pieces wire memory in:

- `PreloadMemoryTool()` in the tool list → memories are injected into the system instruction at the start of each turn (no LLM call needed).
- `after_agent_callback=generate_memories_callback` → at the end of each turn, the session's events get shipped to Memory Bank for distillation.

> ⚠️ **Gotcha.** "Auto-summarized" means the *framework* picks what to remember. If you need to remember a specific structured fact (an order number, a license plate), don't trust the summarizer to keep it — write it to `user:`-state instead. Memory Bank is for *fuzzy* personalization, not record-keeping.

> ❓ **Ask the student:** "Why does Memory Bank live inside Agent Engine, not in the ADK library?" *(Expected: because summarization needs an LLM call + storage + lifecycle; that's a managed service, not a library function.)*

> **🚀 In Production**
>
> Memory items accumulate forever. Set per-user retention (cold-storage or delete after N days) before launch. See `07_InProduction.md`.

---

[← Prev: 11_Memory/02_InMemoryMemoryService]  [↑ Map](../../MAP.md)  [Next: 11_Memory/04_VertexAIRagMemoryService →]
