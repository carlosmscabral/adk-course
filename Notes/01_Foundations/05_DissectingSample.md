---
module: 01_Foundations
page: 05_DissectingSample
title: Re-reading fun-facts/agent.py with arrows
estimated_minutes: 15
prereqs: [01_Foundations/04]
concepts: [agent, runner, session, event, runtime-plumbing]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 01_Foundations/04_StateLivesOnSession](04_StateLivesOnSession.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/06_InProduction →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 05 Dissecting fun-facts (again)

# 🧠 Re-reading fun-facts with arrows

Open [`adk-samples/python/agents/fun-facts/fun_facts/agent.py`](../../../adk-samples/python/agents/fun-facts/fun_facts/agent.py) again. Same file as Module 00, page 04. Now annotate it with what we've learned.

```python
from google.adk.agents import Agent       # ← this is LlmAgent (alias)
from google.adk.tools import google_search

root_agent = Agent(                        # ← config object. STATELESS.
    name="Facts",                          # ← appears in every Event.author
    model="gemini-2.5-flash",              # ← which LLM the Runner POSTs to
    instruction="Provide the most...",     # ← system prompt sent on every turn
    description="...",                     # ← only used in multi-agent routing
    tools=[google_search],                 # ← schema sent to Gemini on every call
)

app = App(name="fun_facts", root_agent=root_agent)  # ← deployable wrapper
```

## 🧠 Where's the Runner?

It's invisible — `adk run fun_facts` constructs it for you. Roughly:

```python
# what adk run does, in spirit
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from fun_facts.agent import root_agent

session_service = InMemorySessionService()
runner = Runner(
    app_name="fun_facts",
    agent=root_agent,
    session_service=session_service,
)
# ...then a REPL loop calling runner.run_async(...) and printing events.
```

You'll write that yourself in Module 02. **Today, just trace where each primitive would slot in.**

## 🧠 Where's the Session?

Also invisible. `adk run` calls `session_service.create_session(app_name="fun_facts", user_id="<some-id>", session_id="<new-uuid>")` on startup and reuses it for every turn of the REPL until you `exit`. When the process exits, the in-memory session vanishes.

## 🧠 Where do Events flow?

Each chunk from Gemini becomes an `Event(author="Facts", content=...)`, plus tool-call / tool-result events when the model invokes `google_search`. They're yielded from `runner.run_async(...)` and the CLI prints the text parts.

## 🧠 What the Session's event log actually looks like

Before the pop quiz, look at one. After a single tool-using turn of `fun-facts`, the Session's event log contains four `Event` objects. **The convention to internalize: the user's message is an `Event` too** — not a separate "input" the agent reads. Everything that crosses the runtime boundary is recorded as an event.

```python
session.events == [
    Event(author='user',  content=Content(parts=[Part(text='tell me a fact about whales')])),
    Event(author='Facts', content=Content(parts=[Part(function_call=...)])),       # model requests google_search
    Event(author='tool',  content=Content(parts=[Part(function_response=...)])),   # tool result comes back
    Event(author='Facts', content=Content(parts=[Part(text='Whales are...')])),    # final text reply
]
```

Four events for one tool-using turn. Hold that shape — the pop quiz below tests it.

## ❓ Pop quiz before you advance

> ❓ **Ask the student:** in `fun-facts`, if the user asks *"tell me a fact about whales"*:
>
> 1. How many events get appended to the Session in the simplest case (no tool call)?
> 2. How many if Gemini does call `google_search` once?
> 3. Where does the system prompt (`"Provide the most mind-blowing..."`) live across turns?
>
> *(Expected:*
> *1. Two — the user message, and the agent's text reply.*
> *2. Four — user message, tool-call event, tool-result event, agent's text reply.*
> *3. On the `LlmAgent` instance, NOT in the session. The Runner re-sends it on every turn.)*

> 🛠 **Have the student do this:** sketch — on actual paper or a whiteboard — the runtime timeline for one `fun-facts` turn that triggers `google_search`. Label every arrow with which primitive owns it (Runner / Session / Agent / LLM API / Tool). This is the deliverable for the mini-drill on page 08.

> 🤖 **Tutor:** if the student's sketch looks reasonable, advance to Module 02 confidently. If they can't place the `Runner`, slow down and re-walk pages 02 and 05 before any code-writing.

---

[← Prev: 01_Foundations/04_StateLivesOnSession](04_StateLivesOnSession.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/06_InProduction →]
