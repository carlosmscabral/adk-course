---
module: 18_StreamingLive
page: 08_DissectingLiveSample
title: Dissecting bidi-demo — every line, end to end
estimated_minutes: 45
prereqs: [18_StreamingLive/07]
concepts: [bidi-demo, websocket-endpoint, upstream-task, downstream-task]
icon: 🛠
in_production: true
---

[← Prev: 18_StreamingLive/07_LiveProductionPatterns]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/09_InProduction →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 08 Dissecting bidi-demo

## The sample

`/home/carloscabral/study/adk-samples/python/agents/bidi-demo/`

Layout:

```
bidi-demo/
├── app/
│   ├── main.py                       # FastAPI + WebSocket endpoint   ← read this
│   ├── google_search_agent/agent.py  # the Agent definition           ← read this
│   └── static/                       # browser-side audio worklets
├── agent_engine/
│   ├── deploy.py / test.py / cleanup.py   # Vertex Agent Engine bidi
└── README.md
```

> 🛠 **Have the student open** `bidi-demo/app/main.py` in their editor and follow along page-by-page.

## Stage 1: app init (main.py:37-54)

```python
APP_NAME = "bidi-demo"
app = FastAPI()
session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)
```

One agent, one runner, one session service, **shared across all connections**. Each WebSocket connection later gets its own session inside that service.

## Stage 2: connection setup (main.py:72-168)

```python
@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket, user_id, session_id, ...):
    await websocket.accept()
    # ... pick AUDIO vs TEXT response modality from model name
    run_config = RunConfig(streaming_mode=StreamingMode.BIDI, ...)
    session = await session_service.get_session(...)
    if not session:
        await session_service.create_session(...)
    live_request_queue = LiveRequestQueue()
```

Three things created per connection: the `RunConfig`, the session, and the `LiveRequestQueue`. The queue lives only as long as the WebSocket.

> ❓ **Ask the student:** "Why detect AUDIO vs TEXT from the model name and not let the client pick?" (Native-audio models only support AUDIO. Half-cascade picks TEXT for lower latency. The model dictates valid modalities; the client doesn't get a choice.)

## Stage 3: the two concurrent tasks (main.py:174-244)

`upstream_task`: WebSocket → `LiveRequestQueue`.

```python
async def upstream_task():
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            audio_blob = types.Blob(mime_type="audio/pcm;rate=16000",
                                    data=message["bytes"])
            live_request_queue.send_realtime(audio_blob)
        elif "text" in message:
            json_message = json.loads(message["text"])
            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content)
            elif json_message.get("type") == "image":
                image_data = base64.b64decode(json_message["data"])
                image_blob = types.Blob(mime_type=..., data=image_data)
                live_request_queue.send_realtime(image_blob)
```

Three branches: binary frame = audio, JSON text = content, JSON image = blob. Note `send_realtime` for streaming media, `send_content` for whole text turns.

`downstream_task`: `runner.run_live()` → WebSocket.

```python
async def downstream_task():
    async for event in runner.run_live(
        user_id=user_id, session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    ):
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)
```

That's it. The model emits an event, we serialize it and ship it. **All the streaming complexity is inside `run_live`.**

## Stage 4: orchestration + cleanup (main.py:246-265)

```python
try:
    await asyncio.gather(upstream_task(), downstream_task())
except WebSocketDisconnect:
    logger.debug("Client disconnected normally")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
finally:
    live_request_queue.close()
```

`asyncio.gather` runs both tasks. If either raises, the other is cancelled. The `finally` always closes the queue — that's what tells `run_live` to wind down.

## ASCII

See `_figures/live_topology.txt` for the box diagram. The two tasks + queue map directly onto the two arrows.

## Where to look next

- `bidi-demo/app/static/js/pcm-recorder-processor.js` — browser-side AudioWorklet that does the same int16 conversion you saw in page 04, but in JavaScript.
- `bidi-demo/agent_engine/test.py` — the same client pattern, but talking to a deployed Agent Engine instead of a local FastAPI.
- `realtime-conversational-agent/server/main.py` — same architecture, more elaborate event-routing logic (input vs output transcription split, voice config).

> 🤖 **Tutor:** ask the student to point at the line in `main.py` where:
>   (a) audio bytes leave the client and enter the queue,
>   (b) model events leave the queue and reach the client,
>   (c) the queue gets closed on disconnect.
>
> If they can't, re-read stage 3 together.

[← Prev: 18_StreamingLive/07_LiveProductionPatterns]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/09_InProduction →]
