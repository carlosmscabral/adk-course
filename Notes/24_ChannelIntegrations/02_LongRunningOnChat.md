---
module: 24_ChannelIntegrations
page: 02_LongRunningOnChat
title: Long-running responses on chat platforms — ACK + background
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/01]
concepts: [3_second_ack, background_task, thread_update, message_edit, defer_response]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 01_WebhookToRunnerPattern](01_WebhookToRunnerPattern.md)  [↑ Map](../../MAP.md)  [Next: 03_SlackBot →](03_SlackBot.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 02 Long Running On Chat

# 🛠 Three seconds, then go

Every chat platform has the same hostile constraint:

> "We will retry the webhook if you don't ACK within 3 seconds."

Your ADK agent — especially one doing tool calls or research — takes longer than 3 seconds. If you do the work in the webhook handler:

- Platform times out at 3s, retries the webhook.
- You start a *second* run for the same user message.
- Two replies post; users are confused; you've doubled your LLM bill.

The fix is universal: **ACK fast, do the work in the background, post updates to the thread.**

## The two-stage handler

```python
# Work/24_channels/long_running_adapter.py — the standard shape
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent
from google.genai import types

agent = Agent(name="research", model="gemini-2.5-flash", instruction="be thorough")
runner = InMemoryRunner(app_name="research", agent=agent)
app = FastAPI()

async def do_work(channel_event, post_back_fn):
    """Runs the agent and posts updates. NOT awaited in the webhook handler."""
    user_id = f"slack:{channel_event['user_id']}"
    session_id = channel_event["thread_id"]
    session = await runner.session_service.get_session(
        app_name="research", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="research", user_id=user_id, session_id=session_id
    )

    # Post "thinking..." immediately
    placeholder_ts = await post_back_fn("⏳ thinking…")

    msg = types.Content(role="user", parts=[types.Part(text=channel_event["text"])])
    reply = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text and not ev.partial:
                    reply.append(p.text)
    final = "".join(reply)

    # Edit the placeholder with the final text
    await edit_message(placeholder_ts, final)

@app.post("/webhook/slack")
async def slack_webhook(request: Request, bg: BackgroundTasks):
    body = await request.json()
    # ... verify, parse, normalize into channel_event dict ...
    channel_event = parse_slack(body)
    bg.add_task(do_work, channel_event, slack_post)  # fire-and-forget
    return {"ok": True}                              # ACK in <100ms

def parse_slack(body): ...
async def slack_post(text): ...
async def edit_message(ts, text): ...
```

The webhook handler does the *minimum* — verify, parse, schedule the background task, ACK. The actual agent run happens off the request path. FastAPI's `BackgroundTasks` works for short-ish work (<minutes). For longer, push to a real queue (Cloud Tasks, Pub/Sub).

## The four UX patterns for "the agent is working"

### A. Placeholder + edit

Post `"⏳ thinking..."` immediately. When the final reply lands, **edit** the same message in place. Works in Slack (`chat.update`), Google Chat (`spaces.messages.patch`), Discord (`editMessage`). Best UX for short waits.

### B. Reactji + reply

React 👀 to the user's message immediately ("seen it"). When done, post a *new* threaded reply. Better for long-running work where the user is doing other things.

### C. Streaming edits

Edit the placeholder every N tokens or every M seconds. The user sees the message grow. Most "alive" feel, **but** chat platforms rate-limit edits (Slack: 1/sec). Throttle.

### D. Deferred + interactive

For multi-minute work: post `"📋 I'll DM you when it's ready"`, do the work, send a fresh DM. Best for long jobs the user shouldn't have to wait for.

```python
# Work/24_channels/streaming_edits.py — pattern C, with throttling
import asyncio, time

async def stream_to_message(events_iter, post_fn, edit_fn):
    ts = await post_fn("⏳")
    buffer = []
    last_edit = 0
    EDIT_INTERVAL = 1.5  # seconds

    async for ev in events_iter:
        if not (ev.content and ev.content.parts):
            continue
        for p in ev.content.parts:
            if p.text:
                buffer.append(p.text)
                now = time.monotonic()
                if now - last_edit > EDIT_INTERVAL:
                    await edit_fn(ts, "".join(buffer))
                    last_edit = now
    # final edit always
    await edit_fn(ts, "".join(buffer))
```

## Background-task survival

`BackgroundTasks` runs in-process. If your Cloud Run instance recycles mid-task, the work is lost. For prod reliability:

1. ACK the webhook.
2. Publish the work to **Pub/Sub** (or Cloud Tasks).
3. A separate worker / Pub/Sub-triggered ADK app processes it.
4. Worker posts back to the channel.

This is **exactly the ambient-agent pattern** from page 07. The channel becomes a doorway to a Pub/Sub-triggered ADK app.

## What about `LongRunningFunctionTool`?

ADK's `LongRunningFunctionTool` is for tools that take time — file uploads, batch ML jobs, etc. The pattern here is **orthogonal**: the chat platform's 3s constraint is about the *webhook ACK*, not the tool's runtime. You can combine both: ACK fast, background task runs Runner with a `LongRunningFunctionTool` inside, which yields progress events you stream to the message edit.

> 🚀 **In Production**
>
> The number-one channel bug: forgetting to ACK and your handler returns after 5 seconds. The platform has already retried 3x. Users see 4 replies. Your ADK has run 4 turns and burned 4x tokens. **Verify the ACK is fast** by logging the time-to-200 in your handler. If it ever exceeds 1s, you have a regression.

> ❓ **Ask the student:** "What's the worst-case symptom if I do the agent work synchronously in the webhook handler instead of backgrounding it?"
>
> (Answer: platform retries → multiple parallel agent runs for the same message → multiple replies → bill multiplied. The user-visible symptom is duplicate replies.)

> 🛠 **Have the student run:** the `long_running_adapter.py` skeleton, simulate a slow webhook (sleep 5s inline), watch the platform's retry behavior with curl — `for i in 1 2 3; do curl -X POST ...; done` and confirm one ACK fires per call.

[← Prev: 01_WebhookToRunnerPattern](01_WebhookToRunnerPattern.md)  [↑ Map](../../MAP.md)  [Next: 03_SlackBot →](03_SlackBot.md)
