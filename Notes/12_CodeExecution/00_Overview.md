---
module: 12_CodeExecution
page: 00_Overview
title: Code execution — letting agents run Python
estimated_minutes: 10
prereqs: [03_Tools/01]
concepts: [code_executor, sandbox, executor matrix]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/09_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/01_WhyCodeExecution →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 00 Overview

# 🛠 Module 12 — Code Execution

## What you'll learn

- *Why* agents need code execution (arithmetic, data, plotting) — and where tools fall short.
- The six executors ADK ships, ranked by isolation and operational fit.
- How to attach a `code_executor` to an `LlmAgent` and how the LLM's `executable_code` part flows through the runtime.
- Why `UnsafeLocalCodeExecutor` is the single most dangerous primitive in this course and the standard prod swaps.
- An end-to-end dissection of `data-science`, which wires `VertexAiCodeExecutor` for a real analytics sub-agent.

## Prereqs

- **03 Tools** — code execution is conceptually a special-case tool. If you haven't internalized "the LLM emits an action, the runtime executes it, the result comes back," redo 03 first.

## Time budget

≈ 2 days. The mini-drill is fast; the executor matrix and security framing are the time sinks.

## Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py` — `VertexAiCodeExecutor` in a real multi-agent system. Dissected in `07_DissectingSample.md`.
- `/home/carloscabral/study/adk-samples/python/agents/machine-learning-engineering/` — heavier code-exec example, ML over real datasets.

## Module map

| Page | Topic |
|------|-------|
| 01 | Why code execution (vs. plain tools) |
| 02 | `UnsafeLocalCodeExecutor` — dev only |
| 03 | `BuiltInCodeExecutor` — Gemini-side |
| 04 | `VertexAiCodeExecutor` — managed sandbox |
| 05 | `ContainerCodeExecutor` and `GkeCodeExecutor` |
| 06 | `AgentEngineSandboxCodeExecutor` |
| 07 | Dissecting `data-science` |
| 08 | In Production |
| 09 | Knowledge Check |
| 10 | Mini Drill |

> 🤖 **Tutor:** This module has more conceptual pages than usual because the choice matrix is the lesson. Spend extra time on `_figures/executor_matrix.txt`.

---

[← Prev: 11_Memory/09_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/01_WhyCodeExecution →]
