---
module: 99_Capstone
page: 00_Overview
title: Capstone — one production-grade agent
estimated_minutes: 60
prereqs: [00_Setup/01, 01_Foundations/01, 02_FirstAgent/04, 03_Tools/02, 04_SessionsState/02, 05_MultiAgent/02, 06_GraphWorkflows/02, 07_Callbacks/02, 08_MCP/02, 09_Skills/02, 10_A2A/02, 10A_EmbeddingsVectorSearch/02, 10B_RAGPipeline/02, 10C_BigQueryAgents/02, 11_Memory/02, 12_CodeExecution/02, 13_Plugins/02, 14_Evaluation/02, 15_Observability/02, 16_ProductionSecurity/02, 17_AdvancedModels/02, 18_StreamingLive/02, 19_Internals/02, 20_FrameworkComparison/02]
concepts: [capstone, integration, production]
icon: 🏁
in_production: true
---

[← Prev: 20_FrameworkComparison/13_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/01_TrackA_ResearchAssistant →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 00 Overview

# 🏁 Capstone — build one production-grade agent

You've made it. Time to **integrate**.

The capstone is **one** agent system that exercises everything you've learned. Pick a track:

| Track | Theme | Headline tech |
|---|---|---|
| **A — Research Assistant** | Multi-agent research with critique | Graph workflow + MCP doc store + A2A |
| **B — Code Reviewer** | Diff-aware reviewer with sandboxed test execution | sub_agents + code execution sandbox + GitHub webhook |
| **C — Personal Knowledge Hub** | Lifelong-memory note-taker | Memory Bank + RAG + Skills packaging |

All three converge on the **same shared requirements** (page 04) so the rubric stays portable across tracks.

## Time

**5 days.** Roughly:

- Day 1: pick a track, scaffold, write the README architecture section.
- Day 2: agents + tools + composition.
- Day 3: state, memory, observability.
- Day 4: evals + guardrails + A2A.
- Day 5: polish, self-review, deploy a smoke version.

## Why a capstone?

The course has been **breadth-first** until now. The capstone is **depth-first** — you'll discover the gaps in your understanding only when you try to integrate. Expect to revisit older modules.

## What "done" means

When you can:

1. Run your agent end-to-end via `adk run` AND via the A2A protocol.
2. Pass at least 5 eval cases (page 04 / shared requirements).
3. Trace a single invocation in Cloud Trace and explain every span to a stranger.
4. Hand the repo to a stranger and have them deploy it from your README in <30 min.

## Grading

Self-graded (with the tutor's help) against the rubric in `06_SelfReviewChecklist.md` + the YAML drill at `09_MiniDrill.yml`. There's no "right answer" — the capstone is an artifact, not a test.

## A note on scope

Each track's spec is **rich** by design. You're expected to **cut**: drop features that don't map to your real use case. The shared requirements at page 04 are the floor; everything else is aspirational.

> 🤖 **Tutor:** push the student to commit to a track in the first hour. Spec-shopping is the #1 capstone failure mode. If they're paralyzed, default them to Track A (Research Assistant) — it's the most balanced.

> ❓ **Ask the student:** "Which track best matches a real problem you face at work or in side projects? Pick that one — the realism will keep you motivated."

[← Prev: 20_FrameworkComparison/13_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/01_TrackA_ResearchAssistant →]
