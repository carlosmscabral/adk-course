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
# first positional is a DIRECTORY containing an __init__.py that exposes `agent.root_agent`
$ adk eval ./path/to/agent_dir path/to/eval_data/cases.test.json
```

Common shape:

```bash
$ adk eval ./llm_auditor eval/data/blueberries.test.json
Running eval set: blueberries
Case 1 of 1 ... score: response_match=0.42, tool_trajectory=1.0
PASS (above thresholds in test_config.json)
```

Flags you'll reach for (from `cli_tools_click.py`, the `adk eval` command):

- `--config_file_path` — path to a config file (overrides default `test_config.json` discovery).
- `--print_detailed_results` — flag; print per-case detail to console.
- `--eval_storage_uri` — optional storage URI for evals (e.g. `gs://<bucket>`).
- `--log_level` — `DEBUG`/`INFO`/`WARNING`/`ERROR` (default `INFO`).

> ⚠️ **No `--num_runs` flag.** It's not CLI-configurable; the CLI path uses the hardcoded `NUM_RUNS = 2` constant in `agent_evaluator.py`. If you need a different number of runs, call the Python API directly: `AgentEvaluator.evaluate(..., num_runs=5)`. There is no `--output_dir` or `--config_path` either — use `--config_file_path` and let `--print_detailed_results` (or your own pytest harness) handle output.

(Run `adk eval --help` on your install to confirm — flags can grow between minor versions.)

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
    adk eval ./my_agent eval/data/ \
      --config_file_path eval/test_config.json \
      --print_detailed_results \
      | tee eval-results.log
- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    path: eval-results.log
```

Capture the detailed-results output yourself; the CLI doesn't write a structured report directory. If you need richer artifacts (PR comments, dashboards), use Shape A (pytest) or drive `AgentEvaluator.evaluate()` from a small Python script.

## Two-stage CI (PR vs nightly)

`num_runs` isn't a CLI knob — it's a Python-API argument (default `NUM_RUNS = 2` in `agent_evaluator.py`). To get the two-stage pattern, use Shape A (pytest) and pass `num_runs` explicitly:

- **PR check.** `AgentEvaluator.evaluate(..., num_runs=1)`. Smoke test; fast, cheap. Catches catastrophic regressions.
- **Nightly.** `AgentEvaluator.evaluate(..., num_runs=5)` or more. Stable signal. Gate on this for releases.

Don't gate releases on a one-run eval — it's flaky-by-design.

## Local dev iteration

For a one-off "did my prompt change break anything":

```bash
$ adk eval ./my_agent eval/data/case_i_care_about.test.json --print_detailed_results
```

Faster than running pytest, useful for tight feedback loops. Note: uses the hardcoded `NUM_RUNS = 2` default — for a single-run smoke test, call the Python API.

> ⚠️ **Gotcha.** `adk eval` and `pytest test_eval.py` should agree. If they don't, check that the module path, data path, and test_config.json are the same in both.

> 🛠 **Have the student run:** From `adk-samples/python/agents/llm-auditor/`, run `adk eval llm_auditor eval/data/blueberries.test.json` and compare to `pytest eval/test_eval.py`. Both should pass (or both fail, identically).

> **🚀 In Production**
>
> Two-stage CI is the rule. PR-time = fast smoke; nightly = stable gate. Track scores over time in a dashboard — `BigQueryAgentAnalyticsPlugin` works for this if you persist eval-run records too.

---

[← Prev: 14_Evaluation/07_BuiltInMetrics]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/09_DissectingSample →]
