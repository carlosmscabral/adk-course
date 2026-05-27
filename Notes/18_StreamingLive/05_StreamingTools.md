---
module: 18_StreamingLive
page: 05_StreamingTools
title: Streaming tools — LongRunningFunctionTool (deferred result) and live input streams
estimated_minutes: 25
prereqs: [03_Tools/02, 18_StreamingLive/01]
concepts: [LongRunningFunctionTool, deferred-result, function_call_id, _call_live, input_stream]
icon: 🛠
in_production: true
---

[← Prev: 18_StreamingLive/04_AudioIO]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/06_VideoInput →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 05 Streaming Tools

## Recap: most tools are not streamed

A vanilla `FunctionTool` is called, runs, returns one value, the LLM keeps going. The user sees a single `function_response` event when it's done. Fine for fast tools.

For tools whose work outlives a single turn — a render job that takes minutes, a human-approval step, a Cloud Workflow — you need a different pattern. `FunctionTool.run_async` is a single `await target(**args)` (see `src/google/adk/tools/function_tool.py:213-274`); there is **no internal yield loop**. So "stream progress out of one tool call" is not how ADK works.

> ⚠️ **Common fabrication:** that `LongRunningFunctionTool` wraps an async generator and that each `yield` becomes a `function_response` event the client renders as a progress bar. It does not. `LongRunningFunctionTool` is the **deferred-result** pattern, described below. If you see snippets like `async def slow_render(): yield {"status": "in_progress"}; yield {"status": "done"}` wired into a `LongRunningFunctionTool`, treat them with suspicion and grep the source.

## `LongRunningFunctionTool` — the deferred-result pattern

The actual contract: the tool kicks off async work and **returns a placeholder immediately**. The runtime stamps that response with a `function_call_id`. The work finishes some time later (seconds, minutes, the next morning). A subsequent turn calls back into the runner with a `function_response` carrying the same `function_call_id` and the *real* payload. From the LLM's perspective, the tool simply took a long time to answer.

This is the round-trip pattern used by `AuthToolArguments` (see `src/google/adk/auth/auth_tool.py:141-148` — auth requests are themselves long-running function calls), human-in-the-loop approvals, and any external job system.

```python
from google.adk.tools import LongRunningFunctionTool

# Step 1 — the tool body. It kicks off the job and returns a *placeholder*.
async def kick_off_render(prompt: str) -> dict:
    job_id = await jobs.submit("render", {"prompt": prompt})  # external system
    return {"status": "pending", "job_id": job_id}

render_tool = LongRunningFunctionTool(func=kick_off_render)
```

When the LLM calls `kick_off_render`, the event stream looks like:

```
Event: function_call(kick_off_render, {"prompt": "..."}, id=fc_abc123)
Event: function_response(kick_off_render, {"status": "pending", "job_id": "j_42"}, id=fc_abc123)
```

The LLM sees `{"status": "pending", "job_id": "j_42"}` and typically acknowledges ("I've started the render, this will take a minute"). The turn ends.

Later — minutes, hours, whenever the job is actually done — your application sends a *new* `function_response` carrying the same `id=fc_abc123` and the real payload:

```python
# Step 2 — when the job finishes, your code (a worker, a webhook handler)
# replays the function_response with the real result.
final_response = types.Content(
    role="user",
    parts=[types.Part(function_response=types.FunctionResponse(
        id="fc_abc123",
        name="kick_off_render",
        response={"status": "done", "url": "gs://demo/out.mp4"},
    ))],
)
async for event in runner.run_async(
    user_id="u", session_id=session.id, new_message=final_response,
):
    ...  # LLM resumes with the real result and replies to the user
```

That is the entire pattern: one tool call, one placeholder response, one delayed completion response. The "streaming" experience for the user comes from the *application* surfacing progress updates out-of-band (polling the job system, a separate SSE channel, a websocket) — **not** from the tool yielding events into the agent's run stream.

> 🚀 **In Production**
>
> Persist the mapping `function_call_id → external_job_id` somewhere durable (Firestore, Cloud SQL). When the worker finishes, it needs to know which session/agent invocation to replay the response into. Lose this mapping and the user's turn is stranded.

## Aside: `_call_live` and live-mode input streaming

There is a separate, **LIVE-only** path on `FunctionTool` — `_call_live(input_stream=...)` (see `src/google/adk/tools/function_tool.py:300`). The runtime invokes it only inside `runner.run_live(...)` and only for tools registered as active streaming tools. The `input_stream` is for tools that need to *consume* a stream from the model (e.g. a tool that ingests transcribed audio chunks while the user is still talking).

This is **not** a progress-reporting mechanism either — it is a streaming-INPUT path. Tools that yield results in this path are yielding *consumed-input acknowledgements* back into the live loop, not progress bars. If your goal is "show the user a progress bar", neither `LongRunningFunctionTool` nor `_call_live` is the right hammer; do it in the application layer as described above.

> 🛠 **Have the student** build the deferred-result example end-to-end against a fake `jobs` module (in-process dict, `asyncio.sleep` to simulate latency). They should observe: tool returns `{"status": "pending"}`, the agent acknowledges, a separate coroutine replays the `function_response` 10 seconds later with the real payload, and the agent picks up where it left off.

> ❓ **Ask the student:** "If your worker crashes after `jobs.submit` returned but before it persists the `function_call_id` mapping, what happens?" (The job runs, but nothing replays the response. The agent turn is stuck pending forever. Lesson: persist the mapping in the same transaction as the job submission, or use a job system that lets you tag jobs with arbitrary metadata.)

[← Prev: 18_StreamingLive/04_AudioIO]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/06_VideoInput →]
