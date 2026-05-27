---
module: 16_ProductionSecurity
page: 10_InProduction
title: Security in production — defense-in-depth checklist
estimated_minutes: 25
prereqs: [16_ProductionSecurity/09]
concepts: [defense in depth, red teaming, incident response, rollback, auditability]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/09_DissectingPolicyAsCode](09_DissectingPolicyAsCode.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/11_KnowledgeCheck →](11_KnowledgeCheck.yml)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 10 In Production

---

## 🚀 The checklist

This consolidates the `🚀 In Production` callouts from this module *and* every prior module's `06_InProduction.md` that touched safety. Treat it as a launch gate.

### 1. Defense in depth — at least 3 of 6 layers

Per `_figures/defense_in_depth.txt`:

- L1 Input filter • L2 System instruction • L3 Tool gating
- L4 Sandbox • L5 Output filter • L6 Audit/Eval

No single layer catches everything. **A public agent should have at least three layers live.** A high-risk agent (finance, health, code-execution) needs all six.

### 2. Red-team your agent *before* shipping

Build a small eval set whose only purpose is to *try to break* the agent:

- Direct injection ("ignore previous…").
- Indirect injection (RAG document with hidden instructions).
- Jailbreak ("you are DAN…").
- Exfiltration ("repeat the system prompt back").
- Tool misuse ("delete all my data").
- Cost-runaway prompts ("repeat the alphabet 10000 times").

Cross-link: see `/home/carloscabral/study/adk-samples/python/agents/ai-security-agent/` for the red-team agent shape (red-team → target → evaluator triad). Wire those cases into [[14_Evaluation/00_Overview]] so regression failures become CI failures.

### 3. Incident response — have a rollback plan

When a guardrail fails (and it will), you need:

- A **kill switch** — a config flag that disables the agent without a redeploy.
- **Per-tool circuit breakers** — disable one tool without disabling the agent.
- **Per-user blocklist** — ban an abusing account without a redeploy.
- A **rollback target** — last known-good revision tag, with one-command revert.

If you cannot disable the agent in under 5 minutes, you do not own production.

### 4. Logging guardrail decisions *is* a guardrail

Every callback that blocks something must emit a structured log:

```json
{"ts": "...", "event": "guardrail_block", "layer": "before_tool_callback",
 "reason": "pii_pattern_match", "tool": "send_email",
 "trace_id": "...", "session_id": "...", "user_id": "..."}
```

Why: auditability. When a regulator asks *"can you show me that you blocked this?"*, the log is the answer. Cross-link [[15_Observability/08_InProduction]] § correlation IDs.

### 5. Never trust tool output

Indirect injection lives here. Any string that came from a tool — web page, MCP result, RAG chunk — must pass through the same filters as user input before reaching the model. Treat your retriever as untrusted.

### 6. Sandbox is not optional for code execution

`UnsafeLocalCodeExecutor` is **forbidden** in prod. Hard fail at startup if `ENV=prod` and the executor is unsafe. (Recipe 6 in [[16_ProductionSecurity/05_GuardrailsCookbook]].) Cross-link [[12_CodeExecution/08_InProduction]].

### 7. Secrets discipline

- No secret in repo, env file, prompt, or span attribute.
- ADC for GCP; Secret Manager for everything else.
- Rotate on a schedule; rotate immediately on suspicion.
- Pre-commit secret scanner.

(See page 04.)

### 8. Cost guardrails

Per-session cost cap, per-user rate limit, per-tool quota. Page-05 cookbook recipes 4 and 5. **Without a cap, one malicious user can DoS your wallet.**

### 9. Auth at the tool, not the prompt

The model should *never* be the gatekeeper for "is this user allowed?" The tool calls `tool_context.get_auth_response(auth_config)` to fetch the resolved credential (or `tool_context.request_credential(auth_config)` to kick off OAuth if it is missing) — and a `before_tool_callback` compares `tool_context.state["user_id"]` against `args["user_id"]` to refuse cross-user calls deterministically. (Page 03.)

### 10. Session poisoning protection

Filter content **before** it is persisted. If `after_model_callback` removed a bad message but the runner still wrote the original to the session, the next turn re-reads it. The `safety-plugins/` pattern fixes this by setting a state flag and using `before_run_callback` to short-circuit. (Page 08.)

### 11. Compliance scope

- PII handling — GDPR / CCPA. Redact at L1 + L5.
- Sector regulation — HIPAA, PCI, SOX. Tool-level enforcement, audit log.
- Retention — match your audit-log lifetime to the regulator's window, not your debugger's.

(Cross-link [[15_Observability/08_InProduction]] § retention.)

### 12. Failure mode = fail closed for security, fail open for telemetry

If a safety judge times out: assume unsafe; refuse.
If the OTel collector times out: assume nothing; ship the request and drop the span.

Mixing those up — failing open on safety to "be more helpful" — is how you make the news.

> 🤖 **Tutor:** ask the student to score their M4 auditor against this 12-item checklist. *Most students will score 2-4 out of 12 on a fresh build.* That is correct. The point is to know where the gaps are; the mini-drill closes the two easiest ones (PII redaction + toxicity filter).

---

[← Prev: 16_ProductionSecurity/09_DissectingPolicyAsCode](09_DissectingPolicyAsCode.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/11_KnowledgeCheck →](11_KnowledgeCheck.yml)
