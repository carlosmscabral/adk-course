---
module: 23_FrontendIntegration
page: 04_WebSocketsFromBrowser
title: WebSockets from the browser — bidi for Live
estimated_minutes: 25
prereqs: [23_FrontendIntegration/03, 18_StreamingLive/02]
concepts: [WebSocket, bidi, LiveRequestQueue, binary_frames, reconnect]
icon: 🛠
in_production: true
detours_suggested: [WebSockets]
---

[← Prev: 03_SseFromTheBrowser](03_SseFromTheBrowser.md)  [↑ Map](../../MAP.md)  [Next: 05_CustomSPApattern →](05_CustomSPApattern.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 04 WebSockets From Browser

# 🛠 When you outgrow SSE

SSE is server→client only. The moment you need **microphone audio going up** or **typed input mid-stream** (cancel, barge-in), you need bidirectional. That's WebSocket.

ADK Live uses bidi under the hood (gRPC server-side, page 18/02). When your client is a browser, you wrap that as a WebSocket from browser → your FastAPI → `runner.run_live()`.

## Browser side — a 12-line client

```javascript
// Work/frontend/ws_min.js
const ws = new WebSocket(`wss://${location.host}/live?session_id=abc&user_id=u1`);
ws.binaryType = "arraybuffer";

ws.onopen = () => console.log("open");
ws.onmessage = (ev) => {
  // server sends JSON events with text or audio b64
  const msg = JSON.parse(ev.data);
  if (msg.text) appendText(msg.text);
  if (msg.audio) playAudio(atob(msg.audio));
};
ws.onclose = () => console.log("closed");
ws.onerror = (e) => console.error(e);

// send typed input
function send(text) {
  ws.send(JSON.stringify({ type: "text", value: text }));
}
```

## Server side — the FastAPI WebSocket → ADK Live bridge

This is the canonical shape from `realtime-conversational-agent/server/main.py`:

```python
# Work/23_frontend/ws_server.py — run with: uv run uvicorn Work.23_frontend.ws_server:app --port 8000
import asyncio, json, base64
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = Agent(name="live_demo", model="gemini-2.5-flash", instruction="be conversational")
app = FastAPI()

async def start(user_id: str):
    runner = InMemoryRunner(app_name="live_demo", agent=agent)
    session = await runner.session_service.create_session(app_name="live_demo", user_id=user_id)
    queue = LiveRequestQueue()
    config = RunConfig(streaming_mode="bidi", response_modalities=["TEXT"])
    # session= is the legacy signature; user_id+session_id is the new preferred form
    # (runners.py:1519-1527). The realtime-conversational-agent sample still uses
    # session= too — flagged here for awareness.
    events = runner.run_live(session=session, live_request_queue=queue, run_config=config)
    return events, queue

async def agent_to_client(ws: WebSocket, events):
    async for event in events:
        if not event.content:
            continue
        for part in event.content.parts:
            if part.text:
                await ws.send_text(json.dumps({"text": part.text, "partial": event.partial}))

async def client_to_agent(ws: WebSocket, queue: LiveRequestQueue):
    while True:
        msg = await ws.receive_text()
        data = json.loads(msg)
        if data["type"] == "text":
            queue.send_content(types.Content(role="user", parts=[types.Part(text=data["value"])]))
        # audio: queue.send_realtime(Blob(mime_type="audio/pcm", data=...))

@app.websocket("/live")
async def live(ws: WebSocket):
    await ws.accept()
    user_id = ws.query_params.get("user_id", "anon")
    events, queue = await start(user_id)
    try:
        await asyncio.gather(agent_to_client(ws, events), client_to_agent(ws, queue))
    except WebSocketDisconnect:
        queue.close()
```

Two coroutines, one for each direction, joined with `gather()`. When the WebSocket disconnects, close the queue — that signals `run_live()` to stop.

## Auth on WebSocket

Same problem as `EventSource`: the WebSocket constructor in browsers doesn't take headers. Workarounds:

1. **Sec-WebSocket-Protocol abuse** — pass token as sub-protocol: `new WebSocket(url, ["bearer", idToken])`. Server reads `request.headers["Sec-WebSocket-Protocol"]`. Common; spec-legal; tokens appear in proxy logs less often than query strings.
2. **Cookie** — same as SSE; if the WS endpoint is same-origin, the browser sends auth cookies.
3. **First-message handshake** — open the socket unauthenticated, first frame is `{type: "auth", token: ...}`, server verifies and only then starts streaming.

## Reconnect

WebSocket does **not** auto-reconnect. You write that loop yourself:

```javascript
function connect() {
  const ws = new WebSocket(url);
  ws.onclose = () => setTimeout(connect, 3000);  // dumbest possible backoff
  return ws;
}
```

For prod: exponential backoff capped at ~30s, plus a circuit breaker on repeated failures. Library: [`reconnecting-websocket`](https://github.com/joewalnes/reconnecting-websocket).

> 🚀 **In Production**
>
> Cloud Run supports WebSockets up to its request timeout (60 min max). Long-lived bidi sessions need either: chunked sessions with reconnect+resume, or move to GKE / Compute Engine where you control the connection lifetime. For Live agents in prod, plan for session resumption (`session_resumption=types.SessionResumptionConfig(transparent=True)` in `RunConfig` — see `realtime-conversational-agent`).

> 🧭 **If the student looks stuck:** suggest detour [[WebSockets]] — covers the protocol primitives in 25 min.

> ❓ **Ask the student:** "Why does our WebSocket server need *two* coroutines (`agent_to_client` and `client_to_agent`) instead of one loop?"
>
> (Answer: both directions are independent async streams. One coroutine doing `recv` blocks on the client; one doing `async for event` blocks on the agent. `gather` runs both.)

> 🛠 **Have the student run:** the `ws_server.py` + the `ws_min.js` in an HTML page. Send a typed message, see the agent reply stream in. Close the browser tab — confirm the server-side coroutines exit cleanly.

[← Prev: 03_SseFromTheBrowser](03_SseFromTheBrowser.md)  [↑ Map](../../MAP.md)  [Next: 05_CustomSPApattern →](05_CustomSPApattern.md)
