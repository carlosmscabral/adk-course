---
module: 00_Setup
page: 04_DissectingSample
title: Reading fun-facts/agent.py line by line
estimated_minutes: 20
prereqs: [00_Setup/03]
concepts: [Agent, App, google_search, root_agent]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 00_Setup/03_RepoTour](03_RepoTour.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/05_InProduction →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 04 Dissecting fun-facts

# 🧠 Dissecting fun-facts/agent.py

Open `adk-samples/python/agents/fun-facts/fun_facts/agent.py`. It's 34 lines including license and blank lines. Here's the meaningful part:

```python
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools import google_search

load_dotenv(override=True)

root_agent = Agent(
    name="Facts",
    model="gemini-flash-latest",
    instruction="Provide the most mind-blowing, obscure, and wacky fun "
                "facts about the topic. Aim for maximum 'wow' factor with "
                "rare and surprising information.",
    description="An Agent to provide fun facts about a given topic.",
    tools=[google_search],
)

app = App(name="fun_facts", root_agent=root_agent)
```

That's it. The entire agent. Let's go line by line.

## 🧠 The imports

* `from dotenv import load_dotenv` — pulls `GOOGLE_API_KEY` out of the `.env` we created.
* `from google.adk.agents import Agent` — `Agent` is the public alias for `LlmAgent`. In Module 02 you'll see both names used interchangeably; they're the same class.
* `from google.adk.apps.app import App` — `App` is the deployable unit. It wraps a root agent with optional plugins, eval cases, and serving config. The `adk run` CLI looks for either an `App` or a bare `root_agent` symbol.
* `from google.adk.tools import google_search` — a built-in tool that calls Google Search server-side via Gemini's grounding API. No keys needed beyond your Gemini key.

## 🧠 The `Agent(...)` call

| Field | Purpose |
|---|---|
| `name="Facts"` | The agent's identifier in events and logs. Pick something searchable. |
| `model="gemini-flash-latest"` | Which LLM to call. We'll standardize on `gemini-2.5-flash` from Module 02 onward (pinning > floating). |
| `instruction=...` | The system prompt. This is the agent's *personality and rules*. |
| `description=...` | A one-liner used by *other* agents when they decide whether to delegate to this one. Empty for single-agent apps; required for multi-agent. |
| `tools=[google_search]` | The list of callable tools the LLM can invoke. |

## 🧠 What's NOT here

You won't see any of these in `fun-facts/agent.py`:

* No `Runner`.
* No `Session` or `InMemorySessionService`.
* No event loop, no `async for`.
* No call to Gemini directly.

That's because `adk run fun_facts` provides all of it. The CLI is a 100-line `main()` wrapping `Runner.run_async(...)`. **In Module 02 you'll write that wrapper yourself** so you understand exactly what got hidden.

> ❓ **Ask the student:** if `adk run` does all the runtime plumbing, what does the file `agent.py` actually need to expose?
> *(Expected: a symbol named `root_agent` — or an `App` whose `root_agent` field points to the agent. The CLI imports the module and looks for these names.)*

> 🛠 **Have the student run:**
> ```bash
> $ python -c "from fun_facts.agent import root_agent; print(type(root_agent).__name__, root_agent.name, root_agent.model)"
> LlmAgent Facts gemini-flash-latest
> ```
> Note the class name: **`LlmAgent`**, not `Agent`. That's the lesson. The import `from google.adk.agents import Agent` rebinds the name — `Agent` *is* `LlmAgent`, no subclass involved. `type(...).__name__` always returns the real class. So `root_agent` is just a normal Python object, and the "framework" you're using is the `LlmAgent` class with a friendlier import name.

> 🤖 **Tutor:** if the student's output prints `Agent` instead of `LlmAgent`, something has gone wrong (probably they're on a much older ADK, or there's a stale `__pycache__`). Verify `adk --version` ≥ 2.0 and have them `rm -rf fun_facts/__pycache__` before re-running.

## 🧭 Detour pointer

If the `App` vs `root_agent` thing feels arbitrary right now, that's fine — `App` becomes important when we deploy (Module 16+). For Foundation Track you can mentally collapse "`App`" into "the wrapper that lets `adk` find your agent."

---

[← Prev: 00_Setup/03_RepoTour](03_RepoTour.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/05_InProduction →]
