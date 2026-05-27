---
module: 17_AdvancedModels
page: 11_DissectingSample
title: Dissecting gemma-food-tour-guide
estimated_minutes: 20
prereqs: [17_AdvancedModels/10A]
concepts: [Gemma via AI Studio, MCP toolset, model swap]
icon: 🔬
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/10A_ModelSelectionPatterns](10A_ModelSelectionPatterns.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/12_InProduction →](12_InProduction.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 11 Dissecting Sample

---

## 🔬 What we're reading

`/home/carloscabral/study/adk-samples/python/agents/gemma-food-tour-guide/`

```
gemma-food-tour-guide/
├── README.md
├── requirements.txt
├── .env.example
└── food_tour_app/
    ├── __init__.py
    └── agent.py
```

A two-file agent. The whole point of the sample is to show that **swapping Gemini → Gemma is one line**, while the rest of the agent (MCP toolset, instruction) is unchanged.

## 🔬 Reading order

### 1. `food_tour_app/agent.py`

Open `/home/carloscabral/study/adk-samples/python/agents/gemma-food-tour-guide/food_tour_app/agent.py` — it is 53 lines total.

**Lines 1-8 — imports.**

```python
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
```

`Gemini` is the class; it can host **either** a Gemini model id (`gemini-2.5-flash`) **or** a Gemma model id (`gemma-4-31b-it`) when served via the same API.

**Lines 10-23 — the system instruction.**

Three things to notice:

1. The instruction is *long and detailed*. Gemma benefits more than Gemini from extremely explicit instructions (page 04 § quality cliff).
2. The CRITICAL RULE lines about `place_id` / `lat_lng` exist because **Gemma is more prone to hallucinate identifiers** than Pro. The prompt compensates.
3. Structured guidance ("Follow these 4 rigorous steps") shrinks the model's degrees of freedom — another Gemma-friendly choice.

**Lines 27-43 — the MCP toolset.**

```python
tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MAPS_MCP_URL,
        headers={"X-Goog-Api-Key": maps_api_key},
    )
)
```

This is **completely model-agnostic**. The Google Maps MCP server doesn't know or care that the consumer is Gemma. That's the value of MCP (see module 08).

**Lines 47-52 — the agent.**

```python
root_agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),   # ← THE line
    name='food_tour_agent',
    instruction=system_instruction,
    tools=[maps_toolset]
)
```

One line. Swap `model="gemini-2.5-flash"` to `model="gemma-4-31b-it"` and you have a Gemma agent. Everything else — instruction, tools, callbacks if any — is identical.

### 2. `README.md`

Open the README. Notice the *"Implementation notes"* section at the bottom — they explicitly call out the prompt techniques used to *reduce hallucinations* for Gemma:

- Rely only on exact `place_id` or `lat_lng` returned by tools.
- Avoid inventing addresses.

This is the **production lesson** of the sample: when you go to a smaller / open-weights model, **your prompt earns more of its keep**. Document this in your codebase.

### 3. `.env.example`

```
MAPS_API_KEY=
GEMINI_API_KEY=
```

`GEMINI_API_KEY` is the AI Studio key — used by the `Gemini` class to route to AI Studio's hosted Gemma endpoint. If you wanted to use vLLM/Ollama instead, you would swap to `LiteLlm` (page 05) and remove the API key.

## 🧠 Lessons to extract

1. **Model swap is one line.** When ADK abstractions are clean, this is what happens.
2. **Prompt compensates for model.** Smaller model → more explicit, structured prompt.
3. **Tools are model-agnostic.** Especially via MCP. Build tools once, attach to any model.
4. **AI Studio is the easiest on-ramp.** For real on-prem you would self-host vLLM/Ollama (page 04 path B).

## 🛠 Exercise

Have the student fork the sample, change one line to `Gemini(model="gemini-2.5-flash")`, and re-run. Is the food tour *better*? Worse? The point: the model is a knob; quality is measurable; defaults should be defensible.

> 🤖 **Tutor:** ask the student why the agent uses `gemma-4-31b-it` rather than the smaller 9B variant. *(Quality cliff — at the 31B size the model is competitive with Flash on tool calling. Below that, you start losing reliability.)*

---

[← Prev: 17_AdvancedModels/10A_ModelSelectionPatterns](10A_ModelSelectionPatterns.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/12_InProduction →](12_InProduction.md)
