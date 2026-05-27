---
module: 17_AdvancedModels
page: 10A_ModelSelectionPatterns
title: Model selection patterns — tiering, config, fallback, cost-aware swap
estimated_minutes: 30
prereqs: [17_AdvancedModels/10, 07_Callbacks/06]
concepts: [tier-by-task, model from config, fallback callback, cost-aware swap, model A/B in eval]
icon: 🎚
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/10_PerAgentModel](10_PerAgentModel.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/11_DissectingSample →](11_DissectingSample.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 10A Model Selection Patterns

---

## 🎚 Why a dedicated synthesis page

Pages 02 and 10 showed *which* model to pick and *where* to plug it in. This page is the **architecture-level discipline**: how a serious codebase encodes those choices so that a model swap is a config diff, a 429 is a fallback (not a 500), and a model bump is an eval run.

Five patterns, each a tool you reach for in production. None of them are new APIs — they are *compositions* of things you already know.

## 1️⃣ Tier-by-task

Treat models as **tiers**, not names. Three tiers cover 90% of agents:

| Tier | Default model | Used for |
|---|---|---|
| `ROUTER` | `gemini-2.5-flash-lite-002` | classify, dispatch, judge |
| `WORKER` | `gemini-2.5-flash-002` | tool-calling, drafting |
| `REASONER` | `gemini-2.5-pro-002` | planning, code, hard synthesis |

Every `LlmAgent` declares its tier; the tier resolves to a model. When you swap providers (or pin a new version) you change *one mapping*, not ten files.

```python
# Work/17_AdvancedModels/10A_tiers.py
TIERS = {
    "ROUTER":   "gemini-2.5-flash-lite-002",
    "WORKER":   "gemini-2.5-flash-002",
    "REASONER": "gemini-2.5-pro-002",
}
router   = LlmAgent(name="router",   model=TIERS["ROUTER"],   instruction="...")
worker   = LlmAgent(name="worker",   model=TIERS["WORKER"],   instruction="...")
reasoner = LlmAgent(name="reasoner", model=TIERS["REASONER"], instruction="...")
```

This is the *architectural* recap of page 02's table. Page 10 added per-agent mixing; this page makes the mixing **a named contract**.

## 2️⃣ Model from config

Hard-coding `"gemini-2.5-flash"` in `agent.py` is a smell. Read it from env or a `Settings` object so dev / staging / prod can diverge.

```python
# Work/17_AdvancedModels/10A_settings.py
import os
from pydantic_settings import BaseSettings
from google.adk.agents import LlmAgent

class Settings(BaseSettings):
    model_name: str = "gemini-2.5-flash"        # default
    router_model: str = "gemini-2.5-flash-lite" # cheap classifier
    class Config:
        env_prefix = "AGENT_"  # AGENT_MODEL_NAME=...

settings = Settings()

worker = LlmAgent(name="worker", model=settings.model_name, instruction="...")
router = LlmAgent(name="router", model=settings.router_model, instruction="...")
```

Now `AGENT_MODEL_NAME=gemini-2.5-pro-002 uv run python ...` is a model bump *without a code change*. The full discipline (12-factor env, secrets, `.env.example`) lives in [[3A_ProjectStructure/07A_ConfigAndEnvVars]].

## 3️⃣ Fallback on 429 / 5xx — `on_model_error_callback`

When the primary provider rate-limits or burps, you don't want the user to see a 500. Retry on a smaller (or different-vendor) model.

```python
# Work/17_AdvancedModels/10A_fallback.py
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types

FALLBACK = Gemini(model="gemini-2.5-flash-lite-002")

async def on_model_error(callback_context, llm_request, error):
    msg = str(error).lower()
    if "429" not in msg and "resource_exhausted" not in msg:
        return None  # let other errors propagate
    # Re-issue against the cheaper model; ADK accepts an LlmResponse.
    response = await FALLBACK.generate_content_async(llm_request)
    return LlmResponse(content=response.content)

agent = LlmAgent(
    name="resilient",
    model=Gemini(model="gemini-2.5-pro-002"),
    instruction="...",
    on_model_error_callback=on_model_error,
)
```

This is the standard "model fallback" recipe. Pair with structured logging (module 15) so the fallback shows up in your dashboards as a *signal*, not a silent degradation.

## 4️⃣ Cost-aware `before_model_callback` — swap on long input

When a turn pulls in a giant RAG context, your Flash quietly stops being cheap. Detect it and route to the more capable model *for that turn*.

```python
# Work/17_AdvancedModels/10A_costaware.py
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

PRO = Gemini(model="gemini-2.5-pro-002")
LONG_INPUT_TOKENS = 64_000  # threshold

async def before_model(callback_context, llm_request):
    # Rough token count: 1 token ~= 4 chars; good enough for routing decisions.
    approx_tokens = sum(
        len(p.text) for c in (llm_request.contents or [])
        for p in (c.parts or []) if p.text
    ) // 4
    if approx_tokens > LONG_INPUT_TOKENS:
        llm_request.model = "gemini-2.5-pro-002"  # bump for this call only
    return None  # let the (now bumped) request proceed

agent = LlmAgent(
    name="adaptive",
    model="gemini-2.5-flash",
    instruction="...",
    before_model_callback=before_model,
)
```

Inverse pattern works too: detect a *short* trivial turn and downshift to Flash-Lite. Either direction, the rule is the same — **the model is a knob the request can tune**.

## 5️⃣ Model A/B in eval

Don't argue about which model is better. Run the eval set against both.

```python
# Work/17_AdvancedModels/10A_ab_eval.py
import asyncio
from google.adk.evaluation import AgentEvaluator

async def run_against(model_name: str):
    return await AgentEvaluator.evaluate(
        agent_module="my_agent",         # exports root_agent
        eval_dataset_file_path_or_dir="evals/auditor.evalset.json",
        config={"override_model": model_name},  # your agent reads this
    )

async def main():
    flash = await run_against("gemini-2.5-flash-002")
    pro   = await run_against("gemini-2.5-pro-002")
    print(f"flash: pass={flash.pass_rate:.2%}  $/case={flash.cost_per_case:.4f}")
    print(f"pro:   pass={pro.pass_rate:.2%}  $/case={pro.cost_per_case:.4f}")

asyncio.run(main())
```

The numbers settle the argument. Run the matrix (model × pass-rate × p95-latency × cost-per-case) every time you consider bumping. Full eval discipline is in [[14_Evaluation/00_Overview]].

## 🧭 How to combine the five

A mature agent uses **all five**:

```
Settings.model_name  ──┐
                       ▼
   tier table ──► LlmAgent ──┬──► before_model_callback (cost-aware swap)
                             │
                             └──► on_model_error_callback (429 fallback)

   evalset × {flash, pro, …}  ──► quarterly model-bump review
```

Patterns 1-2 are *organisation*. Patterns 3-4 are *runtime resilience*. Pattern 5 is *governance*. None of them are optional in prod.

> 🛠 **Have the student run:** wire the cost-aware callback into their M4 auditor. Force one long input (paste a long doc) and confirm the trace shows `model.name = gemini-2.5-pro-002` for that turn while shorter turns stay on Flash.

> ❓ **Ask the student:** in which pattern does the model **string** change, vs the model **object** change? Why does it matter?
> *(Answer: patterns 2 & 4 mutate `llm_request.model` or `Settings.model_name` — a string swap. Patterns 3 & 5 hold actual `Gemini(...)` / `LiteLlm(...)` instances. Strings work for same-family swaps; objects are needed when the provider differs or you want a pre-configured client with its own auth.)*

For the callback mechanics referenced in patterns 3 & 4, see [[07_Callbacks/06_CallbackRecipeCookbook]] — the cookbook covers caching, rate-limiting, redaction, and the exact `LlmResponse` return contract.

> 🚀 **In Production**
>
> Every model-routing callback is a hidden test surface. A buggy `before_model_callback` that always overrides to Pro will silently 10× your bill before anyone notices. Three guardrails: (a) emit a counter for each routing decision (module 15); (b) add an eval case that asserts the *cheap path* is taken on a trivial input; (c) put a max-cost-per-session circuit breaker in the runner layer. Cross-link [[16_ProductionSecurity/05_GuardrailsCookbook]].

---

[← Prev: 17_AdvancedModels/10_PerAgentModel](10_PerAgentModel.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/11_DissectingSample →](11_DissectingSample.md)
