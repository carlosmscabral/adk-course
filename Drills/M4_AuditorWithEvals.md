---
module: Drills
page: M4_AuditorWithEvals
title: Milestone M4 — Auditor with plugins, callbacks, and evals
estimated_minutes: 960
prereqs: [00_Setup/last, 02_FirstAgent/last, 03_Tools/last, 04_SessionsState/last, 05_MultiAgent/last, 07_Callbacks/last, 13_Plugins/last, 14_Evaluation/last]
concepts: [SequentialAgent, before_tool_callback, LoggingPlugin, EvalSet, _END_OF_EDIT_MARK]
icon: 🏁
in_production: false
detours_suggested: []
---

[← Prev: 14_Evaluation/12_MiniDrill]  [↑ Map](../MAP.md)  [Next: 15_Observability/00_Overview →]

You are here: 🗺 Drills ▸ 🏁 M4 Auditor with Evals

## 🏁 What you're building

You'll re-create the **`llm-auditor`** sample from memory — a two-agent sequential pipeline that **criticizes** an LLM-generated answer and then **revises** it — and then bolt on three production-grade additions:

- **(a)** a `LoggingPlugin` for observability (Module 13).
- **(b)** a `before_tool_callback` for safety — blocks search queries that are obviously bad (Module 07).
- **(c)** an `EvalSet` with **5 cases** covering hallucination detection, citation quality, and edit-mark stripping (Module 14).

The exercise pulls together the entire Runtime track. By the end, you'll have a deployable auditor with logs, a safety gate, and a CI-runnable eval set.

## 🎯 Goals

- Recreate a real multi-agent system from spec without copy-pasting the sample.
- Wire a plugin and a callback simultaneously and understand which one fires when.
- Write evals that exercise three distinct failure modes (hallucination, citation, formatting).
- See `_END_OF_EDIT_MARK` stripping in action — and write an eval that breaks if you forget it.

## 📋 Prereqs

- Completed modules 00-04 (basics), 05 (multi-agent), 07 (callbacks), 13 (plugins), 14 (evaluation).
- LLM credentials (Gemini API or Vertex auth).
- `google-adk` installed; `pytest`, `pytest-asyncio`, `dotenv` available.
- Optional: read `adk-samples/python/agents/llm-auditor/` once for orientation, then **close it**. Recreate from memory.

## ⏱ Time

**2 days** (~12-16 hours actual). Day 1: rebuild the auditor + add plugin + callback (~6h). Day 2: write the eval set + iterate until it's stable (~6h).

## 📐 Spec

### Part 1 — Rebuild the auditor

A `SequentialAgent` with two sub-agents:

```
root: llm_auditor (SequentialAgent)
├── critic_agent   (LlmAgent, gemini-2.5-flash)
│      tools: [google_search]
│      after_model_callback: _render_reference   # appends citations
└── reviser_agent  (LlmAgent, gemini-2.5-flash)
       after_model_callback: _remove_end_of_edit_mark
```

#### critic_agent

- **Input** (from user): a `Q: ... A: ...` pair where A is a candidate LLM answer.
- **Job:** identify factual claims in A; for each, do `google_search` and decide if it's correct or wrong; report the inaccuracies.
- **`after_model_callback`** `_render_reference`: append a "Reference:\n* [title](uri): text\n..." block built from `llm_response.grounding_metadata.grounding_chunks`. (Real sample code lives in `llm-auditor/sub_agents/critic/agent.py` — recreate from memory.)

#### reviser_agent

- **Input:** the critic's output (the analysis with references).
- **Job:** produce a revised version of the original A, then emit the literal token `---END-OF-EDIT---` to mark the end.
- **`after_model_callback`** `_remove_end_of_edit_mark`: find `---END-OF-EDIT---` in any part, drop everything after it, strip the marker. If you forget this, the user sees the marker.

The full `_END_OF_EDIT_MARK` constant and the callback shape from the real sample:

```python
_END_OF_EDIT_MARK = "---END-OF-EDIT---"

def _remove_end_of_edit_mark(callback_context, llm_response):
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
    return llm_response
```

### Part 2 — Add the LoggingPlugin

```python
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.plugins import LoggingPlugin

app = App(
    name="auditor",
    root_agent=llm_auditor,
    plugins=[LoggingPlugin()],
)
runner = Runner(app=app, session_service=InMemorySessionService())
```

