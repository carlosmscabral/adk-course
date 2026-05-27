---
module: 23_FrontendIntegration
page: 05_CustomSPApattern
title: A minimal SPA hitting adk api_server
estimated_minutes: 25
prereqs: [23_FrontendIntegration/04, 21_ApiSurface/02]
concepts: [SPA, adk_api_server, CORS, REST_client, no_framework]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_WebSocketsFromBrowser](04_WebSocketsFromBrowser.md)  [↑ Map](../../MAP.md)  [Next: 06_A2UIClient →](06_A2UIClient.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 05 Custom SPA Pattern

# 🛠 The smallest custom client

`adk api_server` (module [21](../21_ApiSurface/)) exposes a JSON HTTP surface: `POST /apps/{app}/users/{user}/sessions`, `POST /run`, `POST /run_sse`, `GET /apps/{app}/users/{user}/sessions`. That's enough to build a chat UI in **one HTML file**.

We'll keep it framework-free — when you wrap it in React/Vue/Svelte the logic is identical, just typed and componentized.

## Start the backend

```bash
# from any directory containing an ADK agent package (one with __init__.py + agent.py)
adk api_server --port 8000
# CORS is permissive by default in api_server; for prod, lock it down (see below).
```

## The whole client — one HTML file

```html
<!-- Work/frontend/spa_min.html — open with: python -m http.server 9000 then http://localhost:9000/spa_min.html -->
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>adk SPA</title></head>
  <body>
    <input id="prompt" placeholder="ask..." style="width:80%">
    <button id="send">Send</button>
    <pre id="out"></pre>

    <script>
      const API = "http://localhost:8000";
      const APP = "my_agent";       // matches your agent package dir name
      const USER = "user-abc";
      let SESSION = null;

      async function ensureSession() {
        if (SESSION) return SESSION;
        const r = await fetch(`${API}/apps/${APP}/users/${USER}/sessions`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: "{}",
        });
        const s = await r.json();
        SESSION = s.id;
        return SESSION;
      }

      async function send(prompt) {
        const session_id = await ensureSession();
        const out = document.getElementById("out");
        out.textContent += `\n> ${prompt}\n`;
        const r = await fetch(`${API}/run_sse`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            app_name: APP,
            user_id: USER,
            session_id,
            new_message: {role: "user", parts: [{text: prompt}]},
            streaming: true,
          }),
        });
        const reader = r.body.getReader();
        const decoder = new TextDecoder();
        let buf = "";
        while (true) {
          const {value, done} = await reader.read();
          if (done) break;
          buf += decoder.decode(value, {stream: true});
          // naive SSE parse: split on blank line
          const parts = buf.split("\n\n");
          buf = parts.pop();
          for (const chunk of parts) {
            const line = chunk.split("\n").find(l => l.startsWith("data: "));
            if (!line) continue;
            const event = JSON.parse(line.slice(6));
            const text = event?.content?.parts?.[0]?.text;
            if (text) out.textContent += text;
          }
        }
      }

      document.getElementById("send").onclick = () => {
        const p = document.getElementById("prompt").value;
        send(p);
      };
    </script>
  </body>
</html>
```

That's the entire client. Two `fetch` calls, a Readable stream reader for SSE, and a naive parser. Drop it in `Work/frontend/spa_min.html`, point it at a running `adk api_server`, and you have a working chat UI.

## What `adk api_server` gives you

| Endpoint | Purpose |
|---|---|
| `POST /apps/{app}/users/{user}/sessions` | Create session (server-mints) — pattern B from page 01 |
| `POST /apps/{app}/users/{user}/sessions/{sid}` | Create with explicit ID — pattern A |
| `GET /apps/{app}/users/{user}/sessions` | List user's sessions (chat history list) |
| `GET /apps/{app}/users/{user}/sessions/{sid}` | Fetch one session's events (replay) |
| `POST /run` | One-shot, return full response |
| `POST /run_sse` | Stream events as SSE |
| `POST /apps/{app}/users/{user}/sessions/{sid}/artifacts/{name}` | Upload artifact |
| `GET /apps/{app}/users/{user}/sessions/{sid}/artifacts/{name}` | Fetch artifact |

Full reference: module [21_ApiSurface](../21_ApiSurface/).

## CORS

`adk api_server` is permissive in dev. For production deployment you'll be running a custom FastAPI wrapper (or `get_fast_api_app(...)`). Add CORS explicitly:

```python
# Work/23_frontend/cors_app.py
from fastapi.middleware.cors import CORSMiddleware
# app = get_fast_api_app(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-frontend.example.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## What about React / Vue / Svelte?

Wrap the two functions (`ensureSession`, `send`) in a hook/composable. The logic doesn't change. Don't reach for a "AI chat SDK" until you've shipped the vanilla version — the SDKs hide the wire and you'll regret it when something breaks.

> 🚀 **In Production**
>
> Never deploy `adk api_server` directly to the internet. It's a dev tool — no auth, no rate limit, no audit. Instead: `get_fast_api_app(agents_dir=..., web=False)` inside your own FastAPI with auth middleware (page 02), CORS as above, and rate limiting. Module [22_DeploymentModels](../22_DeploymentModels/) covers the Cloud Run wrapping.

> ❓ **Ask the student:** "Why does the snippet call `ensureSession()` lazily on first send instead of in page load?"
>
> (Answer: a user might open the tab and never type. Lazy = no wasted session, no wasted state row in the DB.)

> 🛠 **Have the student run:** the HTML page against `adk api_server`. Type three messages — confirm same session_id is reused. Open a new tab, type one message — confirm a new session_id is minted.

[← Prev: 04_WebSocketsFromBrowser](04_WebSocketsFromBrowser.md)  [↑ Map](../../MAP.md)  [Next: 06_A2UIClient →](06_A2UIClient.md)
