---
module: 1A_AppAndRunner
page: 08_DissectingSample
title: Dissecting `memory-bank` — App in a real sample
estimated_minutes: 30
prereqs: [1A_AppAndRunner/07]
concepts: [App, memory-bank, PreloadMemoryTool, after_agent_callback]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 07_RunnerInsideTheApp](07_RunnerInsideTheApp.md)  [↑ Map](../../MAP.md)  [Next: 09_InProduction →](09_InProduction.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 08 Dissecting Sample

# 🔬 Dissecting `memory-bank` — App in a real sample

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/memory-bank/`

> 🤖 **Tutor:** open `adk-samples/python/agents/memory-bank/app/agent.py` in the student's editor. ~100 lines. The reason we chose this sample over the bigger ones (RAG, economic-research) is that **the `App(...)` construction is the last 4 lines of the file** — nothing else is competing for attention, so the App's role is unmissable.

## Why this sample

`memory-bank` is small, uses `App(...)` explicitly, and pairs the App with the `MemoryService` story we set up on page 07 (memory lives on Runner; App declares the agent that uses it). It is the cleanest demo in the sample corpus of "here is an `App`, here is what wraps it".

## What we will trace

By the end of this read-through the student should be able to:

- Point at the line that constructs the `App`.
- Name the fields the sample sets on the App (and the fields it leaves to the default).
- Explain the role of the `after_agent_callback` in connection with memory.
- Predict what changes if you added `resumability_config=ResumabilityConfig(is_resumable=True)` to the `App(...)`.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/memory-bank/` and confirm the layout. Then `ls memory-bank/app/` — they should see `agent.py`, `__init__.py`, and the wrapping `pyproject.toml` / README.

## File-by-file walkthrough

### `memory-bank/app/agent.py` — the whole story is here

Reproduced (load-bearing portion):

```python
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather."""
    ...


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city."""
    ...


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends the session's events to Memory Bank for memory generation."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(model="gemini-2.5-flash", ...),
    instruction=("You are a helpful AI assistant ..."),
    tools=[
        get_weather,
        get_current_time,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
```

Walk it top-down.

#### The two function tools (`get_weather`, `get_current_time`)

Plain Python functions with docstrings. ADK turns them into `FunctionTool` instances automatically when listed in `tools=`. Module 03 covered the pattern; nothing new here.

#### `generate_memories_callback`

An `async` callback registered via `after_agent_callback=`. It runs *after every agent turn* and calls `callback_context.add_session_to_memory()` — handing the session's events to the configured `MemoryService` for fact extraction. The agent does not have to ask; memory generation is a process side-effect.

> ❓ **Ask the student:** "The callback is wired on the agent (`after_agent_callback=`), not on the App. Why isn't there an `after_invocation_callback=` on `App`?"
> *(Expected: callbacks today are per-agent, attached to the `BaseAgent` instance, because they need access to the agent's `CallbackContext`. The App is for *config that applies to every agent*; the callback is for *behavior that wraps one specific agent's turn*. The two layers are deliberate. If you wanted a true app-level lifecycle hook, you would write a Plugin (Module 13) and add it to `App(plugins=[...])` — that is the App-level cross-cutting mechanism.)*

#### `tools=[get_weather, get_current_time, PreloadMemoryTool()]`

`PreloadMemoryTool` is a built-in that **retrieves memories at the start of every turn** and stuffs them into the system instruction. The pair with `generate_memories_callback` (after the turn) closes the loop: memories are written after each turn, read before each turn.

#### `app = App(root_agent=root_agent, name="app")`

The four-line `App` construction. This sample sets **only** the two required fields:

| Field | Set in sample? | Default if not set |
|---|---|---|
| `name` | yes (`"app"`) | required, no default |
| `root_agent` | yes | required, no default |
| `plugins` | no | `[]` |
| `events_compaction_config` | no | `None` (no compaction) |
| `context_cache_config` | no | `None` (no caching) |
| `resumability_config` | no | `None` (not resumable) |

This is the **minimal modern shape**. Every later page in this module showed you how to opt into one of the other four fields. `memory-bank` opts into none, and that is fine — defaults are reasonable for a single-agent app that already uses MemoryService for cross-session state.

## Trace one turn

```
user: "Hello, I prefer dark mode."
  → Runner.run_async receives the message
  → memory_service.search_memory called by PreloadMemoryTool (returns nothing first turn)
  → agent's instruction is interpolated with "no relevant memories"
  → LLM call to gemini-2.5-flash
  → LLM emits final text: "Hi! Noted."
  → Event yielded
  → after_agent_callback fires
  → callback_context.add_session_to_memory() runs
  → MemoryService extracts fact "user prefers dark mode"
  → fact stored in memory bank, keyed by user_id
  → next session sees this fact via PreloadMemoryTool
```

The App's role in that trace: it is the *container that owns the agent that runs*. The `name="app"` field is what `MemoryService` uses (alongside `user_id`) to scope memory entries. Two `App(name="app")` instances against the same memory backend share memories; two with different names do not.

> 🛠 **Have the student run:** the sample (the README in the sample dir has the setup steps for Memory Bank). Multi-turn conversation: introduce yourself in turn 1, ask a follow-up that references the intro in turn 2. Confirm the agent remembers. Then `await session_service.create_session(...)` for a *new* session and ask again — confirm memory persists across sessions because the `app:name` matches.

## Module concepts present in this sample

| Module concept | Where in `memory-bank/app/agent.py` |
|---|---|
| `App(root_agent=, name=)` (page 01) | last 4 lines |
| `App` config defaults (page 01, 04–06) | sample uses defaults for all 4 optional fields |
| `app:` state would be keyed by `name="app"` (page 03) | implicit in the `name` arg |
| Lifecycle hooks (page 02) | not in this file — would live in the FastAPI host or `adk api_server` |
| Runner constructed from this App (page 07) | not in this file — `adk run` / `adk api_server` does the wiring |

The point of the sample: a real-world App can be *four lines*. Everything else in the file is agent config, not App config. That is the correct ratio.

---

[← Prev: 07_RunnerInsideTheApp](07_RunnerInsideTheApp.md)  [↑ Map](../../MAP.md)  [Next: 09_InProduction →](09_InProduction.md)
