---
module: 14_Evaluation
page: 03_AgentEvaluator
title: AgentEvaluator — running an eval set
estimated_minutes: 20
prereqs: [14_Evaluation/02]
concepts: [AgentEvaluator, evaluate, num_runs, pytest integration]
icon: 🛠
in_production: true
detours_suggested: [PY_testing]
---

[← Prev: 14_Evaluation/02_EvalCaseEvalSet]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/04_LlmAsJudge →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 03 AgentEvaluator

# 🛠 The one function that runs everything

```python
from google.adk.evaluation import AgentEvaluator
```

The whole programmatic entry point is `AgentEvaluator.evaluate(...)`.

```python
# from adk-samples/python/agents/llm-auditor/eval/test_eval.py
import pathlib
import pytest
from google.adk.evaluation import AgentEvaluator

@pytest.mark.asyncio
async def test_all():
    await AgentEvaluator.evaluate(
        "llm_auditor",                                           # module path
        str(pathlib.Path(__file__).parent / "data"),             # data dir
        num_runs=5,                                              # each case 5x
    )
```

Three arguments:

1. **Agent module path** (str). The Python module that exports a root agent — the loader figures out the agent. Same string you'd `import`.
2. **Data dir or file path** (str). Points at a directory of `.test.json` files OR a single `.test.json` (plus `test_config.json` for thresholds).
3. **`num_runs`** (int). Each case runs N times; scores aggregate. Higher N → less variance, more cost.

## The pipeline (recap of `_figures/eval_pipeline.txt`)

1. Loads all `.test.json` files in the directory.
2. Loads `test_config.json` thresholds.
3. For each case, runs the agent `num_runs` times against the input.
4. Scores each run against the gold reference using configured metrics.
5. Aggregates → compares to thresholds → asserts pass/fail.
6. On fail: pytest assertion error with details.

## Why pytest

ADK evals integrate with pytest natively. You get:

- CI-runnable out of the box (`pytest` is in everyone's pipeline).
- `pytest_asyncio` for async (the evaluator is async).
- Per-case granularity in test output.

Pattern: keep evals in `eval/` next to the agent code, named `test_eval.py`, exercised by `pytest`.

## Variance and `num_runs`

LLM outputs vary. Running once gives a noisy reading.

- `num_runs=1` — fast smoke test; one bad sample fails you.
- `num_runs=5` — common default; balances cost and stability.
- `num_runs=10+` — for high-stakes gates or noisy metrics like LlmAsJudge.

The eval scores aggregate (mean by default). You can fail if *any* run failed (stricter) or if the average is below threshold (looser).

> ⚠️ **Gotcha.** `num_runs=5` means 5× LLM cost per case. A 20-case eval at num_runs=5 is 100 LLM rollouts. Budget accordingly.

> 🛠 **Have the student run:** From `adk-samples/python/agents/llm-auditor/`, `pytest eval/test_eval.py -v`. Watch one full eval run end to end. Eyeball the output for "what scored what."

> 🧭 **If pytest async feels strange:** detour to [[PY_testing]] for the pytest-asyncio basics.

> **🚀 In Production**
>
> Evals are part of your CI. Decide `num_runs` per pipeline stage: 1-2 for PR-time smoke, 5-10 for nightly gate. Cost is the lever; coverage is the goal.

---

[← Prev: 14_Evaluation/02_EvalCaseEvalSet]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/04_LlmAsJudge →]
