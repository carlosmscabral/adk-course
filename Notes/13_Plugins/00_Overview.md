---
module: 13_Plugins
page: 00_Overview
title: Plugins — cross-cutting concerns at runner scope
estimated_minutes: 10
prereqs: [07_Callbacks/01]
concepts: [Plugin, BasePlugin, runner-scoped hook, cross-cutting]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/10_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/01_WhatIsAPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 00 Overview

# 🛠 Module 13 — Plugins

## What you'll learn

- What a Plugin is, and why ADK has both Plugins and Callbacks.
- The five built-in plugins: `LoggingPlugin`, `ReflectAndRetryToolPlugin`, `ContextFilterPlugin`, `GlobalInstructionPlugin`, `BigQueryAgentAnalyticsPlugin`.
- How to compose plugins (order matters) and write your own.
- The four "non-obvious" plugin failure modes in prod.

## Prereqs

- **07 Callbacks** — plugins use the same hook vocabulary (`before_model`, `after_tool`, etc.). If those names don't ring a bell, do 07 first.

## Time budget

≈ 2 days. The library is small; the design judgement (plugin vs callback, ordering, observability bridge) is the time.

## Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/safety-plugins/` — composes custom safety plugins (LlmAsAJudge, ModelArmorSafetyFilter) onto an `InMemoryRunner`. Canonical "plugin as policy" shape.
- `/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/` — uses `BigQueryAgentAnalyticsPlugin`. The bridge from this module to 15_Observability.

## Module map

| Page | Topic |
|------|-------|
| 01 | What is a Plugin (vs a Callback) |
| 02 | `LoggingPlugin` |
| 03 | `ReflectAndRetryToolPlugin` |
| 04 | `ContextFilterPlugin` |
| 05 | `GlobalInstructionPlugin` |
| 06 | `BigQueryAgentAnalyticsPlugin` |
| 07 | Writing a custom plugin |
| 08 | Dissecting `safety-plugins` |
| 09 | In Production |
| 10 | Knowledge Check |
| 11 | Mini Drill |

> 🤖 **Tutor:** The student already knows callbacks. The trap is "if I have callbacks, why do I need plugins?" The answer — runner-scope, composable across agents, fire on every event — needs the figure. Open `_figures/plugin_hooks.txt` early.

---

[← Prev: 12_CodeExecution/10_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/01_WhatIsAPlugin →]
