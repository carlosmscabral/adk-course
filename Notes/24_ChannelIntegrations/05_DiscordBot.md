---
module: 24_ChannelIntegrations
page: 05_DiscordBot
title: Discord — Interactions API, Ed25519, deferred responses
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/02]
concepts: [discord_interactions, ed25519_verify, slash_command, deferred_response, follow_up]
icon: 🌐
in_production: true
detours_suggested: []
---

[← Prev: 04_GoogleChatApp](04_GoogleChatApp.md)  [↑ Map](../../MAP.md)  [Next: 06_WhatsAppEmail →](06_WhatsAppEmail.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 05 Discord Bot

# 🌐 Discord as a channel

Discord's HTTP **Interactions API** is the cleanest of the three big platforms — it doesn't need a long-running WebSocket gateway connection (you can use the gateway too, but webhook is enough for chat agents).

The shape is identical to Slack/GChat. The differences:

| Concern | Discord |
|---|---|
| **Sig verification** | Ed25519 over `timestamp + body` with your bot's public key |
| **Event** | "Interaction" — almost always a slash command |
| **3s constraint** | Same — but Discord has an official "**deferred response**" pattern |
| **Posting back** | Either the initial response or via "follow-up messages" tied to an interaction token |

## Signature verification — Ed25519

```python
# Work/24_channels/discord_verify.py
import os
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]  # hex string from app's General Info page
verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

def verify_discord(headers, body: bytes) -> bool:
    sig = headers.get("x-signature-ed25519", "")
    ts = headers.get("x-signature-timestamp", "")
    if not sig or not ts:
        return False
    try:
        verify_key.verify(f"{ts}".encode() + body, bytes.fromhex(sig))
        return True
    except BadSignatureError:
        return False
```

`pip install pynacl` for the crypto.

## The deferred-response pattern

Discord lets you formally defer:

1. Webhook fires (slash command).
2. You **immediately** respond with `{"type": 5}` ("DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE"). Discord shows the user "Bot is thinking…" with a spinner.
3. You have **15 minutes** to post a follow-up via the interaction token.

```python
# Work/24_channels/discord_bot.py — run with: uv run uvicorn Work.24_channels.discord_bot:app --port 8000
import os, httpx
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

from Work.24_channels.discord_verify import verify_discord

DISCORD_APP_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

agent = Agent(name="discord_bot", model="gemini-2.5-flash", instruction="be concise")
runner = InMemoryRunner(app_name="discord_bot", agent=agent)
app = FastAPI()

async def run_and_followup(interaction_token: str, channel_id: str, user_id_d: str, text: str):
    user_id = f"discord:{user_id_d}"
    session_id = channel_id                          # per-channel; or per-interaction for stateless
    session = await runner.session_service.get_session(
        app_name="discord_bot", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="discord_bot", user_id=user_id, session_id=session_id
    )
    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=text)])
    parts = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text and not ev.partial:
                    parts.append(p.text)
    reply = "".join(parts) or "(no reply)"

    # Follow-up via webhook URL with the interaction token
    url = f"https://discord.com/api/v10/webhooks/{DISCORD_APP_ID}/{interaction_token}"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"content": reply})

@app.post("/discord/interactions")
async def discord(request: Request, bg: BackgroundTasks):
    body = await request.body()
    if not verify_discord(request.headers, body):
        raise HTTPException(401, "Bad signature")

    payload = await request.json()

    if payload["type"] == 1:                         # PING
        return {"type": 1}                           # PONG (verification handshake)

    if payload["type"] == 2:                         # APPLICATION_COMMAND
        token = payload["token"]
        channel_id = payload["channel_id"]
        user_id = payload["member"]["user"]["id"] if "member" in payload else payload["user"]["id"]
        # Extract the slash command argument
        text = next(
            (o["value"] for o in payload["data"].get("options", []) if o["name"] == "prompt"),
            "",
        )
        bg.add_task(run_and_followup, token, channel_id, user_id, text)
        return {"type": 5}                           # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

    return {"type": 4, "data": {"content": "Unsupported interaction type"}}
```

Two response types:

- `{"type": 5}` — deferred, shows "thinking", you must follow up.
- `{"type": 4, "data": {"content": "..."}}` — immediate text reply (only when the agent is *fast* — rare for ADK).

The follow-up uses the interaction token to POST to `webhooks/{app_id}/{token}` — no auth header needed on that URL, the token IS the auth (it's bound to that one interaction, expires in 15 min).

## Slash command registration

Discord slash commands are registered out-of-band (one-time setup):

```bash
# Work/24_channels/register_discord_cmd.sh
curl -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ask",
    "description": "Ask the ADK agent something",
    "options": [{"name": "prompt", "type": 3, "description": "Your question", "required": true}]
  }' \
  "https://discord.com/api/v10/applications/$DISCORD_APPLICATION_ID/commands"
```

After registration, the `/ask prompt:hello` command appears in any server your bot is in.

## Threading on Discord

Discord has **threads** as a first-class concept (separate from channels). Decide:

- **Per-channel session** (sample above): all `/ask`s in #general share one session.
- **Per-user session**: each user gets one session across all channels.
- **Per-interaction (stateless)**: every slash command is a fresh session. Good for "search bots".

Threads (`payload.channel.type == 11`) can be treated as their own channel — `session_id = thread_id`.

## Why no Discord detour page

Discord's setup (create app → add to server → register commands) is well-documented at [discord.com/developers](https://discord.com/developers/docs/getting-started). Unlike Slack's workspace permissions or Google Chat's GCP integration, there's not enough Discord-specific GCP/IAM/distribution complexity to warrant a detour. The platform docs are sufficient.

> 🚀 **In Production**
>
> The Ed25519 verification **must** happen on the raw body bytes before any JSON parsing. If you `await request.json()` first and then try to verify, FastAPI consumed the body stream and the signature check fails. Always: read body → verify → parse JSON. The snippet above does this correctly.

> ❓ **Ask the student:** "What's the trade-off of `{type: 5}` deferred vs `{type: 4}` immediate?"
>
> (Answer: immediate is simpler but locks you into <3s response time — usually impossible for an LLM. Deferred is the default for ADK agents. The cost: an extra HTTP call to deliver the follow-up.)

> 🛠 **Have the student run:** the Discord bot locally with ngrok + a test server. Register the `/ask` command. Run `/ask prompt:hello` in the server; observe the "thinking" spinner then the follow-up.

[← Prev: 04_GoogleChatApp](04_GoogleChatApp.md)  [↑ Map](../../MAP.md)  [Next: 06_WhatsAppEmail →](06_WhatsAppEmail.md)
