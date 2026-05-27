---
module: 16_ProductionSecurity
page: 00_Overview
title: Production & Security — defense in depth for agents
estimated_minutes: 10
prereqs: [07_Callbacks/06, 13_Plugins/06, 14_Evaluation/06]
concepts: [threat model, prompt injection, defense in depth, guardrails]
icon: 🛡
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/10_MiniDrill](../15_Observability/10_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/01_ThreatModelForAgents →](01_ThreatModelForAgents.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 00 Overview

---

## 🛡 What you'll learn

By the end of this module you will:

- Have a *named threat model* for agents (not just "AI safety" hand-waving).
- Know the prompt-injection taxonomy and the standard defenses for each.
- Wire auth context through `AuthHandler` / `CredentialManager` to a tool.
- Handle secrets without ever putting them in a prompt, log, or trace.
- Own a **Guardrails Cookbook** of 7 callback/plugin recipes you can copy into any agent.
- Read `safety-plugins/` and `policy-as-code/` end-to-end.

This module is **not** the first time you see safety concerns. Every prior module raised them inline next to the tool that introduced them. Here we *integrate* them into defense-in-depth.

## 🧭 Prereqs

- **07 Callbacks** — guardrails *are* callbacks.
- **13 Plugins** — for app-wide guardrails (like `safety-plugins`).
- **14 Evaluation** — for red-teaming eval cases.

## ⏱ Time budget

**3.5 days.** One day for pages 01-04 (the foundations). One day for the cookbook (05) plus the two guardrail-adjacent concept pages (06 agent-vs-user identity, 07 Gemini-as-Judge). One and a half days for the two sample dissections (08-09), the production checklist (10), and the mini-drill (12).

## 📦 Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/safety-plugins/` — two safety plugins (LlmAsAJudge, Model Armor) wired at `Runner` level.
- `/home/carloscabral/study/adk-samples/python/agents/policy-as-code/` — declarative policies enforced via AST validation + sandboxed `exec`.
- `/home/carloscabral/study/adk-samples/python/agents/ai-security-agent/` — red-team agent (attacker / target / evaluator) for testing your own defenses.
- `/home/carloscabral/study/adk-samples/python/agents/cyber-guardian-agent/` — multi-agent incident response pattern.

## 🗺 Page map

| # | Page | Why |
|---|---|---|
| 01 | ThreatModelForAgents | STRIDE for agents — what can go wrong. |
| 02 | PromptInjectionDefense | The taxonomy + the standard defenses. |
| 03 | Authentication | `AuthHandler`, `CredentialManager`, per-user auth in tools. |
| 04 | SecretsHandling | Secret Manager, ADC, .env-only-in-dev. |
| 05 | GuardrailsCookbook | 7 ready-to-copy recipes. |
| 06 | AgentIdentityVsUser | Service-account identity vs end-user identity in tool calls. |
| 07 | GeminiAsJudgePlugin | The `LlmAsAJudge` safety plugin as a runtime classifier. |
| 08 | DissectingSafetyPlugins | Read `safety-plugins/` end-to-end. |
| 09 | DissectingPolicyAsCode | Read `policy-as-code/`. |
| 10 | InProduction | Defense-in-depth checklist + incident response. |
| 11 | KnowledgeCheck | 10 questions. |
| 12 | MiniDrill | PII redaction + LLM-judge toxicity filter on M4 auditor. |

## 🗺 The big picture (ASCII)

```
{{ _figures/defense_in_depth.txt }}
```

(Open `_figures/defense_in_depth.txt` for the full diagram. Six layers; you need at least three live for any public agent.)

> 🤖 **Tutor:** before page 01, ask the student to name three things that could go wrong with their M4 auditor agent if a malicious user got hold of it. Their answers prime page 01.

---

[← Prev: 15_Observability/10_MiniDrill](../15_Observability/10_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/01_ThreatModelForAgents →](01_ThreatModelForAgents.md)
