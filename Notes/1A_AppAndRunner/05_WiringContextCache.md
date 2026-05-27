---
module: 1A_AppAndRunner
page: 05_WiringContextCache
title: Wiring `context_cache_config` on the App
estimated_minutes: 15
prereqs: [1A_AppAndRunner/01]
concepts: [ContextCacheConfig, prompt-cache, gemini-cache, cost-reduction]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_WiringResumability](04_WiringResumability.md)  [↑ Map](../../MAP.md)  [Next: 06_WiringContextCompaction →](06_WiringContextCompaction.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 05 Wiring Context Cache

# 🛠 Wiring `context_cache_config` on the App

Context caching is the Gemini API feature where the *static prefix* of your prompt (the system instruction, the tool schemas, any pinned context) is cached server-side. Subsequent requests with the same prefix pay a fraction of the per-token cost on the cached portion. ADK exposes the config at the App level so every agent in the App gets it.

> 🤖 **Tutor:** this page covers *wiring* only — declaring the config on the App. The full mechanism (when caching kicks in, hit-rate observability, cost math, picking `ttl=`) is taught in [Module 04 § 05 Context Caching](../04_SessionsState/05_ContextCaching.md) (the expanded sub-page).

## 🛠 The wiring

```python
# Work/1A_context_cache_wiring.py
from google.adk.agents import LlmAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App

agent = LlmAgent(
    name="long_prefix_agent",
    model="gemini-2.5-flash",
    instruction=("You are an expert in..." + "very long static instruction" * 100),
)

app = App(
    name="cached_app",
    root_agent=agent,
    context_cache_config=ContextCacheConfig(
        # Fields are framework-defined; see the dedicated Module 04 page for
        # the full schema. Common fields: `cache_intervals`, `min_tokens`, `ttl_seconds`.
        min_tokens=2048,           # only cache prefixes ≥ this many tokens
        ttl_seconds=3600,          # keep cached prefix alive for 1 hour
    ),
)
```

The Runner reads `context_cache_config` from the App when it is constructed:

```python
# from adk-python/src/google/adk/runners.py (~line 240)
self.context_cache_config = app.context_cache_config
```

… and uses it on every model call to decide whether to attempt to cache or hit an existing cache key.

## 🧠 Why App-level instead of agent-level

A natural question: "I have ten agents in my multi-agent app. Should each one have its own cache config?" The answer is **no** — and that is why this lives on the App.

| Reason | Detail |
|---|---|
| **The cache backend is shared.** | Gemini cache keys are scoped to (project, region, content-hash). Two agents in the same App talking to the same model can share cache entries if their prefixes overlap. App-level config keeps that uniform. |
| **The config is operational, not per-agent behavior.** | "Cache stuff ≥ 2048 tokens for 1 hour" is a deploy-wide decision, not a per-agent decision. Same shape as the resumability flag. |
| **Future-proof.** | When ADK adds new caching backends (Vertex distributed cache, local LRU), they wire into one place. |

If you genuinely need per-agent caching policy, the escape hatch is to set the cache config on a per-agent wrapper (a `before_model_callback` that mutates the request). The App-level config covers the 95% case.

## 🧠 What the wiring does NOT do

- It does not *force* every call to be a cache hit. The first call with a given prefix is the cache *write* — it pays full price. Subsequent calls hit.
- It does not silently lower your bill if your prompts are short. Caching has a per-cache overhead; ADK only attempts to cache prefixes ≥ `min_tokens`.
- It does not work cross-region. Cache entries are regional. Pin your `GOOGLE_CLOUD_LOCATION` env if you care about hit rate.

> ❓ **Ask the student:** "If my system instruction is 500 tokens long but my user message is always 5000 tokens, will context caching help?"
> *(Expected: only marginally. The cacheable portion is whatever is **stable across requests** — system instruction, tool schemas, pinned context. The variable user message is never cached. If 500 tokens of stable prefix is below your `min_tokens` threshold, no caching happens at all. The win comes when you pin a *large* document into the prefix — RAG context, codebase snapshots, long system prompts.)*

## 🚀 In Production

> **🚀 In Production**
>
> Context caching is silently effective when it works and silently expensive when it doesn't (cache write overhead with no reads). Wire observability **before** turning on `context_cache_config` in prod — see [15 Observability § 04 Metrics](../15_Observability/04_MetricsAndDashboards.md) for the cache-hit-rate metric. If hit rate < 30% you are losing money; either widen the cached prefix or turn caching off for that agent.

> 🛠 **Have the student do:** open [adk.dev/docs/agents/llm-agents#context-caching](https://adk.dev/) (the live docs) and confirm the field names match what you wrote — the schema is the canonical reference and may have evolved past this snapshot.

---

[← Prev: 04_WiringResumability](04_WiringResumability.md)  [↑ Map](../../MAP.md)  [Next: 06_WiringContextCompaction →](06_WiringContextCompaction.md)
