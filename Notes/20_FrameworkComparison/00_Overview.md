---
module: 20_FrameworkComparison
page: 00_Overview
title: Placing ADK in the agent-framework landscape
estimated_minutes: 20
prereqs: [02_FirstAgent/04, 03_Tools/02, 05_MultiAgent/02, 06_GraphWorkflows/02, 08_MCP/02, 10_A2A/02]
concepts: [comparison, landscape, framework-choice]
icon: 🗺
in_production: true
---

[← Prev: 19_Internals/14_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/01_TheLandscape →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 00 Overview

# 🗺 Framework comparison — orient, don't memorize

You're 19 modules deep in ADK. Now place it on the map.

## Why this module exists

ADK is one of many agent frameworks shipped in the last 2-3 years. When you start a new project — or join a team that already chose something else — you need to:

- Recognize what each framework optimizes for.
- Translate between vocabularies (LangGraph "state graph" ≈ ADK "Workflow"; CrewAI "Crew" ≈ ADK "sub_agents").
- Argue for or against a framework with specifics, not vibes.

## What you'll cover

| Page | Framework |
|---|---|
| 02 | LangChain / **LangGraph** (Harrison Chase / LangChain Inc.) |
| 03 | **CrewAI** (João Moura) |
| 04 | **AutoGen** (Microsoft Research / new AG2 fork) |
| 05 | **OpenAI Agents SDK** (OpenAI; Swarm successor) |
| 06 | **Pydantic AI** (Pydantic team) |
| 07 | **Letta / MemGPT** (Letta.com, ex-MemGPT research) |

Plus a feature matrix (08), a decision flowchart (09), and a "what would each do with the `llm-auditor` sample?" exercise (10).

## What you will **not** do

Build apps in each framework. We **orient**. A real polyglot evaluation takes weeks; this module is two days.

## Time

**2 days.** One day to read 01-08; one day for 09 (the flowchart drill), 10 (the cross-framework sample reading), and the mini-drill.

## A note on freshness

Snapshot date: **2026-05-27**. The agent framework space churns aggressively — versions, names, and even basic abstractions move month-to-month. If you're reading this after 2026-09, **verify the snippets** against the framework's current README before trusting them.

> 🤖 **Tutor:** when the student asks "is X still the best?" the honest answer is: it depends. Push them to articulate *what they're optimizing for* before recommending. The flowchart at page 09 exists to force that conversation.

> ❓ **Ask the student:** "Before reading the rest of this module — if you had to recommend ADK over LangGraph for a project, what's your one-sentence reason?" *(File it; revisit at the end of the module to see if it changed.)*

[← Prev: 19_Internals/14_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/01_TheLandscape →]
