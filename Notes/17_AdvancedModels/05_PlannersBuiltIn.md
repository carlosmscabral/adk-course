---
module: 17_AdvancedModels
page: 05_PlannersBuiltIn
title: Planners — BuiltInPlanner + ThinkingConfig
estimated_minutes: 20
prereqs: [17_AdvancedModels/02]
concepts: [BuiltInPlanner, ThinkingConfig, thinking_budget, include_thoughts, reasoning models]
icon: 🧩
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/04_GemmaLocal](04_GemmaLocal.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/06_PlanReActPlanner →](06_PlanReActPlanner.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 05 Planners — BuiltIn

---

## 🧩 What a planner is

A **planner** is a small object you attach to an `LlmAgent` to change *how the model thinks before it answers*. ADK ships two concrete planners:

| Planner | What it changes | Needs reasoning model? |
|---|---|---|
| **`BuiltInPlanner`** | Forwards a `ThinkingConfig` to the model's native thinking API. | Yes — Gemini 2.5+. |
| **`PlanReActPlanner`** | Adds an NL system instruction that forces plan → reason → act → answer tags. | No — works on any model. |

This page covers the first. Page 06 covers the second.

## 🛠 Minimum wiring

```python
# Work/17_AdvancedModels/05_planner_builtin.py
# Run: uv run python Work/17_AdvancedModels/05_planner_builtin.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = LlmAgent(
    name="thinker",
    model="gemini-2.5-flash",
    instruction="Solve the user's puzzle. Show your final answer plainly.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,   # surface thoughts as Part(thought=True)
            thinking_budget=2048,    # tokens spent thinking; -1 = unlimited; 0 = off
        ),
    ),
)

async def main():
    runner = InMemoryRunner(agent=agent, app_name="planner_demo")
    session = await runner.session_service.create_session(
        app_name="planner_demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(
        text="A frog climbs 3m up a 10m well each day and slips 2m at night. "
             "How many days to escape?")])
    async for ev in runner.run_async(
        user_id="u", session_id=session.id, new_message=msg):
        for p in (ev.content.parts if ev.content else []):
            tag = "[thought]" if getattr(p, "thought", False) else "[final] "
            if p.text:
                print(tag, p.text.strip()[:120])

asyncio.run(main())
```

Output (truncated):

```
[thought] Let me set up: gains 1m net per day, but on the last day...
[thought] So after day 7 the frog is at 7m, day 8 it climbs to 10m and escapes.
[final]  8 days.
```

## 🧠 The three `ThinkingConfig` knobs

| Field | Meaning |
|---|---|
| `thinking_budget=N` | Hard cap on thought tokens. Bigger = more reasoning, more cost, more latency. |
| `thinking_budget=-1` | Let the model decide (dynamic). Production default for "I want quality, accept variance." |
| `thinking_budget=0` | Disable thinking entirely. Use to A/B test "did thinking help?" |
| `include_thoughts=True` | Stream thought parts to the event bus. Off in prod (chatty + leakable). |

## 🧠 When reasoning models help

A `BuiltInPlanner` on `gemini-2.5-pro` or `gemini-2.5-flash` wins **only** for tasks where the model would otherwise jump to a wrong answer:

- Multi-step math / logic.
- Constrained planning (resource allocation, scheduling).
- Code that requires reasoning about edge cases before writing.
- Tool-call sequencing in non-trivial agentic loops.

It is **wasted budget** on:

- Pure summarization, paraphrase, extraction.
- Single-fact lookups.
- Anything that a Flash-Lite handles correctly today.

## 💰 The cost knob

Thinking tokens bill at the same rate as output tokens. A `thinking_budget=4096` on a chatty Pro turn can quietly add **$0.05+** per call. Two failure modes:

1. **Always-on, always-max.** Don't set `-1` everywhere. Measure first.
2. **Thinking + cheap model.** A Flash-Lite with `thinking_budget=2048` is often worse than a Flash without thinking — small models reason worse, even when given budget.

> 🛠 **Have the student run:** the script above twice — once with `thinking_budget=0`, once with `2048`. Same prompt. Compare the final answers and the token counts in the events. Did thinking change the answer? Was it worth the tokens?

> ❓ **Ask the student:** when would you set `include_thoughts=False` even in dev?
> *(Answer: when the thoughts dominate the log noise and you're already confident the planner is on. Verify via metadata, not transcript.)*

## 📦 Real sample anchors

- `adk-samples/python/agents/cyber-guardian-agent/cyber_guardian/agent.py` — `BuiltInPlanner(thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_budget=512))` on the orchestrator.
- `adk-samples/python/agents/sdlc-user-story-refiner/sdlc_user_story_refiner/agent.py` — `thinking_budget=-1` (dynamic) on a refiner agent.
- `adk-samples/python/agents/small-business-loan-agent/small_business_loan_agent/agent.py` — `BuiltInPlanner(thinking_config=ThinkingConfig(include_thoughts=False))` on a workflow orchestrator (thoughts hidden, budget default).

> 🚀 **In Production**
>
> `include_thoughts=True` leaks the model's chain-of-thought into events that may be logged, traced, or sent to clients. Treat thoughts as **internal-only PII** — strip in your `after_model_callback` before they reach a frontend. Cross-link [[07_Callbacks/08_ErrorCallbacks]] for the redaction pattern.

---

[← Prev: 17_AdvancedModels/04_GemmaLocal](04_GemmaLocal.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/06_PlanReActPlanner →](06_PlanReActPlanner.md)
