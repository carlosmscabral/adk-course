---
module: 17_AdvancedModels
page: 09_ApigeeLlm
title: ApigeeLlm — enterprise gateway routing
estimated_minutes: 15
prereqs: [17_AdvancedModels/08]
concepts: [ApigeeLlm, API gateway, policy enforcement, shared LLM pool, quota]
icon: 🏢
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/08_OpenAIModels](08_OpenAIModels.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/10_PerAgentModel →](10_PerAgentModel.md)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 07 Apigee

---

## 🏢 The enterprise problem

You work in an organization with 50+ teams each building agents. Each team:

- Picks their own model, their own provider, their own API key.
- Bills against their own cost center, but the security team has no view.
- Could leak prompts to a provider not on the approved vendor list.

The solution is a **gateway**: every LLM call goes through one chokepoint that you control. Apigee is Google Cloud's enterprise API gateway. `ApigeeLlm` is the ADK adapter that points an agent at it.

## 🛠 Shape

```python
from google.adk.models import ApigeeLlm  # if exposed in your ADK version

agent = LlmAgent(
    model=ApigeeLlm(
        endpoint="https://api.acme.com/llm-gateway/v1/chat",
        api_key=os.environ["APIGEE_KEY"],
        model="enterprise-default",   # the gateway routes this string
    ),
    name="...",
)
```

From the agent's view: one endpoint, one auth, one model name. The complexity of *which* upstream provider serves the call lives in the gateway config, not in your code.

## 🏢 What the gateway buys you

1. **Centralized policy enforcement.** PII redaction, jailbreak filtering, content classification — all enforced once, for every team.
2. **Quota management.** Per-team budgets, per-app rate limits. Stop a runaway agent at the gateway.
3. **Vendor abstraction.** Switch from `gpt-4o` to `claude-sonnet` by changing the gateway route; no agent redeploy.
4. **Audit trail.** Every call logged with caller identity, model, tokens, cost. Compliance gold.
5. **Approved-vendor enforcement.** No team can use a model that hasn't passed legal/security review.

## 🏢 Architecture pattern

```
   [Team A agents]   [Team B agents]   [Team C agents]
          │                │                │
          └────────────────┴────────────────┘
                           │
                  ┌────────▼────────┐
                  │     Apigee      │   policies: PII, quota, routing, audit
                  └────────┬────────┘
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
   [Vertex Gemini]   [Vertex Claude]    [Self-host vLLM]
```

The agents speak one protocol (the gateway). The gateway speaks every upstream provider's protocol on their behalf.

## ⚠️ Gotcha — the gateway is now the SPOF

Centralization is power and risk. The gateway down = every agent down.

Mitigations:
- Multi-region gateway with failover.
- Client-side fallback to the direct provider for tier-1 traffic (with feature flag).
- Cache the most-recent successful responses for *idempotent* lookups (advisory only — never for transactional calls).

## 🛠 When to choose this over per-agent provider auth

| Signal | Pick |
|---|---|
| 1-5 agents, one team | Direct provider (Gemini, Claude, LiteLlm). |
| Multiple teams, regulated industry | Apigee (or your equivalent gateway). |
| Need to switch providers without redeploy | Apigee. |
| Need per-team budgets | Apigee. |
| Need cross-app PII enforcement | Apigee — or, lower-tech, a shared `safety-plugin` library. |

> 🚀 **In Production**
>
> If you adopt `ApigeeLlm`, your gateway team becomes part of every incident response. Get them on the on-call rotation, or your "agent is broken" tickets will play hot potato. See [[17_AdvancedModels/12_InProduction]].

---

[← Prev: 17_AdvancedModels/08_OpenAIModels](08_OpenAIModels.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/10_PerAgentModel →](10_PerAgentModel.md)
