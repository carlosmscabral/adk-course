---
module: 21_AdkApiSurface
page: 01_AdkRunCli
title: adk run — the shortest path from code to live agent
estimated_minutes: 15
prereqs: [21_AdkApiSurface/00]
concepts: [adk run, AgentLoader, agents_dir, REPL]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 01A_AdkRunUnderTheHood →](01A_AdkRunUnderTheHood.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 01 adk run

---

## 🛠 The shape

```
adk run <AGENT_NAME> [--session_db_url ...] [--artifact_storage_uri ...] [--replay JSON] [--resume JSON]
```

You point `adk` at a folder that contains an agent package, and it gives you a REPL.

## 🛠 A minimum agent for `adk run`

```python
# Work/21_AdkApiSurface/research_assistant/__init__.py
from .agent import root_agent  # noqa: F401
```

```python
# Work/21_AdkApiSurface/research_assistant/agent.py — minimal LlmAgent for adk run
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="research_assistant",
    instruction="You answer questions in one sentence.",
)
```

That's the entire agent. The CLI does the rest.

> 🛠 **Have the student run:** from `Work/21_AdkApiSurface/`:
> ```
> adk run research_assistant
> ```
> They should see `[user]:` prompt. Have them type *"What is the speed of light in m/s?"* and read the response.

## 🛠 The contract

Three things the CLI needs:

1. A directory passed as the **last positional arg** (or current dir).
2. That directory must contain a Python **package** (i.e., an `__init__.py`).
3. The package's `__init__.py` must expose a name `root_agent` — either an `Agent` / `LlmAgent` or an `App`.

If any of those is wrong, the CLI errors before the model is ever called. That is the entire interface — the rest is flags.

## 🛠 The flags that matter

| Flag                       | Default       | What it does                                                              |
|----------------------------|---------------|---------------------------------------------------------------------------|
| `--session_db_url`         | (in-memory)   | URI for `DatabaseSessionService` (`sqlite:///`, `postgresql://`, `agentengine://...`). |
| `--artifact_storage_uri`   | (in-memory)   | `gs://bucket` for `GcsArtifactService`.                                   |
| `--replay <path>`          | —             | Run a JSON file of turns non-interactively (regression testing).          |
| `--resume <path>`          | —             | Boot from a saved session JSON. Cross-link to **04B Resume/Cancel**.      |
| `--save_session`           | False         | On exit, dump the full session to JSON.                                   |

The defaults are the **InMemory* trio**: in-memory sessions, in-memory artifacts, in-memory memory. Perfect for hacking; useless for prod.

## ⚠️ Gotcha — `root_agent` not found

If you see `"Cannot find 'root_agent' in <package>"`, three causes in order of frequency:

1. `__init__.py` does not import `agent` (so the binding is invisible).
2. You named the variable `agent` instead of `root_agent`.
3. You passed a *file* path instead of a *package* path.

Fix #1 with `from .agent import root_agent` in `__init__.py` (rule #2 of the contract above).

> ❓ **Ask the student:** "What happens if `__init__.py` exists but is empty?" *(Loader finds the package but can't bind `root_agent` → same error as #1.)*

## 🚀 In Production

> **🚀 In Production**
>
> `adk run` is a TTY REPL. It cannot multiplex users, has no auth, no graceful shutdown, no health endpoint. Use it for **dev and replay-based regression testing only** (the `--replay` flag is genuinely useful in CI). The deployable surface is `adk api_server` (page 02) or `get_fast_api_app()` wrapped in your own process (page 06).

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 01A_AdkRunUnderTheHood →](01A_AdkRunUnderTheHood.md)
