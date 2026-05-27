---
module: 12_CodeExecution
page: 00_Overview
title: Code execution — letting agents run Python
estimated_minutes: 15
prereqs: [03_Tools/01, 04_SessionsState/02]
concepts: [code_executor, sandbox, executor matrix, executable_code, code_execution_result, request/response processors]
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
- The four executor-agnostic sandbox-bypass classes (filesystem, environment, network, privilege escalation) and how each executor scores against them.
- An end-to-end dissection of `data-science`, which wires `VertexAiCodeExecutor` for a real analytics sub-agent.

## Why this module gets extra depth

Code execution is the highest-blast-radius primitive in ADK. A misconfigured tool leaks a single function-call surface; a misconfigured `code_executor` lets the LLM run arbitrary code with whatever privileges your process holds. The module's depth budget is justified by that asymmetry. Read 02 + the new `02A_SandboxBypassClasses` together — the bypass framing is the lesson, not a footnote.

## Prereqs

- **03 Tools** — code execution is conceptually a special-case tool. If you haven't internalized "the LLM emits an action, the runtime executes it, the result comes back," redo 03 first.
- **04 Sessions & State** — `CodeExecutorContext` reads and writes `session.state` keys (`code_executor_context.py:28-34`). Stateful executors and the error-retry counter both live there.

## Time budget

≈ 2 days. The mini-drill is fast; the executor matrix, the bypass-classes page, and the security framing are the time sinks.

## Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py` — `VertexAiCodeExecutor` in a real multi-agent system. Dissected in `07_DissectingSample.md`.
- `/home/carloscabral/study/adk-samples/python/agents/machine-learning-engineering/` — heavier code-exec example, ML over real datasets.

## The event shape, in one paragraph

Code execution rides on two `types.Part` variants — `executable_code` (model says "run this") and `code_execution_result` (runtime says "here's stdout"). The runtime builds these via `CodeExecutionUtils.build_executable_code_part` (`code_execution_utils.py:175-187`) and `build_code_execution_result_part` (`:189-221`). On the wire they appear as sibling parts inside a single `Content`, exactly where you'd expect tool calls. Worked diagram in `_figures/code_exec_event_flow.txt`.

## Where this slots into the runtime

`code_executor=` isn't magic — it's two request/response processors stitched into the LLM flow. `_CodeExecutionRequestProcessor` (`flows/llm_flows/_code_execution.py:117-148`) preps the request (BuiltIn injects a tool here, others mutate `contents`); `_CodeExecutionResponseProcessor` (`:151-169`) catches the model's `executable_code` part and dispatches to `code_executor.execute_code(...)`. Result comes back as a synthesized `code_execution_result` event built at `_code_execution.py:435-470` (`_post_process_code_execution_result`). When you see "executor magic," that file is where it lives.

## Module map

| Page | Topic |
|------|-------|
| 01 | Why code execution (vs. plain tools) |
| 02 | `UnsafeLocalCodeExecutor` — dev only |
| 02A | Sandbox-bypass classes — executor-agnostic threat model |
| 03 | `BuiltInCodeExecutor` — Gemini-side |
| 04 | `VertexAiCodeExecutor` — managed sandbox |
| 05 | `ContainerCodeExecutor` — your Docker daemon |
| 05A | `GkeCodeExecutor` — pods on your cluster |
| 06 | `AgentEngineSandboxCodeExecutor` |
| 07 | Dissecting `data-science` |
| 08 | In Production |
| 09 | Knowledge Check |
| 10 | Mini Drill |

> 🤖 **Tutor:** This module has more conceptual pages than usual because the choice matrix AND the bypass matrix are both the lesson. Spend extra time on `_figures/executor_matrix.txt` (orientation) and `_figures/bypass_matrix.txt` (security posture). The student is allowed to be a little uncomfortable on 02 and 02A — that's the point.

---

[← Prev: 11_Memory/09_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/01_WhyCodeExecution →]
