---
module: 17_AdvancedModels
page: 07_LiteLlm
title: LiteLlm — the universal adapter
estimated_minutes: 15
prereqs: [17_AdvancedModels/06]
concepts: [LiteLlm, multi-provider, OpenAI, Anthropic, Mistral, Ollama, vLLM]
icon: 🔌
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/06_PlanReActPlanner](06_PlanReActPlanner.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/08_OpenAIModels →](08_OpenAIModels.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 07 LiteLlm

---

## 🔌 What it is

`LiteLlm` is the polyglot adapter in ADK. It wraps the [LiteLLM](https://docs.litellm.ai/) library, which speaks the API dialects of **100+ providers**: OpenAI, Anthropic, Mistral, Cohere, Bedrock, Azure OpenAI, Vertex, Ollama, vLLM, Hugging Face TGI, …

One ADK import:

```python
from google.adk.models.lite_llm import LiteLlm
```

One pattern, every provider.

## 🛠 The model-string convention

LiteLLM uses a `provider/model_id` prefix:

```python
LiteLlm(model="openai/gpt-4o")
LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
LiteLlm(model="vertex_ai/claude-3-5-sonnet-v2@20241022")
LiteLlm(model="mistral/mistral-large-latest")
LiteLlm(model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0")
LiteLlm(model="ollama/llama3")
LiteLlm(model="hosted_vllm/gemma-2-9b-it", api_base="http://localhost:8000/v1")
```

The full list lives in LiteLLM's docs. Pattern: pick provider + model id + auth env vars.

## 🛠 Auth — env vars per provider

LiteLLM reads provider-specific env vars:

| Provider | Env var |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic (direct) | `ANTHROPIC_API_KEY` |
| Vertex (Claude via GCP) | ADC + `GOOGLE_CLOUD_PROJECT` |
| Mistral | `MISTRAL_API_KEY` |
| Ollama | none (local URL) |

Set them via `.env` (dev) or Secret Manager (prod) — same discipline as page 04 of module 16.

## 🛠 Drop-in example: same agent, three providers

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

def build_agent(model_str: str) -> LlmAgent:
    return LlmAgent(
        model=LiteLlm(model=model_str),
        name="summarizer",
        instruction="Summarize the input in 3 bullets.",
    )

a = build_agent("openai/gpt-4o")
b = build_agent("anthropic/claude-3-5-sonnet-20241022")
c = build_agent("ollama/llama3")
```

Same instruction, same tools, three different model backends. **This is what `LiteLlm` exists for.**

## ⚠️ Gotcha — provider feature gaps

Not every provider supports every ADK feature:

- **Tool calling** — most do; check parity for parallel tool calls.
- **JSON mode / structured outputs** — uneven; OpenAI and Anthropic strong, others patchy.
- **Streaming** — yes, but token-by-token semantics differ.
- **Vision** — multimodal input is provider-specific.

LiteLlm hides the *API* differences; it cannot hide *capability* differences.

> 🧭 **If the student looks stuck** trying to remember which provider supports what: send them to LiteLLM's `providers/` matrix. Same shape as the model_matrix.txt figure from this module, but provider-major.

> 🛠 **Have the student run:** swap the M4 critic to `LiteLlm(model="openai/gpt-4o-mini")` (if they have an OpenAI key). Confirm the eval suite still runs. If it doesn't — what feature gap caused the failure?

> 🚀 **In Production**
>
> `LiteLlm` is great for *vendor optionality*, less great for *vendor independence*. Each provider has rate limits, billing, status pages. Track them all if you depend on them all. See [[17_AdvancedModels/12_InProduction]] § rate limits and lock-in.

---

[← Prev: 17_AdvancedModels/06_PlanReActPlanner](06_PlanReActPlanner.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/08_OpenAIModels →](08_OpenAIModels.md)