> ⚠ Legacy `Runner(plugins=[...])` still works but is deprecated (`runners.py:219-220, 287-306`) — plugins now live on `App`, and `App` is passed to `Runner` via `app=`. See Module 1A for the full lifecycle story.

Run one auditor turn. Inspect the log output:

- One `before_agent` per sub-agent (critic, reviser).
- One `before_model` / `after_model` per sub-agent's LLM call.
- One `before_tool` / `after_tool` for the critic's `google_search` call.

You should be able to read the log and reconstruct the conversation.

### Part 3 — Add the safety callback

Wire `before_tool_callback` on the `critic_agent` only:

```python
async def safety_search_guard(tool, args, tool_context):
    if tool.name != "google_search":
        return None
    query = args.get("query", "")
    # Block obvious "bad" queries — design at least 2 deny rules:
    # 1. Queries containing personal identifiers (emails, phones, SSNs).
    # 2. Queries that look like exfiltration attempts ("ignore prior...").
    if _is_obvious_bad_query(query):
        return {"result": "[blocked by safety guard]"}  # short-circuits the tool
    return None
```

Tip: write `_is_obvious_bad_query` as a few regex patterns — this is a drill in **wiring**, not in building a SOTA filter. (For production-grade safety, see `13_Plugins` `safety-plugins` patterns and `16_ProductionSecurity`.)

Verify by sending a user message whose A field contains an exfiltration prompt the LLM might naively search for. Watch the log: `before_tool` fires, the guard short-circuits, the tool returns the blocked string, the LLM gets that as the tool result and reasons around it.

### Part 4 — Write 5 EvalCases

Create `Work/M4/eval/data/auditor_evalset.test.json` with **5 cases**.

| # | Case type | Tests |
|---|-----------|-------|
| 1 | Hallucination — wrong fact | Critic must flag the incorrect claim; reviser must correct it. |
| 2 | Hallucination — no error | Critic should report "no inaccuracies"; reviser should keep the answer or lightly polish. |
| 3 | Citation quality | Critic must produce a `Reference:` block containing at least one URL. |
| 4 | Edit-mark stripping | Reviser response must NOT contain the literal string `---END-OF-EDIT---`. Tests your `_remove_end_of_edit_mark` callback. |
| 5 | Safety guard fires | An A field that would cause an exfiltration-style search. Expected `tool_uses` for `google_search` should be EMPTY (or replaced by the blocked sentinel). |

Also write `Work/M4/eval/data/test_config.json` with thresholds:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.8,
    "response_match_score": 0.3
  }
}
```

Trajectory at 0.8 (not 1.0) because case 5's expected-empty trajectory creates ambiguity; relax just enough to avoid flakiness.

> 🟡 The flat `criteria` dict shape above is **deprecated** per `agent_evaluator.py:135`. Modern `EvalConfig` shape is preferred: `EvalConfig(criteria={k: BaseCriterion(threshold=v)})`. The old shape is auto-mapped for now — see `agent_evaluator.py:140-143`.

Write `Work/M4/eval/test_eval.py`:

```python
import pathlib
import dotenv
import pytest
from google.adk.evaluation import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()

@pytest.mark.asyncio
async def test_all():
    await AgentEvaluator.evaluate(
        "auditor",  # your module path
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=3,
    )
