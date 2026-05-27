---
module: 21_AdkApiSurface
page: 05_WebSocketsForLive
title: WebSockets — /run_live for bidi voice/video
estimated_minutes: 25
prereqs: [21_AdkApiSurface/04, 18_StreamingLive/02]
concepts: [WebSocket, /run_live, LiveRequest, Event JSON, RunConfig.response_modalities]
icon: 🎙
in_production: true
detours_suggested: [WebSockets, AudioEncoding]
---

[← Prev: 04_SseEndpoints](04_SseEndpoints.md)  [↑ Map](../../MAP.md)  [Next: 06_WrappingInFastAPI →](06_WrappingInFastAPI.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 05 WebSockets for Live

---

## 🎙 Why WebSockets

SSE is one-way (server→client) and text-only. The Live API needs **bidi**: client streams microphone frames *up*, server streams TTS audio *down*. That's a WebSocket.

```
client                                server
  │── WS upgrade /run_live?... ─────▶ │  (identifiers in query string)
  │── LiveRequest{content=...} ────▶ │  text turn
  │ ◀── Event{content=..., partial=true}  │  streaming model tokens / TTS chunks
  │ ◀── Event{content=..., partial=false} │  final aggregated chunk
  │── LiveRequest{blob=...} ───────▶ │  realtime audio bytes
  │ ◀── Event{turnComplete: true}     │  end of model turn
  │── LiveRequest{close=true} ─────▶ │  client teardown
```

## 🎙 The endpoint

```
WEBSOCKET /run_live?app_name=<a>&user_id=<u>&session_id=<s>&modalities=AUDIO&modalities=TEXT
```

Path is `/run_live`. **All identifiers and `RunConfig` knobs are query-string parameters** because you cannot send a JSON body before the WS handshake. The handler signature lives in `src/google/adk/cli/api_server.py` around line 1517:

| Query param | Type / default | What it does |
|---|---|---|
| `app_name` | str, optional | Falls back to `ADK_DEFAULT_APP_NAME` env var. |
| `user_id` | str, required | — |
| `session_id` | str, required | Must already exist; otherwise the WS closes with 1002. |
| `modalities` | repeatable, default `AUDIO` | One or more of `TEXT`/`AUDIO`. Pass `&modalities=` multiple times. |
| `proactive_audio` | bool, optional | Model speaks unprompted when relevant. |
| `enable_affective_dialog` | bool, optional | Tone-aware Live mode. |
| `enable_session_resumption` | bool, optional | Transparent reconnect across short drops. |
| `save_live_blob` | bool, default `false` | Persist incoming audio blobs into the session. |

After the upgrade succeeds the session must already exist (POST it via REST first — page 07). The server then streams in both directions.

## 🎙 The wire protocol — `LiveRequest` in, `Event` out

ADK does **not** speak the raw Gemini Live protocol on this socket. It speaks ADK's own `LiveRequest` Pydantic model on the way in, and emits ADK `Event` JSON on the way out. The transcoding into Gemini Live happens inside `runner.run_live(...)` on the server.

> ⚠️ **DO NOT** send `{"setup": {...}}`, `{"realtime_input": ...}`, or expect `{"setup_complete": ...}` / `{"server_content": ...}` frames here — that is the Gemini Live native wire and it is *not* what `/run_live` accepts. If you want raw Gemini Live, talk to the Vertex AI endpoint directly; ADK's `/run_live` is a different layer.

### Client → server: `LiveRequest`

Defined in `src/google/adk/agents/live_request_queue.py` (lines 26–57). Exactly one of these top-level fields per frame:

```json
// Text turn (turn-by-turn mode)
{"content": {"role": "user", "parts": [{"text": "Say hi in three words."}]}}

// Realtime audio chunk (microphone frame, base64-encoded PCM)
{"blob": {"mimeType": "audio/pcm", "data": "<base64-pcm-16khz>"}}

// User starts speaking (manual VAD)
{"activityStart": {}}

// User stops speaking (manual VAD)
{"activityEnd": {}}

// Tear down the input queue cleanly
{"close": true}
```

Priority when multiple fields are set: `activity_start > activity_end > blob > content` (see the docstring on `LiveRequest`).

The server JSON-validates each incoming message with `LiveRequest.model_validate_json(data)` — anything that doesn't match is logged and dropped.

### Server → client: `Event`

The server pulls events from `runner.run_live(...)` and writes each one via `event.model_dump_json(exclude_none=True, by_alias=True)`. Field names arrive in **camelCase** (e.g. `invocationId`, `turnComplete`, `functionCall`). Useful fields on each event:

- `author` — `"user"` or the agent's name.
- `content.parts[]` — text / inlineData (audio) / functionCall / functionResponse.
- `partial` — `true` while the model is still streaming this content; `false` (or absent) on the aggregated final chunk.
- `turnComplete` — `true` on the event that closes the model's turn.
- `interrupted` — `true` if the user barged in mid-response.

So an interactive client typically: dispatches on `partial`/`turnComplete` for UI updates, plays any `inlineData` audio chunks immediately, and breaks the loop when `turnComplete` arrives.

## 🎙 A minimal Python client

```python
# Work/21_AdkApiSurface/05_ws_text_only.py — run with: uv run python Work/21_AdkApiSurface/05_ws_text_only.py
# Pre-req:
#   1. adk api_server Work/21_AdkApiSurface --port 8000
#   2. curl -X POST http://localhost:8000/apps/research_assistant/users/alice/sessions/ws-001 \
#        -H "content-type: application/json" -d "{}"
import asyncio
import json

import websockets

URL = (
    "ws://localhost:8000/run_live"
    "?app_name=research_assistant"
    "&user_id=alice"
    "&session_id=ws-001"
    "&modalities=TEXT"
)


async def main() -> None:
    async with websockets.connect(URL) as ws:
        # Send one text turn as a LiveRequest (NOT a Gemini-Live "setup" frame).
        await ws.send(
            json.dumps(
                {
                    "content": {
                        "role": "user",
                        "parts": [{"text": "Say hi in three words."}],
                    }
                }
            )
        )

        # Read ADK Event JSON until the model marks its turn complete.
        async for raw in ws:
            event = json.loads(raw)
            for part in (event.get("content") or {}).get("parts", []) or []:
                if "text" in part:
                    suffix = "" if event.get("partial") else "\n"
                    print(part["text"], end=suffix, flush=True)
            if event.get("turnComplete"):
                break

        # Drain the queue cleanly.
        await ws.send(json.dumps({"close": True}))


asyncio.run(main())
```

```
$ uv run python Work/21_AdkApiSurface/05_ws_text_only.py
Hi there friend!
```

(Pure-text Live is rarely useful in production — the value is bidi audio. This example proves the wire shape without needing a microphone.)

## 🎙 Audio in: `LiveRequest.blob`

For voice you flip two things: request `&modalities=AUDIO` in the query string, and stream microphone frames as `{"blob": {"mimeType": "audio/pcm", "data": "<base64>"}}` LiveRequests. The server forwards each blob into the Live session via `LiveRequestQueue.send_realtime(...)`. The model's reply lands back as `Event`s whose `content.parts[].inlineData` carries base64 audio chunks plus (optionally) a text caption.

Cross-link [[AudioEncoding]] for the exact PCM/Opus framing and sample-rate rules.

## ⚠️ Gotcha — Cloud Run WS timeouts

Cloud Run supports WebSockets but caps them at **15 minutes per connection** (request-timeout maximum is 60 min, but bidirectional idle is shorter in practice). For longer voice sessions you must:

- Periodically reconnect and resume from session state.
- Or deploy on **Agent Engine** (no 15-min cap) or **GKE** (you set the cap).

Cross-link: module **22 Deployment Models** page 05 on Live constraints per platform.

## ⚠️ Gotcha — load balancers

L7 load balancers (Cloud Load Balancing, AWS ALB) need WebSocket support explicitly enabled. The default HTTP/1.1 path strips the Upgrade header. Symptom: handshake works, first frame stalls. Fix: enable WS on the backend service.

## ⚠️ Gotcha — session must exist before connect

If you open the WS against a `session_id` the service-side `SessionService` doesn't know about, the server closes the socket with code `1002` ("Session not found"). Always POST the session via REST (page 07) before opening the WS.

## 🎙 Modalities matrix

| Modality client sends | `modalities` query param | Use                                   |
|-----------------------|--------------------------|---------------------------------------|
| TEXT                  | `TEXT`                   | Chat (use SSE instead unless you need WS). |
| AUDIO                 | `AUDIO`                  | Pure voice agent.                     |
| AUDIO                 | `TEXT&modalities=AUDIO`  | Voice in, voice + caption out (the common case). |
| VIDEO + AUDIO         | `AUDIO`                  | Multimodal (vision + voice in, voice out). |

The server enforces what the underlying model can do. Gemini 2.5 Flash Live supports audio in/out and text-only-input. Cross-link [[AudioEncoding]] for the PCM format details.

## 🚀 In Production

> **🚀 In Production**
>
> WebSocket connections are **stateful per pod**. Standard horizontal scaling falls down — a reconnect after a pod restart loses the live audio context. Two production patterns: (1) terminate WS at an edge that handles reconnect and resume, then proxy to the agent over a fresh connection; (2) deploy on **Agent Engine**, which handles reconnect/resume natively. For self-hosted voice on Cloud Run / GKE, plan the reconnect protocol *before* you ship.

> 🧭 **If the student looks stuck:** suggest detour [[WebSockets]] — covers the protocol primitives and load-balancer caveats in 20 min.

---

[← Prev: 04_SseEndpoints](04_SseEndpoints.md)  [↑ Map](../../MAP.md)  [Next: 06_WrappingInFastAPI →](06_WrappingInFastAPI.md)
