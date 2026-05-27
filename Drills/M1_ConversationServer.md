---
module: Drills
page: M1_ConversationServer
title: Milestone M1 — Conversation Server (CLI loop, two tools, persistent todos)
estimated_minutes: 480
prereqs: [00_Setup/last, 01_Foundations/last, 02_FirstAgent/last, 03_Tools/last, 04_SessionsState/last]
concepts: [LlmAgent, Runner, FunctionTool, ToolContext, state-prefixes, user-scoped-state, in-memory-vs-persistent]
icon: 🏁
in_production: false
detours_suggested: []
---

[← Prev: 04_SessionsState/10_MiniDrill]  [↑ Map](../MAP.md)  [Next: 05_MultiAgent/00_Overview →]

You are here: 🗺 Drills ▸ 🏁 M1 Conversation Server

## 🏁 What you're building

A **CLI todo agent**. The user types into a terminal loop; the agent maintains a todo list across turns using ADK Session state. Two tools:

- `add_todo(text: str, tool_context: ToolContext) -> str` — appends to `state["user:todos"]`.
- `list_todos(tool_context: ToolContext) -> str` — returns the current list.

The loop continues until the user types `exit`. At the end, the script prints the final state for inspection.

This is the **integration test for the Foundation Track**. If you can build M1 without re-reading the modules, you've internalized Agent + Runner + Session + Tools + State. If you can't, the gaps will be visible and you'll know exactly which module to revisit.

## 🎯 Goals

- Wire `LlmAgent`, `Runner`, and `InMemorySessionService` from scratch — no scaffolding.
- Define two `FunctionTool`-eligible functions with proper docstrings (the LLM uses them as the schema, see Module 03 page 03).
- Use `tool_context.state` to read and write — and use the correct `user:` prefix so the todos belong to the user, not to one session.
- Drive a real `async` loop around `runner.run_async`.
- Observe `state_delta` semantics: a tool write is visible to the next LLM turn, not magically before.

## 📋 Prereqs

- Completed `Notes/00_Setup` through `Notes/04_SessionsState`, both mini-drills.
- An LLM key in `.env` (`GOOGLE_API_KEY=...`, `GOOGLE_GENAI_USE_VERTEXAI=FALSE`).
- Python ≥ 3.11, `google-adk` installed.

## ⏱ Time

**~1 day** (~6-8 hours actual). Most of the time goes into discovering the small bugs — state-prefix mistakes, mutation vs. reassignment, async-generator semantics. Embrace those bugs; they're the point.

## 📐 Spec

### File layout

```
Work/M1/
├── conversation_server.py     ← your script
└── (state lives in memory; bonus: persist to sqlite)
```

### Required behavior

1. **CLI loop.**

   ```
   You: add buy milk
   Agent: Added "buy milk" to your todos.
   You: add call dentist
   Agent: Added "call dentist" to your todos.
   You: what's on my list?
   Agent: You have 2 todos: buy milk, call dentist.
   You: exit
   --- Final state ---
   {'user:todos': ['buy milk', 'call dentist']}
   ```

2. **Two tools.** Function signatures (docstrings are the schema — Module 03 page 03):

   ```python
   def add_todo(text: str, tool_context: ToolContext) -> str:
       """Append a todo item to the user's persistent todo list.

       Args:
         text: The text of the todo item to add.

       Returns:
         A confirmation string the agent can relay to the user.
       """
       ...

   def list_todos(tool_context: ToolContext) -> str:
       """Return the user's current todo list as a human-readable string.

       Returns:
         A short summary like "You have 2 todos: buy milk, call dentist."
         If the list is empty, says so.
       """
       ...
   ```

3. **State key: `user:todos`** — with the `user:` prefix. The list survives across `session_id`s for the same `user_id`. (Test this in the bonus.)

4. **List mutation discipline.** Don't `state["user:todos"].append(x)` in place. Do:

   ```python
   todos = list(tool_context.state.get("user:todos", []))
   todos.append(text)
   tool_context.state["user:todos"] = todos     # reassign the whole value
   ```

   (Why: in-place mutation can confuse delta tracking. Module 04 page 04 warned you.)

5. **One Runner, one session for the whole loop.** Create them once at startup, reuse on every turn. Do NOT create a fresh session per turn — you'd lose all context.

6. **At exit, print the final session state** so you can verify the todos persisted.

### Sample skeleton (don't copy verbatim — write it from memory first)