```

Run: `pytest Work/M4/eval/test_eval.py -v`.

## ✅ Verification rubric

| Check | Pass criterion |
|---|---|
| Auditor produces criticized + revised text | Running once with a wrong A: stdout contains both the critique (with at least one citation) and a revised A. |
| LoggingPlugin output is informative | The log shows the full chain: before_agent critic → before_model → before_tool google_search → after_tool → after_model → ... → reviser ... → after_model → final event. |
| Safety callback blocks designed input | The "exfiltration A" case shows a `[blocked by safety guard]` tool result in the log and the LLM not surfacing the raw exfiltration text in its answer. |
| Eval set runs green on 4/5 cases | `pytest eval/test_eval.py -v` passes ≥ 4 of 5. (1 acceptable flake is the budget — diagnose, don't loosen.) |
| Edit-mark gone | Case 4's response output does not contain `---END-OF-EDIT---` anywhere. |

Place outputs at:

```
Work/M4/
├── auditor/
│   ├── __init__.py
│   ├── agent.py                  ← SequentialAgent root
│   └── sub_agents/
│       ├── critic/agent.py       ← LlmAgent + google_search + render_reference
│       └── reviser/agent.py      ← LlmAgent + remove_end_of_edit_mark
├── plugins_and_callbacks.py      ← LoggingPlugin wiring + safety_search_guard
├── eval/
│   ├── data/
│   │   ├── auditor_evalset.test.json
│   │   └── test_config.json
│   └── test_eval.py
└── M4_notes.md                   ← short reflection (see stretch)
```

## 🌟 Stretch goals

1. **Add a `RubricBasedEvaluator`** alongside the default metrics — rubric criteria: "critic_called_search", "reviser_changed_answer", "citation_has_url". Compare your rubric scores against `FinalResponseMatchV2Evaluator` (metric key `final_response_match_v2`; source: `evaluation/final_response_match_v2.py:130`) over the 5 cases.
2. **Make the safety guard a Plugin** instead of a callback. Subclass `BasePlugin`; override `before_tool_callback`. Notice the difference: now the guard fires for *every* agent in the runner, not just critic. Is that what you want?
3. **Log eval runs to BigQuery.** Wire `BigQueryAgentAnalyticsPlugin` (module 13) and verify each eval run produces rows in your events table. Cross-link to 15_Observability. (Deep import required — not in `plugins/__init__.py __all__`: `from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin`.)
4. **Add a 6th case** that uses `LlmAsJudge` to score "is the revised A more accurate than the original A?" Compare judge stability across `num_runs=5` runs.

## 🤖 Tutor notes

Common pitfalls to watch for:

- **Forgetting `_END_OF_EDIT_MARK` stripping.** Symptom: case 4 fails and user-facing output contains the literal marker. Fix: confirm the callback is wired as `after_model_callback=` on the *reviser*, not the critic.
- **Eval cases too tight → flake.** Especially the "no inaccuracies" case: reviser may rephrase even when nothing was wrong. If case 2 fails 60% of runs, your gold reference is too strict. Either loosen the reference or convert to LlmAsJudge.
- **Trajectory threshold too high.** The safety case will hurt if you set `tool_trajectory_avg_score: 1.0`. 0.8 is the right floor; lower further only if the case is unambiguously valid.
- **`google_search` rate limits / quota.** If the critic hammers the API across `num_runs=3 × 5 cases`, you may hit a quota. Either reduce `num_runs` for the heavy cases or mock `google_search` for eval (use a fake tool with canned results).
- **Plugin vs callback confusion.** Have the student state — out loud — which one fires for *every* agent vs *only* critic. The safety guard is a callback because it's scope-bound to the search-having agent. The logging is a plugin because logs are cross-cutting.
- **Citation rendering misses.** `_render_reference` relies on `grounding_metadata.grounding_chunks` being non-empty. If the model didn't ground, no citation. That's a real product property — case 3 may need explicit "use search" instruction language.

## ❓ Self-check questions

> ❓ **Before coding:**
> 1. Which agent does `_render_reference` go on, and why? (Critic — it's the one with `google_search`, so grounding metadata is on its responses.)
> 2. Which agent gets `_remove_end_of_edit_mark`? (Reviser — only the reviser emits the marker.)
> 3. Where would you put the safety guard if you wanted it to apply to a hypothetical 3rd sub-agent that also searches? (Make it a plugin, not a callback.)

> ❓ **After the auditor runs but before evals:**
> 1. Read your log output and trace one full turn end-to-end. Can you tell, from the log alone, which agent was speaking at any point?
> 2. Trigger the safety guard intentionally. What does the LLM say after it gets `[blocked by safety guard]` back?

> ❓ **After the evals run:**
> 1. Which case has the highest variance across `num_runs`? Why?
> 2. If you swap the reviser to `gemini-2.5-pro`, which scores rise and which fall?
> 3. If your auditor were deployed and one eval case started failing in nightly CI, what's your first debugging move?

---

[← Prev: 14_Evaluation/12_MiniDrill]  [↑ Map](../MAP.md)  [Next: 15_Observability/00_Overview →]
