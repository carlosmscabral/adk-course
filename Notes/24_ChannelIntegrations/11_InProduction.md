---
module: 24_ChannelIntegrations
page: 11_InProduction
title: In Production — channel integration hardening checklist
estimated_minutes: 20
prereqs: [24_ChannelIntegrations/10]
concepts: [production_channels, signature, ack_speed, oauth_token_storage, rate_limit, idempotency]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 12_KnowledgeCheck →](12_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 11 In Production

# 🚀 In Production — Channel Integrations

> 🤖 **Tutor:** consolidates the inline `> 🚀 In Production` callouts. Walk the student through against their actual channel adapter if they have one, or against the mini-drill solution.

---

## Checklist

### 1. Signature verification is non-negotiable

- **Risk**: skipped verification → your endpoint is a public agent-trigger for anyone on the internet. Free abuse vector + bill amplification.
- **Mitigation**: verify before *anything else*. Use raw body bytes (not parsed JSON). Reject on missing or stale timestamps.
- **Inline source**: [01_WebhookToRunnerPattern § In Production](01_WebhookToRunnerPattern.md), [03_SlackBot § In Production](03_SlackBot.md), [05_DiscordBot § In Production](05_DiscordBot.md)

### 2. ACK within the platform's deadline (3s for chat)

- **Risk**: handler runs the agent synchronously, takes 5s, platform retries → duplicate replies, duplicate bills.
- **Mitigation**: `BackgroundTasks` for short work; Pub/Sub / Cloud Tasks for long. Log time-to-200; alert if >1s.
- **Inline source**: [02_LongRunningOnChat § In Production](02_LongRunningOnChat.md)

### 3. Don't loop on your own bot's messages

- **Risk**: bot reply triggers `message` event → bot reads it → bot replies → forever.
- **Mitigation**: check `bot_id` / `bot_user_id` on every incoming message and ignore self.
- **Inline source**: [03_SlackBot § In Production](03_SlackBot.md)

### 4. Throttle `chat.update` to platform rate limits

- **Risk**: streaming edits at 5/s → 429s → dropped updates → users see stale "thinking" messages.
- **Mitigation**: throttle to 1/sec per channel (Slack); batch tokens before each edit; flush at most every N seconds.
- **Inline source**: [03_SlackBot § In Production](03_SlackBot.md)

### 5. Pin Chat App URLs (Google Chat) / register fresh on redeploy

- **Risk**: redeploy → service URL changes → platform silently stops calling you.
- **Mitigation**: custom domains pinned in DNS; redeployment runbook re-registers webhook URLs if needed.
- **Inline source**: [04_GoogleChatApp § In Production](04_GoogleChatApp.md)

### 6. Ed25519 verify before JSON parse (Discord)

- **Risk**: `await request.json()` consumes the body stream; signature check then fails on empty body.
- **Mitigation**: always read body bytes → verify → parse JSON. Order matters.
- **Inline source**: [05_DiscordBot § In Production](05_DiscordBot.md)

### 7. WhatsApp 24-hour window + send budgets

- **Risk**: agent generates 200 outbound replies in a loop → WhatsApp throttles per-phone-per-day → silent failures.
- **Mitigation**: per-channel send budget with alerting; respect customer-service window; use templates for proactive outreach.
- **Inline source**: [06_WhatsAppEmail § In Production](06_WhatsAppEmail.md)

### 8. Pub/Sub at-least-once → idempotent agent behavior

- **Risk**: duplicate Pub/Sub deliveries → duplicate agent runs → duplicate side effects.
- **Mitigation**: de-dupe by Pub/Sub `messageId` in session state; ACK before doing work where possible.
- **Inline source**: [07_AmbientAgentsAsChannels § In Production](07_AmbientAgentsAsChannels.md)

### 9. Refresh tokens are passwords

- **Risk**: leaked refresh token = persistent compromise; perpetual access without revocation.
- **Mitigation**: KMS encryption at rest, audit logging on read, rotate on anomaly, never in env files / git.
- **Inline source**: [08_AuthAndPerUserSession § In Production](08_AuthAndPerUserSession.md)

### 10. File-size cap on multimedia before passing to Gemini

- **Risk**: a 100MB voice note blows past context limits; Gemini returns 400; webhook fails late after burning bandwidth.
- **Mitigation**: soft cap at 20-50MB; reject early with a friendly platform reply; size-based routing for large files.
- **Inline source**: [09_HandlingMultimedia § In Production](09_HandlingMultimedia.md)

### 11. Channel adapters need persistent session storage

- **Risk**: `InMemorySessionService` + multi-replica deployment → session vanishes on round-robin or restart → loses thread context mid-conversation.
- **Mitigation**: `DatabaseSessionService` (Postgres) or `VertexAiSessionService` from day one for channel adapters. The cost is one DB row per session.
- **Inline source**: cross-ref to [22_DeploymentModels](../22_DeploymentModels/) and the ambient sample's terraform.

### 12. Trust boundary — IAM on Pub/Sub push to Cloud Run

- **Risk**: Cloud Run set to "allow unauthenticated" → anyone can POST to `/trigger/pubsub` → free agent triggering.
- **Mitigation**: set ingress to "Internal and Cloud Load Balancing only" OR require auth on `/trigger/pubsub` via the Pub/Sub push auth SA.
- **Inline source**: [07_AmbientAgentsAsChannels § In Production](07_AmbientAgentsAsChannels.md)

---

## Cross-references

- [16 Production & Security](../16_ProductionSecurity/) — the cross-cutting security module.
- [22 Deployment Models](../22_DeploymentModels/) — where channel adapters live (almost always Cloud Run).
- [13 Plugins](../13_Plugins/) — `ReflectAndRetryToolPlugin` for ambient agents that must be reliable.
- [4B Human-in-the-Loop](../4B_HITL/) — the HITL pattern the ambient-expense-agent uses.
- [23 Frontend Integration](../23_FrontendIntegration/) — same rules, different doorway (browser).

> 🚀 **In Production** — composite reminder
>
> Channel integrations have the broadest blast radius in the course — a bad bot can spam thousands of users in minutes. Walk every callout above. If you can't answer "what's the abuse / leak / cost runaway scenario?" for each item, you have a gap.

---

[← Prev: 10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 12_KnowledgeCheck →](12_KnowledgeCheck.yml)
