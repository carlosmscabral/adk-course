---
module: 21_AdkApiSurface
page: 10_InProduction
title: In Production — API surface hardening checklist
estimated_minutes: 20
prereqs: [21_AdkApiSurface/09]
concepts: [auth, CORS, rate limits, SSE keepalive, sticky sessions, event redaction]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 11_KnowledgeCheck →](11_KnowledgeCheck.yml)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 10 In Production

---

## 🚀 The checklist

Consolidates the `🚀 In Production` callouts from this module's concept pages, plus the gotchas you only see under load.

### 1. Never ship `adk run` or `adk web` as the user-facing surface

- **Risk**: REPL has no auth, no multi-user, no quotas. Web has the Builder routes (unprotected CSRF surface) and a dev UI that exposes full event history.
- **Mitigation**: ship `adk api_server` (or `get_fast_api_app`) behind an ingress with auth.
- **Inline source**: [00_Overview § In Production](00_Overview.md#-in-production) and [01B_AdkWebUnderTheHood § In Production](01B_AdkWebUnderTheHood.md#-in-production).

### 2. Pin one uvicorn worker per pod, scale by pod count

- **Risk**: uvicorn `--workers > 1` breaks ADK's in-process session caches; you get stale state and lost events.
- **Mitigation**: 1 worker per pod; horizontal scale by replicas; if you cannot do sticky-by-session-id routing, push session state to `DatabaseSessionService` (Postgres) or `VertexAiSessionService` so any pod can serve any request.
- **Inline source**: [02_AdkApiServer § In Production](02_AdkApiServer.md#-in-production).

### 3. Redact event payloads before sending to clients

- **Risk**: `/run` returns full `Event` objects with `actions.state_delta`, tool args, tool responses. Some of that is internal — pricing tiers, prompt scaffolding, raw search results.
- **Mitigation**: response transformer middleware that strips `actions` and `functionCall`/`functionResponse` parts unless the UI explicitly needs them.
- **Inline source**: [03_RestShapes § In Production](03_RestShapes.md#-in-production); cross-link [16_ProductionSecurity/05_GuardrailsCookbook](../16_ProductionSecurity/05_GuardrailsCookbook.md).

### 4. Keep SSE streams alive with periodic comments

- **Risk**: load balancers / browsers close idle SSE connections at 30-120s. Long tool calls die.
- **Mitigation**: emit `: keepalive\n\n` every 15s during model thinking. Clients ignore comment lines.
- **Inline source**: [04_SseEndpoints § In Production](04_SseEndpoints.md#-in-production).

### 5. Reconnect protocol for `/run_live` WebSockets

- **Risk**: Cloud Run caps WS at ~15min. Pod restarts kill open sessions. Voice users get cut off.
- **Mitigation**: client-side reconnect that resumes from saved session state. Or deploy on Agent Engine / GKE for longer connection budgets.
- **Inline source**: [05_WebSocketsForLive § In Production](05_WebSocketsForLive.md#-in-production); cross-link [22_DeploymentModels/05_ScalingAndColdStart](../22_DeploymentModels/05_ScalingAndColdStart.md).

### 6. Own the deployment when you wrap with `get_fast_api_app`

- **Risk**: `adk deploy cloud_run` only builds what the loader sees — it can't include your custom `/feedback` route or middleware.
- **Mitigation**: when you wrap, write your own Dockerfile (Module 22 page 02) and your own CI. Don't try to extend `adk deploy`.
- **Inline source**: [06_WrappingInFastAPI § In Production](06_WrappingInFastAPI.md#-in-production).

### 7. Authorize `user_id` against the URL

- **Risk**: ADK does **not** check that the URL's `user_id` matches the authenticated user. Anyone with a token can read anyone else's session by guessing `user_id`s.
- **Mitigation**: middleware that derives `user_id` from the verified token and rejects requests where the URL `user_id` doesn't match. Page 08 has the snippet.
- **Inline source**: [08_AuthenticatingTheApi § In Production](08_AuthenticatingTheApi.md#-in-production).

### 8. CORS once, with a real allow-list

- **Risk**: `allow_origins=["*"]` plus credentialed requests = browser refuses, OR (worse) allows cross-origin reads from arbitrary attacker sites if you weakened the `*` rule.
- **Mitigation**: explicit list of allowed origins. Per environment (dev list ≠ prod list). One CORS layer only — picking either the factory kwarg or your own middleware, not both.
- **Inline source**: implicit across [02 / 06 / 08].

### 9. Skip auth on `/health` and `/version`, on those routes only

- **Risk**: k8s readiness probes hit `/health` without tokens. If your auth middleware 401s the probe, the pod is marked unhealthy and gets killed.
- **Mitigation**: middleware skips auth iff path matches a small allow-list (`/health`, `/version`, `/livez`). Everything else requires auth.
- **Inline source**: [08_AuthenticatingTheApi § In Production](08_AuthenticatingTheApi.md#-in-production).

### 10. Rate-limit per `user_id`, not per IP

- **Risk**: agents are expensive (LLM cost + tool quota). A bad actor with 5 IPs can burn through your budget.
- **Mitigation**: rate limit middleware keyed on the **authenticated** `user_id`. Bucket per (user_id, route) — different limits for `/run` (expensive) vs `/sessions GET` (cheap). Use Redis or your edge provider's built-in.
- **Inline source**: new in this checklist (not on a concept page).

---

> 🤖 **Tutor:** before the mini-drill on page 12, walk this checklist against the student's M4 auditor. Most fresh builds violate 6-8 of the 10 items. Don't fix them all in one sitting — pick the two most relevant to *this* module (probably #4 SSE keepalive and #7 user_id authz) and have them ship a fix.

> 🚀 **In Production** — composite reminder
>
> The API surface is **the deployment boundary**. Every gotcha above is a real outage in someone's postmortem. If you cannot answer "what happens when X fails?" for items 1-10, you are not ready to ship.

---

[← Prev: 09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 11_KnowledgeCheck →](11_KnowledgeCheck.yml)
