---
module: 18_StreamingLive
page: 01_StreamingFundamentals
title: Streaming fundamentals — async generators, partials, backpressure
estimated_minutes: 30
prereqs: [18_StreamingLive/00]
concepts: [async-for, async-generator, partial-event, turn_complete, backpressure]
icon: 🧠
in_production: false
detours_suggested: [PY_async, PY_generators]
---

[← Prev: 18_StreamingLive/00_Overview]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/02_GeminiLiveIntro →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 01 Fundamentals

## 🧠 The core mental model

`runner.run_async(...)` is **not** a function that returns a list of events. It returns an **async iterator** that yields events as they're produced.

```python
# Work/01_streaming_loop.py — run with: uv run python Work/01_streaming_loop.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = LlmAgent(name="streamer", model="gemini-2.5-flash",
                 instruction="Reply with a short sentence.")

async def main():
    runner = InMemoryRunner(agent=agent, app_name="demo")
    session = await runner.session_service.create_session(app_name="demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(text="hi")])
    # StreamingMode.NONE is the default — you would only see the final aggregated
    # event. Opt into SSE to get partial chunks.
    run_config = RunConfig(streaming_mode=StreamingMode.SSE)
    async for event in runner.run_async(
        user_id="u", session_id=session.id, new_message=msg, run_config=run_config,
    ):
        text = event.content.parts[0].text if event.content and event.content.parts else None
        print(event.author, "->", text)

asyncio.run(main())
```

> ⚠️ **`StreamingMode.NONE` is the default** (see `src/google/adk/agents/run_config.py` — `streaming_mode: StreamingMode = StreamingMode.NONE`). Without `RunConfig(streaming_mode=StreamingMode.SSE)`, `run_async` yields **one** aggregated event per turn and no `event.partial=True` chunks. Every example on this page assumes SSE; if you forget the `run_config=`, the "live" feeling disappears.

Three things to internalize:

1. The loop body runs **once per event**.
2. The producer (ADK runtime) is **paused** while your loop body runs. There is no internal buffer — you set the pace.
3. The loop ends when the generator says "I'm done." For a normal turn, that's after the final event.

## Partial vs final

A streamed turn comes out as N partial events plus 1 final event (only when `run_config=RunConfig(streaming_mode=StreamingMode.SSE)` is passed — otherwise you just get the final):

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

run_config = RunConfig(streaming_mode=StreamingMode.SSE)
async for event in runner.run_async(..., run_config=run_config):
    is_partial = event.partial is True            # incremental chunk
    is_final   = event.turn_complete is True      # turn is over
    text = event.content.parts[0].text if event.content and event.content.parts else ""
    print(("...", "==")[is_final], repr(text))
```

The **partial events carry deltas** (just the new tokens since the last event). The **final event carries the consolidated turn** (or sometimes is empty if `turn_complete` is the only thing being signaled). You generally want to render partials live and use the final to "commit" the turn to your transcript.

> ❓ **Ask the student:** If you only ever read `event.turn_complete` events, what do you lose? (Answer: live token-by-token UX; you wait for the whole turn.)

## Backpressure — the gotcha

The producer is paused inside your loop body. If you `await` a slow I/O call inside that loop, **you slow down the stream**.

```python
from google.adk.agents.run_config import RunConfig, StreamingMode
run_config = RunConfig(streaming_mode=StreamingMode.SSE)

# BAD — every token waits for a DB write
async for event in runner.run_async(..., run_config=run_config):
    await db.write(event)        # blocks the producer
    print(event.content.parts[0].text)

# BETTER — fan out to a queue
queue = asyncio.Queue()
async def writer():
    while True:
        event = await queue.get()
        await db.write(event)

asyncio.create_task(writer())
async for event in runner.run_async(..., run_config=run_config):
    print(event.content.parts[0].text)
    queue.put_nowait(event)      # never awaits
```

> 🚀 **In Production**
>
> Telemetry, audit logging, content filters all want to hook the event stream. Do them on a queue/task, not inline. A 50ms hook inside the loop turns a 200ms TTFT into 1.5s.

## Why an async generator and not a callback

The async-iterator shape lets *you* own the loop. You can `break` out, `try/except` per chunk, skip events, await a cancel token between events. A callback API would hide all of that.

> 🛠 **Have the student run:**
>
> ```python
> import asyncio
> async def gen():
>     for i in range(5):
>         await asyncio.sleep(0.2)
>         yield i
>
> async def main():
>     async for x in gen():
>         print(x)
> asyncio.run(main())
> ```
>
> Then ask them to add `await asyncio.sleep(1)` inside the loop and watch the total time double. That's backpressure.

> 🧭 **If the student looks stuck on `async for`:** suggest detour [[PY_async]] then [[PY_generators]] (20 min each).

[← Prev: 18_StreamingLive/00_Overview]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/02_GeminiLiveIntro →]
