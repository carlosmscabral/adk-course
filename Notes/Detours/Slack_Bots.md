---
module: Detours
page: Slack_Bots
title: Slack bots — Events API, scopes, and the response_url pattern
estimated_minutes: 30
icon: 🌐
prereqs: []
concepts: [app_manifest, OAuth_scopes, Events_API, Slash_Commands, Interactive_Components, threading, response_url, Block_Kit]
---

[← Back to: 24_ChannelIntegrations]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Slack bots

> 🧭 **Optional.** Take this if Slack's three-headed event model (Events vs Slash Commands vs Interactive) is confusing, or if you've never wired the 3-second-ack `response_url` pattern. Without these, your agent will hit Slack's timeout and surface "dispatch_failed" to users. ~30 min.

---

## 🌐 1. The mental model — Slack delivers events, your bot acks fast

```
  user → Slack workspace
              │
              ├── posts a message            ──► Events API   POST /events
              ├── runs /agent help            ──► Slash Command POST /commands
              └── clicks button / submits form ──► Interactivity POST /interact

  your bot must:
    1. respond 200 within 3 seconds  (Slack's hard timeout)
    2. do real work after            (the response_url pattern, or chat.postMessage)
```

Slack's three event surfaces share an obsession with the 3-second ack. Miss it and Slack retries 3 times, then gives up and shows the user "dispatch_failed" or "this app didn't respond." Every Slack-integration bug report eventually traces back to violating the 3-second rule.

---

## 🌐 2. App manifest — the YAML that defines your app

You create a Slack app once, configure it via a manifest, install it into workspaces. Minimum viable manifest:

```yaml
# slack-manifest.yml
display_information:
  name: My ADK Agent
features:
  bot_user:
    display_name: agent
    always_online: true
  slash_commands:
    - command: /agent
      url: https://my-agent.example.com/slack/commands
      description: Ask the agent
      usage_hint: "[your question]"
oauth_config:
  scopes:
    bot:
      - chat:write           # post messages
      - commands             # receive slash commands
      - app_mentions:read    # see when @mentioned
      - im:history           # read DMs
      - im:write             # reply to DMs
settings:
  event_subscriptions:
    request_url: https://my-agent.example.com/slack/events
    bot_events:
      - app_mention
      - message.im
  interactivity:
    is_enabled: true
    request_url: https://my-agent.example.com/slack/interact
```

Paste this into https://api.slack.com/apps → Create App from Manifest → install to your workspace. Now you have a bot token (`xoxb-...`) and a signing secret.

---

## 🌐 3. OAuth scopes — least privilege

The scopes you ask for at install are *the* security boundary. Common bot scopes:

| scope               | grants                                | when to ask                       |
|---------------------|---------------------------------------|-----------------------------------|
| `chat:write`        | post as the bot                       | always                            |
| `commands`          | receive slash commands                | if you have any                   |
| `app_mentions:read` | see @mentions in channels             | for channel-aware agents          |
| `im:history`        | read DMs to the bot                   | for DM chat agents                |
| `im:write`          | start DMs                             | for proactive notifications       |
| `channels:history`  | read ALL public-channel messages      | rarely justified; review-board   |
| `files:read`        | download uploaded files               | if your agent handles attachments |
| `users:read`        | look up user profiles                 | for personalization               |
| `users:read.email`  | look up user emails                   | for cross-system identity         |

Don't ask for `channels:history` "just in case" — workspace admins notice and reject installs. Start minimal, request more in a versioned reinstall.

---

## 🌐 4. Events vs Slash Commands vs Interactive Components

| surface              | how triggered                          | response window      | response method                  |
|----------------------|----------------------------------------|----------------------|----------------------------------|
| **Events API**       | something happened in the workspace    | ack within 3 s       | `chat.postMessage` later         |
| **Slash Commands**   | user typed `/agent ...`                | ack within 3 s       | `response_url` OR `chat.postMessage` |
| **Interactivity**    | user clicked a button / submitted modal| ack within 3 s       | `response_url` OR `chat.postMessage` |

Slash Commands and Interactivity each give you a per-invocation **`response_url`** in the payload — a one-time URL good for 30 minutes that lets you respond to the same message context multiple times (initial loading state, then final answer). Events API doesn't have this; you post a fresh message instead.

---

## 🌐 5. The `response_url` pattern — survive the 3-second timeout

The canonical handler shape:

```python
# Work/slack_handler.py — run with: uv run uvicorn Work.slack_handler:app --port 8000
import os, asyncio, httpx
from fastapi import FastAPI, Request, BackgroundTasks
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent
from google.genai import types as gtypes

app = FastAPI()

agent = Agent(model="gemini-2.5-flash", name="slackbot",
               instruction="Answer concisely in <=200 words.")
runner = InMemoryRunner(agent=agent, app_name="slackbot")

async def _do_work(response_url: str, user_id: str, text: str):
    session = await runner.session_service.create_session(
        app_name="slackbot", user_id=user_id)
    final = ""
    async for ev in runner.run_async(
        user_id=user_id, session_id=session.id,
        new_message=gtypes.Content(role="user", parts=[gtypes.Part(text=text)]),
    ):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text:
                    final += p.text
    async with httpx.AsyncClient() as cx:
        await cx.post(response_url, json={"text": final, "response_type": "in_channel"})

@app.post("/slack/commands")
async def slash(req: Request, bg: BackgroundTasks):
    form = await req.form()
    text = form.get("text", "")
    user = form.get("user_id", "")
    response_url = form.get("response_url")
    bg.add_task(_do_work, response_url, user, text)
    # Ack immediately — Slack shows this ephemeral "thinking" message
    return {"response_type": "ephemeral", "text": "thinking..."}
```

Two phases: **ack fast**, then **deliver on `response_url`** when ready. Slack will swap the "thinking" message for your final answer.

For Events API (no `response_url`), use `chat.postMessage` from the same background task, targeting the event's `channel` and the original message's `thread_ts`.

> **🚀 In Production**
>
> Always **verify the Slack signature** on inbound requests using your signing secret — otherwise anyone with your URL can hit your agent. Slack docs detail the HMAC-SHA256 scheme; libraries like `slack-bolt` handle it for you. Without verification, your `/slack/commands` is an open prompt-injection portal.

---

## 🌐 6. Threading — replies that stay in the thread

When the Events API delivers a message, the payload includes `ts` (timestamp = message ID) and optionally `thread_ts` (the parent of a thread). To reply *in the thread*:

```python
await client.chat_postMessage(
    channel=event["channel"],
    text="...",
    thread_ts=event.get("thread_ts") or event["ts"],
)
```

Rule: pass the *outer* thread's `ts` as `thread_ts`. If the user posted top-level, use `event["ts"]`; if they posted inside a thread, use `event["thread_ts"]`. Mixing this up scatters replies across the channel.

Map Slack threads to ADK session IDs: `session_id = f"{channel}:{thread_ts}"`. Now a thread is a session — context persists, users can "continue the conversation" naturally.

---

## 🌐 7. Block Kit primer — rich messages

A plain `text` message is the floor. For structured output (cards, buttons, tables), use **Block Kit** — a JSON layout language:

```json
{
  "channel": "C1234",
  "text": "fallback for notifications",
  "blocks": [
    {"type": "section", "text": {"type": "mrkdwn", "text": "*Research Summary*"}},
    {"type": "divider"},
    {"type": "section", "text": {"type": "mrkdwn",
        "text": "Found 3 papers on Mars 2026 mission."}},
    {"type": "actions", "elements": [
      {"type": "button", "text": {"type": "plain_text", "text": "Show all"},
       "action_id": "show_all_papers", "value": "mars-2026"}
    ]}
  ]
}
```

Always include `text` for notification fallbacks (mobile push, screen readers). Use the official **Block Kit Builder** at https://app.slack.com/block-kit-builder to compose visually, then paste the JSON.

When a user clicks a button, Slack hits your **Interactivity** endpoint with `action_id` and `value` — route those to the same background-task pattern from section 5.

---

## 🛠 Have the student try

Wire a minimal Slack bot end-to-end:

1. Create the app from the manifest in section 2 (replace URLs with your dev tunnel — `ngrok http 8000` or Cloudflare Tunnel).
2. Run `Work/slack_handler.py` from section 5.
3. In Slack, run `/agent what is the largest moon of Jupiter?` → expect a "thinking..." ephemeral, then a real answer ~3-5 s later.
4. Add HMAC signature verification (`slack-bolt` or hand-rolled per the docs) and confirm an unsigned curl request to `/slack/commands` returns 401.
5. Bonus: convert the reply to Block Kit with a `divider` and a `button`. Wire the button to a second handler that posts "you clicked it" back to the thread.

---

[← Back to: 24_ChannelIntegrations/02_SlackIntegration](../24_ChannelIntegrations/02_SlackIntegration.md)  [↑ Map](../../MAP.md)

**When you're done:** return to module 24. The dissecting-sample page walks the same patterns through a production-shape Slack agent.
