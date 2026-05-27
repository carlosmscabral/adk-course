---
module: Detours
page: GoogleChat_Apps
title: Google Chat Apps — config, message vs card responses, threading
estimated_minutes: 25
icon: 🌐
prereqs: []
concepts: [chat_app_config, message_response, card_v2, threading, audience_IAM, slash_commands, sync_vs_async_response]
---

[← Back to: 24_ChannelIntegrations]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Google Chat Apps

> 🧭 **Optional.** Take this if you're standing up a Google Chat agent and the GCP-Console-driven config is unfamiliar. Compared to Slack, Chat Apps are easier to auth (Google IAM) but the message format (Card v2) is fussier. ~25 min.

---

## 🌐 1. The mental model — sync-by-default, IAM-gated

```
  user → Google Chat
              │
              ├── DM to app or @mention in space  ──► POST your endpoint
              │
              │   your bot:
              │     - returns JSON within 30 s        (synchronous; simplest)
              │     - or 200 OK + posts async later   (Chat REST API)
              │
              └── IAM controls who can install + who can mention
```

Unlike Slack's 3-second-ack-then-callback pattern, Google Chat gives you a **generous 30-second window** to respond synchronously. For agent workloads that finish in <30 s, you can return the answer in the same HTTP response — much simpler than Slack.

For longer work, you 200 OK immediately and use the Chat REST API to post follow-up messages into the same space/thread.

---

## 🌐 2. App config in GCP Console

Google Chat Apps are **GCP-project-scoped**, configured at https://console.cloud.google.com/apis/api/chat.googleapis.com → "Configuration":

```
  App name:     my-adk-agent
  Avatar URL:   gs:// or https://
  Description:  "Research assistant"

  Functionality:
    [x] Receive 1:1 messages
    [x] Join spaces and group conversations

  Connection settings:
    ( ) Apps Script
    ( ) Cloud Functions
    (x) HTTP endpoint URL:  https://my-agent.example.com/chat
        Authentication audience: Project **Number** (or your HTTPS endpoint URL — JWT mode vs OIDC mode)

  Slash commands:
    /research       command_id: 1   description: Research a topic
    /summarize      command_id: 2   description: Summarize a doc

  Permissions:
    ( ) Specific people and groups in your domain: ops-team@example.com
    (x) Everyone in your domain
    ( ) Everyone   <-- only for marketplace apps
```

