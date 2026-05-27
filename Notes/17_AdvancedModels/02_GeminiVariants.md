---
module: 17_AdvancedModels
page: 02_GeminiVariants
title: Gemini variants — Flash-Lite, Flash, Pro
estimated_minutes: 15
prereqs: [17_AdvancedModels/01]
concepts: [Gemini Flash-Lite, Gemini Flash, Gemini Pro, cost vs quality, latency]
icon: ⚡
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/01_LLMRegistry](01_LLMRegistry.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/03_ClaudeViaVertex →](03_ClaudeViaVertex.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 02 Gemini Variants

---

## ⚡ The three you actually use

| Model | Strength | When to pick |
|---|---|---|
| **Gemini Flash-Lite** | Fastest, cheapest. Tiny reasoning. | Classifiers, routers, simple extraction, the **judge** in LlmAsAJudge. |
| **Gemini Flash** | Balanced. Most agents use this as default. | Tool-calling agents, drafts, summaries, single-turn Q&A. |
| **Gemini Pro** | Strongest reasoning, larger context, slowest. | Heavy code, multi-step planning, complex synthesis. |

There are more variants (multimodal-specific, audio-tuned, region-pinned) but these three carry 90% of production traffic.

## 🛠 Switching is one line

```python
from google.adk.agents import Agent

cheap = Agent(model="gemini-2.5-flash-lite", name="router", ...)
mid   = Agent(model="gemini-2.5-flash",      name="worker", ...)
heavy = Agent(model="gemini-2.5-pro",        name="planner", ...)
```

The instruction, the tools, the callbacks — all reusable. The model is a knob.

## 🧠 The router-worker pattern

The canonical cost/quality compromise:

```
user prompt ──► [router: Flash-Lite] ──classifies──► one of:
                                                      ├─ [worker: Flash]  (simple)
                                                      └─ [worker: Pro]    (hard)
```

The router runs on every request (cheap). The expensive Pro only runs when needed. Net result: ~10× cost savings vs always-Pro, ~2× quality vs always-Flash.

See `/home/carloscabral/study/adk-samples/python/agents/policy-as-code/policy_as_code_agent/config.py` — they expose `GEMINI_MODEL_FLASH` and `GEMINI_MODEL_PRO` and pick per-task.

## 🧠 The "cost matrix" mental model

Don't optimize for cost-per-token. Optimize for cost-per-resolved-task.

A Pro that solves it in 1 turn is often cheaper than a Flash that fumbles for 5 turns. Measure with your eval suite (module 14).

## ⚠️ Gotcha — context window does not equal *good with long context*

Gemini Pro has a 1M+ token context. That does **not** mean you should stuff 800k tokens into a prompt:

- Latency scales with input length.
- Quality degrades past ~200k for most tasks (needle-in-haystack performance drops).
- Cost scales linearly with input.

Use RAG (module 10B) to find the relevant 5k tokens instead.

> 🛠 **Have the student run:** the M4 auditor with `gemini-2.5-flash-lite` vs `gemini-2.5-flash` vs `gemini-2.5-pro`. Compare eval scores from module 14. Which gives the best score-per-dollar?

> 🚀 **In Production**
>
> Pin the version. For the 2.5+ family the **bare name** (`gemini-2.5-flash`) is itself the stable pinned alias; dated previews use the `gemini-2.5-flash-preview-MM-YYYY` form. The `-001 / -002` suffix convention belonged to 1.5 / 2.0 — don't graft it onto 2.5 names. Schedule a quarterly *model bump review* where you re-run your evals against the next family (2.5 → 3.0, etc.) and decide whether to promote.

---

[← Prev: 17_AdvancedModels/01_LLMRegistry](01_LLMRegistry.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/03_ClaudeViaVertex →](03_ClaudeViaVertex.md)
