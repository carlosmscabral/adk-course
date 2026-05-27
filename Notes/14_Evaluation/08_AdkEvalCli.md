---
module: 14_Evaluation
page: 08_AdkEvalCli
title: adk eval — the CLI entry point
estimated_minutes: 15
prereqs: [14_Evaluation/03]
concepts: [adk eval, CLI, CI integration]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/07_BuiltInMetrics]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/09_DissectingSample →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 08 adk eval CLI

# 🛠 Running evals without pytest

`adk eval` runs an EvalSet from the command line. Same machinery as `AgentEvaluator.evaluate()`; no test file required.

```bash
# from a project containing your agent module
$ adk eval my_agent_module path/to/eval_data/cases.test.json
```

Common shape:

```bash
$ adk eval llm_auditor eval/data/blueberries.test.json
Running eval set: blueberries
Case 1 of 1 ... score: response_match=0.42, tool_trajectory=1.0
PASS (above thresholds in test_config.json)
```

Flags you'll reach for:

- `--num_runs N` — same as the Python arg. Default 1 (cheap smoke test).
- `--output_dir` — where to write detailed per-case reports.
- `--config_path` — override `test_config.json` location.

(Exact flag set depends on the ADK version — `adk eval --help` for the truth on your install.)

## CI integration

Two shapes:

### Shape A — pytest in CI

```yaml
# .github/workflows/eval.yml (sketch)
- name: Run agent evals
  run: pytest eval/test_eval.py -v
```

Same as the pattern in `academic-research/eval/`. CI just runs pytest; the eval is one test function.

### Shape B — `adk eval` direct

```yaml
- name: Run agent evals
  run: |
    adk eval my_agent eval/data/ --num_runs 5 --output_dir eval-results/
- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    path: eval-results/
```

When you want to publish detailed reports as a CI artifact (PR comments, dashboards).

## Two-stage CI (PR vs nightly)

Typical:

- **PR check.** `num_runs=1`. Smoke test; fast, cheap. Catches catastrophic regressions.
- **Nightly.** `num_runs=5` or more. Stable signal. Gate on this for releases.

Don't gate releases on a one-run eval — it's flaky-by-design.

## Local dev iteration

For a one-off "did my prompt change break anything":

```bash
$ adk eval my_agent eval/data/case_i_care_about.test.json --num_runs 1
```

Faster than running pytest, useful for tight feedback loops.

> ⚠️ **Gotcha.** `adk eval` and `pytest test_eval.py` should agree. If they don't, check that the module path, data path, and test_config.json are the same in both.

> 🛠 **Have the student run:** From `adk-samples/python/agents/llm-auditor/`, run `adk eval llm_auditor eval/data/blueberries.test.json` and compare to `pytest eval/test_eval.py`. Both should pass (or both fail, identically).

> **🚀 In Production**
>
> Two-stage CI is the rule. PR-time = fast smoke; nightly = stable gate. Track scores over time in a dashboard — `BigQueryAgentAnalyticsPlugin` works for this if you persist eval-run records too.

---

[← Prev: 14_Evaluation/07_BuiltInMetrics]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/09_DissectingSample →]
