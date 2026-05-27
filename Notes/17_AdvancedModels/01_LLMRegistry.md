---
module: 17_AdvancedModels
page: 01_LLMRegistry
title: LLMRegistry — how ADK resolves a model
estimated_minutes: 15
prereqs: [17_AdvancedModels/00]
concepts: [LLMRegistry, BaseLlm, model resolution, registration]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/02_GeminiVariants →](02_GeminiVariants.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 01 LLMRegistry

---

## 🧠 What it is

Every ADK model — `Gemini`, `Claude`, `LiteLlm`, `ApigeeLlm`, your own — registers itself with a central directory called `LLMRegistry`. The registry is what makes this work:

```python
from google.adk.agents import Agent

agent = Agent(model="gemini-2.5-flash", name="...", ...)
```

You pass a *string*; the registry maps it to a concrete `BaseLlm` instance. No class import needed for the common case.

You can also pass an instance directly:

```python
from google.adk.models import Gemini
agent = Agent(model=Gemini(model="gemini-2.5-flash"), ...)
```

Both forms are equivalent. The string form is more ergonomic; the instance form lets you tune parameters (temperature, safety settings, region).

## 🧠 The resolution path

```
"gemini-2.5-flash"            "claude-3-5-sonnet-v2@20241022"          "ollama/llama3"
        │                                  │                                    │
        ▼                                  ▼                                    ▼
  ┌───────────┐                     ┌────────────┐                       ┌────────────┐
  │ LLMRegistry │ ──── lookup ────► │  Gemini    │      LLMRegistry ───► │  LiteLlm   │
  │             │                   │  class     │                       │  (any prov)│
  └───────────┘                     └────────────┘                       └────────────┘
```

The registry uses pattern matching (often a prefix) to route a model string to the right class. `gemini-*` → `Gemini`; `claude-3-*` / `claude-*-4*` (on Vertex) → `Claude`; provider-prefixed strings → `LiteLlm`.

## 🛠 Discovery

```python
from google.adk.models import LLMRegistry
LLMRegistry.list_models()  # or similar — varies by minor version
```

Check the framework source at `/home/carloscabral/study/adk-python/src/google/adk/models/registry.py` for the exact API in your installed version. The point is: the registry is *introspectable*. You can list what is wired in, and you can register new models.

## 🛠 Registering a custom model

```python
from google.adk.models import BaseLlm, LLMRegistry

class MyCustomLlm(BaseLlm):
    async def generate_content_async(self, llm_request):
        # call your backend, return an LlmResponse
        ...

LLMRegistry.register("mycorp/internal-v1", MyCustomLlm)

# Now anywhere in your code:
agent = Agent(model="mycorp/internal-v1", ...)
```

The seven canonical classes (Gemini, Claude, LiteLlm, OpenAILlm, ApigeeLlm, Gemma, Gemma3Ollama) self-register at import time via the lazy-provider table in `google/adk/models/__init__.py`. Your own `BaseLlm` subclass needs `LLMRegistry.register(...)` once.

## ⚠️ Gotcha — model string typos fail late

```python
agent = Agent(model="gemin-2.5-flash", ...)  # typo: missing 'i'
```

You will get an error when the *runner* first calls the model, not when you build the agent. In CI, wire a `make sure all models resolve` test that constructs the agent and calls `agent.model` to force resolution at import time.

> 🛠 **Have the student run:** import their M4 auditor's `root_agent`, print `type(agent.model)`. Confirm it is `Gemini`. Then change the model string to something nonsensical and rerun — see *when* the error pops.

> 🚀 **In Production**
>
> Pin your model versions explicitly (`gemini-2.5-flash-002` not `gemini-2.5-flash`). The unqualified alias drifts as the provider rolls out new revisions, and your prompts may regress overnight. See [[17_AdvancedModels/12_InProduction]].

---

[← Prev: 17_AdvancedModels/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/02_GeminiVariants →](02_GeminiVariants.md)
