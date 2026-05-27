---
module: Detours
page: PY_testing
title: pytest — fixtures, mocks, and what tests do not test
estimated_minutes: 30
icon: 🐍
prereqs: [PY_async]
concepts: [pytest, fixture, monkeypatch, parametrize, AsyncMock, snapshot, tests_vs_evals]
---

[← Back to Map](../../MAP.md)

Triggered from: `14_Evaluation` (the test-vs-eval distinction), M1-M5 milestones ("now write tests"), `19_Internals`.

> Take this detour if you'd like to test your agent code but aren't sure where pytest stops and ADK's eval harness starts. ~30 min. Assumes [[PY_async]].

---

## 🐍 1. The minimum viable pytest

Discovery: any file named `test_*.py` or `*_test.py`, any function starting with `test_`.

```python
# test_math.py
def test_add():
    assert 1 + 1 == 2

def test_zero():
    assert 0 + 0 == 0
```

Run:

```bash
$ pytest -q
..                                                                       [100%]
2 passed in 0.01s
```

No `unittest.TestCase`, no `self.assertEqual`. Just `assert`. Pytest rewrites the assert so failures show the values:

```
>       assert 1 + 1 == 3
E       assert 2 == 3
```

---

## 🐍 2. Fixtures — reusable setup

```python
import pytest

@pytest.fixture
def sample_session():
    return {"user_id": "u1", "history": []}

def test_starts_empty(sample_session):
    assert sample_session["history"] == []

def test_can_append(sample_session):
    sample_session["history"].append("hi")
    assert len(sample_session["history"]) == 1
```

Each test gets a fresh `sample_session`. Scope it up if construction is expensive:

```python
@pytest.fixture(scope="module")   # one instance per test file
def db_connection(): ...

@pytest.fixture(scope="session")  # one for the whole test run
def gemini_client(): ...
```

> ⚠️ Module/session fixtures are mutated across tests if you're not careful. Default `function` scope is the safe one.

---

## 🐍 3. `monkeypatch` and `parametrize`

`monkeypatch` for env vars / small attribute patches:

```python
def test_uses_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    import myapp
    assert myapp.get_api_key() == "fake-key"
```

`parametrize` for table-driven tests:

```python
@pytest.mark.parametrize("op,a,b,want", [
    ("+", 1, 2, 3),
    ("-", 5, 3, 2),
    ("*", 4, 4, 16),
])
def test_calc(op, a, b, want):
    assert calc(op, a, b) == want
```

Three tests for the price of one function — and each failure reports which row failed.

---

## 🐍 4. Mocking the LLM with `AsyncMock`

`runner.run_async` is async, so you need `AsyncMock` (not plain `Mock`):

```python
from unittest.mock import AsyncMock, MagicMock

async def test_agent_uses_tool_response(monkeypatch):
    # Fake a single event with the final text we want
    fake_event = MagicMock()
    fake_event.content.parts = [MagicMock(text="Paris is sunny.")]
    fake_event.is_final_response.return_value = True

    async def fake_run_async(**_):
        yield fake_event

    runner = MagicMock()
    runner.run_async = fake_run_async   # async generator function

    final_text = ""
    async for ev in runner.run_async(user_id="u", session_id="s", new_message=None):
        if ev.is_final_response():
            final_text = ev.content.parts[0].text

    assert "Paris" in final_text
```

This tests *your wiring* — the loop that drains events, picks the final one, extracts text. It does **not** test whether Gemini is any good at the task.

---

## 🐍 5. Snapshot tests with `syrupy`

For agent outputs that are long but stable, snapshot testing diffs against a saved file:

```python
def test_agent_summary(snapshot):
    out = my_agent.summarize("...long input...")
    assert out == snapshot   # first run: saves. Subsequent runs: diffs.
```

`pytest --snapshot-update` regenerates them. Useful for deterministic post-processing of LLM output (e.g., a parser). Don't snapshot raw LLM text — it's non-deterministic and you'll just thrash.

---

## 🐍 6. The big distinction — tests verify CODE, evals verify BEHAVIOR

```
pytest                                  ADK evals (module 14)
──────                                  ─────────────────────
your code paths                         the agent's reasoning quality
deterministic, fast, hermetic           probabilistic, slower, calls real LLM
mock the LLM                            test against the real LLM
"does the function return X?"           "does the agent get the right answer?"
runs in CI on every push                runs nightly or pre-release
```

If you find yourself writing a pytest that asserts `"Paris" in agent.respond(...).text` against the **real** Gemini, you've drifted into eval territory. Move it to an `EvalSet` (module 14) where it belongs.

> ⚠️ **In Production**: pytest in PR CI, eval suite in a separate (slower, costly) pipeline. Don't gate every PR on real-LLM calls — flakiness will train your team to ignore failures.

---

## 🛠 Have the student try

A 10-line test that mocks an LLM response and asserts substring presence:

```python
# test_agent.py
import asyncio
from unittest.mock import MagicMock, AsyncMock

def fake_runner(text):
    fake_event = MagicMock()
    fake_event.content.parts = [MagicMock(text=text)]
    fake_event.is_final_response.return_value = True
    async def run_async(**_):
        yield fake_event
    r = MagicMock(); r.run_async = run_async
    return r

async def collect_final(runner):
    async for ev in runner.run_async():
        if ev.is_final_response():
            return ev.content.parts[0].text

def test_final_contains():
    runner = fake_runner("Berlin is the capital of Germany.")
    out = asyncio.run(collect_final(runner))
    assert "Berlin" in out
```

Run `pytest -q`. Then change the fake text to `"Paris"`. Watch the assertion fail cleanly — that's the value of pytest's assert rewriting.

---

Back to: whichever page triggered this — likely `14_Evaluation/01_TestsVsEvals` or any milestone's "now write tests" coda.

[← Back to Map](../../MAP.md)
