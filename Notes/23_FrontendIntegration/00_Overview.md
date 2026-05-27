---
module: 23_FrontendIntegration
page: 00_Overview
title: Frontend Integration — browsers and SPAs as ADK clients
estimated_minutes: 15
prereqs: [21_ApiSurface/00, 18_StreamingLive/03]
concepts: [SPA, EventSource, WebSocket, session_id_ownership, auth_propagation, ArtifactService]
icon: 🗺
in_production: true
detours_suggested: [a2UI, WebSockets, FastAPI_for_ADK]
---

[← Prev: 22_Deployment/(last)](../22_DeploymentModels/)  [↑ Map](../../MAP.md)  [Next: 01_WhoOwnsTheSession →](01_WhoOwnsTheSession.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 00 Overview

# 🗺 Module 23 — Frontend Integration

You shipped an ADK agent. Module 21 told you what HTTP surface it exposes. Module 22 told you where to host it. **This module is what the browser does.**

The frontend is a thin, persistent client that holds two things — `user_id` and `session_id` — and turns user gestures into HTTP/SSE/WebSocket calls against the ADK surface from module 21. Nothing more. Every "frontend feature" (file upload, optimistic UI, partial-token rendering, OAuth) is a small JS pattern wrapped around that core.

## 🎯 What you'll walk away knowing

- Who owns the **session_id** (the wrinkle every team gets wrong once).
- How a browser sends `/run` and receives SSE token-by-token (`EventSource`).
- How to upgrade to **WebSocket** for bidi Live.
- How a **Firebase / OIDC / IAP** token rides from browser → backend → `ToolContext`.
- How file uploads land in **ArtifactService**.
- Optimistic UI patterns for pending tool calls.
- How the **A2UI dev frontend** and **AG-UI** protocol slot in.

## 📋 Prereqs

- 21 (the HTTP surface the browser hits — `/run`, `/run_sse`, sessions endpoints).
- 18/03 (you've seen SSE on the server side; here you write the client).
- Basic JS — `fetch`, `EventSource`, `WebSocket`. No framework required.
- Helpful: 16 (production security — auth maps cleanly to what we cover here).

## ⏱ Time

- **Total**: ~4 hours over 2 sessions.
- Heavier if you go deep on Firebase setup. The auth page sketches the wire; full Firebase quickstart is its own thing.

## 🧪 Sample anchor

This module dissects **`deep-search`** at `/home/carloscabral/study/adk-samples/python/agents/deep-search/`. It pairs a Vite/React SPA frontend with an ADK backend that streams research progress as events. The patterns are exactly the ones you'll learn here. (We also reference `realtime-conversational-agent` for the WebSocket bidi case.)

## The mental picture

```
              Browser (SPA)                       Your backend                          ADK
   ┌──────────────────────────────┐    ┌─────────────────────────────┐    ┌────────────────────────────┐
   │  React/Vue/vanilla JS        │    │  FastAPI / Cloud Run        │    │  Runner + Session +        │
   │                              │    │                             │    │  Agent + Tools             │
   │  - holds session_id          │    │  - verifies auth token      │    │                            │
   │  - holds user_id             │    │  - resolves user_id         │    │                            │
   │  - EventSource / WebSocket   │    │  - constructs Runner        │    │                            │
   │  - file inputs               │    │  - bridges HTTP↔runner      │    │                            │
   └────────────┬─────────────────┘    └──────────────┬──────────────┘    └─────────────┬──────────────┘
                │                                     │                                 │
                │  POST /run + Firebase ID token      │                                 │
                │ ──────────────────────────────────► │                                 │
                │                                     │   runner.run_async(...)         │
                │                                     │ ──────────────────────────────► │
                │                                     │                                 │
                │                                     │ ◄────── async for event ──────  │
                │   SSE: event chunks                 │                                 │
                │ ◄────────────────────────────────── │                                 │
```

Full figure at [_figures/browser_backend_adk.txt](_figures/browser_backend_adk.txt).

## 🛣 Plan

1. **01 WhoOwnsTheSession** — `user_id` from auth, `session_id` mint policy
2. **02 AuthContextPropagation** — Firebase / OIDC / IAP token → `ToolContext`
3. **03 SseFromTheBrowser** — `EventSource`, reconnection, error handling
4. **04 WebSocketsFromBrowser** — bidi for Live, browser-side queue
5. **05 CustomSPApattern** — minimal React/Vue client hitting `adk api_server`
6. **06 A2UIClient** — using the A2UI dev frontend, when/how to customize
7. **07 AGUIBridge** — AG-UI protocol if your frontend already speaks it
8. **08 StreamingPartialResults** — partial tokens vs final, render strategy
9. **09 FileUploadFlow** — multipart from browser → ArtifactService
10. **10 OptimisticUI** — show the tool call while it pends
11. **11 DissectingSample** — `deep-search` end-to-end
12. **12 InProduction** — consolidated checklist
13. **13 KnowledgeCheck** — 7 questions
14. **14 MiniDrill** — build a minimal SPA hitting your M1 agent

After this module: → **[24 Channel Integrations](../24_ChannelIntegrations/)** (Slack, Discord, Google Chat — non-browser clients).

> 🤖 **Tutor:** module 21 is the prereq for *what's on the wire*. This module assumes the student can describe `POST /run` from memory. If not, route them back to 21 before page 01.

[← Prev: 22_Deployment/(last)](../22_DeploymentModels/)  [↑ Map](../../MAP.md)  [Next: 01_WhoOwnsTheSession →](01_WhoOwnsTheSession.md)
