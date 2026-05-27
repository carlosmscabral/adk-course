---
module: 02_FirstAgent
page: 01_LlmAgentByHand
title: LlmAgent by hand
estimated_minutes: 15
prereqs: [02_FirstAgent/00]
concepts: [LlmAgent, Agent, instruction, model]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 02_FirstAgent/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/02_RunnerAndSession →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 01 LlmAgent by hand

# 🛠 `LlmAgent` by hand

The simplest possible agent, one line at a time.

## 🛠 Instantiate

```python
# Work/01_llm_agent.py — run with: uv run python Work/01_llm_agent.py
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="Reply in exactly one sentence. Be friendly.",
    description="Greets the user.",
)

print(agent)
print(type(agent).__name__)
```

```text
LlmAgent(name='greeter', model='gemini-2.5-flash', ...)
LlmAgent
```

That's a complete agent. It does nothing yet — it's a **config object**, not a running process. Calling Gemini, building the prompt, looping — that's the Runner's job (next page).

## 🧠 The four required-in-practice kwargs

| kwarg | Why |
|---|---|
| `name` | Used as `Event.author` in logs. Pick something searchable (`"greeter"`, not `"a"`). |
| `model` | The LLM to call. We pin `"gemini-2.5-flash"` throughout Foundation Track. |
| `instruction` | The system prompt. The agent's personality and rules. |
| `description` | Used by *other* agents when deciding whether to delegate. Optional for single-agent apps; required for multi-agent (Module 05). |

`tools=` defaults to `[]` and we'll add some on page 02 of Module 03. `sub_agents=`, `before_*_callback=`, `output_key=`, etc., all default to sensible None/empty.

## 🧠 `Agent` is `LlmAgent`

```python
# Work/01b_agent_alias.py — run with: uv run python Work/01b_agent_alias.py
from google.adk.agents import Agent, LlmAgent

print(Agent is LlmAgent)
```

```text
True
```

The `fun-facts` sample uses `Agent`. Real samples mix both. They are literally the same class — import either.

## ❓ Where's the API call?

> ❓ **Ask the student:** we just created an `LlmAgent`. Did Python call Gemini?
> *(Expected: no. The `LlmAgent(...)` constructor is local-only — it stores config. The API call happens later, inside `runner.run_async(...)`.)*

> 🛠 **Have the student run:** the script above. Then add two prints:
> ```python
> print(agent.instruction)   # 'Reply in exactly one sentence. Be friendly.'
> print(agent.model)         # 'gemini-2.5-flash'
> ```
> Confirm the fields are just attributes on a Python object — no magic.

## 🧭 Two-second peek under the hood

`LlmAgent` is a Pydantic model under the hood. That's why it validates your kwargs and gives you nice repr output. Don't worry about Pydantic specifics now — if you want, take detour [[PY_pydantic]] before Module 04 where we'll see validators on tool args.

---

[← Prev: 02_FirstAgent/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/02_RunnerAndSession →]
