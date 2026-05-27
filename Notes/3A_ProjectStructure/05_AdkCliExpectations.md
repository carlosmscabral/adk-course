---
module: 3A_ProjectStructure
page: 05_AdkCliExpectations
title: What adk web / adk run / adk api_server expect on disk
estimated_minutes: 20
prereqs: [3A_ProjectStructure/04]
concepts: [root_agent-discovery, agents-parent-dir, __init__-import-rule, app-vs-agent]
icon: ⚠️
in_production: true
detours_suggested: []
---

[← Prev: 04_GrowingLayout](04_GrowingLayout.md)  [↑ Map](../../MAP.md)  [Next: 06_DeploymentExpectations →](06_DeploymentExpectations.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 05 What the adk CLI expects

# ⚠️ What `adk web` / `adk run` / `adk api_server` look for

> 🤖 **Tutor:** this page is the "why does my agent not show up?" diagnostic. The vast majority of CLI confusion students will hit comes from one of the **four discovery rules** below. Memorize them — when something doesn't load, walk these rules first.

## The four discovery rules

### Rule 1 — the working directory has to be the **parent** of the agent package

`adk web` and `adk run` look in *your current directory* for child folders that are agent packages. So if your layout is:

```
my_project/
└── agents/
    └── my_agent/
        ├── __init__.py
        └── agent.py
```

You run:

```bash
cd my_project/agents
adk web          # finds my_agent/
# or
adk run my_agent
```

**Not** from `my_project/agents/my_agent/`. The CLI treats *your CWD* as the agent registry — children of CWD become picklist entries.

> ⚠️ Running `adk web` from inside `my_agent/` will show an empty list. The student will assume their agent is broken; it's just the wrong directory.

You can also pass the parent directory explicitly as a positional argument — `adk web ./agents`. `agents_dir` is positional in `adk web` / `adk run` / `adk api_server` (see `cli/cli_tools_click.py:1745-1751`); defaults to cwd if omitted. We show this in [06 Deployment](06_DeploymentExpectations.md) for Cloud Run.

### Rule 2 — `__init__.py` typically does `from . import agent` for env-var ordering

```python
# my_agent/__init__.py
from . import agent
```

Samples typically include `from . import agent` in `__init__.py` so that package-level side effects (like `dotenv.load_dotenv()`) run before agent construction. ADK's loader will find the agent without this import — `cli/utils/agent_loader.py:155-204` calls `importlib.import_module(f"{agent_name}.agent")` directly, so an empty `__init__.py` works for discovery. The requirement is environmental setup, not discovery.

**Why samples still do it**: `travel_concierge/__init__.py` sets `GOOGLE_CLOUD_PROJECT` / `GOOGLE_GENAI_USE_VERTEXAI` and then `from . import agent`, guaranteeing the env vars are present when `agent.py` constructs its Gemini clients at import time. `fun-facts` achieves the same end by calling `load_dotenv()` inside `agent.py` itself; both are valid.

**Symptom of getting it wrong**: not "agent not found" — discovery still works — but `agent.py` constructs a client before your env vars are set, and you get a confusing auth/config error at first model call.

### Rule 3 — the variable must be named `root_agent` (or `app`)

```python
# inside agent.py
root_agent = LlmAgent(...)
```

ADK's CLI looks for one of these module-level names, in order:

1. `app` — an `App` instance (the 2.0-preferred shape; see [Module 1A](../1A_AppAndRunner/)).
2. `root_agent` — a plain agent instance (any of `LlmAgent`, `SequentialAgent`, `WorkflowAgent`, …).

If your variable is named `agent`, `my_agent`, `the_agent`, or anything else, the CLI cannot find it. `fun-facts` uses `app`; `llm-auditor` uses `root_agent`. Both work.

```python
# Acceptable
app = App(name="fun_facts", root_agent=root_agent)

# Also acceptable
root_agent = LlmAgent(...)

# NOT discovered
my_root = LlmAgent(...)        # ← wrong name; CLI won't find it
```

### Rule 4 — the package name is the picklist entry

Whatever the **directory** is called is the name `adk web` shows and `adk run` accepts:

```
agents/
├── auditor/          ← shows up as "auditor"
└── research_bot/     ← shows up as "research_bot"
```

So if you want the user-facing name to be `customer-service` (with a dash), you can't — Python package names can't have dashes. Real samples work around this with `customer-service/` (the **outer** project folder, hyphenated) containing `customer_service/` (the **inner** Python package, underscored). The CLI sees the inner one.

## A diagnostic walk

When the student says "my agent doesn't show up":

> 🛠 **Have the student run, in order:**
>
> ```bash
> pwd                          # are we in the parent of the agent package?
> ls                           # is `my_agent/` a child here?
> cat my_agent/__init__.py     # if env vars are needed, is `from . import agent` (or `load_dotenv()`) wired before construction?
> grep -n root_agent my_agent/agent.py    # is there a `root_agent =` line?
> ```
>
> One of these four answers will be wrong. The fix is mechanical.

## `adk run` vs `adk web` vs `adk api_server`

All three follow the same discovery rules. They differ in **what they do** once they find the agent:

| Command | What it does | When to use |
|---|---|---|
| `adk run <name>` | Drops into a REPL; one user-input → one model turn. | Quick smoke tests, no UI needed. |
| `adk web` | Boots a Next.js UI on `localhost:8000`. Lets you switch agents, see events, replay sessions. | The default during development. |
| `adk api_server` | Serves the FastAPI surface (`/run`, `/run_sse`, sessions, events) without the UI. | When you want to hit the agent from `curl` / a frontend, or test as if Cloud Run were serving it. |

Full coverage of these commands and their HTTP endpoints lives in [Module 21 ADK API Surface](../21_AdkApiSurface/).

## The `App` vs `root_agent` choice

2.0 prefers an `App` wrapper:

```python
# agent.py with App
from google.adk.agents import LlmAgent
from google.adk.apps.app import App

root_agent = LlmAgent(name="x", model="gemini-2.5-flash", instruction="...")
app = App(name="my_agent", root_agent=root_agent)
```

The `App` is the container for runtime config — startup/shutdown hooks, resumability, context caching, compaction. For toy agents the bare `root_agent` is enough; for anything you'll deploy, prefer `app`. Full treatment in [Module 1A](../1A_AppAndRunner/).

> **🚀 In Production**
>
> Always set `app = App(...)` in production, even if you don't use the lifecycle hooks yet. Adding `app:` state (the cross-session boundary) later, or wiring resumability, becomes a single-line change instead of a refactor. The minimal `App(name=..., root_agent=...)` form is free.

> ❓ **Ask the student:** "Why does `adk run my_agent` work but `python my_agent/agent.py` raise `ImportError: attempted relative import with no known parent package`?"
>
> *(Expected: `python file.py` runs the file as `__main__`, severing it from its package context; `adk run` imports it as part of the `my_agent` package, so `from .prompts import ...` resolves.)*

---

[← Prev: 04_GrowingLayout](04_GrowingLayout.md)  [↑ Map](../../MAP.md)  [Next: 06_DeploymentExpectations →](06_DeploymentExpectations.md)
