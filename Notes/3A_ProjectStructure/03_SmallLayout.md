---
module: 3A_ProjectStructure
page: 03_SmallLayout
title: The small layout — agent + tools + prompts split
estimated_minutes: 18
prereqs: [3A_ProjectStructure/02]
concepts: [tools-py, prompts-py, three-file-split, relative-imports]
icon: 📦
in_production: true
detours_suggested: [PY_packaging]
---

[← Prev: 02_MinimalLayout](02_MinimalLayout.md)  [↑ Map](../../MAP.md)  [Next: 04_GrowingLayout →](04_GrowingLayout.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 03 The small layout

# 📦 The small layout — three files, one agent

> 🤖 **Tutor:** the migration from minimal → small is **one of the most common refactors** in real ADK projects. Walk the student through doing it on their own `Work/` file at the end of this page — it's literally cut/paste/import.

## Shape on disk

```
agents/
└── my_agent/
    ├── __init__.py
    ├── agent.py            ← only wiring: root_agent = LlmAgent(..., tools=[...])
    ├── tools.py            ← function definitions, no agent
    └── prompts.py          ← INSTRUCTION strings, no agent
```

Three files. The agent file shrinks to ~15 lines and becomes *all wiring, no logic*. That's the point.

## `my_agent/prompts.py`

```python
# agents/my_agent/prompts.py — no ADK imports here, just strings.

ROOT_INSTRUCTION = """\
You are a helpful research assistant.

Use the `lookup_customer` tool when the user asks about a specific customer.
Use the `recent_orders` tool when they ask about purchase history.

Be concise. If a tool returns nothing, say so explicitly.
"""

LOOKUP_DESCRIPTION = "Look up a customer by ID and return their profile."
```

Prompts are **pure strings**. No imports from `google.adk`. This makes them easy to test (just `assert "concise" in ROOT_INSTRUCTION`) and easy to diff in PRs.

## `my_agent/tools.py`

```python
# agents/my_agent/tools.py — function definitions only, no LlmAgent.
from google.adk.tools import ToolContext


def lookup_customer(customer_id: str, tool_context: ToolContext) -> dict:
    """Look up a customer by ID. Returns their profile or {'error': ...}."""
    # In real code: query a DB. Here: stub.
    if customer_id == "C001":
        return {"id": "C001", "name": "Ada Lovelace", "tier": "gold"}
    return {"error": f"no customer with id {customer_id!r}"}


def recent_orders(customer_id: str, limit: int = 5) -> list[dict]:
    """Return the most recent `limit` orders for `customer_id`."""
    return [{"order_id": f"O{i}", "customer": customer_id} for i in range(limit)]
```

Tools are **plain functions** (no `FunctionTool(...)` wrapper needed — see [03_Tools/02_FunctionTool](../03_Tools/02_FunctionTool.md)). The agent imports them as callables.

## `my_agent/agent.py`

```python
# agents/my_agent/agent.py — wiring only.
from google.adk.agents import LlmAgent

from .prompts import ROOT_INSTRUCTION
from .tools import lookup_customer, recent_orders

root_agent = LlmAgent(
    name="research_assistant",
    model="gemini-2.5-flash",
    instruction=ROOT_INSTRUCTION,
    description="Looks up customers and their order history.",
    tools=[lookup_customer, recent_orders],
)
```

This is what "all wiring, no logic" looks like. Compare to the minimal version — same agent, the prompt + tool source moved out.

## `my_agent/__init__.py` — unchanged

```python
# agents/my_agent/__init__.py
from . import agent
```

The discovery hook does not change as you scale up. It always says "execute `agent.py` on package import."

## The relative-import gotcha

In `agent.py` you wrote `from .prompts import ROOT_INSTRUCTION` (note the dot). This **only works because `__init__.py` exists** — the dot tells Python "look inside this package." If you run `python my_agent/agent.py` directly, you'll get `ImportError: attempted relative import with no known parent package`. That's fine — you're not supposed to run it that way; use `adk run my_agent` or `adk web`.

> 🧭 **If the student gets the import error:** they're trying to run `agent.py` as a script. Show them `adk run my_agent` from the parent dir instead.

## Refactor: minimal → small in 3 minutes

> 🛠 **Have the student** open their `Work/03_calc_agent.py` (or any single-file agent they wrote) and:
>
> 1. Make a folder `Work/calc_agent/`.
> 2. Move the function bodies into `Work/calc_agent/tools.py`.
> 3. Move the `INSTRUCTION` constant into `Work/calc_agent/prompts.py`.
> 4. Move the `root_agent = LlmAgent(...)` construction into `Work/calc_agent/agent.py`, with `from .prompts import ...` and `from .tools import ...` at the top.
> 5. Add `Work/calc_agent/__init__.py` with one line: `from . import agent`.
> 6. From `Work/`, run `adk web` and confirm `calc_agent` appears in the dropdown.
>
> Time-box: 5 minutes. If they're stuck past 5, the failure is almost certainly the missing `__init__.py` or running from the wrong directory.

## When this layout stops fitting

The small layout cracks when **any** of these is true:

- You add a **sub-agent** — now there are 2 LlmAgents and 2 prompts; `prompts.py` and `agent.py` both fight for ownership.
- `tools.py` grows past ~6 functions and you want to group them (search vs auth vs storage).
- A helper function is shared between agent code and a tool, and you want a `shared/` home for it.

When any hits, → [04 Growing layout](04_GrowingLayout.md).

> **🚀 In Production**
>
> The small layout is what **most** customer-facing ADK projects look like on day one of prod. Don't escalate before you have a *second* agent, an actual reuse case, or test pain. Premature directories are not free — every new folder needs an `__init__.py`, an import in some other file, and a slot in `pyproject.toml`'s package list.

> ❓ **Ask the student:** "If we move `lookup_customer` into `tools.py`, do we have to wrap it in `FunctionTool(...)` to register it?"
>
> *(Expected: no — `tools=[lookup_customer]` works because ADK auto-wraps callables. See [03_Tools/02_FunctionTool](../03_Tools/02_FunctionTool.md).)*

---

[← Prev: 02_MinimalLayout](02_MinimalLayout.md)  [↑ Map](../../MAP.md)  [Next: 04_GrowingLayout →](04_GrowingLayout.md)
