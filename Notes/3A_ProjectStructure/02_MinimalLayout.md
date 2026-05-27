---
module: 3A_ProjectStructure
page: 02_MinimalLayout
title: The minimal layout — one agent.py
estimated_minutes: 15
prereqs: [3A_ProjectStructure/01]
concepts: [root_agent, single-file-agent, adk-discovery-minimum]
icon: 📦
in_production: true
detours_suggested: []
---

[← Prev: 01_WhyStructureMatters](01_WhyStructureMatters.md)  [↑ Map](../../MAP.md)  [Next: 03_SmallLayout →](03_SmallLayout.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 02 The minimal layout

# 📦 The minimal layout — one `agent.py`

> 🤖 **Tutor:** make sure the student understands that *this is a real, production-acceptable layout for the right project*. It's not "just a tutorial shape." `fun-facts` ships this way.

## Shape on disk

```
agents/                                ← parent dir (used by `adk web`)
└── my_agent/                          ← the agent package
    ├── __init__.py                    ← one line: imports `agent`
    └── agent.py                       ← root_agent + tools + prompt all here
```

That's it. Two files. The `agents/` parent is the directory you `cd` into before running `adk web` — the CLI scans its children.

## `my_agent/agent.py` — everything in one file

```python
# agents/my_agent/agent.py — runnable; `cd agents && adk web` to try it
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

INSTRUCTION = "Answer the user with one wacky fun fact about their topic."

root_agent = LlmAgent(
    name="fun_facts",
    model="gemini-2.5-flash",
    instruction=INSTRUCTION,
    description="Returns one weird fun fact per query.",
    tools=[google_search],
)
```

Three things to notice:

1. The module-level variable is named **exactly** `root_agent`. ADK's discovery looks for that name (more in [05](05_AdkCliExpectations.md)).
2. `INSTRUCTION` is a module-level constant. When this grows past ~20 lines, you'll move it to `prompts.py` — that's the page-02 → page-03 trigger.
3. No `if __name__ == "__main__":` block needed. You run the agent via `adk web` or `adk run my_agent`, not by `python agent.py`.

## `my_agent/__init__.py` — the import line that matters

```python
# agents/my_agent/__init__.py
from . import agent
```

That single import is the **discovery hook**. It tells Python "loading `my_agent` should execute `agent.py`," which is when `root_agent` becomes attached to the `my_agent.agent` namespace. Without it, `adk web` will silently show no agents.

> ⚠️ **The `__init__.py` gotcha** — if `__init__.py` is empty (or missing), `adk web` will list the directory but never load `root_agent`. The error message is usually unhelpful. We treat this as **the** ADK CLI gotcha; full reference in [05_AdkCliExpectations](05_AdkCliExpectations.md).

## Run it

> 🛠 **Have the student run:**
>
> ```bash
> cd agents
> adk web
> # then visit http://localhost:8000 and pick `my_agent` from the dropdown
> ```
>
> If the dropdown is empty, the `__init__.py` is wrong. If it lists `my_agent` but loading errors out, the import inside `agent.py` is wrong (almost always: forgot to install `google-adk`).

## When this layout stops fitting

The minimal layout starts cracking when **any one** of these is true:

- `INSTRUCTION` is longer than ~30 lines (prompt sprawl).
- You're adding a third tool to `tools=[...]` (multi-tool fatigue).
- You want to `import lookup_customer` from a test file (testability).

When any of those hits, → [03 Small layout](03_SmallLayout.md).

> **🚀 In Production**
>
> `fun-facts` ships in production with literally this shape. Don't apologize for the minimal layout — it's the *correct* answer for any agent whose prompt fits on a screen and whose tools list fits on a line. We revisit this in [10_InProduction](10_InProduction.md).

> ❓ **Ask the student:** look at the `fun-facts` sample (`adk-samples/python/agents/fun-facts/fun_facts/agent.py`). How many lines of "real code" does it have, excluding the license header? (Expected: ~10. Yes — that's a real, deployed agent.)

---

[← Prev: 01_WhyStructureMatters](01_WhyStructureMatters.md)  [↑ Map](../../MAP.md)  [Next: 03_SmallLayout →](03_SmallLayout.md)
