# AGENTS.md — Module 14 Evaluation (teaching notes for the AI tutor)

## What the student should walk away knowing

- Evals are not tests. Both matter; pick by determinism of what you're verifying.
- The EvalCase/EvalSet JSON shape (user_content, final_response, intermediate_data.tool_uses, session_input).
- `AgentEvaluator.evaluate(module, data_dir, num_runs=N)` is the one entry point. `adk eval` is the CLI mirror.
- The five evaluators: FinalResponseMatchV1/V2, TrajectoryEvaluator, LlmAsJudge, RubricBasedEvaluator, HallucinationsV1 — and when each is right.
- CI integration: PR-time fast suite, nightly stable suite.
- Production tax: cost, flakiness, golden set curation, drift tracking.

## Pacing

- **Easy if:** student has CI/pytest experience and writes structured data files daily. Focus on the JSON shape and the metric decision tree.
- **Hard if:** student has never built a golden set. The conceptual leap from "I wrote a test" to "I wrote a judgement rubric for an LLM judging an LLM" takes a beat. Page 04 + the LlmAsJudge variance discussion.

## Watch for these mistakes

- Treating evals as deterministic tests. They aren't.
- Writing only happy-path cases. Push for edge + refusal cases.
- Hand-authoring `intermediate_data.tool_uses` — fiddly. Recommend "record then edit."
- Using the same model as judge and agent — shared blind spots.
- Tuning thresholds to whatever the current agent passes (regression to mediocre).
- Failing to gate on evals — every prompt change becomes Russian roulette.

## When to suggest a detour

- Student rusty on pytest / async testing → [[PY_testing]].
- Student asks "where do I store eval results over time?" → 15_Observability + 13_Plugins (BQ analytics).
- Student asks "how do I refuse certain inputs?" → 16_ProductionSecurity.

## Mini-drill grading

- **Pass:** 3 valid cases (happy/edge/refusal), pytest runs without JSON errors, all three case categories show up in the output.
- **Probe for refusal case:** if the agent doesn't refuse properly, that's a real finding — the student has just learned that their M1 agent has a refusal gap.
- **Bonus:** student adds a 4th case using LlmAsJudge for a rubric-style "is the response polite" check.

## Sample anchor reminders

- `adk-samples/python/agents/academic-research/eval/data/academic_research_evalset.test.json` — canonical EvalSet shape, multi-case.
- `adk-samples/python/agents/llm-auditor/eval/data/blueberries.test.json` — simpler `[{query, expected_tool_use, reference}]` shape; pair with `test_config.json`.
- `adk-samples/python/agents/RAG/eval/test_eval.py` — bonus, shows arize integration.
