---
module: 14_Evaluation
page: 00_Overview
title: Evaluation — testing agent behavior
estimated_minutes: 10
prereqs: [02_FirstAgent/00, 03_Tools/00]
concepts: [EvalSet, EvalCase, AgentEvaluator, LlmAsJudge, TrajectoryEvaluator]
icon: 🧪
in_production: true
detours_suggested: [PY_testing]
---

[← Prev: 13_Plugins/11_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/01_EvalsAreNotTests →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 00 Overview

# 🧪 Module 14 — Evaluation

## What you'll learn

- Why evals are different from tests, and why both matter.
- The `EvalCase`/`EvalSet` format and how to write your own.
- The full `AgentEvaluator` workflow from JSON to `pytest` verdict.
- The five evaluator types: `FinalResponseMatch{V1,V2}`, `TrajectoryEvaluator`, `LlmAsJudge`, `RubricBasedEvaluator`, `HallucinationsV1`.
- How to run `adk eval` from the CLI and wire it into CI.
- Real-world tax: cost, flakiness, golden-set curation, score-over-time tracking.

## Prereqs

- **Any agent module.** You need *something* to evaluate. Bring an agent — your M1 todo agent, M2 research agent, anything.
- **`[[PY_testing]]`** if `pytest` feels new. Evals integrate with pytest.

## Time budget

≈ 3 days. The library is small; the *judgement* (what to evaluate, how rigorously, what threshold) is the work.

## Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/academic-research/eval/` — `AgentEvaluator.evaluate(..., num_runs=5)` against a JSON EvalSet.
- `/home/carloscabral/study/adk-samples/python/agents/RAG/eval/` — RAG-specific evaluation including arize integration.
- `/home/carloscabral/study/adk-samples/python/agents/llm-auditor/eval/` — simpler eval pattern; one EvalCase per file (`.test.json`), shared `test_config.json` with thresholds.

> 🧭 Eval files live in an `eval/` directory parallel to your agent. See [[3A_ProjectStructure/08_EvalAndTestsLayout]] for the standard layout that `adk eval` expects (and how to keep eval fixtures, test_config.json, and your `tests/` directory cleanly separated).

## Module map

| Page | Topic |
|------|-------|
| 01 | Evals are not tests |
| 02 | EvalCase / EvalSet |
| 03 | AgentEvaluator |
| 04 | LlmAsJudge |
| 05 | RubricBasedEvaluator |
| 06 | TrajectoryEvaluator |
| 07 | Built-in metrics (Hallucinations, FinalResponseMatch) |
| 08 | `adk eval` CLI |
| 09 | Dissecting `academic-research/eval/` |
| 10 | In Production |
| 11 | Knowledge Check |
| 12 | Mini Drill |

> 🤖 **Tutor:** This module has the largest "judgement payload" in the course. Don't let the student drown in metrics taxonomy — push them through pages 02, 03, and 12 (the mini-drill) first; the metric pages are reference-style afterwards.

---

[← Prev: 13_Plugins/11_MiniDrill]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/01_EvalsAreNotTests →]
