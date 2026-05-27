---
module: 3A_ProjectStructure
page: 00_Overview
title: Project Structure — the smallest layout that still works
estimated_minutes: 10
prereqs: [03_Tools/11]
concepts: [project-layout, root_agent-discovery, adk-cli-expectations, deployment-shape]
icon: 📦
in_production: false
detours_suggested: [PY_packaging]
---

[← Prev: 03_Tools/11_MiniDrill](../03_Tools/13_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyStructureMatters →](01_WhyStructureMatters.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 00 Overview

# 📦 Module 3A — Project Structure

> 🤖 **Tutor:** this module is **pragmatic, not dogmatic**. The whole point is "the smallest layout that still works, escalate only when you feel the pressure." Do **not** prescribe the growing layout for a student building their first toy — that's a way to make ADK feel heavier than it is.

A 30-line `agent.py` is a *fine* ADK project. So is a 12-folder monorepo. This module shows the three layouts students will see in the wild, the **pressure** that pushes you from one to the next, and what `adk web` / `adk run` / Cloud Run / Agent Engine expect at each size.

## 🎯 Goals

By the end of this module you can:

- Pick the right layout for the project you have *right now* (not the one you imagine).
- Name the three migration triggers that escalate **minimal → small → growing**.
- Explain what `adk web` / `adk run` / `adk api_server` look for on disk (the `root_agent` discovery rule and the `__init__.py` gotcha).
- Shape a project for **local testing** and **deployment** (Cloud Run, Agent Engine) without rewriting it.
- Read a real sample's tree (`fun-facts` vs `travel-concierge`) and predict where each concept lives.

## 📋 Prereqs

- Module **02 FirstAgent** — you've built an `LlmAgent` and run it.
- Module **03 Tools** — you've split a tool out of the agent file at least once.
- Comfortable with Python packaging basics (`__init__.py`, `pyproject.toml`). If not, take [[PY_packaging]] first (20 min).

## ⏱ Estimated time

- **Total**: ~2 hours over 1–2 sessions.
- Per-page estimates in each page's frontmatter.

## 🧪 Sample anchors

This module dissects **two** real samples side-by-side in [09_DissectingSample](09_DissectingSample.md):

- [`fun-facts`](../../../adk-samples/python/agents/fun-facts/) — the minimal layout. One `agent.py`, one `__init__.py`.
- [`travel-concierge`](../../../adk-samples/python/agents/travel-concierge/) — the growing layout. 6 sub-agents, `tools/`, `prompts/`, `shared_libraries/`, `eval/`, `tests/`, `deployment/`.

Putting them next to each other makes the migration triggers concrete.

## 🛣 Plan

1. **01 Why structure matters** — what breaks first (prompt sprawl, tool reuse, testability).
2. **02 The minimal layout** — one `agent.py` with `root_agent` at module top.
3. **03 The small layout** — split into `agent.py` + `tools.py` + `prompts.py`.
4. **04 The growing layout** — `tools/`, `prompts/`, `sub_agents/` directories.
5. **05 What the `adk` CLI expects** — `root_agent` discovery, `__init__.py` gotchas, the `agents/` parent dir.
6. **06 What deployment expects** — Cloud Run Dockerfile shape, Agent Engine packing.
7. **07 Shared utilities** — `shared/` across multiple agents.
8. **07A Config & env vars** — single `Settings` class, env-driven, multi-env separation.
9. **08 Eval + tests layout** — where `eval/`, `tests/`, fixtures live.
9. **09 Dissecting samples** — `fun-facts` vs `travel-concierge` side-by-side.
10. **10 In Production** — version pinning, dependency boundaries, monorepo of agents.
11. **11 Knowledge check** — 5–7 questions.
12. **12 Mini-drill** — refactor `Work/03_calc_agent.py` into the small layout; verify `adk web` still finds it.

After this module: → **[04 Sessions & State](../04_SessionsState/)**.

## 🗺 The three layouts at a glance

```
    MINIMAL                  SMALL                      GROWING
    (prototype)              (~2-5 tools, 1 agent)      (sub-agents, eval, deploy)

    my_agent/                my_agent/                  my_agent/
    ├── __init__.py          ├── __init__.py            ├── __init__.py
    └── agent.py             ├── agent.py               ├── agent.py
                             ├── tools.py               ├── prompts/
                             └── prompts.py             ├── tools/
                                                        ├── sub_agents/
        │                        │                      └── shared/
        ▼                        ▼                              ▲
        TRIGGER:                 TRIGGER:                       │
        prompt > 30 lines OR     2nd LlmAgent (sub) OR          │
        adding 3rd tool OR       tools.py > 6 fns OR            │
        tool needs own test      shared helper appears          │
        ──────────►              ──────────►                    │
                                                                │
```

The full ASCII version with annotations lives in [`_figures/layout_evolution.txt`](_figures/layout_evolution.txt). Pages 02–04 walk each layout in detail.

---

[← Prev: 03_Tools/11_MiniDrill](../03_Tools/13_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyStructureMatters →](01_WhyStructureMatters.md)
