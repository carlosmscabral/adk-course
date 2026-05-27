---
module: 23_FrontendIntegration
page: 03_SseFromTheBrowser
title: SSE from the browser — EventSource, reconnection, errors
estimated_minutes: 25
prereqs: [23_FrontendIntegration/02, 18_StreamingLive/03]
concepts: [EventSource, SSE, reconnect, Last-Event-ID, error_handling]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 02_AuthContextPropagation](02_AuthContextPropagation.md)  [↑ Map](../../MAP.md)  [Next: 04_WebSocketsFromBrowser →](04_WebSocketsFromBrowser.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 03 SSE From The Browser

# 🛠 `EventSource` — six lines, one footgun

Module 18 taught you the SSE server. Now the client. The browser has a one-line API for this:

```javascript
// Work/frontend/sse_min.js — load with <script src="sse_min.js"></script>
const es = new EventSource("/run_sse?session_id=abc&user_id=u1&q=hello");
es.onmessage = (e) => console.log("chunk:", e.data);
es.addEventListener("done", () => es.close());
es.onerror = (e) => console.error("sse error", e);
```

`EventSource` handles framing (`data:`, `\n\n` separators), auto-reconnect, and `Last-Event-ID` resumption. You write none of that.

## Footgun #1 — `EventSource` cannot set custom headers

This is the rough edge. `EventSource` only sends cookies. **You cannot attach `Authorization: Bearer ...`** from the constructor. Your options:

1. **Auth via cookie** — set a session cookie at sign-in, the browser sends it automatically. Fine for same-origin SPAs.
2. **Token in query string** — `?token=...` — works, but tokens land in server access logs. Acceptable for short-lived ID tokens, not refresh tokens.
3. **Polyfill** — libraries like [`@microsoft/fetch-event-source`](https://www.npmjs.com/package/@microsoft/fetch-event-source) wrap `fetch` and let you set headers. Use this for production.

```javascript
// Work/frontend/sse_with_auth.js — polyfill version
import { fetchEventSource } from "@microsoft/fetch-event-source";

await fetchEventSource("/run_sse", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${idToken}`,
  },
  body: JSON.stringify({ user_id, session_id, prompt }),
  onmessage(ev) {
    if (ev.event === "done") return;
    appendToken(JSON.parse(ev.data));
  },
  onerror(err) {
    console.warn("retry", err);
  },
});
```

## A backend that pairs with this client

```python
# Work/23_frontend/sse_server.py — run with: uv run uvicorn Work.23_frontend.sse_server:app --port 8000
import asyncio, json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

agent = Agent(name="chat", model="gemini-2.5-flash", instruction="be helpful and concise")
runner = InMemoryRunner(app_name="chat", agent=agent)

app = FastAPI()

# NOTE: this is a hand-rolled endpoint named `/my_sse` so it can't be confused
# with ADK's built-in `/run_sse` (Module 21). The built-in takes a
# `RunAgentRequest` with `new_message: types.Content` and emits full event JSON
# (see `cli/api_server.py:1499-1506`); the route below uses a simple
# `body["prompt"]` and yields only `p.text`.
@app.post("/my_sse")
async def run_sse(req: Request):
    body = await req.json()
    user_id, session_id, prompt = body["user_id"], body["session_id"], body["prompt"]
    session = await runner.session_service.get_session(
        app_name="chat", user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await runner.session_service.create_session(
            app_name="chat", user_id=user_id, session_id=session_id
        )
    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])

    async def stream():
        async for event in runner.run_async(
            user_id=user_id, session_id=session.id, new_message=msg
        ):
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if p.text:
                        yield f"data: {json.dumps(p.text)}\n\n"
        yield "event: done\ndata: ok\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # disable proxy buffering
    })
```

## Footgun #2 — reconnection storms

`EventSource` reconnects automatically with a ~3s backoff. If your backend is down, every browser tab pounds it every 3s. Backoff yourself or the load comes in flat.

For polyfills: set `openWhenHidden: false` and a custom `onerror` that returns a delay or throws to stop. With native `EventSource`, send a `retry: 10000\n` line from the server to suggest a 10s reconnect interval — clients honor it.

```python
yield "retry: 10000\n\n"  # tell the browser: wait 10s before reconnecting on disconnect
```

## Footgun #3 — proxy buffering

Same warning as page 18/03: behind Nginx/Cloud Run, the proxy may buffer your stream and deliver it all at once. The `X-Accel-Buffering: no` header above disables Nginx buffering. For Cloud Run, the HTTP/2 streaming response works out of the box — *unless* you're using a custom load balancer; then set the equivalent.

> 🚀 **In Production**
>
> SSE keeps an HTTP connection open. On Cloud Run, the per-request timeout is **60 minutes max** (configurable, default smaller). If your agent runs longer than the timeout, the browser disconnects and `EventSource` reconnects — which the server treats as a *new* request. Send checkpoints (event IDs, state writes) so a reconnect can resume gracefully. Or use a polling fallback for long jobs.

> ❓ **Ask the student:** "Why can't `EventSource` set an `Authorization` header? What's the standard workaround?"
>
> (Answer: it's a spec limit, the constructor takes only a URL. Workaround: cookie-based auth, query-string token, or the fetch-event-source polyfill.)

> 🛠 **Have the student run:** the FastAPI server above + a tiny HTML page with the `EventSource` snippet. Watch tokens stream into the DOM. Then `kill` the server mid-stream — see the auto-reconnect attempts in DevTools.

[← Prev: 02_AuthContextPropagation](02_AuthContextPropagation.md)  [↑ Map](../../MAP.md)  [Next: 04_WebSocketsFromBrowser →](04_WebSocketsFromBrowser.md)
