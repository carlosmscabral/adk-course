---
module: 17_AdvancedModels
page: 06_PlanReActPlanner
title: PlanReActPlanner — plan, reason, act on any model
estimated_minutes: 20
prereqs: [17_AdvancedModels/05]
concepts: [PlanReActPlanner, ReAct, planning tags, model-agnostic reasoning, BasePlanner]
icon: 🗺
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/05_PlannersBuiltIn](05_PlannersBuiltIn.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/07_LiteLlm →](07_LiteLlm.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 06 Plan-Re-Act Planner

---

## 🗺 The idea

`PlanReActPlanner` is the **model-agnostic** planner. It does not need a reasoning-capable Gemini. Instead, it **injects a system instruction** that forces the model to emit tagged sections in order:

```
/*PLANNING*/      ← decompose the user request into numbered steps
/*ACTION*/        ← invoke a tool
/*REASONING*/     ← summarize tool outputs and decide next step
/*ACTION*/        ← (loop)
/*REPLANNING*/    ← if the original plan no longer fits
/*FINAL_ANSWER*/  ← single, precise answer to the user
```

The planner then post-processes the response: text under planning/reasoning/replanning tags gets marked as `thought=True` (so the client can hide it), and only the `/*FINAL_ANSWER*/` portion goes to the user.

## 🛠 Minimum wiring

```python
# Work/17_AdvancedModels/06_planner_react.py
# Run: uv run python Work/17_AdvancedModels/06_planner_react.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",   # any model works — no thinking required
    instruction="Answer the user with tool-gathered evidence.",
    tools=[google_search],
    planner=PlanReActPlanner(),  # zero config
)

async def main():
    runner = InMemoryRunner(agent=agent, app_name="react_demo")
    s = await runner.session_service.create_session(
        app_name="react_demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(
        text="What language is most spoken in Argentina, and what is its capital?")])
    async for ev in runner.run_async(
        user_id="u", session_id=s.id, new_message=msg):
        for p in (ev.content.parts if ev.content else []):
            if p.text:
                tag = "[thought]" if getattr(p, "thought", False) else "[final] "
                print(tag, p.text.strip()[:140])

asyncio.run(main())
```

The transcript will contain `/*PLANNING*/` and `/*REASONING*/` sections tagged as thought, and one clean `/*FINAL_ANSWER*/` part.

## 🧠 BuiltIn vs Plan-Re-Act — pick one

| You want… | Use |
|---|---|
| The model's native thinking (Gemini 2.5+, fast, no instruction overhead) | `BuiltInPlanner` |
| A model without thinking support (Gemma, GPT-4o-mini, Claude Haiku via LiteLlm) | `PlanReActPlanner` |
| Explicit, visible plan/reason/action sections in the event stream | `PlanReActPlanner` |
| Lowest latency on simple tool-using turns | Neither — skip the planner |
| Tool-heavy ReAct loops with replanning on failure | `PlanReActPlanner` |
| Multi-step math / logic on Gemini Pro | `BuiltInPlanner` (cheaper than the tag overhead) |

Rule of thumb: **`BuiltInPlanner` first if the model supports it; fall back to `PlanReActPlanner` for non-thinking models or when you need the tags as audit evidence.**

## 🧠 Why the tags matter

The planner's `process_planning_response` walks each response part and marks reasoning text with `Part.thought=True`. This means:

- Your UI can hide thoughts by filtering on `p.thought`.
- Your `after_model_callback` can strip or summarize them before persistence.
- Your eval can still inspect the *full* plan to detect reasoning regressions, even after redaction at the user boundary.

This is the same `thought` field `BuiltInPlanner` uses — so downstream consumers don't care which planner produced them.

## 📦 Real sample anchors

`PlanReActPlanner` is the workhorse of the **supply-chain** sample family — seven sub-agents use it:

- `adk-samples/python/agents/supply-chain/supply_chain/agent.py` — root coordinator.
- `.../sub_agents/ops_insight/agent.py`, `weather_report/agent.py`, `demand_sense/agent.py`, `chart_generator/agent.py`, `market_pulse/agent.py` — each specialist.
- `adk-samples/python/agents/sdlc-technical-designer/sdlc_technical_designer/agent.py` — designer.
- `adk-samples/python/agents/swe-benchmark-agent/swe_benchmark_agent/orchestrator.py` — orchestrator.
- `adk-samples/python/agents/tau2-benchmark-agent/tau2_agent/adk_agent.py` — benchmark agent.

These samples picked Plan-Re-Act over Built-In because the planner output **is** the audit trail — investigators need to see the plan, not just the answer.

> 🛠 **Have the student run:** the script above. Then re-run with `planner=None`. Diff the event stream. The planner version should emit visibly tagged reasoning; the bare run should not.

> ❓ **Ask the student:** what stops you from using both planners at once on the same agent?
> *(Answer: an agent has a single `planner` field. They are mutually exclusive by design — the system instructions would conflict and the thinking config would attach to a model that may not honor it.)*

> 🚀 **In Production**
>
> The tag-based protocol is **not enforced** — it's an instruction the model is asked to follow. Weak models occasionally skip `/*FINAL_ANSWER*/` or close it early. Add a defensive `after_model_callback` that flags responses missing the final-answer tag and retries once. See the recipes in [[07_Callbacks/06_CallbackRecipeCookbook]].

---

[← Prev: 17_AdvancedModels/05_PlannersBuiltIn](05_PlannersBuiltIn.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/07_LiteLlm →](07_LiteLlm.md)
