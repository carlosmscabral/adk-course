---
module: 04_SessionsState
page: 06_ContextCompaction
title: Context compaction — summarize old turns to fit the window
estimated_minutes: 20
prereqs: [04_SessionsState/05]
concepts: [ContextCompactionConfig, LlmEventSummarizer, window-management, summarization]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/05_ContextCaching](05_ContextCaching.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/07_SessionRewind →](07_SessionRewind.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 06 Context Compaction

# 🚀 Context compaction (NEW in 2.0)

Caching saves cost; **compaction saves the window**. A conversation that runs 200 turns will eventually overflow the model's context window. ADK 2.0 added automatic compaction: every N events, summarize the older ones and replace them with the summary.

## 🧠 The config

```python
# Work/06_compaction.py — run with: uv run python Work/06_compaction.py
from google.adk.agents import LlmAgent
from google.adk.agents.context_compaction_config import ContextCompactionConfig
from google.adk.agents.llm_event_summarizer import LlmEventSummarizer
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio


summarizer = LlmEventSummarizer(
    model="gemini-2.5-flash",
    instruction=(
        "Summarize this slice of conversation into 3 bullet points. "
        "Preserve any user-stated facts (names, preferences, decisions)."
    ),
)


agent = LlmAgent(
    name="long_running",
    model="gemini-2.5-flash",
    instruction="Be helpful.",
    context_compaction_config=ContextCompactionConfig(
        compaction_interval=20,    # compact every 20 events
        keep_recent_events=10,     # always keep last 10 verbatim
        summarizer=summarizer,
    ),
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="compaction_demo")
    sess = await runner.session_service.create_session(
        app_name="compaction_demo", user_id="u1",
    )
    for i in range(25):
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
    print(f"events on session: {len(refreshed.events)}  (compacted ≈ 20 → 1 summary)")


asyncio.run(main())
```

```
$ uv run python Work/06_compaction.py
events on session: 15  (compacted ≈ 20 → 1 summary)
```

After 25 turns, the session holds the summary event plus the most recent 10 turns plus a few framing events — instead of 50+ raw events.

## 🧠 How compaction is triggered

ADK checks the trigger after each turn:

* event count since last compaction ≥ `compaction_interval`, **and**
* the model is about to receive more than `keep_recent_events` worth of old content.

When both hold, the runner:

1. Slices `events[: -keep_recent_events]`.
2. Hands them to the `summarizer.summarize(...)` call.
3. Emits a synthetic `compaction` event whose `content` is the summary.
4. Marks the original events as compacted; the LLM rebuild step ignores them and reads only the summary + recent tail.

The original events stay on disk (rewind in page 07 needs them) — they are just hidden from the next LLM build.

## ⚠️ The compaction tradeoff

* **Win:** finite cost-per-turn even as conversations grow unbounded.
* **Loss:** the LLM no longer sees verbatim phrasing of old turns; it sees the summary. **Facts the summarizer drops are gone** from the live context (you can still find them on disk).

Mitigation: write a summarizer prompt that **explicitly preserves** "names, decisions, IDs, file paths, and any value the user emphasized." Treat the summarizer prompt as production-critical text.

## 🧠 Compaction vs. caching

| | Cache | Compaction |
|---|---|---|
| Goal | Cheaper turns | Bounded window |
| Mechanism | Server-side prefix reuse | Replace old events with a summary |
| Cost effect | Saves input tokens | Saves input tokens AND prevents overflow |
| Lossy? | No | Yes (summary ≠ verbatim) |
| Use together? | Yes — they compose | Yes — they compose |

## ❓ Quiz

> ❓ **Ask the student:** you compact at every 20 events with a 10-event tail. The user mentioned a deadline in event 3. After turn 25, does the LLM still see "the deadline is March 15"?
> *(Expected: only if your summarizer prompt preserved it. The raw event was compacted away after turn 20. This is why the summarizer prompt matters — instruct it to keep dates, names, decisions verbatim.)*

> 🛠 **Have the student run:** the script above, then print `refreshed.events[0].content.parts[0].text` to see the summary the model now reads in place of the first 20 turns.

> **🚀 In Production**
>
> Compaction's summarizer is **another LLM call** — it costs money and latency. For chatty production agents the rule is: `compaction_interval` ≥ 20 AND `keep_recent_events` ≥ 10. Lower numbers mean you summarize constantly. Track summarizer cost as its own line item in [[15_Observability/00_Overview]]; it can rival the agent's own LLM cost on long sessions.

---

[← Prev: 04_SessionsState/05_ContextCaching](05_ContextCaching.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/07_SessionRewind →](07_SessionRewind.md)
