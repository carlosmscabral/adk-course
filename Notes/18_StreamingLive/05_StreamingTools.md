---
module: 18_StreamingLive
page: 05_StreamingTools
title: Streaming tools — LongRunningFunctionTool and progress events
estimated_minutes: 25
prereqs: [03_Tools/02, 18_StreamingLive/01]
concepts: [LongRunningFunctionTool, async-generator-tool, progress-events]
icon: 🛠
in_production: true
---

[← Prev: 18_StreamingLive/04_AudioIO]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/06_VideoInput →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 05 Streaming Tools

## Recap: most tools are not streamed

A vanilla `FunctionTool` is called, runs, returns one value, the LLM keeps going. The user sees a single `function_response` event when it's done. Fine for fast tools.

For slow tools (web search, file download, video render) the user is staring at "..." for 30 seconds. We can do better.

## `LongRunningFunctionTool`

ADK's `LongRunningFunctionTool` (covered in 03_Tools) wraps a function that **yields progress** instead of returning a single value. Each yield becomes an event in the run stream. The final yielded value is the tool's return value.

```python
from google.adk.tools import LongRunningFunctionTool

async def slow_render(prompt: str):
    """Render a 3-frame storyboard. Yields progress."""
    yield {"status": "starting", "frames_done": 0}
    for i in range(1, 4):
        await asyncio.sleep(1)   # pretend we're rendering
        yield {"status": "in_progress", "frames_done": i}
    yield {"status": "done", "frames_done": 3, "url": "gs://demo/out.mp4"}

render_tool = LongRunningFunctionTool(func=slow_render)
```

Wire it into an `Agent` like any other tool. When the LLM calls it, your `async for event in runner.run_async(...)` loop will see one event per `yield`. Your client (CLI, browser via SSE) renders them as a live progress bar.

## What the event stream looks like

```
Event: function_call(slow_render, {"prompt": "..."})
Event: function_response(slow_render, {"status": "starting", "frames_done": 0})
Event: function_response(slow_render, {"status": "in_progress", "frames_done": 1})
Event: function_response(slow_render, {"status": "in_progress", "frames_done": 2})
Event: function_response(slow_render, {"status": "in_progress", "frames_done": 3})
Event: function_response(slow_render, {"status": "done", ...})
Event: <model token chunks...>
```

The LLM does NOT see every intermediate event — only the final return value goes back into the context. So the LLM sees `{"status": "done", "frames_done": 3, "url": "gs://demo/out.mp4"}`. The progress yields are purely for the runtime/client to observe.

## Threading tool progress into Live

In a Live session, the same pattern holds. The progress events show up alongside audio/text events in your `runner.run_live(...)` loop. Your UI can render a "downloading 47%" overlay while the model is still streaming audio.

> 🛠 **Have the student modify** the streaming CLI from page 03 to use a `LongRunningFunctionTool` (use the `slow_render` snippet above). Verify they see one `function_response` event per yield.

> 🚀 **In Production**
>
> If you `yield` a million times you flood your event stream. Yield at coarse-enough intervals that the UI actually re-renders meaningfully (every 5-10% of progress, or every 500ms — whichever is less frequent).

> ⚠️ **Gotcha:** the LLM only sees the *final* yielded value. If you forget to yield a "done" payload with the actual result, the LLM gets `None`. Always end with the result the model needs.

> ❓ **Ask the student:** "If your slow tool raises mid-stream, what does the LLM see?" (A `function_response` whose payload encodes the error; the LLM can decide whether to retry or apologize. The exception does NOT propagate to your `async for` caller unless you let it.)

[← Prev: 18_StreamingLive/04_AudioIO]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/06_VideoInput →]
