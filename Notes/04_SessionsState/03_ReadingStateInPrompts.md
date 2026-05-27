---
module: 04_SessionsState
page: 03_ReadingStateInPrompts
title: Reading state in the instruction prompt
estimated_minutes: 15
prereqs: [04_SessionsState/02]
concepts: [prompt-template, instruction-template, optional-var]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 04_SessionsState/02_StateScopes](02_StateScopes.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/04_WritingStateFromTools →]

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 03 Reading state in prompts

# 🛠 `{var}` and `{var?}` in the instruction

The `LlmAgent.instruction` string is a **template**. ADK substitutes state values before sending it to Gemini.

```python
agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="You are talking to {user:name?}. Be warm.",
)
```

Each turn, before the LLM call, ADK reads state and replaces:
* `{user:name}` → the value, or **errors** if missing.
* `{user:name?}` → the value, or **empty string** if missing (the `?` marks the var as optional).

## 🛠 See substitution at work

```python
# Work/03_state_in_prompt.py — run with: uv run python Work/03_state_in_prompt.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

agent = LlmAgent(
    name="greeter", model="gemini-2.5-flash",
    instruction="Greet {user:name} by name.",
)

async def main():
    ss = InMemorySessionService()
    session = await ss.create_session(
        app_name="x", user_id="u", session_id="s",
        state={"user:name": "Carlos"},          # seed it
    )
    runner = Runner(app_name="x", agent=agent, session_service=ss)
    async for event in runner.run_async(
        user_id="u", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text="hi")]),
    ):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)

asyncio.run(main())
```

```text
Hello Carlos!
```

The LLM sees `"Greet Carlos by name."` because `{user:name}` was substituted from `state` before the model call.

The template is **rendered fresh each turn** — so if the user changes their name mid-conversation, the next turn's prompt reflects it.

## 🧠 Optional vs required

```python
"You are talking to {user:name}.   Be warm."   # required; errors if state missing key
"You are talking to {user:name?}.  Be warm."   # optional; renders as empty if missing
```

For genuinely optional context, **always use `?`**. The required form is for things the agent literally cannot function without (e.g., a current task description in a workflow).

## 🧠 What templating is NOT

* It is NOT Jinja2 / f-strings / format(). It's a small grammar specific to ADK that supports `{name}` and `{name?}` only.
* It is NOT a way to inject arbitrary computed values. The value substituted is whatever is in `state[name]` at render time, as-is. No formatting, no conditionals, no loops.

For richer dynamic prompts, use a **prompt provider** (a callable on the agent) — Module 07 shows the pattern.

## ❓ Quiz

> ❓ **Ask the student:** what's the substitution for `instruction="{user:name?}, how can I help?"` when `state["user:name"]` doesn't exist?
> *(Expected: `, how can I help?` — empty substitution for the missing optional var. The leading comma is a stylistic gotcha; a polished prompt would handle it like `"{user:greeting?}how can I help?"` and store the comma in the value.)*

> 🛠 **Have the student run:** the script above, varying the `state=` seed. They should see the LLM's behavior change without changing any code. **State is the difference between a one-shot agent and a conversational one.**

> 🤖 **Tutor:** if the student wonders "what if I want to substitute computed values, like the current time?" — note that you have three options: (a) a tool that returns the time, (b) a `before_model_callback` (Module 07) that rewrites the instruction, (c) a custom prompt provider. Don't dive in here — flag and move on.

---

[← Prev: 04_SessionsState/02_StateScopes](02_StateScopes.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/04_WritingStateFromTools →]
