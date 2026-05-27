---
module: 24_ChannelIntegrations
page: 03_SlackBot
title: Slack bot — Events API, slash commands, threading
estimated_minutes: 30
prereqs: [24_ChannelIntegrations/02]
concepts: [slack_events_api, slash_command, hmac_signature, threading, slack_sdk]
icon: 🌐
in_production: true
detours_suggested: [Slack_Bots]
---

[← Prev: 02_LongRunningOnChat](02_LongRunningOnChat.md)  [↑ Map](../../MAP.md)  [Next: 04_GoogleChatApp →](04_GoogleChatApp.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 03 Slack Bot

# 🌐 Slack as a channel

The full Slack-side setup (app manifest, permissions, OAuth, distribution) lives in detour [[Slack_Bots]]. This page is the **ADK side** — verifying Slack signatures, parsing Slack Events API JSON, posting back with `slack_sdk`.

If you've never built a Slack app before, take [[Slack_Bots]] first — 20 min for the workspace setup. Then return here.

## Three Slack entry points

| Entry point | What | Webhook URL |
|---|---|---|
| **Events API** | User mentions your bot in a channel; bot is DM'd; etc. | `POST /slack/events` |
| **Slash command** | User types `/yourbot some text` | `POST /slack/commands/yourbot` |
| **Interactive components** | User clicks a button on a message | `POST /slack/interactions` |

All three use the same signing secret and the same 3-second ACK constraint. We'll wire Events API + a slash command.

## The signature verifier

```python
# Work/24_channels/slack_verify.py
import hashlib, hmac, os, time

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

def verify_slack(headers, body: bytes) -> bool:
    ts = headers.get("x-slack-request-timestamp", "")
    sig = headers.get("x-slack-signature", "")
    if not ts or not sig:
        return False
    # Reject replays older than 5 min
    if abs(time.time() - int(ts)) > 60 * 5:
        return False
    base = f"v0:{ts}:{body.decode()}".encode()
    digest = hmac.new(SLACK_SIGNING_SECRET.encode(), base, hashlib.sha256).hexdigest()
    expected = f"v0={digest}"
    return hmac.compare_digest(expected, sig)
```

Drop this in front of every Slack endpoint. **Never** skip the timestamp check — without it, an attacker who captures one valid signature can replay it forever.

## The Events API handler

```python
# Work/24_channels/slack_bot.py — run with: uv run uvicorn Work.24_channels.slack_bot:app --port 8000
# Expose via ngrok: ngrok http 8000; paste the https URL into your Slack app's Event Subscriptions.
import os, asyncio
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from slack_sdk.web.async_client import AsyncWebClient
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

from Work.24_channels.slack_verify import verify_slack  # the helper above

slack = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
agent = Agent(name="slack_bot", model="gemini-2.5-flash", instruction="be concise and helpful")
runner = InMemoryRunner(app_name="slack_bot", agent=agent)
app = FastAPI()

async def run_and_reply(event_payload: dict):
    channel = event_payload["channel"]
    user = event_payload["user"]
    text = event_payload["text"]
    thread_ts = event_payload.get("thread_ts") or event_payload["ts"]

    user_id = f"slack:{user}"
    session_id = thread_ts          # one session per Slack thread

    session = await runner.session_service.get_session(
        app_name="slack_bot", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="slack_bot", user_id=user_id, session_id=session_id
    )

    placeholder = await slack.chat_postMessage(
        channel=channel, thread_ts=thread_ts, text="⏳ thinking…"
    )

    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=text)])
    parts = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text and not ev.partial:
                    parts.append(p.text)

    await slack.chat_update(
        channel=channel, ts=placeholder["ts"], text="".join(parts) or "(no reply)"
    )

@app.post("/slack/events")
async def slack_events(request: Request, bg: BackgroundTasks):
    body = await request.body()
    if not verify_slack(request.headers, body):
        raise HTTPException(401, "Bad Slack signature")

    payload = await request.json()

    # URL verification challenge (one-time, on subscription setup)
    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})

    # We only respond to messages mentioning the bot or in DMs
    if event.get("type") not in ("app_mention", "message"):
        return {"ok": True}
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return {"ok": True}                        # ignore our own posts

    bg.add_task(run_and_reply, event)
    return {"ok": True}                            # ACK in <100ms
```

Notes:

- `thread_ts = event.thread_ts or event.ts` — if the message starts a new thread, its `ts` becomes the thread root. Either way, **one Slack thread = one ADK session**.
- `chat_postMessage(thread_ts=...)` + `chat_update(ts=placeholder.ts)` = the placeholder-edit pattern from page 02 (UX pattern A).
- Bot messages have `bot_id` set; ignore them or your bot will infinite-loop reading its own replies.

## Slash commands

```python
# Work/24_channels/slack_slash.py
@app.post("/slack/commands/research")
async def slash_research(request: Request, bg: BackgroundTasks):
    body = await request.body()
    if not verify_slack(request.headers, body):
        raise HTTPException(401)

    # Slash commands arrive as urlencoded form, not JSON
    form = await request.form()
    fake_event = {
        "channel": form["channel_id"],
        "user": form["user_id"],
        "text": form["text"],
        "ts": str(asyncio.get_event_loop().time()),
        "thread_ts": None,                          # commands start fresh
    }
    bg.add_task(run_and_reply, fake_event)
    return {"response_type": "ephemeral", "text": "⏳ on it…"}
```

Slash commands give you a free initial response via the HTTP body (`{"response_type": "in_channel", "text": "..."}`). Use that as the placeholder, then `chat.update` it.

## Threading policy — the choice that matters

| Choice | What | When to use |
|---|---|---|
| **One session per thread** | Each Slack thread is a new ADK session. | Default for support bots. Conversations have natural boundaries. |
| **One session per channel** | All messages in #general share a session. | Rarely. Cross-talk gets messy. |
| **One session per user (DM)** | DMs are long-running per user. | DM-first bots like personal assistants. |
| **Per-message stateless** | New session every message. | One-shot Q&A; no follow-ups. |

The sample above chose **per-thread**; you can mix (DMs = per-user, channels = per-thread).

## What lives in detour [[Slack_Bots]]

- Workspace setup, App Manifest YAML, OAuth scopes.
- Distribution (single-workspace vs marketplace).
- Tunnel options (ngrok, Cloud Run with public URL).
- Slack Bolt vs raw HTTP (we use raw here; Bolt is fine too).

> 🚀 **In Production**
>
> Slack rate-limits `chat.update` to about **1/sec per channel**. If you're streaming edits (page 02 pattern C) at 5/sec you'll get 429s and dropped updates. Throttle aggressively or batch tokens before each edit. Also: store `SLACK_BOT_TOKEN` in Secret Manager, never in env files in git.

> ❓ **Ask the student:** "Why does the handler check `event.bot_id` and ignore those?"
>
> (Answer: when your bot posts a reply, that post also fires an `event` to your webhook. Without the check, the bot reads its own reply and loops forever.)

> 🛠 **Have the student run:** the Slack bot locally + ngrok, point a real Slack workspace at it, mention the bot in a channel. Watch placeholder → final edit. Then try a slash command.

[← Prev: 02_LongRunningOnChat](02_LongRunningOnChat.md)  [↑ Map](../../MAP.md)  [Next: 04_GoogleChatApp →](04_GoogleChatApp.md)
