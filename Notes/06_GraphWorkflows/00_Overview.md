---
module: 06_GraphWorkflows
page: 00_Overview
title: Graph workflows — beyond Sequential / Parallel / Loop
estimated_minutes: 15
prereqs: [05_MultiAgent/11]
concepts: [WorkflowAgent, nodes, edges, routing, HITL]
icon: 🧠
in_production: true
detours_suggested: [VisualBuilder]
---

[← Prev: 05_MultiAgent/11_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/01_LegacyTemplates →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 00 Overview

## 🧠 What you'll learn

ADK 2.0's **graph workflow** is the new primary primitive for non-trivial orchestrations. You define **nodes** (each wraps a sub-agent or a function) and **edges** (each carries an optional route label). The runtime walks the graph until it terminates.

Before we get there, we cover the **legacy** workflow templates you still see everywhere: `SequentialAgent`, `ParallelAgent`, `LoopAgent`. They compose nicely — `story_teller` nests all three.

## 🗺 Prereqs

- `05_MultiAgent/06_SequentialAgent` — you already met one workflow template.
- `04_SessionsState/04_OutputKey` — state is how nodes pass data.
- Comfort with `async`/`await` (light) — graphs are async under the hood. If shaky → detour [[PY_async]].

## ⏱ Time budget

**3 days**, ~6 hours actual work. Two dissection passes (one for the mixed-legacy `story_teller`, one for the new graph).

## 📦 Sample anchors

- `adk-samples/python/agents/story_teller/` — **legacy mixed**: a `SequentialAgent` containing a `LoopAgent` that wraps a `ParallelAgent`. Three templates, one file.
- `adk-samples/python/agents/workflows-sequential/` — minimal `WorkflowAgent` proof-of-life (3-node linear graph).
- `adk-samples/python/agents/workflow-concurrent_research_writer/` — **the** graph sample: research workflow + blog workflow, with parallel workers, function nodes, dynamic routing by output route, two nested `WorkflowAgent`s.
- `adk-samples/python/agents/workflows-HITL_concierge/` — HITL pause/resume using `RequestInput` and `rerun_on_resume=True`.

## 🎯 Where this sits in the spiral

In 05 we built the research-assistant team with `sub_agents`. Here we rebuild it as a graph: planner → parallel researchers → writer → reviewer (which can loop back to writer). The graph version lets us add a dynamic "good enough" check that the `SequentialAgent` couldn't express.

## 🛠 Pages in this module

| Page | Topic |
|------|-------|
| 01 | Legacy templates: Sequential, Parallel, Loop, `exit_loop`. |
| 02 | Legacy mixed — `story_teller` walk-through. |
| 03 | Why graphs — what templates can't express. |
| 04 | Graph intro — `WorkflowAgent`, nodes, edges. |
| 05 | Defining nodes — `FunctionNode`, agent nodes, `ParallelWorker`. |
| 06 | Routing edges — static vs dynamic, route labels. |
| 07 | Human-in-the-loop — `RequestInput`, resume token, Resume/Cancel. |
| 08 | 🛠 Dissecting `workflow-concurrent_research_writer`. |
| 09 | 🚀 In production — observability, cycles, idempotence. |
| 10 | ❓ Knowledge check. |
| 11 | 🏋 Mini-drill: 3-node graph that routes on input length. |

> 🤖 **Tutor:** if the student hasn't internalized that a `SequentialAgent` *has no model*, send them back to `05_MultiAgent/06` for 5 min — that misunderstanding poisons all of module 06.

> 🧭 **Detour suggestion:** ADK 2.0 ships a Visual Builder that exports to / imports from these graphs. Worth a peek after page 08 — see [[VisualBuilder]] (when authored).

---

[← Prev: 05_MultiAgent/11_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/01_LegacyTemplates →]
