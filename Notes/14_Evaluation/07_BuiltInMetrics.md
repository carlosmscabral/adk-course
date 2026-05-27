---
module: 14_Evaluation
page: 07_BuiltInMetrics
title: HallucinationsV1 and FinalResponseMatchV1/V2
estimated_minutes: 20
prereqs: [14_Evaluation/06]
concepts: [HallucinationsV1, FinalResponseMatchV1, FinalResponseMatchV2, metric selection]
icon: 🧪
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/06_TrajectoryEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/08_AdkEvalCli →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 07 Built-in Metrics

# 🧪 The three metrics ADK ships out of the box

## `FinalResponseMatchV1`

String/regex-style match between the agent's final response and the gold reference. Returns a similarity score (typically token-overlap based).

Use when:

- The expected response is short and well-defined.
- You want a fast, cheap, deterministic check.

Avoid when:

- The response is freeform — V1 will score paraphrases low.
- You care about *meaning* over wording.

## `FinalResponseMatchV2`

Semantic match. Typically backed by an LLM (or strong embedding model) that judges "does this response say the same thing as the gold?"

Use when:

- The response can be paraphrased.
- Wording matters less than meaning.

Cost: more expensive than V1 (LLM call), more forgiving of paraphrase.

Convention: V1 for tight format-locked answers, V2 for everything else.

## `HallucinationsV1`

Specialized metric for retrieval/RAG agents. Checks whether the agent's claims are grounded in the retrieved sources. Marks claims that are confident-sounding but unsupported.

Use when:

- Your agent retrieves docs (RAG, search, memory).
- Citation and groundedness are part of the contract.

Avoid when:

- The agent has no retrieval surface — there's no "source" to ground against. Other metrics apply.

## Picking the right metric

A short decision tree:

```
Is this a retrieval / RAG agent?
  yes → HallucinationsV1 + FinalResponseMatchV2
  no  → does response have a fixed format?
        yes → FinalResponseMatchV1
        no  → FinalResponseMatchV2 (or LlmAsJudge for open-ended)
Always also: TrajectoryEvaluator if tool use matters.
```

## Combining metrics

Multiple metrics can run on one EvalSet. Each contributes a score; `test_config.json` thresholds gate each independently:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.6,
    "hallucination_score": 0.9
  }
}
```

All thresholds must pass for the eval to pass. (`AND` semantics.)

> ⚠️ **Gotcha.** Don't use V1 and V2 for the same response — they'd be measuring almost the same thing. Pick one based on whether you care about wording or meaning.

> ❓ **Ask the student:** "You added citations to your RAG agent and the FinalResponseMatchV1 score tanked. Why, and what do you do?" *(Expected: V1 is token-overlap; adding citation text shifts the wording. Switch to V2 (semantic) — or rewrite gold references to include the new citation format.)*

> **🚀 In Production**
>
> Don't tune thresholds to whatever your current agent passes. Pick the threshold that represents real quality; if the agent currently fails, that's a regression to fix, not a threshold to lower.

---

[← Prev: 14_Evaluation/06_TrajectoryEvaluator]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/08_AdkEvalCli →]
