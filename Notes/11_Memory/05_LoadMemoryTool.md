---
module: 11_Memory
page: 05_LoadMemoryTool
title: load_memory and PreloadMemoryTool
estimated_minutes: 20
prereqs: [11_Memory/02]
concepts: [load_memory, PreloadMemoryTool, system instruction injection, on-demand retrieval]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/04_VertexAIRagMemoryService]  [↑ Map](../../MAP.md)  [Next: 11_Memory/06_DissectingMemoryBank →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 05 LoadMemoryTool

# 🛠 Two ways the LLM sees memory

Writing memory is a callback. Reading memory is a **tool** (or a tool-like preload).

## On-demand: `load_memory`

`load_memory` is a built-in tool. The LLM calls it like any other tool, with a query string. The Runner routes it to the configured `memory_service` and returns hits.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import load_memory   # NOTE: built-in

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="recall",
    instruction=(
        "When the user references something from a past conversation, "
        "call load_memory(query=<short search phrase>) to fetch relevant memories. "
        "Otherwise answer normally."
    ),
    tools=[load_memory],
)
```

**Pattern.** Prompt the LLM explicitly. The model will not invoke `load_memory` by intuition — the instruction must say *when* to call it. If your test "what did we discuss?" turn doesn't recall, the first place to look is the instruction.

## Always-on: `PreloadMemoryTool`

`PreloadMemoryTool` (from `google.adk.tools.preload_memory_tool`) is the opposite end of the spectrum. It retrieves memories **before** the model is invoked and injects them into the system instruction. No tool call, no LLM decision.

```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = LlmAgent(
    ...,
    tools=[PreloadMemoryTool()],
)
```

Trade-off:

| Approach | When | Cost | Latency |
|----------|------|------|---------|
| `load_memory` (on-demand) | LLM decides relevance | only when called | +1 LLM round-trip when used |
| `PreloadMemoryTool` (always) | every turn | every turn | retrieval is parallel-ish |

> ⚠️ **Gotcha.** `PreloadMemoryTool` injects *all* matched memories into the system instruction. With a noisy memory bank, you bloat context every turn. Throttle with the service's `similarity_top_k` knob (see 04) or switch to `load_memory`.

## Putting reads and writes together

```python
async def remember_after_turn(ctx):
    await ctx.add_session_to_memory()
    return None

agent = LlmAgent(
    model="gemini-2.5-flash",
    instruction="...if past context relevant, call load_memory...",
    tools=[load_memory],                                    # READ
    after_agent_callback=remember_after_turn,               # WRITE
)
```

> 🛠 **Have the student run:** Wire the above with `InMemoryMemoryService`. Turn 1: "remember that I'm allergic to peanuts." Turn 2 (same session): "any dessert ideas?" Turn 3 (NEW session, same user): "any dessert ideas?" Expected: Turn 3 invokes `load_memory`, retrieves the allergy, avoids peanuts.

> 🤖 **Tutor:** If the student's turn 3 fails: check (a) did `remember_after_turn` fire on turn 1: (b) is the new session using the same `user_id`: (c) does the instruction tell the model when to call `load_memory`. All three matter.

---

[← Prev: 11_Memory/04_VertexAIRagMemoryService]  [↑ Map](../../MAP.md)  [Next: 11_Memory/06_DissectingMemoryBank →]
