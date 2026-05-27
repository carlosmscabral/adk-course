---
module: 01_Foundations
page: 03_ToolsArePythonFunctions
title: Tools are just Python functions
estimated_minutes: 10
prereqs: [01_Foundations/02]
concepts: [tool, FunctionTool, docstring, schema]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 01_Foundations/02_RunnerSessionEvent](02_RunnerSessionEvent.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/04_StateLivesOnSession →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 03 Tools are Python functions

# 🛠 Tools are just Python functions

This is a **preview** — Module 03 is the deep dive. Goal here: deflate the word "tool" before it acquires mystique.

## 🛠 The whole punchline

```python
def get_weather(city: str) -> dict:
    """Return the current weather for the given city."""
    # ...go fetch it...
    return {"city": city, "temp_c": 19, "conditions": "drizzly"}

agent = LlmAgent(
    name="weatherbot",
    model="gemini-2.5-flash",
    instruction="Help the user with weather questions.",
    tools=[get_weather],
)
```

That's it. You pass the bare function. ADK:

1. Inspects the **type hints** and **docstring** to build a JSON schema Gemini can read.
2. Includes that schema in every LLM call so the model knows the tool exists.
3. When the model emits a tool call, ADK matches the name, deserializes arguments, calls your function, and feeds the return value back as a tool-result Event.

The class `FunctionTool` exists in `google.adk.tools`, and you can wrap explicitly with `FunctionTool(get_weather)`, but the agent accepts a bare function and wraps it for you. Both forms appear in real samples.

## 🧠 What Gemini actually sees

Roughly speaking, ADK turns the snippet above into:

```json
{
  "name": "get_weather",
  "description": "Return the current weather for the given city.",
  "parameters": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]
  }
}
```

The docstring becomes `description`. The type hints become `properties`. **No docstring → the model has no idea when to call the tool.** No type hints → the model has no idea what to pass. Module 03 has the receipts.

> ❓ **Ask the student:** if you defined `def get_weather(city, country='US'):` with no type hints, no docstring, what's the most likely failure mode?
> *(Expected: the LLM either never calls the tool, or calls it with garbage arguments. The schema is too vague to be useful.)*

## 🛠 Built-in tools

Not everything is a function you write. ADK ships built-in tools:

* `google_search` — grounded search (we saw this in `fun-facts`).
* `load_memory` — fetches from `MemoryService` (Module 11).
* `exit_loop` — used inside `LoopAgent` for early termination.
* `transfer_to_agent` — used in multi-agent routing (Module 05).

Built-ins look like regular tools to the agent. They just live in the framework instead of your codebase.

> 🛠 **Have the student do this on paper:** sketch what tools you'd give a "personal-finance-assistant" agent. (`get_balance`, `list_recent_transactions`, `add_expense`, etc.) For each, write one sentence of docstring. Notice how quickly the docstring quality determines whether the LLM would pick the right tool.

---

[← Prev: 01_Foundations/02_RunnerSessionEvent](02_RunnerSessionEvent.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/04_StateLivesOnSession →]
