---
module: 11_Memory
page: 06_DissectingMemoryBank
title: Dissecting the memory-bank sample
estimated_minutes: 30
prereqs: [11_Memory/05]
concepts: [sample read-through, Memory Bank wiring, PreloadMemoryTool in practice]
icon: 🧪
in_production: false
detours_suggested: []
---

[← Prev: 11_Memory/05_LoadMemoryTool]  [↑ Map](../../MAP.md)  [Next: 11_Memory/07_InProduction →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 06 Dissecting memory-bank

# 🧪 Reading a real Memory Bank wiring

Sample: `/home/carloscabral/study/adk-samples/python/agents/memory-bank/`

```
memory-bank/
├── app/
│   ├── agent.py              ← the agent + memory wiring (we focus here)
│   ├── agent_engine_app.py   ← deploys to Agent Engine; that's where the
│   │                            VertexAiMemoryBankService implicitly comes from
│   ├── app_utils/            ← telemetry + typing helpers
│   └── fast_api_app.py
├── Makefile
├── README.md
└── pyproject.toml
```

## Read along: `app/agent.py`

Three things to find. Have the student open the file and locate each.

### 1) Which memory tool is on the agent

```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

root_agent = Agent(
    ...,
    tools=[get_weather, get_current_time, PreloadMemoryTool()],
)
```

➜ `PreloadMemoryTool`, **not** `load_memory`. So memories are injected automatically every turn, no LLM decision needed.

### 2) How writing is wired

```python
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

root_agent = Agent(
    ...,
    after_agent_callback=generate_memories_callback,
)
```

➜ After every agent turn, the whole session's events are shipped to memory. The comment in the file flags the alternative: `callback_context.add_events_to_memory(events=...)` for incremental control.

### 3) Where the actual `MemoryService` instance comes from

It's **not** in `agent.py`. The agent declares the *intent* to use memory (callback + tool); the *backend* is wired by Agent Engine when the app is deployed. Look at `app/agent_engine_app.py`:

```python
class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        vertexai.init()
        ...
```

➜ `AdkApp` (the Agent Engine template) injects the `VertexAiMemoryBankService` automatically because the agent's `app_engine_id` ties it to the Reasoning Engine resource that owns the Memory Bank. Locally, you'd pass `memory_service=VertexAiMemoryBankService(...)` to a Runner yourself.

## The whole flow on one turn

```
   user: "I prefer celsius"
        │
        ▼
   PreloadMemoryTool retrieves "user prefers celsius"  (no-op first time, empty)
        │
        ▼
   LLM responds "Got it. Today in SF: 16°C and foggy."
        │
        ▼
   after_agent_callback fires → add_session_to_memory()
        │
        ▼
   Memory Bank summarizer extracts "user prefers celsius"
        │
        ▼
   New session, same user_id, asks weather
        │
        ▼
   PreloadMemoryTool retrieves "user prefers celsius" → injected into instruction
        │
        ▼
   LLM answers in °C without being asked. ← THIS is the payoff.
```

> ❓ **Ask the student:** "If we swapped `PreloadMemoryTool()` for `load_memory`, what would change in the user experience?" *(Expected: the model would only fetch when it thinks it needs to — first-turn recall might miss; cost goes down; consistency drops.)*

> 🤖 **Tutor:** This is the canonical Memory Bank shape. The student should be able to draw the diagram above from memory before moving on to 07_InProduction.

---

[← Prev: 11_Memory/05_LoadMemoryTool]  [↑ Map](../../MAP.md)  [Next: 11_Memory/07_InProduction →]
