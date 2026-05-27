---
module: 18_StreamingLive
page: 03_TextStreaming
title: Text streaming — tokens to stdout, then SSE to a browser
estimated_minutes: 35
prereqs: [18_StreamingLive/02]
concepts: [run_async, SSE, partial-event, chunk-reassembly]
icon: 🛠
in_production: true
detours_suggested: [WebSockets]
---

[← Prev: 18_StreamingLive/02_GeminiLiveIntro]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/04_AudioIO →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 03 Text Streaming

## The minimal streaming CLI

```python
# stream_cli.py
import asyncio, time
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

agent = Agent(name="streamer", model="gemini-2.5-flash",
              instruction="Be helpful and a little verbose.")
runner = InMemoryRunner(app_name="demo", agent=agent)

async def main():
    session = await runner.session_service.create_session(app_name="demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(text="Explain async iterators in 3 sentences.")])
    # MUST opt into SSE — RunConfig defaults to StreamingMode.NONE, which would
    # give us one final event and no chunks.
    run_config = RunConfig(streaming_mode=StreamingMode.SSE)
    t0 = time.time()
    async for event in runner.run_async(
        user_id="u", session_id=session.id, new_message=msg, run_config=run_config,
    ):
        if not event.content or not event.content.parts:
            continue
        text = event.content.parts[0].text or ""
        tag = "FINAL" if event.turn_complete else "chunk"
        print(f"[{time.time()-t0:5.2f}s {tag}] {text!r}")

asyncio.run(main())
```

Run it. You should see several `[chunk]` lines arriving over the course of a second or two, then one `[FINAL]`.

> 🛠 **Have the student run:** the script above. Then have them paste 2-3 lines of the output here so you can confirm the chunk timestamps are *different* (not all the same value within rounding).

## ASCII

See `_figures/streaming_lifecycle.txt`:

```
client                Runner                  LLM
  |---- user msg ------>|                      |
  |                     |---- prompt --------->|
  |<--- chunk 1 --------|<-- partial chunk 1 --|
  |<--- chunk 2 --------|<-- partial chunk 2 --|
  ...
  |<--- final ----------|<--- final  ----------|
```

## SSE — the simplest web wire format for one-way streaming

SSE = Server-Sent Events. Plain HTTP, plain text, browsers parse it natively with `EventSource`. The wire is just:

```
data: chunk one\n
\n
data: chunk two\n
\n
event: done\n
data: ok\n
\n
```

Each event ends with a blank line. `data:` lines accumulate. Optional `event:` names a type. Done.

> 🧭 **If the student wonders WebSockets vs SSE:** SSE is server→client only and rides plain HTTP — perfect for streaming a model reply. WS is bidirectional and you need it for Live audio. For text streaming a reply, SSE is the right default. If they want detail, suggest detour [[WebSockets]].

## SSE wrapper around `run_async`

```python
# sse_app.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

agent = Agent(name="streamer", model="gemini-2.5-flash")
runner = InMemoryRunner(app_name="sse-demo", agent=agent)
app = FastAPI()

@app.get("/stream")
async def stream(q: str):
    session = await runner.session_service.create_session(app_name="sse-demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(text=q)])
    run_config = RunConfig(streaming_mode=StreamingMode.SSE)

    async def gen():
        async for event in runner.run_async(
            user_id="u", session_id=session.id, new_message=msg,
            run_config=run_config,
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text or ""
                if text:
                    # SSE: data lines + blank line separator
                    yield f"data: {text}\n\n"
            if event.turn_complete:
                yield "event: done\ndata: ok\n\n"
                return

    return StreamingResponse(gen(), media_type="text/event-stream")
```

Client side, a 10-line HTML page:

```html
<script>
  const es = new EventSource("/stream?q=hello");
  es.onmessage = (e) => document.body.append(e.data);
  es.addEventListener("done", () => es.close());
</script>
```

> ⚠️ **Gotcha:** SSE chunks must end with `\n\n`. A single `\n` will *buffer the chunk until the next one arrives* and you'll think streaming is broken.

> 🚀 **In Production**
>
> Behind Nginx/Cloud Run, set `proxy_buffering off` (Nginx) or use the `X-Accel-Buffering: no` response header. Otherwise the proxy holds your SSE bytes and the browser sees the whole reply at once.

> ❓ **Ask the student:** "What does an SSE client see if the server forgets the blank line after each `data:`?" (Nothing arrives until the connection closes — the parser is waiting for the delimiter.)

[← Prev: 18_StreamingLive/02_GeminiLiveIntro]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/04_AudioIO →]
