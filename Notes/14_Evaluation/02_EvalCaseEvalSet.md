---
module: 14_Evaluation
page: 02_EvalCaseEvalSet
title: EvalCase and EvalSet
estimated_minutes: 25
prereqs: [14_Evaluation/01]
concepts: [EvalCase, EvalSet, JSON format, session_input, intermediate_data]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/01_EvalsAreNotTests]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/03_AgentEvaluator →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 02 EvalCase & EvalSet

# 🧠 The unit of evaluation

An **EvalCase** is *one input + the expected behavior*. An **EvalSet** is a list of EvalCases sharing config (app name, criteria).

ADK serializes both as JSON files. Two filenames you'll see:

- `<name>.test.json` — a single EvalCase (the simpler shape; `llm-auditor` uses it).
- `<name>_evalset.test.json` — a full EvalSet with many cases (`academic-research` uses it).

## Shape of a simple EvalCase (`llm-auditor/eval/data/blueberries.test.json`)

```json
[
  {
    "query": "Q: Why the blueberries are blue? A: Because blueberries have pigments on their skin.",
    "expected_tool_use": [],
    "reference": "I will revise the answer to address the inaccuracies identified in the previous analysis. Revised answer: Because blueberries have a coating of wax on their surface that scatters blue light."
  }
]
```

Three fields:

- `query` — what the user asked.
- `expected_tool_use` — list of tool calls you expect the agent to make.
- `reference` — the gold final response (matched fuzzily, not literally).

## Shape of a full EvalSet (`academic-research/eval/data/academic_research_evalset.test.json`)

```json
{
  "eval_set_id": "academic_research_evalset",
  "name": "academic_research_evalset",
  "eval_cases": [
    {
      "eval_id": "hello",
      "conversation": [
        {
          "invocation_id": "e-...",
          "user_content": {
            "parts": [{ "text": "hello" }],
            "role": "user"
          },
          "final_response": {
            "parts": [{ "text": "Hello! I am an AI Research Assistant...." }]
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "academic_research",
        "user_id": "user",
        "state": {}
      }
    }
  ]
}
```

Key fields:

- `conversation` — the user turn(s) and gold response(s). Can be multi-turn.
- `intermediate_data.tool_uses` — the gold tool calls. The evaluator compares the agent's actual trajectory.
- `session_input.state` — starting state for the session. Use to test stateful flows.

## `test_config.json` — the pass thresholds

Alongside the data files, a `test_config.json` defines what "passing" means:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.35
  }
}
```

- `tool_trajectory_avg_score: 1.0` — every tool call must match exactly.
- `response_match_score: 0.35` — response similarity must clear 0.35.

The thresholds are intentionally lax for response (LLM output is paraphrastic) and tight for trajectory (tool choice is more deterministic).

## Building cases

Two paths:

1. **By hand.** Author JSON. Reasonable for small golden sets.
2. **Recorded.** Run the agent, capture an actual session, save it as the gold. The `adk web` UI supports this; `adk` CLI also has commands. Then *edit* the gold to be what you wanted, not what happened.

> ⚠️ **Gotcha.** Hand-authoring `intermediate_data.tool_uses` is fiddly — the schema matters. Recording is easier; "record then edit" is the fastest path to good cases.

> ❓ **Ask the student:** "What's `session_input` for, and why might you use it?" *(Expected: to start the case with pre-existing state — testing flows that depend on user prefs, conversation history, or app-level config.)*

> 🤖 **Tutor:** Don't get stuck on JSON shape memorization. Have the student look at one real `.test.json` from samples, then write *one* case from scratch.

---

[← Prev: 14_Evaluation/01_EvalsAreNotTests]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/03_AgentEvaluator →]
