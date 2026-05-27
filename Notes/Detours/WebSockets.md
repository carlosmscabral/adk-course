---
module: Detours
page: WebSockets
title: WebSockets — the bidirectional cousin of HTTP
estimated_minutes: 20
prereqs: []
concepts: [WebSocket, frame, ping-pong, close-code, SSE-comparison]
icon: 🌐
---

[← Triggered from: 18_StreamingLive/03_TextStreaming, 18_StreamingLive/06_VideoInput]  [↑ Map](../MAP.md)

You are here: 🗺 Detours ▸ WebSockets

> 🧭 **This is optional.** Take it if WebSockets feel hand-wavy. 20 min. Comes back to module 18.

## What WebSockets are

A WebSocket is a **persistent, bidirectional byte-stream over a single TCP connection**, started by upgrading an HTTP/1.1 request. After the handshake, the protocol is no longer HTTP — it's a framed message protocol where both sides can send anytime.

```
Client                                Server
  │  GET /ws HTTP/1.1                   │
  │  Upgrade: websocket               ──▶│
  │  Sec-WebSocket-Key: ...             │
  │                                     │
  │   HTTP/1.1 101 Switching Protocols  │
  │◀── Upgrade: websocket               │
  │                                     │
  │  ── frame (text)  "hello" ───────▶ │
  │  ◀─ frame (text)  "hi" ──────────  │
  │  ── frame (binary)  <bytes> ─────▶ │
  │  ◀─ ping ───────────────────────── │
  │  ── pong ────────────────────────▶ │
  │  ── close 1000 ──────────────────▶ │
```

## Frames

Two types you care about: **text** (UTF-8) and **binary** (arbitrary bytes). The protocol also has control frames: **ping**, **pong**, **close**. RFC 6455 allows a frame payload up to 2^63 bytes — there is **no 64 KB cap in the protocol itself**. Individual libraries impose their own caps for memory safety: the Python `websockets` library defaults to `max_size=2**20` (1 MiB) per message and will fragment messages above its `write_limit` into continuation frames. (The "64 KB" figure that circulates in tutorials is the default *fragment* size in some libraries — including older versions of `websockets` — not a protocol limit. Tune `max_size` and `write_limit` on `serve()` / `connect()` if you need larger messages.)

For Gemini Live, the binary frame carries PCM audio bytes. The text frame carries JSON envelopes. You saw both in `bidi-demo/app/main.py:182-227`.

## Ping/pong — heartbeats

Either side can send a ping; the other must respond with a pong (same payload). Used to:
- Detect a half-open TCP connection (router silently dropped state).
- Prevent NAT timeouts (most NATs close idle UDP/TCP after 5-60 min).

Most libraries do this automatically every 20-30 s. Tune up if you have hostile middleboxes.

## Close codes

A close frame carries a uint16 code. Memorize three:

- **1000** — Normal closure. Either side said "I'm done."
- **1001** — Going away. Server shutdown, page navigation, etc.
- **1006** — Abnormal closure (no close frame received). **Network problem**, not the application. This is the one your reconnection logic should retry on.

The full registry is at IANA but those three cover 95% of what you'll see.

## WebSocket vs SSE vs HTTP/2 streaming

| | SSE | WebSocket | HTTP/2 server push |
|---|---|---|---|
| Direction | server → client only | bidi | server → client only |
| Wire | plain HTTP/1.1, `text/event-stream` | upgraded TCP frames | HTTP/2 frames |
| Browser support | `EventSource` native | `WebSocket` native | being deprecated |
| Behind proxies | usually fine | usually fine, sometimes blocked | varies |
| Audio/binary | no (text only) | yes | yes |

For streaming text replies: **SSE** is the right default.
For Live voice/video bidi: you need **WebSocket** (or gRPC).
HTTP/2 server push: don't bother in 2026, it's effectively dead.

## Why does Live use WebSockets *or* gRPC?

gRPC's bidi streaming is built on HTTP/2. From a Python server, gRPC is more efficient and the natural choice — what the Vertex AI SDK uses. From a browser, gRPC over HTTP/2 is awkward (browsers can't speak gRPC natively; you need gRPC-Web). So Google exposes a **WebSocket transport** for browser clients of the same Live backend.

The `bidi-demo` browser client uses WebSocket to talk to the FastAPI server, and the FastAPI server uses ADK (which uses gRPC under the hood) to talk to Vertex.

## Minimal Python echo server + client

```python
# server.py — `pip install websockets`
import asyncio, websockets

async def echo(ws):
    async for msg in ws:
        await ws.send(f"echo: {msg}")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
```

```python
# client.py
import asyncio, websockets

async def main():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send("hello")
        print(await ws.recv())   # echo: hello

asyncio.run(main())
```

That's the whole protocol from your code's POV: send and receive.

## 🧪 Mini-exercise

Modify the echo server above to:
1. Send a ping every 5 s and log when it gets the pong.
2. On a `WebSocketDisconnect` with code 1006, log a warning (the others log info).
3. Run the client in another terminal, then kill it with Ctrl-C and watch the server output.

Bonus: have the client send a 100 KB binary payload (`b'\x00' * 100000`) and confirm the server receives it intact.

## Back to module 18

- For text streaming, you actually don't need WebSockets — SSE in `03_TextStreaming` is simpler.
- For voice/video Live, the WebSocket layer is exactly what `bidi-demo/app/main.py` puts between the browser and the ADK runner. With this detour done, you should read that file as "WebSocket frame in → blob to queue → event from runner → JSON frame out."

[← Back: 18_StreamingLive/03_TextStreaming](../18_StreamingLive/03_TextStreaming.md) · [Back: 18_StreamingLive/06_VideoInput](../18_StreamingLive/06_VideoInput.md)  [↑ Map](../MAP.md)