```python
import asyncio, uuid
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

load_dotenv()

APP_NAME = "todo_app"
USER_ID  = "carlos"

def add_todo(text: str, tool_context: ToolContext) -> str:
    """Append a todo item to the user's persistent todo list."""
    todos = list(tool_context.state.get("user:todos", []))
    todos.append(text)
    tool_context.state["user:todos"] = todos
    return f'Added "{text}".'

def list_todos(tool_context: ToolContext) -> str:
    """Return the user's current todo list as a string."""
    todos = tool_context.state.get("user:todos", [])
    if not todos:
        return "You have no todos."
    return f"You have {len(todos)} todos: " + ", ".join(todos)

agent = LlmAgent(
    name="todo_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You help the user manage a todo list. When they want to add an item, "
        "call add_todo. When they want to see the list, call list_todos. "
        "Keep replies short."
    ),
    tools=[add_todo, list_todos],
)

async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=str(uuid.uuid4())
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() == "exit":
            break
        content = types.Content(role="user", parts=[types.Part(text=user_text)])
        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            if event.is_final_response() and event.content:
                print("Agent:", event.content.parts[0].text)

    final = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print("--- Final state ---")
    print(dict(final.state))

if __name__ == "__main__":
    asyncio.run(main())
```

## ✅ Verification rubric

Run the script and execute this exact sequence:

```
You: add buy milk
You: add call dentist
You: add ship the readme
You: what's on my list?
You: exit
```

| Check | Pass criterion |
|---|---|
| Turn 1-3 succeed | Agent confirms each add. No tracebacks. |
| Turn 4 lists all 3 todos | The reply mentions "buy milk", "call dentist", and "ship the readme" in some order. |
| Final state print | Contains `'user:todos': ['buy milk', 'call dentist', 'ship the readme']`. |
| Prefix discipline | The key is **`user:todos`**, not bare `todos`. (Grep your code.) |
| Reassignment discipline | Tool reassigns the whole list to `state["user:todos"]`, not `.append()` in place. |

If the final-state print shows `'todos': [...]` (no prefix), **fail** — refactor before moving on. The whole Foundation Track has been pushing you to that prefix.

## 🌟 Stretch goals

1. **`remove_todo(index: int)`.** Add a third tool that removes a todo by 1-based index. Trains you to think about argument types and validation (what if the LLM passes index 0 or 99?).
2. **Persist across script runs with SQLite.** Swap `InMemorySessionService` for `DatabaseSessionService(db_url="sqlite:///Work/M1/state.db")`. Re-run the script with a **new** `session_id` but the same `user_id` — turn 1 should see the previous run's todos because `user:todos` is user-scoped, not session-scoped. (Module 04 page 06.)
3. **`complete_todo(index: int)`.** Mark a todo as done rather than removing it. Store todos as `{"text": "...", "done": False}` dicts instead of strings. Forces you to confront the reassign-don't-mutate rule when toggling a nested field.

## 🤖 Tutor notes

- **The #1 failure mode is the `user:` prefix.** If the student writes `state["todos"]` (no prefix), the script *passes* turns 2-4 in the same session — state lookup works fine within one session. The bug only surfaces on the stretch goal where a new `session_id` is used. Watch for it on first read of their code; flag it before they run.
- **The #2 failure mode is in-place mutation.** `state["user:todos"].append(x)` will probably work in the in-memory backend, but it's brittle and breaks once they swap to `DatabaseSessionService` (Stretch #2) where state writes go through a delta-diff layer. Push them to the read-copy-reassign pattern even when the current run "works."
- **A subtler bug: creating a fresh session per turn.** Some students wrap the session creation inside the `while True` loop. Symptom: every turn forgets the previous one entirely. The agent sounds like it has amnesia. Fix: create the session once before the loop.
- **`is_final_response()` is the right event filter.** If they iterate every event and print, they'll see tool-call events too and the UX is noisy. Module 02 page 03 covered this.
- **Don't let them skip the final-state print.** That's how they *see* the state structure. Without it, the prefix bug is invisible.
- **Stretch #2 is where everything they learned in Module 04 comes home.** If they get there and the persistence works on a fresh `session_id`, they have truly internalized state scopes. Celebrate it.

## ❓ Self-check questions

> ❓ **Before coding:**
> 1. What's the difference between `state["todos"]` and `state["user:todos"]`?
> 2. Why does `tool_context.state["x"] = y` work but `state["x"] = y` (outside a tool) not?
> 3. If your script creates a new session every turn, what does the agent forget?

> ❓ **After it works:**
> 1. Why does Stretch #2 require *no* code change to the tools — only the session service swap?
> 2. If two users share a process (different `user_id`s, same `app_name`), do they share `user:todos`? Why or why not?
> 3. If you wanted a todo list that resets every conversation but a *name* that persists across conversations, which prefixes would you use for which?

---

[← Prev: 04_SessionsState/10_MiniDrill]  [↑ Map](../MAP.md)  [Next: 05_MultiAgent/00_Overview →]
