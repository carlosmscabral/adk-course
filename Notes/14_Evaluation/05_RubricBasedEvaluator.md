---
module: 14_Evaluation
page: 05_RubricBasedEvaluator
title: RubricBasedEvaluator
estimated_minutes: 15
prereqs: [14_Evaluation/04]
concepts: [RubricBasedEvaluator, fixed rubric, quantitative scoring]
icon: 🧪
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/04_LlmAsJudge]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/06_TrajectoryEvaluator →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 05 RubricBasedEvaluator

# 🧪 Rubric-as-data

`LlmAsJudge` is open-ended; the judge writes prose. `RubricBasedEvaluator` is the structured cousin — the rubric is *data*, scored per-criterion, then aggregated.

## You don't construct it directly

Like `LlmAsJudge`, `RubricBasedEvaluator` is **not** re-exported from `google.adk.evaluation`; that package's `__init__.py` only exposes `AgentEvaluator`. The rubrics themselves are not passed to the constructor either — they live on the criterion config (`RubricsBasedCriterion.rubrics`), and the evaluator reads them off `self._criterion.rubrics`.

The real constructor (for subclass authors only) is:

```python
# google/adk/evaluation/rubric_based_evaluator.py
class RubricBasedEvaluator(LlmAsJudge):
    def __init__(
        self,
        eval_metric: EvalMetric,
        criterion_type: type[BaseCriterion],
        auto_rater_response_parser: AutoRaterResponseParser = DefaultAutoRaterResponseParser(),
        per_invocation_results_aggregator: PerInvocationResultsAggregator = MajorityVotePerInvocationResultsAggregator(),
        invocation_results_summarizer: InvocationResultsSummarizer = MeanInvocationResultsSummarizer(),
        rubric_type: Optional[str] = None,
    ): ...
```

What you actually do is feed rubrics into the criterion config:

```python
# Conceptual shape — your test_config.json criterion (or programmatic
# RubricsBasedCriterion). The framework instantiates the evaluator.
{
    "metric_name": "rubric_based_final_response_quality_v1",
    "threshold": 0.8,
    "criterion": {
        "threshold": 0.8,
        "judge_model_options": {"judge_model": "gemini-2.5-pro"},
        "rubrics": [
            {"rubric_id": "answers_question",
             "rubric_content": {"text_property": "Does the response answer the user's question?"}},
            {"rubric_id": "cites_source",
             "rubric_content": {"text_property": "Does the response cite at least one source?"}},
            {"rubric_id": "concise",
             "rubric_content": {"text_property": "Is the response under 5 sentences?"}}
        ]
    }
}
```

Each rubric is scored independently by the judge model and then aggregated by the configured `per_invocation_results_aggregator` (default: majority vote) and `invocation_results_summarizer` (default: mean).

## What you gain over `LlmAsJudge`

- **Per-criterion visibility.** Pass/fail per axis. You can see which dimension is failing across cases.
- **Stable aggregation.** Weights are fixed; the judge can't drift them.
- **Smaller decisions.** "Does this cite a source?" is a tighter judgement than "is this good?"

## What you give up

- **Open-ended insight.** A free-form judge might say "this is technically correct but misses the user's intent" — a fixed rubric misses subtext unless you've written a criterion for it.

## Composing rubrics

Common rubric for a retrieval agent:

```
{name: "answer_grounded",    weight: 0.4}  — every claim backed by retrieved doc
{name: "citation_correct",   weight: 0.2}  — citation points to actual source
{name: "answers_question",   weight: 0.3}  — addresses what the user asked
{name: "no_hallucination",   weight: 0.1}  — no fabricated facts
```

Pattern: 3-5 criteria, weighted to sum to 1.0, each judgeable in isolation.

## Pairing with the trajectory evaluator

Rubric on the response, trajectory on the path. Both add up to "did the agent do what we wanted, the way we wanted." See page 06.

> ⚠️ **Gotcha.** Don't write rubrics with overlapping criteria ("answers question" AND "addresses user intent" — same thing). Each criterion should be independently judgeable; overlap dilutes the score.

> ❓ **Ask the student:** "When would you prefer LlmAsJudge over RubricBasedEvaluator?" *(Expected: early in an agent's life when you don't yet know which dimensions matter; the open-ended judge surfaces failure modes you didn't pre-list.)*

> **🚀 In Production**
>
> Start with `LlmAsJudge` to find your failure modes. After ~50 cases, convert the recurring failure modes into rubric criteria. The rubric becomes a rolling spec of what "good" looks like.

---

[← Prev: 14_Evaluation/04_LlmAsJudge]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/06_TrajectoryEvaluator →]
