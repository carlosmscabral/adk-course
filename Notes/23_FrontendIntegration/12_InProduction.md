---
module: 23_FrontendIntegration
page: 12_InProduction
title: In Production — frontend integration hardening checklist
estimated_minutes: 20
prereqs: [23_FrontendIntegration/11]
concepts: [production_frontend, auth, CORS, rate_limit, reconnect, body_size]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 13_KnowledgeCheck →](13_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 12 In Production

# 🚀 In Production — Frontend Integration

> 🤖 **Tutor:** consolidates the inline `> 🚀 In Production` callouts. Walk this checklist against the student's actual SPA if they have one, or against the mini-drill solution.

---

## Checklist

### 1. Never trust client-supplied `user_id`

- **Risk**: IDOR — user A asserts `user_id="userB"`, your backend creates / reads userB's session.
- **Mitigation**: verify the auth token server-side; derive `user_id` from the verified claim; ignore body field except for logging hint.
- **Inline source**: [01_WhoOwnsTheSession § In Production](01_WhoOwnsTheSession.md)

### 2. Don't deploy `adk api_server` directly to the internet

- **Risk**: no auth, no rate limit, no CORS lockdown, no audit.
- **Mitigation**: wrap with `get_fast_api_app(web=False)` + your own FastAPI middleware (auth, CORS, rate-limit).
- **Inline source**: [05_CustomSPApattern § In Production](05_CustomSPApattern.md), [06_A2UIClient § In Production](06_A2UIClient.md)

### 3. SSE reconnect storms

- **Risk**: backend goes down, every browser tab reconnects every 3s and pounds you on recovery.
- **Mitigation**: server emits `retry: 30000\n\n`; client uses exponential backoff + circuit breaker.
- **Inline source**: [03_SseFromTheBrowser § In Production](03_SseFromTheBrowser.md)

### 4. Cloud Run / Nginx request timeouts cap long sessions

- **Risk**: 60-minute hard cap on Cloud Run; long agents drop mid-stream.
- **Mitigation**: SSE → checkpoint events + resumable reconnect; WebSocket → session resumption (`RunConfig.session_resumption`); or move to GKE / Compute Engine for unbounded sessions.
- **Inline source**: [03_SseFromTheBrowser § In Production](03_SseFromTheBrowser.md), [04_WebSocketsFromBrowser § In Production](04_WebSocketsFromBrowser.md)

### 5. In-memory session service doesn't survive restart or scale

- **Risk**: `InMemorySessionService` + multi-replica = sessions vanish on round-robin or restart.
- **Mitigation**: `DatabaseSessionService` (Postgres/SQLite) or `VertexAiSessionService`. See [22_DeploymentModels](../22_DeploymentModels/).
- **Inline source**: [01_WhoOwnsTheSession § In Production](01_WhoOwnsTheSession.md)

### 6. Token validation must check `iss`, `aud`, `exp`

- **Risk**: a token from a sibling Firebase project will verify against Google's JWKS.
- **Mitigation**: pin `aud` to your exact project; reject expired; rotate JWKS cache periodically.
- **Inline source**: [02_AuthContextPropagation § In Production](02_AuthContextPropagation.md)

### 7. IAP headers must not be trusted unless ingress is locked

- **Risk**: IAP headers are easy to spoof if anyone can reach your service bypassing IAP.
- **Mitigation**: lock Cloud Run ingress to "Internal and Cloud Load Balancing only" before trusting `X-Goog-Authenticated-*` headers.
- **Inline source**: [02_AuthContextPropagation § In Production](02_AuthContextPropagation.md)

### 8. Render storms on partial token events

- **Risk**: ~50-200ms-spaced partials trigger reconcile-per-event; UI janks under load.
- **Mitigation**: throttle with `requestAnimationFrame` or batch every N events into a single state update.
- **Inline source**: [08_StreamingPartialResults § In Production](08_StreamingPartialResults.md)

### 9. Upload path: enforce size limits + MIME allow-list

- **Risk**: 500 MB upload OOMs a FastAPI worker; spoofed MIME smuggles malicious content.
- **Mitigation**: reject early with 413 above a threshold; MIME allow-list + content sniffing; route large files through signed URL (Path B from page 09).
- **Inline source**: [09_FileUploadFlow § In Production](09_FileUploadFlow.md)

### 10. Optimistic UI must show terminal failure states

- **Risk**: user sees the optimistic success, action silently failed; support tickets.
- **Mitigation**: every optimistic action has a confirmed/failed final state visible to the user with a retry affordance.
- **Inline source**: [10_OptimisticUI § In Production](10_OptimisticUI.md)

### 11. Lock down CORS to your origins

- **Risk**: any origin can call your backend with the user's cookie / token forwarded by the browser.
- **Mitigation**: explicit `allow_origins=[...]` in `CORSMiddleware`; never `["*"]` with credentials.
- **Inline source**: [05_CustomSPApattern § In Production](05_CustomSPApattern.md)

---

## Cross-references

- [16 Production & Security](../16_ProductionSecurity/) — the full security checklist (auth, secrets, network).
- [22 Deployment Models](../22_DeploymentModels/) — where the backend runs (Cloud Run, GKE, Agent Engine).
- [21 ADK API Surface](../21_AdkApiSurface/) — what your frontend is consuming.
- [24 Channel Integrations](../24_ChannelIntegrations/) — Slack/Discord/Google Chat: a different "frontend" with the same backend constraints.
- [4B Human-in-the-Loop](../4B_HumanInTheLoop/) — backend half of the optimistic-UI / approval pattern.

> 🚀 **In Production** — composite reminder
>
> Walk every callout above before you ship. If you can't answer "what happens when this fails?" for each item, you have a gap. Frontend bugs in production are user-visible *instantly* — there's no batch job grace period.

---

[← Prev: 11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 13_KnowledgeCheck →](13_KnowledgeCheck.yml)
