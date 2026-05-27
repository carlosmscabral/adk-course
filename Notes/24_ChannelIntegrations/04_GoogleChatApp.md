---
module: 24_ChannelIntegrations
page: 04_GoogleChatApp
title: Google Chat app — Apps Script-free, IAM-secured
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/02]
concepts: [google_chat_api, chat_event, jwt_verify, IAM, space_message]
icon: 🌐
in_production: true
detours_suggested: [GoogleChat_Apps]
---

[← Prev: 03_SlackBot](03_SlackBot.md)  [↑ Map](../../MAP.md)  [Next: 05_DiscordBot →](05_DiscordBot.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 04 Google Chat App

# 🌐 Google Chat as a channel

Detour [[GoogleChat_Apps]] covers app registration in the Chat API console, the manifest, OAuth scopes, and which trigger types you can subscribe to. **Take that first** if you've never published a Chat app. This page is the ADK adapter.

## What's different from Slack

| Concern | Slack | Google Chat |
|---|---|---|
| **Auth at the door** | HMAC over body | Bearer JWT signed by Google |
| **Event shape** | `event.type` namespace | `type: MESSAGE | ADDED_TO_SPACE | ...` |
| **Threading** | `thread_ts` per message | `thread.name` (resource path) |
| **Posting back** | `chat.postMessage` + tokens | `spaces.messages.create` + service account |
| **3s ACK** | same | same |

The structure of your handler is identical to Slack — five steps from page 01, place-holder + edit pattern from page 02. Only the platform-specific functions differ.

## Signature verification — Google JWT

Google Chat signs every event with a JWT. Verify against Google's public keys:

```python
# Work/24_channels/gchat_verify.py
import os
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token

CHAT_APP_PROJECT_NUM = os.environ["CHAT_APP_PROJECT_NUM"]
# The audience is your app's project number, as a string.

def verify_gchat_jwt(authorization_header: str) -> dict:
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Missing bearer token")
    token = authorization_header.removeprefix("Bearer ")
    claims = id_token.verify_token(token, g_requests.Request(), audience=CHAT_APP_PROJECT_NUM)
    # Issuer must be chat-api@system.gserviceaccount.com
    if claims.get("iss") != "chat@system.gserviceaccount.com":
        raise ValueError(f"Unexpected issuer: {claims.get('iss')}")
    return claims
```

If verification fails, return 401. Don't even peek at the body.

## The Chat handler

```python
# Work/24_channels/gchat_app.py — run with: uv run uvicorn Work.24_channels.gchat_app:app --port 8000
import os
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
from googleapiclient.discovery import build
from google.oauth2 import service_account

from Work.24_channels.gchat_verify import verify_gchat_jwt

agent = Agent(name="gchat_bot", model="gemini-2.5-flash", instruction="be concise")
runner = InMemoryRunner(app_name="gchat_bot", agent=agent)

# Service account with the chat.bot scope
creds = service_account.Credentials.from_service_account_file(
    os.environ["GCHAT_SA_JSON"],
    scopes=["https://www.googleapis.com/auth/chat.bot"],
)
chat_service = build("chat", "v1", credentials=creds, cache_discovery=False)

app = FastAPI()

async def run_and_reply(event: dict):
    space_name = event["space"]["name"]                     # spaces/AAAA...
    thread = event["message"].get("thread", {}).get("name") # spaces/AAAA/threads/BBBB
    sender = event["message"]["sender"]["name"]             # users/CCCC
    text = event["message"]["argumentText"] or event["message"]["text"]

    user_id = f"gchat:{sender}"
    session_id = thread or space_name                       # per-thread; fallback per-space

    session = await runner.session_service.get_session(
        app_name="gchat_bot", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="gchat_bot", user_id=user_id, session_id=session_id
    )

    # Post placeholder
    placeholder = chat_service.spaces().messages().create(
        parent=space_name,
        body={"text": "⏳ thinking…", "thread": {"name": thread} if thread else None},
    ).execute()

    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=text)])
    parts = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text and not ev.partial:
                    parts.append(p.text)

    chat_service.spaces().messages().update(
        name=placeholder["name"],
        updateMask="text",
        body={"text": "".join(parts) or "(no reply)"},
    ).execute()

@app.post("/gchat")
async def gchat_webhook(request: Request, bg: BackgroundTasks):
    try:
        verify_gchat_jwt(request.headers.get("authorization", ""))
    except Exception as e:
        raise HTTPException(401, f"Bad JWT: {e}") from e

    event = await request.json()

    if event["type"] == "ADDED_TO_SPACE":
        return {"text": "👋 hi, I'm online. Mention me in a thread to chat."}
    if event["type"] == "REMOVED_FROM_SPACE":
        return {"text": ""}
    if event["type"] != "MESSAGE":
        return {"text": ""}

    bg.add_task(run_and_reply, event)
    return {}                                  # synchronous empty ACK
```

Three event types you must handle: `ADDED_TO_SPACE` (greeting), `REMOVED_FROM_SPACE` (cleanup), `MESSAGE` (run the agent). Everything else returns empty.

## IAM — who can call your webhook

Two options:

1. **Cloud Run + Chat-app service account** — set Cloud Run ingress to "Internal and Cloud Load Balancing only" and grant `roles/run.invoker` to `chat-api@system.gserviceaccount.com`. The JWT verify is then defense-in-depth.
2. **Public Cloud Run** — anyone can hit the URL; JWT verify is the only auth. Slightly weaker but simpler.

For prod, prefer option 1. Detour [[Cloud_Run]] has the IAM commands.

## Posting back — service account vs. OAuth

The snippet above uses a **service account** (`from_service_account_file`) — your bot posts AS the bot identity. That's the right default.

If you need to post AS the user (e.g., "I'll send this message from you"), you need full OAuth with `chat.messages` scope and a stored refresh token per user. Almost no bots need this; if you do, page 08 covers the per-user OAuth pattern.

## Threading policy

Google Chat threads are first-class — every message has a `thread.name`. Use that as `session_id`. For DMs (1:1 chats with the bot), there's only one thread per space, so per-thread and per-space converge.

> 🚀 **In Production**
>
> Your Cloud Run service URL must match the **App URL** you registered in the Chat API console. If you re-deploy and the URL changes (it shouldn't with Cloud Run domains, but custom domains can drift), Chat will silently stop calling you. Pin the custom domain and document the redeployment runbook.

> ❓ **Ask the student:** "Why is the audience for the JWT check the project *number*, not the project ID?"
>
> (Answer: Google's chat-api signer puts the project number in the `aud` claim. The project ID is human-readable; the number is the immutable canonical ID — that's what's in the JWT.)

> 🛠 **Have the student run:** if they have a Workspace tenant — register a Chat app pointing at their ngrok URL, add to a space, send a message, watch the placeholder edit. If no Workspace — read the page, defer the live run to detour [[GoogleChat_Apps]].

[← Prev: 03_SlackBot](03_SlackBot.md)  [↑ Map](../../MAP.md)  [Next: 05_DiscordBot →](05_DiscordBot.md)
