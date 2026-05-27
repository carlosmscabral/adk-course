---
module: 21_AdkApiSurface
page: 00_Overview
title: Overview — what ADK exposes over the wire
estimated_minutes: 10
prereqs: [04_SessionsState/08, 15_Observability/10]
concepts: [adk run, adk web, adk api_server, FastAPI, SSE, websockets]
icon: 🌐
in_production: true
detours_suggested: [FastAPI_for_ADK]
---

[← Prev: 20_FrameworkComparison/99_ChoosingAFramework](../20_FrameworkComparison/99_ChoosingAFramework.md)  [↑ Map](../../MAP.md)  [Next: 01_AdkRunCli →](01_AdkRunCli.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 00 Overview

---

## 🌐 What you'll learn

By the end of this module you will:

- Know every entry point ADK ships: `adk run`, `adk web`, `adk api_server`, `adk eval`, `adk create`, `adk deploy`.
- Read the **real call graph** behind `adk run` and `adk web` — what classes get instantiated, what defaults apply, what hot-reload actually does.
- Hit the HTTP API by hand: `POST /run`, `POST /run_sse` for streaming, `GET/POST /apps/{app}/users/{user}/sessions`.
- Distinguish **JSON `/run`** (single-shot), **SSE `/run_sse`** (streaming text events), and **WS `/run_live`** (bidi voice/video).
- Wrap an ADK App inside your own FastAPI process with `get_fast_api_app(...)`.
- Add auth at the API boundary — IAP, OIDC token verification, custom middleware.

## 🧭 Prereqs

- **04 SessionsState** — you must know that every API call needs `app_name`, `user_id`, `session_id`. The wire format mirrors that triple exactly.
- **15 Observability** — once you serve over HTTP you will want traces. We re-use the wiring from there.

## ⏱ Time budget

**1.5 days.** Half a day on pages 01-01C (the CLI under the hood). Half a day on pages 02-08 (HTTP shapes, SSE, WS, FastAPI wrap, auth). The last half day is the dissection plus mini-drill.

## 📦 Sample anchor

`/home/carloscabral/study/adk-samples/python/agents/currency-agent/` — exposes the same `LlmAgent` three ways: `adk run` (REPL), `adk web` (browser UI), and an A2A server built from `to_a2a(root_agent, port=10000)`. We read the surface in [09_DissectingSample](09_DissectingSample.md).

## 🗺 Page map

| #   | Page                            | Why                                                              |
|-----|---------------------------------|------------------------------------------------------------------|
| 01  | AdkRunCli                       | The shortest path to a live agent.                               |
| 01A | AdkRunUnderTheHood              | The actual call graph from `argv` to first event.                |
| 01B | AdkWebUnderTheHood              | What the dev UI does behind the browser.                         |
| 01C | FullCliFamily                   | `run`, `web`, `api_server`, `eval`, `create`, `migrate`, `deploy`. |
| 02  | AdkApiServer                    | The headless server: ports, mounts, root path.                   |
| 03  | RestShapes                      | `/run`, `/sessions`, the event JSON shape.                       |
| 04  | SseEndpoints                    | Streaming events with `/run_sse`.                                |
| 05  | WebSocketsForLive               | Bidi voice/video on `/run_live`.                                 |
| 06  | WrappingInFastAPI               | Owning the process — `get_fast_api_app(...)`.                    |
| 07  | SessionAndEventResources        | The session + event REST resources in detail.                    |
| 08  | AuthenticatingTheApi            | IAP, OIDC, custom middleware.                                    |
| 09  | DissectingSample                | Read `currency-agent` served three ways.                         |
| 10  | InProduction                    | The hardening checklist.                                         |
| 11  | KnowledgeCheck                  | 7 questions.                                                     |
| 12  | MiniDrill                       | Stand up `/run_sse` for the M4 auditor and consume from `curl`.  |

> 🤖 **Tutor:** Before page 01, ask the student to recall the last `runner.run_async()` loop they wrote by hand (from module 04). The whole point of this module is: *the CLI and the HTTP server are just two thin wrappers around that same loop*. Anchor every concept on that loop.

> 🚀 **In Production**
>
> Don't ship `adk run` or `adk web` to prod. They are dev surfaces — single-process, no auth, no quotas. The deployable target is `adk api_server` (or `get_fast_api_app()` inside your own process) behind a real ingress. Module **22 Deployment Models** picks up from there.

---

[← Prev: 20_FrameworkComparison/99_ChoosingAFramework](../20_FrameworkComparison/99_ChoosingAFramework.md)  [↑ Map](../../MAP.md)  [Next: 01_AdkRunCli →](01_AdkRunCli.md)
