---
module: 03_Tools
page: 05_BuiltInTools
title: Built-in tools — google_search, load_memory, exit_loop, transfer_to_agent
estimated_minutes: 15
prereqs: [03_Tools/04]
concepts: [google_search, load_memory, exit_loop, transfer_to_agent]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/04_ToolContext](04_ToolContext.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/06_ComputerUse →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 05 Built-in tools

# 🛠 Built-in tools

Not every tool is yours to write. ADK ships built-ins for common needs. Add them to `tools=[…]` like any other.

## 🛠 `google_search`

```python
from google.adk.tools import google_search

agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Answer factual questions. Use search when you need fresh info.",
    tools=[google_search],
)
```

* **What it does:** uses Gemini's grounding API to query Google Search server-side and feeds results back to the model.
* **When to use:** factual answers, recent events, public-web lookups. Used in `fun-facts` and `academic-research`.
* **Cost:** counts against your Gemini grounding quota. Free tier is generous.

## 🛠 `load_memory`

```python
from google.adk.tools import load_memory

agent = LlmAgent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="If the user references past conversations, use `load_memory`.",
    tools=[load_memory],
)
```

* **What it does:** fetches relevant past events from a configured `MemoryService` (different from Session — Memory is across-session, semantic search).
* **When to use:** long-running personal assistants, agents that need to remember user preferences over weeks.
* **Requires:** a `memory_service` attached to the Runner. Module 11 is the deep dive.

## 🛠 `exit_loop`

```python
from google.adk.tools import exit_loop

agent = LlmAgent(
    name="worker",
    model="gemini-2.5-flash",
    instruction="If you've finished the task, call exit_loop to stop early.",
    tools=[exit_loop],
)
# ... wrap inside a LoopAgent
```

* **What it does:** signals the surrounding `LoopAgent` to stop iterating early.
* **When to use:** loops where the agent itself decides when it's "done" rather than running to a fixed `max_iterations`.
* **Doesn't make sense outside a `LoopAgent`** — Module 05 covers that container.

## 🛠 `transfer_to_agent`

```python
# implicitly available in multi-agent setups.
# the LLM emits transfer_to_agent(agent_name="weather_specialist")
# to hand control to a sibling.
```

* **What it does:** routes control to a named sibling agent in a multi-agent app.
* **When to use:** explicit delegation in coordinator-worker patterns.
* **Module 05** covers the full delegation story. Mention only here.

## 🧠 When NOT to use a built-in

* `google_search` is for *public web* lookups. If you have an internal API, write a `FunctionTool` against it.
* `load_memory` is overkill for short-lived chat — Session state already remembers within a conversation.
* `exit_loop` only makes sense inside `LoopAgent`; using it elsewhere is a no-op.

## ❓ Quick map

> ❓ **Ask the student:** match each user need to the right tool kind:
> 1. "Tell me a fact about whales." → ?
> 2. "What's the exchange rate from USD to EUR?" → ?
> 3. "Remember that I prefer metric units." → ?
> 4. "OK, I'm done with this task." → ?
>
> *(Expected:*
> *1. `google_search` (built-in).*
> *2. Custom FunctionTool calling an FX API (or MCP server like `currency-agent`).*
> *3. Custom FunctionTool that writes to `user:preferences` state.*
> *4. `exit_loop`, if you're inside a `LoopAgent`. Otherwise the agent just replies with a closing message.)*

> 🛠 **Have the student do this:** open `adk-samples/python/agents/academic-research/academic_research/sub_agents/academic_websearch/agent.py` and note the `tools=[google_search]` line. That's the entire "research" half of the multi-agent app — one built-in tool plus a careful prompt.

---

[← Prev: 03_Tools/04_ToolContext](04_ToolContext.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/06_ComputerUse →]
