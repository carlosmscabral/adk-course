---
module: 99_Capstone
page: 04A_DissectingACapstone
title: Dissecting a capstone-shaped sample (travel-concierge)
estimated_minutes: 20
prereqs: [99_Capstone/04]
concepts: [dissection, sample-walkthrough, rubric-mapping]
icon: 🔎
in_production: false
---

[← Prev: 99_Capstone/04_SharedRequirements]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/05_BuildingPlan →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 04A Dissecting a capstone

# 🔎 Dissecting a capstone-shaped sample

The capstone modules can't be dissected in the usual sense — they ARE the deliverable. So instead we walk through ONE existing sample that approximates the M5 shape and grade it against the page-04 rubric. This gives you a worked reference for what "≥3 agents · ≥2 tools · memory · evals · callbacks · OTel" actually looks like in code.

## 🔎 What we're reading

- `/home/carloscabral/study/adk-samples/python/agents/travel-concierge/travel_concierge/agent.py`
- `/home/carloscabral/study/adk-samples/python/agents/travel-concierge/travel_concierge/sub_agents/` (6 sub-agents)
- `/home/carloscabral/study/adk-samples/python/agents/travel-concierge/travel_concierge/tools/` (`memory.py`, `places.py`, `search.py`)
- `/home/carloscabral/study/adk-samples/python/agents/travel-concierge/travel_concierge/tracing.py`
- `/home/carloscabral/study/adk-samples/python/agents/travel-concierge/eval/`

## 🔎 Scorecard against the M5 rubric

| Rubric (page 04) | travel-concierge | Where |
|---|---|---|
| ≥3 agents composed | ✅ 6 sub-agents under one root | `agent.py:42-49` (`sub_agents=[inspiration, planning, booking, pre_trip, in_trip, post_trip]`) |
| ≥2 tools (≥1 non-built-in) | ✅ `memory.py`, `places.py`, `search.py` | `tools/` |
| Persistent state | ⚠️ Not in the sample — uses default in-memory | (your capstone must add `DatabaseSessionService`) |
| Memory service | ⚠️ Custom `memory.py` tool, not a `MemoryService` | `tools/memory.py` — `_load_precreated_itinerary` |
| ≥5 eval cases | ✅ Eval suite | `eval/test_eval.py` + `eval/data/` |
| ≥1 plugin | ❌ Not used | (your capstone must add one) |
| ≥2 callbacks (≥1 guardrail) | ⚠️ Only one (`before_agent_callback`) | `agent.py:51` |
| A2A | ❌ Not exposed | (your capstone must add `to_a2a(root_agent)`) |
| OpenTelemetry | ✅ via `openinference` + Arize | `tracing.py` (`GoogleADKInstrumentor().instrument(...)`) |
| README | ✅ Architecture diagram + run instructions | `README.md` + `travel-concierge-arch.png` |

## 🧭 What this tells you

travel-concierge is a **70% capstone**. It nails composition, tools, eval, and observability — those are the hardest pieces. The gaps are exactly the production hardening that the rubric forces you to add: persistent sessions, a real memory service, a plugin, a second guardrail callback, and A2A.

> 🤖 **Tutor:** when the student starts their own capstone, point them at travel-concierge as the "shape" reference. The six-sub-agent pattern with one router root is a clean, scalable composition that maps onto Track A (Research Assistant) and Track B (Code Reviewer) with minor renaming.

## 🛠 Have the student do this

> 🛠 Open `travel-concierge/travel_concierge/agent.py` alongside `99_Capstone/04_SharedRequirements.md`. Walk down the rubric and verbally call out, line by line, which checkbox each piece of the sample satisfies — and which ones it leaves to you.

[← Prev: 99_Capstone/04_SharedRequirements]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/05_BuildingPlan →]
