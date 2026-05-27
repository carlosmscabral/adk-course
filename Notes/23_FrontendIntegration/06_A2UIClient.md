---
module: 23_FrontendIntegration
page: 06_A2UIClient
title: A2UI / adk web — the dev frontend, and customizing it
estimated_minutes: 20
prereqs: [23_FrontendIntegration/05]
concepts: [adk_web, a2ui, dev_ui, customization, embedded_iframe]
icon: 🛠
in_production: false
detours_suggested: [a2UI]
---

[← Prev: 05_CustomSPApattern](05_CustomSPApattern.md)  [↑ Map](../../MAP.md)  [Next: 07_AGUIBridge →](07_AGUIBridge.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 06 A2UI Client

# 🛠 The pre-built frontend

You don't have to write the SPA from page 05 to *test* an agent. ADK ships **`adk web`** — a pre-built dev frontend that gives you chat, event timeline, state inspector, and artifact browser, against any local agent. Same wire as your custom client.

Detour `[[a2UI]]` covers the tour. This page covers **when to use it, when to outgrow it, and how to embed it**.

## When to use it (dev only)

- Building an agent and want to *see* the events without writing JS.
- Debugging a state mutation — the state inspector flashes changes.
- Showing teammates an agent over screen-share.
- Sanity-checking a deployment by pointing `adk web --api-endpoint https://...` at it.

```bash
# from the dir containing your agent package
adk web --port 8001
# open http://localhost:8001
```

## When to outgrow it

- Your users expect *your* brand, not Google's.
- You need custom rendering (markdown tables, code blocks with copy buttons, latex).
- You need optimistic UI for tool calls (page 10 in this module).
- You need to gate by org-specific permissions.

The migration is straightforward — `adk web` is itself just a SPA hitting the same `adk api_server` endpoints from page 05. You build your own client against the same surface.

## Customization paths (in order of effort)

### 1. Override the agent card / branding via env

`adk web` reads a small set of env vars for branding (logo, accent color). Cheap; doesn't change layout.

### 2. Embed `adk web` in your app

If you want *some* parts of your UI to be custom and the chat to stay stock, iframe `adk web`:

```html
<!-- Work/frontend/embed_adkweb.html -->
<iframe
  src="http://localhost:8001?agent=my_agent"
  width="100%"
  height="600"
  style="border: 0"
></iframe>
```

Pass through user identity via query params. The dev UI honors them.

### 3. Fork and modify

`adk web` is a Vite/React build that ships with ADK. You can clone it and modify. **This is rarely the right call** — you're forking a dev tool to use in prod. Build fresh against the API instead.

### 4. Build your own (the production path)

This is page 05 / page 11's deep-search dissection. Build a real SPA against `adk api_server` (or your own `get_fast_api_app` wrapper).

## A2UI vs your custom SPA — the wire is the same

```
   ┌──────────────────────┐                      ┌─────────────────────┐
   │   adk web (dev UI)   │ ───── same wire ─────│  your custom SPA    │
   │  - chat + timeline   │                      │  - your branding    │
   │  - state inspector   │                      │  - custom render    │
   └──────────┬───────────┘                      └──────────┬──────────┘
              │                                             │
              └──────────── POST /run_sse ──────────────────┘
                       (and friends from module 21)
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ adk api_server   │
                         │   or your        │
                         │ get_fast_api_app │
                         └──────────────────┘
```

You can swap between them at any point — even mid-session — because the session is server-side. A user can start a conversation in `adk web` and continue in your SPA so long as they hit the same backend with the same `user_id` / `session_id`.

> 🚀 **In Production**
>
> `adk web` is dev-only. It has no auth, accepts any `user_id`, and exposes session contents to whoever can reach it. Lock the port to localhost; don't deploy it. The standard prod pattern is: your own SPA (page 05/11) + `get_fast_api_app(web=False)` wrapped with auth.

> ❓ **Ask the student:** "Why would you embed `adk web` in an iframe instead of just linking to it as a separate page?"
>
> (Answer: same-session cookies, shared layout/nav, single-app feel. Trade-off: iframe sandboxing limits what your outer app can do with the chat.)

> 🛠 **Have the student run:** `adk web` in their agent dir, then immediately run the page 05 SPA against the *same* backend. Confirm both see the same session list.

[← Prev: 05_CustomSPApattern](05_CustomSPApattern.md)  [↑ Map](../../MAP.md)  [Next: 07_AGUIBridge →](07_AGUIBridge.md)
