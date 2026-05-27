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

There is **no `LLMRegistry.list_models()`** API. The registry is a private regex→class dict (`_llm_registry_dict` in `google/adk/models/registry.py`). The public surface is three static methods: `register(llm_cls)`, `resolve(model)`, `new_llm(model)`.

For a one-shot introspection in a REPL, call `resolve` against a candidate string and inspect the returned class:

```python
from google.adk.models import LLMRegistry
LLMRegistry.resolve("gemini-2.5-flash")        # <class 'google.adk.models.google_llm.Gemini'>
LLMRegistry.resolve("claude-3-5-sonnet-v2@20241022")  # <class 'google.adk.models.anthropic_llm.Claude'>
```

The canonical list of regex patterns and their classes lives in the lazy-provider table at the top of `google/adk/models/__init__.py` — that is the documentation. Read it directly when you need to know what is wired in.

## 🛠 Registering a custom model

A `BaseLlm` subclass advertises which model strings it handles via the classmethod `supported_models() -> list[str]`. Each entry is a **regex** matched against the full model string. `LLMRegistry.register(llm_cls)` reads `supported_models()` and registers one entry per regex (see `registry.py:99-107`).

```python
from google.adk.models import BaseLlm, LLMRegistry

class MyCustomLlm(BaseLlm):
    @classmethod
    def supported_models(cls) -> list[str]:
        return [r"mycorp/internal-v\d+"]   # regex, not literal

    async def generate_content_async(self, llm_request, stream=False):
        # call your backend, yield LlmResponse objects
        ...

LLMRegistry.register(MyCustomLlm)             # single arg — the class

# Now anywhere in your code:
agent = Agent(model="mycorp/internal-v1", ...)
```

⚠️ **Common mistake**: writing `LLMRegistry.register("mycorp/internal-v1", MyCustomLlm)` — the two-arg form does not exist. The class declares its own supported regexes via `supported_models()`.

The canonical classes (Gemini, Claude, LiteLlm, ApigeeLlm, Gemma) self-register at import time via the lazy-provider table in `google/adk/models/__init__.py`. Your own `BaseLlm` subclass needs `LLMRegistry.register(MyCustomLlm)` once.

## ⚠️ Gotcha — model string typos fail late

```python
agent = Agent(model="gemin-2.5-flash", ...)  # typo: missing 'i'
```

You will get an error when the *runner* first calls the model, not when you build the agent. In CI, wire a `make sure all models resolve` test that constructs the agent and calls `agent.model` to force resolution at import time.

> 🛠 **Have the student run:** import their M4 auditor's `root_agent`, print `type(agent.model)`. Confirm it is `Gemini`. Then change the model string to something nonsensical and rerun — see *when* the error pops.

> 🚀 **In Production**
>
> Pin your model versions explicitly. For the 2.5+ family the bare name (`gemini-2.5-flash`) **is** the stable pinned alias; dated previews use the `gemini-2.5-flash-preview-MM-YYYY` form. The older `-001/-002` suffix convention applied to 1.5 / 2.0 only — don't paste it onto 2.5 names. Either way, when you bump (e.g., 2.5 → 3.0), re-run your evals before promoting. See [[17_AdvancedModels/12_InProduction]].

---

[← Prev: 17_AdvancedModels/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/02_GeminiVariants →](02_GeminiVariants.md)
