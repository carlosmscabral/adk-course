---
module: 16_ProductionSecurity
page: 01_ThreatModelForAgents
title: A threat model for agents
estimated_minutes: 20
prereqs: [16_ProductionSecurity/00]
concepts: [STRIDE, threat model, attack surface]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/02_PromptInjectionDefense →](02_PromptInjectionDefense.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 01 Threat Model

---

## 🧠 Why "STRIDE for agents"

STRIDE is a Microsoft-era threat-modeling acronym (Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Elevation of Privilege). It still applies to web apps. **It under-fits agents** because agents have two attack surfaces a web app does not:

1. **Natural-language input** that can rewrite the system instruction.
2. **Tool outputs** that are *also* model input — and equally untrusted.

So we adapt: same flavor, agent-specific categories.

## 🧠 Seven agent-shaped threats

```
{{ _figures/threat_model.txt }}
```

(Open `_figures/threat_model.txt` — table version is more readable.)

In words:

1. **Direct prompt injection.** User pastes "Ignore previous instructions, do X." The simplest attack, and the most over-confidently dismissed.
2. **Indirect prompt injection.** A web page or RAG document the agent loaded contains hidden instructions. The model treats them as input. *This is the dominant attack class for agents that browse or RAG.*
3. **Jailbreak.** Persuasive narrative that gets the model to do what the system instruction forbids. ("You are DAN…", role-play, hypothetical framing.)
4. **Exfiltration.** Model is induced to leak data (system prompt, prior turns, secret tool args) through a tool call or its reply.
5. **Unauthorized action.** Model invokes a tool the user shouldn't have been able to trigger (delete-user, refund, send-email).
6. **Cost runaway.** Loop bug + paid model = $$$ in minutes. Or a user crafts a prompt that maximizes token usage.
7. **Hallucination-as-fact.** Not malicious — just wrong. Becomes a security issue when the wrong answer is acted on (a billing system, a medical chart, a legal opinion).

Bonus class:

8. **Session poisoning.** A filtered-once turn gets persisted; on the next turn, the model reads its own removed content as context and reproduces the harm. This is why `safety-plugins/` overwrites unsafe content before it reaches the session — not after.

## 🧠 The mental discipline

When you draft an agent architecture, walk the *threat_model.txt* table top to bottom and ask: *which layer in defense-in-depth catches this?* If the answer is "none" for any row, the design is incomplete.

> ❓ **Ask the student:** which of the eight threats does *no amount of prompt engineering* defend against? *(All of them — at least partially. Prompt engineering is layer L2, and the figure on page 00 puts it as the weakest layer for exactly this reason.)*

> 🚀 **In Production**
>
> Threats #4 (exfil) and #7 (hallucination-as-fact) are the ones that show up in news stories. They are also the easiest to test for: a small eval set of jailbreak attempts + a small eval set of factually-checkable questions cover most of the headline risk. See [[14_Evaluation/05_RubricBasedEvaluator]] for the eval shape.

---

[← Prev: 16_ProductionSecurity/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/02_PromptInjectionDefense →](02_PromptInjectionDefense.md)
