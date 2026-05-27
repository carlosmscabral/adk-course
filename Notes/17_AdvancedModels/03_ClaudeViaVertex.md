---
module: 17_AdvancedModels
page: 03_ClaudeViaVertex
title: Claude via Vertex AI
estimated_minutes: 20
prereqs: [17_AdvancedModels/02]
concepts: [Claude (Vertex), Anthropic on Vertex, LiteLlm fallback, prompt portability]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/02_GeminiVariants](02_GeminiVariants.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/04_GemmaLocal →](04_GemmaLocal.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 03 Claude

---

## 🧠 Why Claude

Anthropic's Claude models (3.5 Sonnet v2 is the current ADK 2.0 default on Vertex; Opus and Haiku are also available) are strong at:

- Long-form *careful* reasoning (legal, code review, structured analysis).
- Following nuanced multi-paragraph instructions.
- Refusing edge-case requests gracefully (less brittle on guardrails).

They are weaker at:

- Multimodal (Gemini is ahead on image / audio).
- Tool-call latency in some configurations.
- Live / streaming voice (Gemini Live is the right pick).

For an agent that does **deep document review** or **complex code reasoning**, Claude is often a better default than Gemini Pro.

## 🛠 Wiring — preferred path: Vertex Model Garden

Claude is offered as a first-party model in Google Cloud's Vertex Model Garden. Auth is your existing ADC. No separate API key.

```python
import os
from google.adk.agents import Agent
from google.adk.models import Claude  # exported from google.adk.models in ADK 2.0

# Auth picks up project + region from env. Claude on Vertex has region
# restrictions (us-east5 and a handful of others). Set these before import.
os.environ["GOOGLE_CLOUD_PROJECT"] = "my-gcp-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east5"

claude_agent = Agent(
    model=Claude(model="claude-3-5-sonnet-v2@20241022"),  # ADK 2.0 default
    name="code_reviewer",
    instruction="You are a careful code reviewer.",
)
# For complex reasoning runs, swap the model string for "claude-opus-4-..."
# (Opus 4.x is also on Vertex but costs more and is slower).
```

The class is `Claude` (subclass of `AnthropicLlm`) — `ClaudeLlm` is *not* a real name. Constructor args can vary between minor versions; always check `/home/carloscabral/study/adk-python/src/google/adk/models/anthropic_llm.py` for what your installed version exposes.

## 🛠 Wiring — fallback path: LiteLlm

If you prefer vendor-portable code (or want to use a model string the registry doesn't auto-route, like a Bedrock variant):

```python
from google.adk.models.lite_llm import LiteLlm

claude_agent = Agent(
    model=LiteLlm(model="vertex_ai/claude-3-5-sonnet-v2@20241022"),
    name="code_reviewer",
)
```

`LiteLlm` is covered on page 05; it is a universal adapter.

## ⚠️ Gotcha — prompt portability is imperfect

A prompt tuned for Gemini may not score as well on Claude (and vice versa). The model families differ in:

- **System prompt placement** — Claude prefers a top-level `system:` field; Gemini accepts it as the first content.
- **Tool-call syntax** — both support function calling, but the JSON shapes ADK adapts may carry small quirks.
- **Refusal style** — Claude refuses with more elaborate prose; your output parser may need adjustment.

When swapping models, re-run your eval suite (module 14) — *do not assume* parity.

## 🧠 When Claude beats Gemini for a task

Heuristics from production deployments:

| Task | Often-better choice | Why |
|---|---|---|
| Long-form legal/policy synthesis | Claude (Sonnet/Opus) | Holds nuance over many paragraphs. |
| Code review with style commentary | Claude (Sonnet) | More careful, fewer false positives. |
| Multimodal extraction (image → JSON) | Gemini (Flash / Pro) | Multimodal native. |
| Live voice agent | Gemini Live | Only Gemini Live API in ADK today. |
| Cost-sensitive classifier | Gemini Flash-Lite | Smallest, cheapest. |

The honest answer: measure both with an eval set on *your* task.

> 🛠 **Have the student run:** wire the auditor's *critic* sub_agent to Claude (via Vertex or LiteLlm). Re-run the M4 eval set. Did pass-rate change? Did latency? Did cost?

> 🚀 **In Production**
>
> Even with LiteLlm masking the differences, you are *still* coupled to two vendors' availability. Add a **fallback chain**: if Claude returns 429/5xx, retry once on Gemini Flash. The router callback pattern (page 10) is where this lives. See also [[17_AdvancedModels/12_InProduction]] § rate limits.

---

[← Prev: 17_AdvancedModels/02_GeminiVariants](02_GeminiVariants.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/04_GemmaLocal →](04_GemmaLocal.md)
