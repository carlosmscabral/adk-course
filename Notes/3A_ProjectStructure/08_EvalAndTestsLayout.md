---
module: 3A_ProjectStructure
page: 08_EvalAndTestsLayout
title: Eval + tests layout — where adk eval and pytest look
estimated_minutes: 15
prereqs: [3A_ProjectStructure/07A]
concepts: [eval-dir, tests-dir, eval-data, pytest-discovery, agent-evaluator]
icon: 🧪
in_production: true
detours_suggested: [PY_testing]
---

[← Prev: 07A_ConfigAndEnvVars](07A_ConfigAndEnvVars.md)  [↑ Map](../../MAP.md)  [Next: 09_DissectingSample →](09_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 08 Eval + tests layout

# 🧪 Eval + tests — where they live, what discovers them

> 🤖 **Tutor:** the student does not need to write evals yet — Module 14 handles that. This page is **layout-only**: where the files go so that the eval and test infrastructure can find them when the time comes.

## The two parallel directories

```
my_project/
├── pyproject.toml
├── my_agent/
│   ├── __init__.py
│   └── agent.py
├── eval/                    ← used by `adk eval` and pytest-based eval scripts
│   ├── test_eval.py         ← pytest test that calls AgentEvaluator.evaluate(...)
│   └── data/                ← JSON test cases / EvalSets
│       ├── happy_path.evalset.json
│       └── edge_cases.evalset.json
└── tests/                   ← classic unit/integration tests with pytest
    ├── test_agents.py
    └── test_tools.py
```

`eval/` and `tests/` are **separate directories**, not subfolders of each other. They serve different purposes:

| Directory | Tool | What it tests |
|---|---|---|
| `tests/` | `pytest` | Pure-code correctness: tools return the right shape, callbacks fire, no exceptions on import. Fast (<1s per test). |
| `eval/` | `pytest` + `AgentEvaluator`, or `adk eval` | Agent **behavior**: given input X, does the agent's trajectory + final response match the expected pattern? Slow (LLM calls). |

## `tests/` — classic pytest, no LLM

```python
# tests/test_tools.py
from my_agent.tools.search import web_search

def test_web_search_returns_list():
    result = web_search("python")
    assert isinstance(result, list)
    assert all("title" in r for r in result)
```

```python
# tests/test_agents.py — light agent test using InMemoryRunner
import pytest
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from my_agent.agent import root_agent

pytest_plugins = ("pytest_asyncio",)

@pytest.mark.asyncio
async def test_happy_path():
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user")
    content = UserContent(parts=[Part(text="hello")])
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=content):
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
    assert response  # non-empty
```

(Verbatim shape from `llm-auditor/tests/test_agents.py`. Real production tests look like this.)

## `eval/` — `AgentEvaluator`, ships with test data

```python
# eval/test_eval.py
import pathlib
import pytest
from google.adk.evaluation import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)

@pytest.mark.asyncio
async def test_all():
    """Run all EvalSets in eval/data/ against the agent."""
    await AgentEvaluator.evaluate(
        "my_agent",                                            # package name
        str(pathlib.Path(__file__).parent / "data"),           # eval data dir
        num_runs=5,
    )
```

`AgentEvaluator.evaluate(...)` takes:

1. The **import path** to your agent package (string, dotted if nested).
2. The **path to the directory** containing `.evalset.json` files.
3. `num_runs=` — how many times to run each case (LLMs are nondeterministic).

It will:

- Spin up the agent.
- For each case in `data/`, run the input, capture the trajectory, compare to expected.
- Fail the pytest test if any case scores below threshold.

Full coverage of `EvalCase`, `EvalSet`, `LlmAsJudge`, and the judging criteria lives in [Module 14 Evaluation](../14_Evaluation/).

## `pyproject.toml` wiring

```toml
[tool.pytest.ini_options]
pythonpath = "."
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests", "eval"]            # ← both dirs

[dependency-groups]
dev = [
    "google-adk[eval]>=1.31.0",         # ← [eval] extra pulls in AgentEvaluator deps
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]
```

Two things to notice:

1. `testpaths = ["tests", "eval"]` — pytest finds tests in both. You can also opt-in to one via `pytest tests/` or `pytest eval/`.
2. `google-adk[eval]` — the eval-specific dependencies (judges, rubrics) come from an extras group. Without `[eval]`, `from google.adk.evaluation import AgentEvaluator` errors.

## `adk eval` — the CLI alternative

```bash
adk eval my_agent eval/data/happy_path.evalset.json
```

`adk eval` is the **CLI** alternative to writing your own `pytest` wrapper. Same machinery underneath. Use it for ad-hoc runs; use the pytest wrapper for CI.

## Where `.evalset.json` files come from

You don't write them by hand for long. Workflow:

1. Use `adk web` and have a normal conversation.
2. Click "Save as eval set" — it captures the session as an EvalSet.
3. The file appears under `eval/data/<your_name>.evalset.json`.
4. Optionally edit by hand to refine the expected criteria.

This roundtrip is why `eval/` and `eval/data/` should be checked in — they're test fixtures, not artifacts.

> ⚠️ **Don't put eval data under `tests/data/`.** `adk eval` looks specifically under `eval/`, and `AgentEvaluator.evaluate(..., str(parent / "data"))` is the convention. Misplacing the directory means CI runs the unit tests but silently skips the evals.

> **🚀 In Production**
>
> Tests gate every PR; evals gate every release. Run `pytest tests/` on every push (fast). Run `pytest eval/` on a schedule or pre-release (slow, costs LLM tokens). Many teams use a smaller `eval/smoke/` subdir for the PR gate and the full `eval/data/` only for releases. Module 14 develops this discipline.

> 🛠 **Have the student** look at `adk-samples/python/agents/llm-auditor/`:
>
> ```bash
> ls /home/carloscabral/study/adk-samples/python/agents/llm-auditor/
> ls /home/carloscabral/study/adk-samples/python/agents/llm-auditor/eval/
> ls /home/carloscabral/study/adk-samples/python/agents/llm-auditor/tests/
> ```
>
> Confirm: `eval/test_eval.py` + `eval/data/`, `tests/test_agents.py`. Layout matches the template above exactly.

> ❓ **Ask the student:** "If your `tests/test_tools.py` imports `from my_agent.tools.search import web_search`, what has to be true about `my_agent/tools/search.py` for the import to succeed without running the agent?"
>
> *(Expected: no top-level side effects — no `LlmAgent(...)` construction, no `google.auth.default()` at import time. Functions only. This is one of the three pressures from page 01 made concrete.)*

---

[← Prev: 07A_ConfigAndEnvVars](07A_ConfigAndEnvVars.md)  [↑ Map](../../MAP.md)  [Next: 09_DissectingSample →](09_DissectingSample.md)
