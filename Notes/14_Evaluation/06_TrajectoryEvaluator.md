---
module: 14_Evaluation
page: 06_TrajectoryEvaluator
title: TrajectoryEvaluator — score the path, not just the answer
estimated_minutes: 20
prereqs: [14_Evaluation/05]
concepts: [TrajectoryEvaluator, tool_trajectory_avg_score, multi-agent assertions]
icon: 🧪
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/05_RubricBasedEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/07_BuiltInMetrics →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 06 TrajectoryEvaluator

# 🧪 The final answer can be right by accident

Suppose the agent should fetch a fact via `search()` and report it. The agent skips `search()` and "happens to" know the answer. The response matches the gold; the trajectory doesn't.

That's a failure you want to catch:

- The "correct" answer was a guess; production may not be so lucky.
- For a multi-agent system, you want to know that *the right sub-agent* fired.
- For an audit story, you want the tool log to match policy.

`TrajectoryEvaluator` compares the **actual tool-call sequence** to the gold sequence.

## What it measures

From the eval case:

```json
"intermediate_data": {
  "tool_uses": [
    {"name": "search", "args": {"query": "..."}},
    {"name": "summarize", "args": {"text": "..."}}
  ]
}
```

The evaluator walks the agent's actual event stream, extracts the `tool_call` events, and compares (by tool name; optionally by args).

Scoring: `tool_trajectory_avg_score` — 1.0 if exact match, partial credit for partial overlap, 0.0 if missing or extra tools.

## In `test_config.json`

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.35
  }
}
```

`1.0` is the typical threshold for trajectory — for "the right tool, in the right order," anything less is a regression.

## Especially powerful for multi-agent

For a multi-agent tree:

- Did root transfer to the right sub-agent?
- Did the sub-agent call its specialist tool?
- Was there a backtrack / re-transfer?

The trajectory captures all of it (transfers show up as events). You can write a case asserting "root → sub_a → tool_x → root → final" and the evaluator verifies the whole flow.

## When to relax

- Open-ended agents where multiple tool-call orders are valid. Drop the score threshold or convert to "did at least one of [tool_a, tool_b] fire" rules.
- Agents that retry. Allow N attempts of the same tool.

## Pairing

Trajectory on the path + LlmAsJudge or RubricBased on the answer = the standard combination. Catch both "right answer wrong path" and "right path wrong answer."

> ⚠️ **Gotcha.** Tightening `tool_trajectory_avg_score` to 1.0 will fight you if your agent does sane things you didn't anticipate (asking a clarifying question first, double-checking with a second tool). Calibrate to the agent's actual variance.

> ❓ **Ask the student:** "If response matches gold but trajectory is empty, what does that tell you?" *(Expected: the model didn't use tools at all — answered from training. May be acceptable for facts, never acceptable when you need a *live* source.)*

> **🚀 In Production**
>
> Trajectory thresholds catch silent regressions (a prompt change makes the model skip a tool). Pair with alerting: if trajectory pass rate drops without response pass rate dropping, the agent is faking it.

---

[← Prev: 14_Evaluation/05_RubricBasedEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/07_BuiltInMetrics →]
