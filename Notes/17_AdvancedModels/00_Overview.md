---
module: 17_AdvancedModels
page: 00_Overview
title: Advanced Models — beyond Gemini
estimated_minutes: 10
prereqs: [02_FirstAgent/06]
concepts: [LLMRegistry, multi-model, LiteLlm, Gemma, Claude, OpenAI]
icon: 🧬
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/10_MiniDrill](../16_ProductionSecurity/12_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/01_LLMRegistry →](01_LLMRegistry.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 00 Overview

---

## 🧬 What you'll learn

By the end of this module you will:

- Understand the `LLMRegistry` and how ADK resolves a model string.
- Know the Gemini family (Flash-Lite, Flash, Pro) and when to use each.
- Attach a `BuiltInPlanner` (with `ThinkingConfig`) or a `PlanReActPlanner` to drive better reasoning.
- Wire Claude (via Vertex), Gemma (local), OpenAI, and arbitrary models via `LiteLlm`.
- Use `ApigeeLlm` for enterprise gateway routing.
- Configure different models for different sub_agents in a single graph.
- Apply the five model-selection patterns (tier-by-task, model-from-config, 429 fallback, cost-aware swap, A/B in eval).
- Read `gemma-food-tour-guide/` end-to-end.

> See also: Detour [[Detours/Grounding]] — model choice interacts with grounding strategy (Search Grounding requires Gemini; Agentic RAG is model-agnostic).

## 🧭 Prereqs

- **02 FirstAgent** — `LlmAgent(model=...)` and the `model="gemini-..."` string contract. We re-ground in that mechanism on page 01.

## ⏱ Time budget

**2.5 days.** Day 1 — pages 01-04 (registry + Gemini/Claude/Gemma). Day 2 — pages 05-09 (planners, LiteLlm, OpenAI, Apigee). Half-day 3 — pages 10, 10A (per-agent + selection patterns), 11 dissection, 12 in-prod, mini-drill.

## 📦 Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/gemma-food-tour-guide/` — Gemma via AI Studio, with Google Maps MCP. The cleanest "non-Gemini-default" sample.
- `/home/carloscabral/study/adk-samples/python/agents/customer-service/` — config-driven model selection (any Gemini variant), a pattern you will copy.

## 🗺 Page map

| # | Page | Why |
|---|---|---|
| 01 | LLMRegistry | The central directory. |
| 02 | GeminiVariants | Flash-Lite / Flash / Pro tradeoffs. |
| 03 | ClaudeViaVertex | When Claude beats Gemini. |
| 04 | GemmaLocal | Open-weights for on-prem. |
| 05 | PlannersBuiltIn | `BuiltInPlanner` + `ThinkingConfig` for reasoning models. |
| 06 | PlanReActPlanner | Model-agnostic plan → reason → act tag protocol. |
| 07 | LiteLlm | Universal adapter. |
| 08 | OpenAIModels | GPT-4o / o1 via LiteLlm. |
| 09 | ApigeeLlm | Enterprise gateway routing. |
| 10 | PerAgentModel | Sub_agents with different models. |
| 10A | ModelSelectionPatterns | Synthesis: tier-by-task, config, fallback, cost-aware, A/B. |
| 11 | DissectingSample | Read gemma-food-tour-guide. |
| 12 | InProduction | Routing, lock-in, rate-limits. |
| 13 | KnowledgeCheck | 12 questions. |
| 14 | MiniDrill | Mixed-model sub_agents in one runner. |

## 🗺 The big picture (ASCII)

```
{{ _figures/model_matrix.txt }}
```

(Open `_figures/model_matrix.txt` for the full version.)

> 🤖 **Tutor:** before page 01, ask the student to name the *one* property they care most about in a model for their target use case (cost, latency, quality, vendor independence, on-prem). Use the matrix to keep them honest as they read the rest of the module.

---

[← Prev: 16_ProductionSecurity/10_MiniDrill](../16_ProductionSecurity/12_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/01_LLMRegistry →](01_LLMRegistry.md)
