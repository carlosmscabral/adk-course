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

`LlmAsJudge` is open-ended; you write a prose rubric. `RubricBasedEvaluator` is the structured cousin — the rubric is *data*, scored per-criterion, then aggregated.

```python
from google.adk.evaluation import RubricBasedEvaluator

rubric = [
    {"name": "answers_question", "weight": 0.5, "description": "Does the response answer the user's question?"},
    {"name": "cites_source",     "weight": 0.3, "description": "Does the response cite at least one source?"},
    {"name": "concise",          "weight": 0.2, "description": "Is the response under 5 sentences?"},
]

evaluator = RubricBasedEvaluator(rubric=rubric)
```

(Exact API per framework; the idea: list of criteria, each weighted, each scored independently.)

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
