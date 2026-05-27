---
module: 14_Evaluation
page: 04_LlmAsJudge
title: LlmAsJudge — an LLM rates the answer
estimated_minutes: 20
prereqs: [14_Evaluation/03]
concepts: [LlmAsJudge, rubric prompt, semantic match, non-determinism]
icon: 🧪
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/03_AgentEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/05_RubricBasedEvaluator →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 04 LlmAsJudge

# 🧪 When string matching breaks

For freeform answers, comparing strings (or even cosine similarity) is too brittle. "The capital of France is Paris" should match "Paris is the capital of France" and "France's capital is Paris."

`LlmAsJudge` evaluates with another LLM. The judge sees:

- The user's input.
- The agent's response.
- The gold reference (or a rubric describing what good looks like).

…and returns a score (typically 0.0 to 1.0) plus a short rationale.

## How you actually use it

`LlmAsJudge` is an **abstract base class** the framework instantiates internally — it is not in `google.adk.evaluation.__init__` (the only public export there is `AgentEvaluator`). You do not `from google.adk.evaluation import LlmAsJudge` and call its constructor; you configure a judge-backed metric via the EvalCase / EvalSet config and let `AgentEvaluator` wire it up.

The lever for "use a stronger model for judging" lives on the criterion config — specifically `judge_model_options` (declared in `google.adk.evaluation.eval_metrics.JudgeModelOptions`):

```python
# Conceptual shape of a judge-backed metric config (in your test_config.json
# or programmatically via EvalMetric + LlmAsAJudgeCriterion).
{
    "metric_name": "rubric_based_final_response_quality_v1",
    "threshold": 0.8,
    "criterion": {
        "threshold": 0.8,
        "judge_model_options": {
            "judge_model": "gemini-2.5-pro",   # stronger model for judging
            "num_samples": 5                   # repeated samples → aggregated
        }
    }
}
```

The constructor for `LlmAsJudge` itself (for reference, if you ever subclass it for a custom metric) is:

```python
# google/adk/evaluation/llm_as_judge.py
class LlmAsJudge(Evaluator):
    def __init__(
        self,
        eval_metric: EvalMetric,
        criterion_type: type[BaseCriterion],
        expected_invocations_required: bool = False,
    ): ...
```

Notice: no `model="..."` kwarg. The judge model comes from `self._criterion.judge_model_options.judge_model`.

## When LlmAsJudge wins

- Open-ended answers (creative writing, summaries, explanations).
- Multi-acceptable answers ("recommend a book" — many are right).
- Factual answers with paraphrasing latitude.

## When it loses

- Strict format requirements ("must be valid JSON conforming to schema X"). Use a programmatic match.
- Exact-match scenarios ("is the SQL query exactly `SELECT ... FROM users`"). Use string compare.
- High-volume cheap evals — LlmAsJudge costs an extra LLM call per run.

## Why "use a stronger model for judging"

The judge's quality bounds the eval's quality. A weaker judge will miss subtle errors and let bad responses through. Convention: set `judge_model_options.judge_model` to `gemini-2.5-pro` (or whatever your strongest available) — even when the agent under test uses a smaller model. The default in `JudgeModelOptions` is `gemini-2.5-flash`; override it when stakes are high.

## Variance — the cost of using an LLM to evaluate

LlmAsJudge is itself non-deterministic. Running the same eval twice may give slightly different scores. Mitigations:

- Higher `num_runs` at the `AgentEvaluator` level (see page 03) — repeats the whole inference.
- Higher `judge_model_options.num_samples` (default 5) — repeats the *judge* call per invocation and aggregates.
- Lower temperature on the judge call via `judge_model_options.judge_model_config` (default for evaluators is often 0.0, but check).
- Use a rubric that yields binary or ordinal decisions ("pass/fail" or 1-5), not free 0.0-1.0 — easier for the judge to be consistent.

> ⚠️ **Gotcha.** A vague rubric ("rate the quality") gives noisy scores. A specific rubric ("1.0 iff response contains the city name AND it is in the gold reference") gives stable scores. Write your rubrics like code.

> ❓ **Ask the student:** "Why don't we just use the agent's own model as the judge?" *(Expected: shared blind spots — if the model is biased toward an error, the same model won't catch it. Use a different, stronger model.)*

> **🚀 In Production**
>
> Pair LlmAsJudge with a cheaper deterministic metric (e.g., FinalResponseMatchV1 as a sanity floor). Track judge agreement over time — if your judge scores drift relative to human review, the rubric is decaying.

---

[← Prev: 14_Evaluation/03_AgentEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/05_RubricBasedEvaluator →]
