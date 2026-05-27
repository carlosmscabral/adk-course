---
module: 04_SessionsState
page: 06_ContextCompaction
title: Context compaction — summarize old turns to fit the window
estimated_minutes: 20
prereqs: [04_SessionsState/05]
concepts: [EventsCompactionConfig, LlmEventSummarizer, window-management, summarization]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/05_ContextCaching](05_ContextCaching.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/07_SessionRewind →](07_SessionRewind.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 06 Context Compaction

# 🚀 Context compaction (NEW in 2.0)

Caching saves cost; **compaction saves the window**. A conversation that runs 200 turns will eventually overflow the model's context window. ADK 2.0 added automatic compaction: every N invocations, summarize the older ones and have the LLM read the summary in place of the raw events.

Like caching, compaction config attaches to the **`App`**, not to an individual `LlmAgent`.

## 🧠 The config

```python
# Work/06_compaction.py — run with: uv run python Work/06_compaction.py
from google.adk.agents import LlmAgent
from google.adk.apps import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio


summarizer = LlmEventSummarizer(
    llm=Gemini(model="gemini-2.5-flash"),
    prompt_template=(
        "Summarize this slice of conversation into 3 bullet points. "
        "Preserve any user-stated facts (names, preferences, decisions).\n\n"
        "{conversation_history}"
    ),
)


agent = LlmAgent(
    name="long_running",
    model="gemini-2.5-flash",
    instruction="Be helpful.",
)

app = App(
    name="compaction_demo",
    root_agent=agent,
    events_compaction_config=EventsCompactionConfig(
        summarizer=summarizer,
        compaction_interval=5,     # every 5 new user invocations, run a compaction
        overlap_size=1,            # carry 1 invocation of overlap into the next window
    ),
)


async def main():
    runner = InMemoryRunner(app=app)
    sess = await runner.session_service.create_session(
        app_name="compaction_demo", user_id="u1",
    )
    for i in range(12):
        async for event in runner.run_async(
            user_id="u1", session_id=sess.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=f"turn {i}: tell me a fact")],
            ),
        ):
            pass
    refreshed = await runner.session_service.get_session(
        app_name="compaction_demo", user_id="u1", session_id=sess.id,
    )
    print(f"events on session: {len(refreshed.events)}  (with synthetic summary events)")


asyncio.run(main())
```

```
$ uv run python Work/06_compaction.py
events on session: 26  (with synthetic summary events)
```

The total event count grows — compaction does **not** delete old events; it appends a new `compaction` event that the LLM-rebuild step uses instead of the raw range.

## 🧠 How compaction is triggered

The runner checks the trigger **after each invocation** (not after every event). With `EventsCompactionConfig`:

* `compaction_interval` — number of *new* user-initiated invocations that, once fully represented in the session's events, trigger a compaction.
* `overlap_size` — number of preceding invocations to include from the end of the last compacted range, so consecutive summaries overlap and don't lose continuity.
* `token_threshold` *(optional)* — if the latest observed prompt token count crosses this, run a token-based post-invocation compaction.
* `event_retention_size` *(required when `token_threshold` is set)* — for token-based compaction, keep the last N raw events un-compacted.

When the trigger fires, the runner:

1. Selects the sliding window of events to compact.
2. Calls `summarizer.maybe_summarize_events(events=...)`.
3. Appends a synthetic event whose `actions.compaction` carries `start_timestamp`, `end_timestamp`, and `compacted_content`.
4. On the next LLM build, the runner reads the summary in place of the covered range.

The original events stay on disk (rewind in page 07 walks `session.events` and needs them) — they are just hidden from the next LLM build.

## ⚠️ The compaction tradeoff

* **Win:** finite cost-per-turn even as conversations grow unbounded.
* **Loss:** the LLM no longer sees verbatim phrasing of old turns; it sees the summary. **Facts the summarizer drops are gone** from the live context (you can still find them on disk).

Mitigation: write a summarizer prompt that **explicitly preserves** "names, decisions, IDs, file paths, and any value the user emphasized." Treat the summarizer prompt as production-critical text.

## 🧠 Inspecting the summary

After the script above runs, look for the synthetic event:

```python
for ev in refreshed.events:
    if ev.actions and ev.actions.compaction:
        print(ev.actions.compaction.compacted_content.parts[0].text[:200])
```

That printed text is what the LLM will see in place of the covered invocation range on the next turn.

## 🧠 Compaction vs. caching

| | Cache | Compaction |
|---|---|---|
| Goal | Cheaper turns | Bounded window |
| Mechanism | Server-side prefix reuse | Replace old events with a summary |
| Cost effect | Saves input tokens | Saves input tokens AND prevents overflow |
| Lossy? | No | Yes (summary ≠ verbatim) |
| Use together? | Yes — they compose | Yes — they compose |

## ❓ Quiz

> ❓ **Ask the student:** you set `compaction_interval=5, overlap_size=1`. The user mentioned a deadline on invocation 2. After invocation 12, does the LLM still see "the deadline is March 15"?
> *(Expected: only if your summarizer prompt preserved it. The raw event sits past the overlap window and is no longer visible to the LLM build. This is why the summarizer prompt matters — instruct it to keep dates, names, decisions verbatim.)*

> 🛠 **Have the student run:** the script above, then iterate `refreshed.events` looking for `ev.actions.compaction` to inspect the summary the model now reads in place of the covered invocation range.

> **🚀 In Production**
>
> Compaction's summarizer is **another LLM call** — it costs money and latency. Push `compaction_interval` higher for chatty agents so you summarize less often, and use `overlap_size` ≥ 1 so consecutive summaries don't lose the connecting thread. If you set `token_threshold`, you must also set `event_retention_size` (the validator rejects setting one without the other). Track summarizer cost as its own line item in [[15_Observability/00_Overview]]; it can rival the agent's own LLM cost on long sessions.

---

[← Prev: 04_SessionsState/05_ContextCaching](05_ContextCaching.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/07_SessionRewind →](07_SessionRewind.md)
