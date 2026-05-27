---
module: 07_Callbacks
page: 00_Overview
title: Module 07 — Callbacks (lifecycle hooks for shaping, guardrails, observability)
estimated_minutes: 10
prereqs: [05_MultiAgent/00]
concepts: [callbacks, lifecycle, before_model, after_model, before_tool, after_tool, error_callbacks]
icon: 🗺
in_production: true
detours_suggested: [PY_async, PY_logging]
---

[← Prev: 06_GraphWorkflows](../06_GraphWorkflows/00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/01_WhyCallbacks →](01_WhyCallbacks.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 00 Overview

# 🗺 Module 07 — Callbacks

You finished the agent and it almost behaves. The instruction won't keep it from booking flights to the moon. The tool returns a dict you wish were 30% smaller. The model produces a great answer but no citations. **Callbacks are where you intercept.**

There are 6 hook points in the invocation lifecycle plus 2 error hooks. They are plain Python functions (sync or `async`) registered on the agent. Returning `None` is the passthrough; returning a value short-circuits or overrides.

## 🎯 What you'll walk away knowing

- The 6 sync hook points: `before/after_agent`, `before/after_model`, `before/after_tool`.
- The 2 error hooks: `on_model_error_callback`, `on_tool_error_callback`.
- Three idioms: **filter** (drop / rewrite input), **guard** (block tool calls), **decorate** (post-process output).
- Callbacks-as-policy: why guardrails live here and not in the prompt.

## 🧰 Prereqs

- 02 (LlmAgent), 03 (tools), 04 (state / `CallbackContext`).
- 05 (sub-agents) — callbacks register per-agent, so they fire per-sub-agent in a tree.
- Helpful: [[PY_async]] (callbacks may be `async def`).

## ⏱ Time

~2 days. The concepts are small but the patterns multiply.

## 📦 Sample anchors

- `adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/critic/agent.py` — `after_model_callback=_render_reference` appends Google Search grounding URLs to the response.
- `adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/reviser/agent.py` — `after_model_callback=_remove_end_of_edit_mark` strips a sentinel suffix.
- `adk-samples/python/agents/travel-planner-google-maps-mcp/travel_planner_agent/agent.py` — imports the full callback surface alongside an `MCPToolset`.
- `adk-samples/python/agents/safety-plugins/safety_plugins/plugins/model_armor.py` — same idioms as plugins (and the plugin-vs-callback distinction is the next thing you'll learn).

## 🗺 Map of this module

```
00 Overview                          ← you are here
01 Why Callbacks
02 Before/After Model
03 Before/After Tool
04 Before/After Agent
05 CallbackContext Anatomy           ← what's in ctx, what isn't, gotchas
06 Callback Recipe Cookbook          ← cache · rate-limit · PII · cite · budget · gate · audit
07 Callbacks vs Plugins              ← decision rubric
08 Error Callbacks
09 Dissecting Sample (llm-auditor)
10 In Production
11 Knowledge Check
12 Mini Drill
```

> 🤖 **Tutor:** if the student already wrote a guardrail in the system prompt and is wondering why it fails 5% of the time, that's the perfect lead-in to 01.

[← Prev: 06_GraphWorkflows](../06_GraphWorkflows/00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/01_WhyCallbacks →](01_WhyCallbacks.md)
