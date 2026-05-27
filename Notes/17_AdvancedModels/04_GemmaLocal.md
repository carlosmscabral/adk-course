---
module: 17_AdvancedModels
page: 04_GemmaLocal
title: Gemma — open-weights, local
estimated_minutes: 20
prereqs: [17_AdvancedModels/03]
concepts: [Gemma, open weights, vLLM, Ollama, on-prem, AI Studio]
icon: 🏠
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/03_ClaudeViaVertex](03_ClaudeViaVertex.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/05_PlannersBuiltIn →](05_PlannersBuiltIn.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 04 Gemma Local

---

## 🏠 Why Gemma

Open-weights model family from Google. Three reasons it appears in production:

1. **Data residency / PII.** Patient records, financial data, government workloads. The prompt and response never leave your network.
2. **No per-token cost.** Once the GPU is amortized, inference is free at the margin.
3. **Latency under your control.** No vendor rate limits, no shared queue.

The tradeoffs: weaker than Pro on hard reasoning, you own the GPU, and cold-start matters.

## 🛠 Three deployment paths

| Path | Best for |
|---|---|
| **Google AI Studio** | Trying it out via API key (cloud-hosted Gemma). Used by the sample. |
| **vLLM** | Self-hosted, high-throughput serving on your GPU. |
| **Ollama** | Self-hosted, single-developer use; great for laptop dev. |

### Path A — Google AI Studio (cloud, easy)

```python
from google.adk.agents import LlmAgent
from google.adk.models import Gemini  # Gemma served through the Gemini API on AI Studio

agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),
    name="food_tour_agent",
    instruction="...",
)
```

This is exactly what `gemma-food-tour-guide/` does. See `/home/carloscabral/study/adk-samples/python/agents/gemma-food-tour-guide/food_tour_app/agent.py` line 48 — one line to switch a Gemini agent to Gemma.

### Path B — vLLM / Ollama (local)

Run vLLM:

```bash
vllm serve google/gemma-2-9b-it --port 8000
```

Then point LiteLlm at it (covered on page 05):

```python
from google.adk.models.lite_llm import LiteLlm
agent = LlmAgent(model=LiteLlm(model="hosted_vllm/gemma-2-9b-it",
                               api_base="http://localhost:8000/v1"), ...)
```

Or Ollama:

```bash
ollama pull gemma2:9b
```

```python
agent = LlmAgent(model=LiteLlm(model="ollama/gemma2:9b"), ...)
```

## 🧠 Latency profile

| Hop | Cloud Gemini | Gemma on vLLM (warm) | Gemma on vLLM (cold) |
|---|---|---|---|
| First token | 200-600ms | 50-200ms | 5-30s (model load) |
| Per token | ~30ms | ~10-50ms | n/a |

Steady-state Gemma can be *faster* than cloud Gemini for short replies because there is no internet hop. **Cold-start kills the impression** — plan to keep at least one worker warm.

## 🛠 Pattern: warmup ping

```python
async def warm_pool():
    while True:
        await runner.run_async(user_id="warmup", new_message=tiny_prompt)
        await asyncio.sleep(60)
```

A tiny periodic prompt keeps the model loaded in GPU memory and the JIT caches warm. Cheap insurance.

## ⚠️ Gotcha — Gemma's quality cliff

Gemma 2B / 9B can fail at complex tool-calling that Flash handles easily. If you choose Gemma:

- Keep prompts *short*.
- Use Pydantic-shaped outputs (structured outputs make Gemma feel smarter).
- Pre-test against your eval suite — don't assume capability.

> 🛠 **Have the student run:** swap one sub_agent of the M4 auditor to `gemma-4-31b-it` via AI Studio (path A — easiest). Run the eval set. Compare scores to Gemini Flash. The student will get a data-driven feel for the quality tradeoff.

> 🚀 **In Production**
>
> Capacity planning matters. A single A100 serves ~10-30 concurrent Gemma users on vLLM (varies with prompt length). Forecast traffic; over-provision modestly; auto-scale on queue depth, not GPU utilization. See [[17_AdvancedModels/12_InProduction]] § cold start.

---

[← Prev: 17_AdvancedModels/03_ClaudeViaVertex](03_ClaudeViaVertex.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/05_PlannersBuiltIn →](05_PlannersBuiltIn.md)
