---
module: 14_Evaluation
page: 09_DissectingSample
title: Dissecting the academic-research eval
estimated_minutes: 30
prereqs: [14_Evaluation/08]
concepts: [sample read-through, evalset structure, pytest wiring]
icon: 🧪
in_production: false
detours_suggested: []
---

[← Prev: 14_Evaluation/08_AdkEvalCli]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/10_InProduction →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 09 Dissecting academic-research

# 🧪 Reading a real eval

Sample: `/home/carloscabral/study/adk-samples/python/agents/academic-research/eval/`

```
academic-research/
└── eval/
    ├── data/
    │   └── academic_research_evalset.test.json
    └── test_eval.py
```

## File 1: `test_eval.py`

```python
import pathlib
import dotenv
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()

@pytest.mark.asyncio
async def test_all():
    await AgentEvaluator.evaluate(
        "academic_research",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=5,
    )
```

Three things to highlight:

1. **`pytest_asyncio` is registered** — the eval is async.
2. **`load_env` fixture** — pulls credentials, model IDs from `.env`. Important: evals talk to real LLMs, real credentials needed.
3. **`num_runs=5`** — chosen to balance signal and cost.

That's the whole test file. The complexity lives in the data.

## File 2: `data/academic_research_evalset.test.json`

Open the file. Walk through what each top-level field encodes:

- `eval_set_id` / `name` — identifiers.
- `eval_cases` — list of cases (the academic-research sample only has 1: `eval_id: "hello"`).

For the `hello` case, focus on:

```json
"conversation": [
  {
    "user_content": { "parts": [{ "text": "hello" }], "role": "user" },
    "final_response": {
      "parts": [{ "text": "Hello! I am an AI Research Assistant. I can help you analyze a seminal paper..." }]
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
```

Annotate aloud with the student:

- `user_content` = input.
- `final_response` = gold response.
- `intermediate_data.tool_uses = []` → no tools should be called for "hello." A greeting case.
- `session_input.state = {}` → start with a fresh state.

## What's NOT here

- No `test_config.json` in this dir at the time of this writing. Without it, defaults apply (or the framework requires you to add one for stricter thresholds). Compare with `llm-auditor/eval/data/test_config.json`, which sets explicit thresholds.

## Run it conceptually

```
$ pytest eval/test_eval.py -v
   collected 1 item
   ▶ for case "hello":
      ▶ run 1/5: agent received "hello" → emitted greeting → score: response_match=0.78, tools=ok
      ▶ run 2/5: ... 0.82, ok
      ▶ run 3/5: ... 0.71, ok
      ▶ run 4/5: ... 0.75, ok
      ▶ run 5/5: ... 0.80, ok
   ▶ aggregate: response_match_avg=0.77, tool_trajectory_avg=1.0
   PASS
```

> ❓ **Ask the student:** "What would happen to this eval if you replaced `model='gemini-2.5-flash'` with `model='gemini-2.5-pro'` in the agent?" *(Expected: response_match scores probably rise as pro paraphrases more like the gold; trajectory probably unchanged. Discuss whether you should rebaseline the threshold.)*

> 🤖 **Tutor:** The academic-research eval is small on purpose. Use it to establish the *shape*; the student's own mini-drill will build a richer set.

---

[← Prev: 14_Evaluation/08_AdkEvalCli]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/10_InProduction →]
