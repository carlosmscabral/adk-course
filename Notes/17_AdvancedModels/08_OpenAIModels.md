---
module: 17_AdvancedModels
page: 08_OpenAIModels
title: OpenAI models in ADK
estimated_minutes: 15
prereqs: [17_AdvancedModels/07]
concepts: [OpenAILlm, GPT-4o, GPT-5, o1, JSON mode, tool calling]
icon: 🌐
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/07_LiteLlm](07_LiteLlm.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/09_ApigeeLlm →](09_ApigeeLlm.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 08 OpenAI

---

## 🌐 Two paths

ADK 2.0 lets you use OpenAI models two ways:

### Path A — `OpenAILlm` (if exposed)

Set `OPENAI_API_KEY` in env first — `OpenAILlm` doesn't accept it as a constructor kwarg. The class declares only `model` and `max_tokens` (`adk-python/src/google/adk/labs/openai/_openai_llm.py:349-350`); the underlying `AsyncOpenAI()` reads the key from env.

```python
from google.adk.models import OpenAILlm  # lazy re-export; canonical home is google.adk.labs.openai

agent = LlmAgent(
    model=OpenAILlm(model="gpt-4o"),
    name="researcher",
)
```

When present, `OpenAILlm` is a *first-class* adapter: it speaks OpenAI's API directly and may expose features (system prompt placement, JSON mode flags) more cleanly than the generic LiteLlm path.

### Path B — `LiteLlm` (always available)

```python
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o"),
    name="researcher",
)
```

This always works. Use it if `OpenAILlm` is not in your ADK version, or if you want one code shape across all providers.

Check `/home/carloscabral/study/adk-python/src/google/adk/models/__init__.py` to see which is exported in your install.

## 🧠 When to reach for OpenAI

The honest landscape today:

| Need | OpenAI strength |
|---|---|
| Strict JSON mode | `response_format={"type": "json_object"}` is solid. |
| Tool-call parity | Wide ecosystem familiarity; many libraries assume the OpenAI shape. |
| GPT-5 / o-series reasoning | When a workload needs the latest frontier reasoning model and you have an OpenAI relationship. |
| Vendor diversification | Hedge against single-vendor outage. |
| Embeddings (`text-embedding-3-*`) | Often cheapest per-token for RAG (see [[10A_EmbeddingsVectorSearch/00_Overview]]). |

When you should *not* reach for OpenAI:

- You need Live voice — Gemini Live API is the only ADK-native path.
- You need multimodal-native — Gemini is ahead.
- You need data residency in GCP — use Gemini or Gemma.

## ⚠️ Gotcha — the OpenAI tool-call shape

OpenAI returns tool calls as `tool_calls: [{id, function: {name, arguments}}]`. ADK adapts this internally, but if you have a custom `after_model_callback` reading the raw response, you may see provider-specific structures. Always go through `llm_response.content.parts` and `llm_response.tool_calls` (ADK's normalized fields) instead of raw provider JSON.

## 🛠 Mixing: GPT-4o for the heavy step, Flash for the rest

A common production split:

```python
researcher = LlmAgent(model=LiteLlm(model="openai/gpt-4o-mini"),
                     name="researcher", tools=[google_search])

writer = LlmAgent(model="gemini-2.5-flash",
                 name="writer")

root = LlmAgent(model="gemini-2.5-flash-lite",
               name="router",
               sub_agents=[researcher, writer])
```

Why: GPT-4o-mini has excellent web-search-tool-using behavior; Gemini Flash writes well; Flash-Lite is a cheap router. Cost is dominated by the *router* (cheapest model, called every turn), not the workers.

> 🛠 **Have the student run:** pick the M4 auditor. Swap *only* the critic to `LiteLlm(model="openai/gpt-4o-mini")`. Confirm: events show two different model authors in the trace (one OpenAI, one Gemini).

> 🚀 **In Production**
>
> OpenAI rate limits hit independently of your Google quotas. A single-vendor failure shouldn't take you down; a router with a *fallback* chain (page 03) is the cheapest insurance. See [[17_AdvancedModels/12_InProduction]] § rate limits.

---

[← Prev: 17_AdvancedModels/07_LiteLlm](07_LiteLlm.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/09_ApigeeLlm →](09_ApigeeLlm.md)
