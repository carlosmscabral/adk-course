---
module: 1A_AppAndRunner
page: 06_WiringContextCompaction
title: Wiring `events_compaction_config` on the App
estimated_minutes: 15
prereqs: [1A_AppAndRunner/05]
concepts: [EventsCompactionConfig, summarization, context-window, BaseEventsSummarizer]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 05_WiringContextCache](05_WiringContextCache.md)  [↑ Map](../../MAP.md)  [Next: 07_RunnerInsideTheApp →](07_RunnerInsideTheApp.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 06 Wiring Context Compaction

# 🛠 Wiring `events_compaction_config` on the App

Long conversations exceed the context window. **Context compaction** is the 2.0 feature that periodically replaces a range of session events with an LLM-generated summary, freeing tokens without losing the gist. Like cache and resumability, you wire it at the App level.

> 🤖 **Tutor:** this page covers *wiring* only. The full mechanism (picking a summarizer, tuning `compaction_interval` and `overlap_size`, token-threshold vs invocation-threshold triggers) is in [Module 04 § 06 Context Compaction](../04_SessionsState/06_ContextCompaction.md) (the expanded sub-page).

## 🧠 What it does

After every N user-initiated invocations (or when prompt tokens exceed a threshold), ADK:

1. Selects the contiguous range of events to compact.
2. Calls a `BaseEventsSummarizer` (default: an LLM-driven summarizer) on them.
3. Replaces the range with a single summary event.
4. Keeps an `overlap_size` window of recent events un-compacted, so the next turn still has continuity.

The session shrinks. Future LLM calls see the summary instead of the raw history.

## 🛠 The wiring

```python
# Work/1A_compaction_wiring.py
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps._configs import EventsCompactionConfig

agent = LlmAgent(
    name="chatty",
    model="gemini-2.5-flash",
    instruction="You are a chatty assistant who explains things in detail.",
)

app = App(
    name="compacted_app",
    root_agent=agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,    # compact after every 20 user-initiated invocations
        overlap_size=4,            # keep the last 4 invocations un-compacted
        # Optional: token-based triggers in addition to invocation-based.
        token_threshold=80_000,    # if prompt tokens ≥ this, compact early
        event_retention_size=10,   # ...but keep the last 10 raw events when we do
        # summarizer=None → default LLM summarizer (uses the same model as the agent)
    ),
)
```

The Runner reads this off the App via the standard wiring path you saw on the previous two pages.

## 🧠 Schema crib sheet

| Field | What it controls |
|---|---|
| `compaction_interval` | After every N user-initiated invocations whose events are fully written, run compaction. The primary trigger. |
| `overlap_size` | When compacting events 1..K, keep the last `overlap_size` invocations *un-compacted* — the summary covers `1..K-overlap_size`. Prevents losing recent context. |
| `token_threshold` (optional) | A second, token-based trigger. If the prompt token count of the most recent invocation meets this, trigger compaction early. Useful for long single turns (one big RAG dump). |
| `event_retention_size` (optional) | Paired with `token_threshold` — when a token-based compaction fires, keep the last N raw events un-compacted. Pydantic will reject setting one without the other. |
| `summarizer` | A `BaseEventsSummarizer` instance. None = default LLM summarizer (calls the agent's model with a "summarize these events" prompt). |

## 🧠 Compaction vs caching vs memory — three different things

The three are often confused because they all "deal with context":

| Feature | What it does | When it kicks in |
|---|---|---|
| `context_cache_config` | Caches the **static prefix** of the prompt server-side (Gemini cache). Costs less per token on cached portion. | Every LLM call where the prefix ≥ `min_tokens`. |
| `events_compaction_config` | Replaces a **range of historical events** in the Session with an LLM summary. Shrinks history. | After every N invocations, or when token count exceeds threshold. |
| `MemoryService` (Module 11) | Extracts **facts** from a session, stores them in a separate memory store, and lets future *different* sessions retrieve them. | When you explicitly call `memory_service.add_session_to_memory(...)` or via a callback. |

Compaction shrinks **this session's history**. Memory carries facts **across sessions**. Cache shrinks **per-call cost**. You will often use all three together; they do not overlap.

> ❓ **Ask the student:** "I have a 200-turn conversation that has hit the context window. Should I reach for compaction or memory?"
> *(Expected: compaction first — it is the right tool for shrinking *this* conversation's history. Memory is for "this user told me last week they prefer dark mode" — facts that should outlive the session. The two compose: compact the running session, and have a `memory_service` snapshotting interesting bits to long-term storage.)*

## 🚀 In Production

> **🚀 In Production**
>
> Each compaction is an extra LLM call against the summarizer. The cost compounds for chatty agents: a 1000-turn day with `compaction_interval=20` is 50 extra LLM calls just for compaction. Two mitigations: (1) Use a cheap model for the summarizer — wire it explicitly with
> ```python
> from google.adk.models import Gemini
> from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
> summarizer = LlmEventSummarizer(llm=Gemini(model="gemini-2.5-flash-lite"))
> ```
> even if your main agent runs `gemini-2.5-pro`. Note the signature: `LlmEventSummarizer(llm: BaseLlm, prompt_template: Optional[str] = None)` — it takes an `llm=` BaseLlm instance, NOT a `model=` string. (2) Tune `compaction_interval` upward for low-stakes chat; downward only when you have evidence of context-window hits. The default ADK ships with may not match your workload — measure before pinning a number.

> 🛠 **Have the student do:** without running anything, talk through "if `compaction_interval=20` and `overlap_size=4`, after 25 invocations how many compactions have run and how many raw invocations are still in the session?"
> *(Answer: one compaction fired at invocation 20, summarizing invocations 1..16; invocations 17..25 are still raw (9 raw events). The next compaction fires at invocation 40.)*

---

[← Prev: 05_WiringContextCache](05_WiringContextCache.md)  [↑ Map](../../MAP.md)  [Next: 07_RunnerInsideTheApp →](07_RunnerInsideTheApp.md)
