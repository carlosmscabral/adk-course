---
module: 21_AdkApiSurface
page: 04_SseEndpoints
title: SSE — streaming events with /run_sse
estimated_minutes: 25
prereqs: [21_AdkApiSurface/03]
concepts: [Server-Sent Events, text/event-stream, /run_sse, partial events]
icon: 📡
in_production: true
detours_suggested: []
---

[← Prev: 03_RestShapes](03_RestShapes.md)  [↑ Map](../../MAP.md)  [Next: 05_WebSocketsForLive →](05_WebSocketsForLive.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 04 SSE

---

## 📡 Why SSE

`/run` returns the full list at the end of the turn. For a 12-second tool-heavy turn, the user stares at a spinner. SSE turns the same data into a live stream:

```
client                       server
  │── POST /run_sse ─────────▶ │
  │                            │  runner starts
  │ ◀── data: {ev1}             │  event 1 (function_call)
  │ ◀── data: {ev2}             │  event 2 (function_response)
  │ ◀── data: {ev3 "partial"}   │  partial text token
  │ ◀── data: {ev3 "partial"}   │  more tokens
  │ ◀── data: {ev4 "final"}     │  final text
  │ ◀──    (connection close)   │  runner done
```

Each `data:` line is a complete `Event` JSON (same shape as page 03), prefixed per the SSE spec.

## 📡 The endpoint

```
POST /run_sse
Content-Type: application/json
Accept: text/event-stream
```

Same JSON body as `/run`:

```json
{
  "app_name": "research_assistant",
  "user_id": "alice",
  "session_id": "sess-001",
  "new_message": {"role": "user", "parts": [{"text": "..."}]},
  "streaming": true
}
```

Set `"streaming": true` to opt the LLM into per-token partial events. With `false` you still get one event per major step (function_call, function_response, final text) — useful when you want UI progress without token-level updates.

## 📡 Consuming SSE in Python

```python
# Work/21_AdkApiSurface/04_sse_client.py — run with: uv run python Work/21_AdkApiSurface/04_sse_client.py
# Pre-req: adk api_server Work/21_AdkApiSurface --port 8000
import json
import httpx

BASE = "http://localhost:8000"
APP, USER, SESSION = "research_assistant", "alice", "sse-001"

httpx.post(f"{BASE}/apps/{APP}/users/{USER}/sessions/{SESSION}", json={})

body = {
    "app_name": APP,
    "user_id": USER,
    "session_id": SESSION,
    "new_message": {
        "role": "user",
        "parts": [{"text": "Write a 3-line haiku about Toronto winters."}],
    },
    "streaming": True,  # ← per-token partials
}

with httpx.stream("POST", f"{BASE}/run_sse", json=body, timeout=120.0) as r:
    for line in r.iter_lines():
        if not line or not line.startswith("data:"):
            continue
        payload = json.loads(line.removeprefix("data:").strip())
        # partial text events have content.parts[*].text; print them inline
        parts = payload.get("content", {}).get("parts") or []
        for p in parts:
            if "text" in p:
                print(p["text"], end="", flush=True)
print()
```

Expected (the text streams in chunks; final output is a complete haiku):

```
$ uv run python Work/21_AdkApiSurface/04_sse_client.py
Snow falls on Queen Street
Trams crawl through the dimmed white air
February sighs
```

> 🛠 **Have the student run:** the script above. They should see text appear progressively, not all at once. If it appears all at once, the model is too small or too fast to demonstrate streaming — try a longer prompt.

## 📡 `partial` vs final events

When `streaming=true`, the model emits **partial** events (incremental tokens) followed by one **final** event with the full content. The flag is on `event.partial`:

```python
if event.partial:
    # append the delta tokens to the UI buffer
    ...
else:
    # finalize the buffer; this is the canonical text
    ...
```

A safe rendering rule: render `partial` events as tentative (gray, italic), then replace with the `final` event's content on arrival.

## ⚠️ Gotcha — proxy buffering

Many reverse proxies (and load balancers) buffer responses to disk by default. SSE breaks under buffering — clients see nothing until the whole response is done.

- **nginx**: `proxy_buffering off; proxy_cache off;` on the SSE location.
- **Cloud Run**: streaming is supported up to the request-timeout; bump it to 60min if you have long tool calls (default is 5min).
- **CDNs**: most need an explicit "skip cache" header — `Cache-Control: no-cache`.

## ⚠️ Gotcha — JSON parsing

Each `data:` line is **one** complete JSON object, not a fragment. Do not concatenate multiple `data:` lines and `json.loads` the result. The SSE protocol allows multi-line `data:` segments (joined with `\n`), but ADK only emits single-line ones.

## 📡 When to choose SSE vs WebSocket

- **SSE** (this page): one-way server→client, text events, simple HTTP semantics, works through HTTP/2.
- **WebSocket** (page 05): bidi, supports binary (audio/video), needs a different protocol upgrade.

For text agent chat: SSE wins. For voice/video: WebSocket. Mixing is fine — the same server serves both.

## 🚀 In Production

> **🚀 In Production**
>
> Long SSE connections die. Browsers, load balancers, and intermediate proxies will close idle streams after 30-120s. Two mitigations: (1) send a **keepalive comment line** (`: ping\n\n`) every 15s during slow tool calls — SSE clients ignore comment lines; (2) make the client **resumable** by sending the `Last-Event-Id` header on reconnect (you implement the matching server-side support; ADK does not currently track stream cursors).

> ❓ **Ask the student:** "If a tool call takes 90 seconds, how does the client know the stream is alive vs hung?" *(Without keepalives — it can't. Recommend adding a keepalive comment from middleware, page 06.)*

---

[← Prev: 03_RestShapes](03_RestShapes.md)  [↑ Map](../../MAP.md)  [Next: 05_WebSocketsForLive →](05_WebSocketsForLive.md)
