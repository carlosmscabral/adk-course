---
module: 3A_ProjectStructure
page: 09_DissectingSample
title: Dissecting fun-facts vs travel-concierge side-by-side
estimated_minutes: 30
prereqs: [3A_ProjectStructure/08]
concepts: [minimal-real-layout, growing-real-layout, side-by-side]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 08_EvalAndTestsLayout](08_EvalAndTestsLayout.md)  [↑ Map](../../MAP.md)  [Next: 10_InProduction →](10_InProduction.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 09 Dissecting samples

# 🔬 Dissecting two samples side-by-side

> 🤖 **Tutor:** this page is **the payoff for pages 02–04**. The student should open both sample directories in their file explorer and walk file-by-file. Do *not* paste the code — point at the file paths and have the student read along. The goal is "I can predict where things live without looking."

Two samples, opposite ends of the spectrum:

- [`fun-facts`](../../../adk-samples/python/agents/fun-facts/) — **minimal**. Two files. ~30 lines of real code.
- [`travel-concierge`](../../../adk-samples/python/agents/travel-concierge/) — **growing**. 6 sub-agents, prompts/tools/profiles/shared_libraries dirs, full deployment.

Both are real, deployed samples maintained by Google. Both work. The difference is purely "how much pressure has the project felt."

> 🛠 **Have the student run:**
> ```bash
> ls /home/carloscabral/study/adk-samples/python/agents/fun-facts/
> ls /home/carloscabral/study/adk-samples/python/agents/fun-facts/fun_facts/
> ls /home/carloscabral/study/adk-samples/python/agents/travel-concierge/
> ls /home/carloscabral/study/adk-samples/python/agents/travel-concierge/travel_concierge/
> ```
> Have them count files in each `*_agent/` package. (~2 vs ~15.)

## Side-by-side trees

### `fun-facts`

```
fun-facts/
├── README.md
├── pyproject.toml
├── uv.lock
├── img/                             ← marketing screenshots, not code
└── fun_facts/                       ← the package
    ├── __init__.py                  ← `from .agent import app`
    └── agent.py                     ← root_agent + App + google_search; ~20 LOC
```

That is the **whole** sample. No `tools/`, no `prompts/`, no `sub_agents/`, no `eval/`, no `deployment/`, no `tests/`.

### `travel-concierge`

```
travel-concierge/
├── README.md
├── pyproject.toml
├── uv.lock
├── travel-concierge-arch.png        ← architecture diagram
├── tests/                           ← pytest unit/integration
├── eval/                            ← AgentEvaluator + .evalset.json
├── deployment/
│   └── deploy.py                    ← Agent Engine packing
└── travel_concierge/                ← the package
    ├── __init__.py                  ← env-var setup, then `from . import agent`
    ├── agent.py                     ← root_agent: Agent with 6 sub_agents=[...]
    ├── prompt.py                    ← ROOT_AGENT_INSTR (file, not dir — 1 root prompt)
    ├── tracing.py                   ← OpenInference/Arize tracing setup
    ├── profiles/                    ← static user-profile fixtures
    ├── shared_libraries/
    │   ├── __init__.py
    │   ├── constants.py             ← Pydantic types
    │   └── types.py
    ├── tools/
    │   ├── __init__.py
    │   ├── memory.py                ← _load_precreated_itinerary (before_agent_callback)
    │   ├── places.py                ← Google Places API wrapper
    │   └── search.py                ← search tool
    └── sub_agents/
        ├── booking/
        │   ├── __init__.py
        │   ├── agent.py
        │   └── prompt.py
        ├── in_trip/
        ├── inspiration/
        ├── planning/
        ├── post_trip/
        └── pre_trip/                ← (each sub-agent: agent.py + prompt.py)
```

Two key observations:

1. The **internal shape** matches the growing-layout template from [page 04](04_GrowingLayout.md) — `tools/`, `sub_agents/`, optional `shared_libraries/`, a single top-level `prompt.py` for the root.
2. The **outer shape** matches the deployment template from [page 06](06_DeploymentExpectations.md) — `pyproject.toml` at root, `deployment/deploy.py` for Agent Engine, `eval/` + `tests/`.

## The exact same line in both: `root_agent`

In `fun-facts/fun_facts/agent.py`:

```python
root_agent = Agent(
    name="Facts",
    model="gemini-flash-latest",   # the sample uses a moving-target tag — for production work pin to a stable name
    instruction="Provide the most mind-blowing, obscure, and wacky fun facts ...",
    description="An Agent to provide fun facts about a given topic.",
    tools=[google_search],
)

app = App(name="fun_facts", root_agent=root_agent)
```

In `travel-concierge/travel_concierge/agent.py`:

```python
root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        inspiration_agent, planning_agent, booking_agent,
        pre_trip_agent, in_trip_agent, post_trip_agent,
    ],
    before_agent_callback=_load_precreated_itinerary,
)
```

**Same primitive, same name.** ADK's discovery doesn't care which layout you picked — it looks for `root_agent` (or `app`) at the module top, full stop. The complexity of the layout has zero bearing on how the CLI finds the agent.

## The migration triggers, made concrete

If you imagine walking `fun-facts` forward to `travel-concierge`, the migrations are:

| When | What changes |
|---|---|
| Prompt grows past ~30 lines | `agent.py`'s inline string → `prompt.py` (file) |
| Add a second LlmAgent (sub-agent) | `sub_agents/<name>/agent.py` + `prompt.py` appear |
| Add a 3rd tool | (still fine in `agent.py`); when it's the 5th, `tools/` appears |
| Two tools share a helper | `shared_libraries/` (or `shared/`) appears |
| First Pydantic model used by >1 file | `shared_libraries/types.py` |
| You want CI gating on behavior | `eval/` + `tests/` appear |
| You're deploying to Agent Engine | `deployment/deploy.py` appears |

Notice: **nothing about the inner package shape needed to change as you went up the trigger ladder.** The growing layout is literally "the small layout, but each file is now a directory." That's why the trajectory is non-disruptive.

## What's *missing* from `fun-facts` that you'd add for prod

Looking at `fun-facts` honestly, even though it's "minimal," to ship in production you'd want:

- `pyproject.toml` ✅ (it has one)
- A pinned Python version ✅ (`requires-python = ">=3.11"`)
- `eval/` ❌ — would add for any real-world quality bar
- `tests/` ❌ — same
- `deployment/deploy.py` ❌ — sample is for `adk web` demos, not deploy

But the **agent code itself** would not need to change. You'd add the deploy machinery around it.

## ❓ Comprehension checks

> ❓ **Ask the student:**
>
> 1. In `travel-concierge`, why does the root `agent.py` have `from .sub_agents.booking.agent import booking_agent` (3 dots in the path) instead of `from .sub_agents.booking import booking_agent`?
>    *(Answer: it could use the shorter form **if** `sub_agents/booking/__init__.py` re-exported `booking_agent`. Travel-concierge doesn't — it imports the explicit path. Style choice; both work. `llm-auditor`'s critic uses the re-export style: `from .agent import critic_agent as critic_agent`.)*
>
> 2. `fun-facts/fun_facts/__init__.py` is `from .agent import app`. `travel-concierge/travel_concierge/__init__.py` does **env-var setup first, then** `from . import agent`. Why the difference?
>    *(Answer: travel-concierge needs `GOOGLE_CLOUD_PROJECT`, `GOOGLE_GENAI_USE_VERTEXAI` set **before** `agent.py` constructs Gemini clients at import time. `fun-facts` uses `load_dotenv()` inside `agent.py` itself, so the order is the same — just achieved differently. Both are valid.)*
>
> 3. Could `travel-concierge` work without a `prompt.py` file (with the prompt inline in `agent.py`)?
>    *(Answer: yes, technically. But `ROOT_AGENT_INSTR` is ~80 lines; inlining would bury the `sub_agents=[...]` registration. The split is purely for readability — the prompt and the wiring don't deserve the same screen.)*

## What to take away

- **Pick the minimum size that matches today's pressure.** `fun-facts` shape for fun-facts-sized problems.
- **Migrating up is mechanical.** File → directory, same exports.
- **The CLI doesn't care which size you picked.** Discovery is `root_agent` (or `app`), full stop.

> 🚀 **In Production**
>
> When you're picking a layout for a new project, **pull up `fun-facts/` and `travel-concierge/` side-by-side in your editor** and ask: which of these is closer to what I'm building? Pick that as the starting point and let the migration triggers guide you up. Skipping ahead "to be safe" costs you setup time you'll never recover. We consolidate this in [10_InProduction](10_InProduction.md).

---

[← Prev: 08_EvalAndTestsLayout](08_EvalAndTestsLayout.md)  [↑ Map](../../MAP.md)  [Next: 10_InProduction →](10_InProduction.md)
