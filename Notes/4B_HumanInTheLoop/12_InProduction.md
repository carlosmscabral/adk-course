---
module: 4B_HumanInTheLoop
page: 12_InProduction
title: In Production — HITL hardening checklist
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/11]
concepts: [TTL, approval-binding, audit-log, idempotency, durable-session-backend]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 13_KnowledgeCheck →](13_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 12 In Production

# 🚀 In Production — HITL

> 🤖 **Tutor:** walk this checklist against the mini-drill solution (page 14) or — better — against the student's own HITL-enabled work. Every item below has a real-world failure mode. Don't let the student skim.

The course teaches production-readiness inline (brief rule #14); this is the consolidation for shipping anything HITL-enabled.

---

## Checklist

> ❓ **Ask the student:** "Open the most recent `Work/4B_*.py` you've written. We're going to walk this checklist against it."

### 1. Durable session backend

- **Risk**: pause survives process restart only if the session backend persists. `InMemorySessionService` (the default in many examples) loses everything on Cloud Run scale-to-zero.
- **Mitigation**: production runs must use `DatabaseSessionService`, `SqliteSessionService`, or `VertexAiSessionService`. Verify in your `Runner(...)` construction.
- **Inline source**: [04_RunnerResumeAndCancel § 🚀 In Production](04_RunnerResumeAndCancel.md#-in-production), and the broader [04_SessionsState/06_PersistentSessions](../04_SessionsState/06_PersistentSessions.md).

### 2. `resumability_config.is_resumable = True`

- **Risk**: `App(resumability_config=ResumabilityConfig(is_resumable=False))` (or no config at all) silently drops the checkpoint — resume calls raise.
- **Mitigation**: set `is_resumable=True` in the `App` construction; smoke-test resume in CI on every release.
- **Inline source**: [04_RunnerResumeAndCancel § 🚀 In Production](04_RunnerResumeAndCancel.md#-in-production).

### 3. Idempotent side-effecting tools

- **Risk**: at-least-once resume semantics — the framework can re-run the tool body. Non-idempotent operations (charge card, send email, delete file) execute twice.
- **Mitigation**: every confirmable tool that touches the outside world includes an idempotency key (UUID stashed in `payload`). Side-effect path checks "have I already done op X?" before acting.
- **Inline source**: [04_RunnerResumeAndCancel § 🚀 In Production](04_RunnerResumeAndCancel.md#-in-production).

### 4. No side effects in the pre-confirm branch

- **Risk**: a tool that does any real work *before* checking `ctx.tool_confirmation` is an exploit — the user can trigger the action just by mentioning it.
- **Mitigation**: code review rule — in the `if ctx.tool_confirmation is None` branch the only lines are `ctx.request_confirmation(...)` and `return {}`. PR template should flag violations.
- **Inline source**: [02_RequestConfirmation § 🚀 In Production](02_RequestConfirmation.md#-in-production).

### 5. Identity binding on resume

- **Risk**: leaked `invocation_id` + `function_call_id` lets any caller approve. Especially bad when approvers come from Slack/Chat — the platform user is not the same as your application user.
- **Mitigation**: pending-approvals table stores `approver_user_id`. Resume handler verifies the caller's authenticated identity matches before forwarding to `runner.run_async`.
- **Inline source**: [03_RequestedToolConfirmations § 🚀 In Production](03_RequestedToolConfirmations.md#-in-production), [09_ChatPlatformApprovals § Identity binding](09_ChatPlatformApprovals.md#identity-binding--the-only-critical-security-note).

### 6. TTL on pending approvals + sweeper

- **Risk**: approvals queued and never decided clog the session store, hold open background context, can be approved by stale approvers (someone left the company).
- **Mitigation**: pending-approvals table has `expires_at`. A scheduled job (Cloud Scheduler → Cloud Run job) sweeps expired rows, marks `decision="timeout"`, appends a terminal event to the session so the audit trail is closed, and never resumes the invocation. There is no `runner.cancel()` — page 04 walks the abandon pattern. Standard TTLs: 24h for routine, 7 days for legal review.
- **Inline source**: [04_RunnerResumeAndCancel § Abandoning a pending invocation](04_RunnerResumeAndCancel.md#abandoning-a-pending-invocation), [05_LongRunningFunctionTool § 🚀 In Production](05_LongRunningFunctionTool.md#-in-production).

### 7. Audit log of every decision

- **Risk**: "who approved this?" with no answer = failed audit. Logging only the *request* is insufficient.
- **Mitigation**: emit a structured log on every decision (approve / reject / timeout / cancel) with: `invocation_id`, `function_call_id`, `approver_user_id`, `decision`, `payload_snapshot`, `timestamp`. Pipe to Cloud Logging / SIEM. Bonus: post outcome back into the chat channel where it was requested (page 09).
- **Inline source**: [01_WhyHITL § 🚀 In Production](01_WhyHITL.md#-in-production), [09_ChatPlatformApprovals § Render the outcome back](09_ChatPlatformApprovals.md#render-the-outcome-back).

### 8. Ambient: dedup at the trigger

- **Risk**: Pub/Sub at-least-once + 10-minute ack deadline means a redelivered message can spawn duplicate workflows.
- **Mitigation**: first node parses a stable event id (Pub/Sub `messageId` / GCS `eventId` / your business id), checks a dedup set in the session store, short-circuits if already processed.
- **Inline source**: [07_AmbientAgents § 🚀 In Production](07_AmbientAgents.md#-in-production).

### 9. Frontend dedup of double-clicks

- **Risk**: user double-clicks approve, browser POSTs twice, both succeed, tool runs twice.
- **Mitigation**: client-side: disable the button on click, dedupe in the API gateway by request id. Server-side: belt + suspenders, the idempotency from item #3 catches what the client missed.
- **Inline source**: [08_FrontendDrivenApprovals § 🚀 In Production](08_FrontendDrivenApprovals.md#-in-production).

### 10. Know when to graduate to durable execution

- **Risk**: pushing ADK resume past its envelope (multi-day pauses, complex retry policies, in-flight versioning) ends with un-resumable workflows after a deploy.
- **Mitigation**: at the design phase, score the workflow against the criteria in page 10. If it scores in "durable execution territory", wrap the ADK agent in a Temporal/Dapr activity from day one — don't migrate later.
- **Inline source**: [10_DurableExecutionIntegrations § 🚀 In Production](10_DurableExecutionIntegrations.md#-in-production).

---

## Cross-references

- The cross-cutting production module: [16 Production & Security](../16_ProductionSecurity/) — re-read items #5 and #7 against the security chapter.
- The observability module: [15 Observability](../15_Observability/) — every pending approval should show up as a tracked span; alert on stale ones.
- The session module: [04 Sessions & State](../04_SessionsState/) — the substrate everything in this module rides on.
- Forward to [23 Frontend Integration](../23_FrontendIntegration/) and [24 Channel Integrations](../24_ChannelIntegrations/) for the client-side patterns referenced from items #5 and #9.

> 🚀 **In Production** — composite reminder
>
> A HITL feature that ships without items #1, #2, #3, #5, and #7 is not in production. It is a demo on a public URL. Walk the list, every release.

---

[← Prev: 11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 13_KnowledgeCheck →](13_KnowledgeCheck.yml)
