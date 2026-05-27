---
module: 24_ChannelIntegrations
page: 01_WebhookToRunnerPattern
title: The universal webhook → Runner adapter
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/00, 21_ApiSurface/02]
concepts: [webhook, signature_verification, channel_event_parse, user_id_mapping, runner_invocation]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_LongRunningOnChat →](02_LongRunningOnChat.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 01 Webhook To Runner Pattern

# 🛠 One pattern, every channel

Every channel integration in this module — Slack, Google Chat, Discord, WhatsApp, email — is the **same** five-step adapter:

```
   1. Verify signature
   2. Parse channel event
   3. Resolve user_id + session_id
   4. Invoke Runner
   5. Post response back to channel
```

If you internalize this one shape, every channel page after this one is just "what's the signature scheme, what's the event JSON, what's the post-message endpoint?". Three things differ; the structure is invariant.

## The skeleton — in Python

```python
# Work/24_channels/adapter_skeleton.py — the template you'll specialize per channel
from fastapi import FastAPI, Request, HTTPException
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

agent = Agent(name="chat_bot", model="gemini-2.5-flash", instruction="be helpful")
runner = InMemoryRunner(app_name="chat_bot", agent=agent)

app = FastAPI()

@app.post("/webhook/{channel}")
async def channel_webhook(channel: str, request: Request):
    raw = await request.body()

    # 1. Verify signature (channel-specific)
    if not verify_signature(channel, request.headers, raw):
        raise HTTPException(401, "Bad signature")

    # 2. Parse channel event (channel-specific)
    event = parse_event(channel, raw)
    if event.kind != "message":
        return {"ok": True}                  # ignore non-message events

    # 3. Resolve user_id + session_id
    user_id = f"{channel}:{event.user_id}"   # namespace by channel
    session_id = event.thread_id or event.dm_id

    # 4. Invoke Runner
    session = await runner.session_service.get_session(
        app_name="chat_bot", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="chat_bot", user_id=user_id, session_id=session_id
    )
    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=event.text)])
    reply_chunks = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text:
                    reply_chunks.append(p.text)
    reply = "".join(reply_chunks)

    # 5. Post back to channel (channel-specific)
    await post_back(channel, event, reply)

    return {"ok": True}

def verify_signature(channel, headers, body): ...
def parse_event(channel, raw): ...
async def post_back(channel, event, reply): ...
```

Read it twice. The 80% that's the same across channels is the middle three steps. The 20% that differs is the three function stubs at the bottom.

## Step-by-step, what each step does

### 1. Verify signature

Every chat platform signs webhook deliveries. If you don't verify, anyone on the internet can post fake events to your endpoint and trigger your agent.

- Slack: HMAC-SHA256 over `v0:{timestamp}:{body}` with your signing secret. Header `X-Slack-Signature`.
- Google Chat: Bearer JWT signed by Google; verify with Google's JWKS.
- Discord: Ed25519 signature with the bot's public key. Headers `X-Signature-Ed25519`, `X-Signature-Timestamp`.

Each channel page covers the specific code. The *rule* is invariant: **verify before doing anything else**.

### 2. Parse channel event

The platform JSON varies wildly. Normalize into a small dataclass your code uses:

```python
# Work/24_channels/event.py
from dataclasses import dataclass

@dataclass
class ChannelEvent:
    kind: str          # "message" | "command" | "callback" | "join" | ...
    user_id: str       # channel-native user identifier
    text: str          # the user's message text (or command + args)
    thread_id: str | None
    dm_id: str | None
    channel_meta: dict # raw payload for channel-specific re-posting
```

Each `parse_event(channel, raw)` returns this normalized shape. Now your downstream code is channel-agnostic.

### 3. Resolve `user_id` + `session_id`

This is where the rules from module 23/01 apply, with one twist: in a channel, you don't have a Firebase login. The channel **is** the auth — Slack already knows who the user is. Your job is to namespace:

- `user_id = f"{channel}:{event.user_id}"` — namespace channel UIDs so two users with the same Slack UID and Discord UID don't collide.
- `session_id` — depends on UX:
  - **Per-thread** (`event.thread_id`): conversation continues in a thread. Most natural for support bots.
  - **Per-DM** (`event.dm_id`): one long-running session per user.
  - **Per-message**: stateless, no continuity. Good for one-shot Q&A bots.

Pick a policy per channel and document it. Page 08 goes deep on the auth/session mapping.

### 4. Invoke Runner

This is the same `runner.run_async()` you've been using since module 02. The only twist is the response shape: chat platforms want **one message back** (or a sequence of edits to one message). So you either:

- Collect all events, concatenate text, post once (simple, what the skeleton above does).
- Stream events into thread updates / message edits (real-time feel; page 02 covers).

### 5. Post back to channel

Each platform has its own REST API for posting messages. Slack: `chat.postMessage`. Google Chat: `spaces.messages.create`. Discord: `interactions/{id}/{token}/callback`. The platform pages cover details.

## A first test — without a real channel

```python
# Work/24_channels/fake_channel.py — run with: uv run python Work/24_channels/fake_channel.py
import asyncio
from dataclasses import dataclass

@dataclass
class FakeEvent:
    kind: str = "message"
    user_id: str = "U12345"
    text: str = "what's 2+2?"
    thread_id: str | None = "thread-abc"
    dm_id: str | None = None
    channel_meta: dict | None = None

async def main():
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = Agent(name="math", model="gemini-2.5-flash", instruction="answer briefly")
    runner = InMemoryRunner(app_name="math", agent=agent)
    event = FakeEvent()
    user_id = f"slack:{event.user_id}"
    session_id = event.thread_id
    session = await runner.session_service.create_session(
        app_name="math", user_id=user_id, session_id=session_id
    )
    msg = types.Content(role="user", parts=[types.Part(text=event.text)])
    reply = ""
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text and not ev.partial:
                    reply += p.text
    print(f"would post to slack thread {event.thread_id}: {reply}")

asyncio.run(main())
```

Run this. You're exercising the universal middle of the adapter without standing up a Slack workspace.

> 🚀 **In Production**
>
> Signature verification is non-negotiable. Skipping it is the single most common channel bot vulnerability — your agent becomes a public abuse vector. Even in dev, use the real signing secret with a tunneled local URL ([ngrok](https://ngrok.com), [Cloud Run](https://cloud.google.com/run)). Test with the platform's "send test event" tool.

> ❓ **Ask the student:** "Why namespace `user_id = f'{channel}:{event.user_id}'` instead of just `event.user_id`?"
>
> (Answer: avoid collisions. Slack UID `U123` and Discord UID `U123` are unrelated humans; without the namespace they'd share a session. Also makes per-channel session listings easier.)

> 🛠 **Have the student run:** `fake_channel.py`. Trace each of the five steps to a line in the script. Confirm they can name what each one does without reading.

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_LongRunningOnChat →](02_LongRunningOnChat.md)
