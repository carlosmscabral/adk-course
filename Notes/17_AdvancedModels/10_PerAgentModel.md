---
module: 17_AdvancedModels
page: 10_PerAgentModel
title: Different models for different sub_agents
estimated_minutes: 20
prereqs: [17_AdvancedModels/09, 05_MultiAgent/03]
concepts: [per-agent model, routing, mixed-model graph, cost/quality split]
icon: 🎭
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/09_ApigeeLlm](09_ApigeeLlm.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/10A_ModelSelectionPatterns →](10A_ModelSelectionPatterns.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 10 Per-Agent Model

---

## 🎭 The pattern

`sub_agents` are independent `LlmAgent` instances. Each has its **own** model. You can mix freely.

```python
from google.adk.agents import LlmAgent
from google.adk.models import Gemini, Claude
from google.adk.models.lite_llm import LiteLlm

router = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite"),  # cheap classifier
    name="router",
)

researcher = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o-mini"),    # good with web tools
    name="researcher",
    tools=[google_search],
)

critic = LlmAgent(
    # GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION (us-east5) must be set in env;
    # Claude.model defaults to claude-3-5-sonnet-v2@20241022 in ADK 2.0.
    model=Claude(model="claude-3-5-sonnet-v2@20241022"),  # careful reasoning
    name="critic",
)

writer = LlmAgent(
    model=Gemini(model="gemini-2.5-flash"),       # fast drafting
    name="writer",
)

root = LlmAgent(
    model=Gemini(model="gemini-2.5-flash"),
    name="root",
    sub_agents=[router, researcher, critic, writer],
)
```

One runner orchestrates them all. Each model call is billed to its own provider; OTel spans (from module 15) carry distinct `model.name` attributes.

## 🎭 Routing by capability

Common shapes:

### A. Triage + worker

```
[Flash-Lite router] ── classifies ──► [Flash worker]  (simple)
                                  └─► [Pro worker]    (complex)
```

The router runs every turn (cheap). The expensive worker runs only when needed.

### B. Specialist pool

```
[router] ─► [code specialist: Claude] | [creative: GPT-4o] | [structured: Flash]
```

Pick by problem domain, not by difficulty.

### C. Cost-aware fallback

```
[try GPT-4o-mini]
       │
   on 429 / 5xx
       ▼
[fallback to Gemini Flash]
```

Implement in a callback or a wrapper `BaseLlm` class. Pair with retry plugin from [[13_Plugins/00_Overview]].

## 🧠 Why mix at all

| Scenario | Mix wins |
|---|---|
| 80% of turns are simple, 20% are hard | Cheap default + expensive escalation. |
| Tool ecosystem favors one model | OpenAI tools + Gemini summarization. |
| Compliance bans one provider for a data class | Route PII-touching turns to on-prem Gemma. |
| Vendor outage risk | Multi-vendor with fallback. |

## 🛠 Code skeleton — mini-drill preview

```python
critic = LlmAgent(model=Gemini(model="gemini-2.5-flash"),
                 name="critic", instruction="Critique the code; be honest.")
reviser = LlmAgent(model=LiteLlm(model="anthropic/claude-3-5-sonnet-20241022"),
                  name="reviser", instruction="Apply the critique; return the new code.")

root = LlmAgent(model=Gemini(model="gemini-2.5-flash-lite"),
               name="root",
               sub_agents=[critic, reviser])

runner = InMemoryRunner(agent=root, app_name="mixed_auditor")
# Run a prompt; check the trace for distinct model.name attributes per sub_agent.
```

This is essentially the mini-drill (page 12). Get it running with two providers and you have understood the pattern.

> 🛠 **Have the student run:** the skeleton above. Then look at the OTel trace (from module 15) and confirm there are *two different model spans* with different `model.name` attributes.

> 🚀 **In Production**
>
> When a sub_agent is on Claude and the parent is on Gemini, *prompt-tuning bleed* is real. A change in the parent's instruction can shift what the critic sees enough to change Claude's behavior. Re-run evals on the *whole graph*, not just the changed agent. See [[14_Evaluation/00_Overview]] for the eval-set discipline.

---

[← Prev: 17_AdvancedModels/09_ApigeeLlm](09_ApigeeLlm.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/10A_ModelSelectionPatterns →](10A_ModelSelectionPatterns.md)