The key field is **Authentication audience**: when set, Google signs the inbound request with a bearer token whose `aud` claim is either your **project number** (JWT mode) or your HTTPS endpoint URL (OIDC mode). Your endpoint should verify this token — proves the request really came from Google Chat. (Slack's HMAC analogue.) Using the wrong value (e.g., project ID instead of project number) silently fails verification.

---

## 🌐 3. The inbound event payload

A user @mentions the bot or posts to a DM → Google POSTs your endpoint with:

```json
{
  "type": "MESSAGE",
  "eventTime": "2026-05-27T14:32:01Z",
  "space": {
    "name": "spaces/AAAA",
    "type": "DM"
  },
  "user": {
    "name": "users/123",
    "displayName": "Ada Lovelace",
    "email": "ada@example.com"
  },
  "message": {
    "name": "spaces/AAAA/messages/BBBB",
    "sender": {"name": "users/123"},
    "text": "@my-adk-agent what is the largest moon of Jupiter?",
    "thread": {"name": "spaces/AAAA/threads/CCCC"},
    "slashCommand": {"commandId": 1}
  }
}
```

`type` is the event class — `MESSAGE`, `ADDED_TO_SPACE`, `REMOVED_FROM_SPACE`, `CARD_CLICKED`. Most logic branches on this.

---

## 🌐 4. Message responses — text vs card

Two response shapes. Both are JSON bodies you return directly (sync) or POST to the Chat REST API (async).

**Plain text** — the floor:

```json
{
  "text": "The largest moon of Jupiter is Ganymede."
}
```

**Card v2** — rich layout with sections, widgets, buttons:

```json
{
  "cardsV2": [{
    "cardId": "research-result",
    "card": {
      "header": {
        "title": "Research result",
        "subtitle": "Jupiter's moons",
        "imageUrl": "https://example.com/jupiter.png",
        "imageType": "CIRCLE"
      },
      "sections": [{
        "header": "Top match",
        "widgets": [
          {"textParagraph": {"text": "<b>Ganymede</b> — radius 2,634 km, larger than Mercury."}},
          {"buttonList": {"buttons": [
            {"text": "Full report",
             "onClick": {"action": {"function": "show_full", "parameters": [
               {"key": "topic", "value": "jupiter-moons"}
             ]}}}
          ]}}
        ]
      }]
    }
  }]
}
```

The button's `onClick.action.function` is a string Chat sends back when clicked, as a `CARD_CLICKED` event — your handler routes on `event.common.invokedFunction`. Same pattern as Slack Interactivity, GCP-flavored.

Card v2 supports: `textParagraph`, `image`, `decoratedText`, `buttonList`, `divider`, `grid`, `chipList`, plus interactive widgets (`textInput`, `selectionInput`, `dateTimePicker`). For complex output, prefer cards — they render consistently across web/iOS/Android.

---

## 🌐 5. Threading — replies that stay in the thread

Google Chat has two threading models, set per-space:

- **Named threads (default in spaces)** — each reply belongs to a thread. To reply in a specific thread, include `thread` in your response or REST call.
- **Inline threading (newer)** — every message is a top-level message; replies are linked via `quotedMessageMetadata`.

For sync responses to a `MESSAGE` event, return:

```json
{
  "text": "answer",
  "thread": {"name": "spaces/AAAA/threads/CCCC"}
}
```

The `thread.name` comes from the inbound `event.message.thread.name`. Omitting it (or passing a different thread name) creates a new top-level message. Map Chat threads to ADK session IDs the same way you map Slack threads: `session_id = event.message.thread.name`.

---

## 🌐 6. IAM and audience — who can install, who can use

Three layers gate access:

1. **Visibility** (configured in app settings): "Specific people," "Everyone in domain," or "Everyone." Controls install scope.
2. **Workspace admin policy**: admins can block third-party apps wholesale, regardless of your visibility setting.
3. **Inbound auth**: the audience JWT proves the request is from Google Chat — verify it before acting. Endpoint impersonation is the standard attack vector.

Two verification paths depending on the audience mode you picked in app settings:

```python
# JWT mode — audience = your project NUMBER (e.g., "1234567890")
# Token is a self-signed JWT from chat@system.gserviceaccount.com.
from google.auth import jwt
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token

def verify_chat_request_jwt(authz_header: str, project_number: str):
    token = authz_header.removeprefix("Bearer ").strip()
    claims = id_token.verify_token(
        token, g_requests.Request(),
        audience=project_number,  # NOT project ID — the numeric project number
        certs_url="https://www.googleapis.com/service_accounts/v1/metadata/x509/chat@system.gserviceaccount.com",
    )
    assert claims["iss"] == "chat@system.gserviceaccount.com"
    return claims

# OIDC mode — audience = your HTTPS endpoint URL
# Token is a Google-signed OIDC ID token; verify against Google's standard certs.
def verify_chat_request_oidc(authz_header: str, endpoint_url: str):
    token = authz_header.removeprefix("Bearer ").strip()
    claims = id_token.verify_oauth2_token(
        token, g_requests.Request(), audience=endpoint_url,
    )
    # In OIDC mode the issuer is Google; identity comes from the email claim.
    assert claims["iss"] in ("https://accounts.google.com", "accounts.google.com")
    assert claims["email"] == "chat@system.gserviceaccount.com"
    return claims
```

`expected_audience` matches the value you configured in the app settings — your project **number** (JWT mode) or your endpoint URL (OIDC mode). See [Verify requests from Chat](https://developers.google.com/workspace/chat/verify-requests-from-chat) for the full spec.

> **🪧 Official issuer for service-account-authenticated Chat events**
>
> Both the `iss` claim (`chat@system.gserviceaccount.com`) and the X.509 metadata URL above are canonical — see [Verify requests from Chat](https://developers.google.com/workspace/chat/verify-requests-from-chat). ADK's `id_token.verify_token(...)` validates the JWT signature against the public certs published at that metadata URL.

> **🚀 In Production**
>
> Never accept an unauthenticated POST to your Chat endpoint. Even on internal Cloud Run with `--no-allow-unauthenticated`, the request still needs to be a Chat one — set the Chat service account as the only invoker, OR verify the audience JWT inside your handler. The two strategies stack.

---

## 🌐 7. Slash commands

Defined in app config (section 2), commands appear in Chat's autocomplete: type `/` and pick. The inbound event carries `message.slashCommand.commandId` matching the ID you set.

```python
@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    if body["type"] != "MESSAGE":
        return {}
    cmd_id = body["message"].get("slashCommand", {}).get("commandId")
    text = body["message"]["text"]
    user_id = body["user"]["name"]
    thread_name = body["message"]["thread"]["name"]
    if cmd_id == 1:  # /research
        return await handle_research(text, user_id, thread_name)
    if cmd_id == 2:  # /summarize
        return await handle_summarize(text, user_id, thread_name)
    return await handle_mention(text, user_id, thread_name)
```

The `text` for a slash command still includes the command name (`/research jupiter moons`) — strip it before passing to the agent.

---

## 🌐 8. Async responses — going past 30 seconds

For long-running agents, ack immediately and POST follow-ups via the Chat REST API:

```python
# Quick ack
return {"text": "Researching... I'll follow up in this thread."}

# Later, from a background task:
from googleapiclient.discovery import build
chat_svc = build("chat", "v1", credentials=...)  # ADC + chat.bot scope
chat_svc.spaces().messages().create(
    parent="spaces/AAAA",
    body={
        "text": "Done — Ganymede is the largest moon.",
        "thread": {"name": "spaces/AAAA/threads/CCCC"},
    },
    messageReplyOption="REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
).execute()
```

Your service account needs the **`chat.bot`** scope. The Chat app's runtime identity gets the role implicitly when configured with HTTP-endpoint connection, but when you construct credentials in your own code (ADC + an SA), you must request the `https://www.googleapis.com/auth/chat.bot` scope **explicitly** — e.g., `google.auth.default(scopes=["https://www.googleapis.com/auth/chat.bot"])`. The `messageReplyOption` flag controls behavior when the thread no longer exists.

---

## 🛠 Have the student try

End-to-end Google Chat bot on Cloud Run:

1. In GCP Console → Google Chat API → Configuration, create an app with one slash command (`/agent`) and an HTTPS endpoint URL pointing to your dev tunnel (`ngrok http 8080`).
2. Run a minimal FastAPI handler that:
   - Verifies the inbound audience JWT.
   - On a `MESSAGE` event, runs the ADK agent (`runner.run_async`) and returns the final text in the same response, threaded to `event.message.thread.name`.
3. Add the bot to a test space, run `/agent what is 17 * 23?` → expect a threaded reply within 30 s.
4. Convert the response to a Card v2 with a header, one section, and a button. Verify the button click arrives as a `CARD_CLICKED` event.

---

[← Back to: 24_ChannelIntegrations/03_GoogleChatIntegration](../24_ChannelIntegrations/04_GoogleChatApp.md)  [↑ Map](../../MAP.md)

**When you're done:** return to module 24. The In-Production page compares Slack vs Google Chat trade-offs and points to the dissecting-sample for a working Chat agent.
