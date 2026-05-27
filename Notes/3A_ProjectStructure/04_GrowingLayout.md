---
module: 3A_ProjectStructure
page: 04_GrowingLayout
title: The growing layout — directories per concept
estimated_minutes: 20
prereqs: [3A_ProjectStructure/03]
concepts: [sub_agents-dir, tools-dir, prompts-dir, package-init-re-exports]
icon: 📦
in_production: true
detours_suggested: [PY_packaging]
---

[← Prev: 03_SmallLayout](03_SmallLayout.md)  [↑ Map](../../MAP.md)  [Next: 05_AdkCliExpectations →](05_AdkCliExpectations.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 04 The growing layout

# 📦 The growing layout — files become folders

> 🤖 **Tutor:** the student should reach this page only when they have **either** a sub-agent **or** >5 tools. If they don't, stop here and have them re-read [01_WhyStructureMatters](01_WhyStructureMatters.md). The growing layout is **not the goal** — it's a response to specific pressure.

## Shape on disk

```
agents/
└── my_agent/
    ├── __init__.py
    ├── agent.py                          ← root agent wiring, imports sub-agents
    ├── prompts/
    │   ├── __init__.py
    │   ├── root.py                       ← ROOT_INSTRUCTION
    │   └── critic.py                     ← CRITIC_PROMPT
    ├── tools/
    │   ├── __init__.py                   ← optional re-exports
    │   ├── search.py                     ← search-shaped tools
    │   └── memory.py                     ← memory/state-shaped tools
    ├── sub_agents/
    │   ├── __init__.py
    │   ├── critic/
    │   │   ├── __init__.py
    │   │   ├── agent.py                  ← critic_agent = LlmAgent(...)
    │   │   └── prompt.py
    │   └── reviser/
    │       ├── __init__.py
    │       ├── agent.py
    │       └── prompt.py
    └── shared/                           ← optional; see 07_SharedUtilities
        ├── __init__.py
        └── auth.py
```

Files have become directories. Each directory has an `__init__.py`. Conceptually nothing new — *file scopes turned into package scopes* — but the navigation is now meaningfully easier.

## The root `agent.py` still owns wiring

```python
# agents/my_agent/agent.py
from google.adk.agents import SequentialAgent

from .sub_agents.critic.agent import critic_agent
from .sub_agents.reviser.agent import reviser_agent

root_agent = SequentialAgent(
    name="auditor",
    description="Critic + reviser pipeline.",
    sub_agents=[critic_agent, reviser_agent],
)
```

The root file got *shorter*, not longer. All the agent-construction code lives next to the prompt and tools that compose each sub-agent.

## A sub-agent folder, end-to-end

```
sub_agents/critic/
├── __init__.py
├── agent.py
└── prompt.py
```

```python
# sub_agents/critic/__init__.py
from .agent import critic_agent as critic_agent
```

(Re-exporting the agent makes `from .sub_agents.critic import critic_agent` work in the root — slightly shorter than `from .sub_agents.critic.agent import critic_agent`. Both styles appear in real samples; pick one and be consistent.)

```python
# sub_agents/critic/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from .prompt import CRITIC_PROMPT

critic_agent = LlmAgent(
    name="critic",
    model="gemini-2.5-flash",
    instruction=CRITIC_PROMPT,
    tools=[google_search],
)
```

```python
# sub_agents/critic/prompt.py
CRITIC_PROMPT = """\
You verify factual claims. For each claim in the input, label it
Accurate / Inaccurate / Disputed / Unsupported / Not Applicable.
...
"""
```

This is the **exact** shape used in `llm-auditor`. Read `adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/critic/` for the production version.

## `tools/` as a package

When `tools.py` grows past ~6 functions, split into a `tools/` package with one file per category:

```python
# tools/__init__.py — optional re-exports for shorter imports
from .search import web_search, scholar_search
from .memory import save_finding, load_findings
```

```python
# tools/search.py
def web_search(query: str) -> list[dict]:
    """Search the web. Returns top 10 results."""
    ...

def scholar_search(query: str) -> list[dict]:
    """Search Google Scholar. Returns top 5."""
    ...
```

```python
# tools/memory.py
from google.adk.tools import ToolContext

def save_finding(text: str, tool_context: ToolContext) -> dict:
    """Save a finding into session state under 'findings'."""
    findings = tool_context.state.get("findings", [])
    findings.append(text)
    tool_context.state["findings"] = findings
    return {"saved": True, "count": len(findings)}
```

The agent imports stay clean: `from .tools import web_search, save_finding`.

## `prompts/` as a package

Same pattern. Each sub-agent gets its own prompt file:

```
prompts/
├── __init__.py
├── root.py             ← ROOT_INSTRUCTION
└── critic.py           ← CRITIC_PROMPT
```

If a sub-agent already has its own folder under `sub_agents/`, its prompt lives **with** the agent (in `sub_agents/critic/prompt.py`), not in `prompts/`. The top-level `prompts/` is only for the root agent's prompt and any cross-agent shared prompt fragments.

> ⚠️ **Pick one home.** Don't have *both* `prompts/critic.py` and `sub_agents/critic/prompt.py`. Pick: sub-agent prompts go next to the sub-agent (the common convention in samples).

## The package layout in one sentence

**File ↔ directory equivalence is the whole game.** Anywhere you had `prompts.py`, you now have `prompts/` with the same exported names. The agent's import paths stay one level deep — `from .prompts import X` keeps working because of re-exports.

## When this layout stops fitting

It mostly doesn't, for a single agent project. The next escalation isn't "more directories inside `my_agent/`" — it's "two agents that need to share code" → [07 Shared utilities](07_SharedUtilities.md) and "this is a monorepo of agents" → [10 In Production](10_InProduction.md).

> **🚀 In Production**
>
> Big samples (`travel-concierge`, `customer-service`, `academic-research`, `marketing-agency`) all converge on this exact shape: `agent.py` at the top, `prompts/` (or `prompt.py`), `tools/`, `sub_agents/`, optional `shared_libraries/`. When in doubt, copy that. We dissect `travel-concierge` against this template in [09_DissectingSample](09_DissectingSample.md).

> 🛠 **Have the student** open `adk-samples/python/agents/travel-concierge/travel_concierge/` and count files. Compare to the diagram above. Names will differ (it has `profiles/`, `shared_libraries/` plural, `tracing.py`) — the **shape** is the same.

> ❓ **Ask the student:** "If you added an `auth/` directory under `my_agent/`, what file would have to change?"
>
> *(Expected: just whichever modules import from it; `__init__.py` of `my_agent` does not need to know about `auth/` unless you want to re-export. ADK doesn't scan subfolders for tools — it sees only what's wired into `root_agent`.)*

---

[← Prev: 03_SmallLayout](03_SmallLayout.md)  [↑ Map](../../MAP.md)  [Next: 05_AdkCliExpectations →](05_AdkCliExpectations.md)
