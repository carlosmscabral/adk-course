---
module: 21_AdkApiSurface
page: 05_WebSocketsForLive
title: WebSockets — /run_live for bidi voice/video
estimated_minutes: 25
prereqs: [21_AdkApiSurface/04, 18_StreamingLive/02]
concepts: [WebSocket, /run_live, bidi, audio frames, RunConfig.response_modalities]
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
  │── WS upgrade /run_live ─────────▶ │
  │ ◀── {"setup": ack}                │
  │── {"audio": <pcm frames>} ──────▶ │  user speaking
  │── {"audio": <pcm frames>} ──────▶ │  (continues)
  │ ◀── {"text": "I think..."}        │  model partial reply
  │ ◀── {"audio": <pcm frames>}       │  TTS audio frames
  │ ◀── {"turn_complete": true}       │  end of turn
```

## 🎙 The endpoint

```
WEBSOCKET /run_live?app_name=<a>&user_id=<u>&session_id=<s>&modalities=AUDIO,TEXT
```

Path is `/run_live`. Identifiers come in via query string (you cannot send a JSON body before the WS handshake). After the upgrade succeeds, the server expects a **setup** message followed by streaming message frames.

## 🎙 Setup → frames pattern

```json
// 1. client sends first
{
  "setup": {
    "app_name": "voice_helper",
    "user_id": "alice",
    "session_id": "voice-001",
    "run_config": {
      "response_modalities": ["AUDIO"],
      "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Aoede"}}}
    }
  }
}

// 2. server acks
{"setup_complete": {}}

// 3. client then streams audio chunks
{"realtime_input": {"audio": {"data": "<base64-pcm-16khz>", "mime_type": "audio/pcm"}}}
```

The full protocol mirrors the Gemini Live API gRPC. Module **18 Streaming/Live** covers the audio framing, sample rates, and barge-in mechanics in depth — this page is just about the wire envelope on `/run_live`.

## 🎙 A minimal Python client

```python
# Work/21_AdkApiSurface/05_ws_text_only.py — run with: uv run python Work/21_AdkApiSurface/05_ws_text_only.py
# Pre-req: adk api_server Work/21_AdkApiSurface --port 8000 with a voice-capable agent
import asyncio, json
import websockets

URL = ("ws://localhost:8000/run_live"
       "?app_name=voice_helper&user_id=alice&session_id=ws-001&modalities=TEXT")

async def main():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({
            "setup": {
                "app_name": "voice_helper",
                "user_id": "alice",
                "session_id": "ws-001",
                "run_config": {"response_modalities": ["TEXT"]},
            }
        }))
        ack = json.loads(await ws.recv())
        print("setup:", ack)

        await ws.send(json.dumps({
            "realtime_input": {"text": "Say hi in three words."}
        }))

        async for raw in ws:
            msg = json.loads(raw)
            if "server_content" in msg:
                for p in msg["server_content"].get("model_turn", {}).get("parts", []):
                    if "text" in p:
                        print("model:", p["text"])
                if msg["server_content"].get("turn_complete"):
                    break

asyncio.run(main())
```

```
$ uv run python Work/21_AdkApiSurface/05_ws_text_only.py
setup: {'setup_complete': {}}
model: Hi there friend!
```

(Pure-text Live is rarely useful in production — the value is bidi audio. This example proves the wire shape without needing a microphone.)

## ⚠️ Gotcha — Cloud Run WS timeouts

Cloud Run supports WebSockets but caps them at **15 minutes per connection** (request-timeout maximum is 60 min, but bidirectional idle is shorter in practice). For longer voice sessions you must:

- Periodically reconnect and resume from session state.
- Or deploy on **Agent Engine** (no 15-min cap) or **GKE** (you set the cap).

Cross-link: module **22 Deployment Models** page 05 on Live constraints per platform.

## ⚠️ Gotcha — load balancers

L7 load balancers (Cloud Load Balancing, AWS ALB) need WebSocket support explicitly enabled. The default HTTP/1.1 path strips the Upgrade header. Symptom: handshake works, first frame stalls. Fix: enable WS on the backend service.

## 🎙 Modalities matrix

| Modality client sends | `response_modalities` server returns | Use                                   |
|-----------------------|--------------------------------------|---------------------------------------|
| TEXT                  | TEXT                                 | Chat (use SSE instead unless you need WS). |
| AUDIO                 | AUDIO                                | Pure voice agent.                     |
| AUDIO                 | TEXT, AUDIO                          | Voice in, voice + caption out (the common case). |
| VIDEO + AUDIO         | AUDIO                                | Multimodal (vision + voice in, voice out). |

The server enforces what the underlying model can do. Gemini 2.5 Flash Live supports audio in/out and text-only-input. Cross-link [[AudioEncoding]] for the PCM format details.

## 🚀 In Production

> **🚀 In Production**
>
> WebSocket connections are **stateful per pod**. Standard horizontal scaling falls down — a reconnect after a pod restart loses the live audio context. Two production patterns: (1) terminate WS at an edge that handles reconnect and resume, then proxy to the agent over a fresh connection; (2) deploy on **Agent Engine**, which handles reconnect/resume natively. For self-hosted voice on Cloud Run / GKE, plan the reconnect protocol *before* you ship.

> 🧭 **If the student looks stuck:** suggest detour [[WebSockets]] — covers the protocol primitives and load-balancer caveats in 20 min.

---

[← Prev: 04_SseEndpoints](04_SseEndpoints.md)  [↑ Map](../../MAP.md)  [Next: 06_WrappingInFastAPI →](06_WrappingInFastAPI.md)
