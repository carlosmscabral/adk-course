---
module: 24_ChannelIntegrations
page: 08_AuthAndPerUserSession
title: Auth and per-user session — mapping channel users to ADK user_id
desktop: true
estimated_minutes: 20
prereqs: [24_ChannelIntegrations/01, 23_FrontendIntegration/02]
concepts: [channel_user_mapping, oauth_per_user, identity_link_table, state_user_prefix]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 07_AmbientAgentsAsChannels](07_AmbientAgentsAsChannels.md)  [↑ Map](../../MAP.md)  [Next: 09_HandlingMultimedia →](09_HandlingMultimedia.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 08 Auth And Per-User Session

# 🛠 Two questions about identity in chat

When a channel message hits your webhook, ask two questions:

1. **Who is this user?** (Identity — what `user_id` do we store?)
2. **What can this user do?** (Authorization — what tools/data is allowed?)

Page 01 hand-waved both with `user_id = f"{channel}:{event.user_id}"`. That's fine for read-only Q&A bots. The moment your agent acts ON THE USER'S BEHALF — query their BigQuery, send their email, post in their name — you need real per-user OAuth and a linkage table.

## Three identity scenarios

### Scenario A — The bot acts as itself

The simplest. Agent posts as the bot, queries shared data. No per-user OAuth needed.

```python
user_id = f"slack:{event['user']}"   # just for session keying
# Tools use the bot's own credentials
```

State scoping: `user:` prefix for cross-session per-user memory (preferences, name). Shared state (`app:` prefix) for things all users share.

### Scenario B — Bot has shared API access but tracks per-user context

The bot uses one set of API credentials (e.g., shared BigQuery service account) but personalizes per user. Same as A, plus you might enforce per-user permissions in code:

```python
def query_sales(tool_context: ToolContext, region: str) -> dict:
    allowed_regions = tool_context.state.get("user:allowed_regions", [])
    if region not in allowed_regions:
        return {"error": f"You don't have access to {region}"}
    # ... query
```

### Scenario C — Bot acts AS the user (full OAuth)

The agent calls a downstream API with the *user's* OAuth token (e.g., reads their Gmail, posts to their Drive). You need:

1. **Identity linking** — when user first interacts, redirect them through an OAuth flow that maps `slack:U123` → their Google account.
2. **Token storage** — refresh tokens stored per-user, encrypted at rest.
3. **On-call lookup** — the tool function fetches the token by `tool_context.state["user:auth"]["refresh_token"]`.

## The linkage table

For Scenario C, you store:

| ADK user_id | external_provider | external_subject | refresh_token (encrypted) | scopes | linked_at |
|---|---|---|---|---|---|
| `slack:U123` | google | `1085...uid` | `enc(...)`  | `gmail.send, drive.readonly` | 2026-05-20 |
| `slack:U456` | google | `2199...uid` | `enc(...)`  | `gmail.send` | 2026-05-21 |
| `gchat:users/X` | github | `octocat` | `enc(...)` | `repo` | 2026-05-22 |

Storage: a small DB (Postgres, Firestore, Cloud SQL). **Encrypt at rest with KMS**. Never store plaintext refresh tokens.

## The link flow

```
1. User: @bot summarize my last week of emails
2. Bot: I need access to your Gmail. Click here: <oauth-url>
3. User clicks → OAuth consent → callback URL
4. Callback writes link table row, sets state["user:auth"]["provider"]="google"
5. User: @bot summarize my last week of emails  (retries)
6. Bot's gmail_search tool reads tool_context.state["user:auth"], fetches token, queries Gmail
```

The link URL embeds the `slack:U123` user_id in `state` (the OAuth state param, not ADK state) so the callback knows who's linking.

```python
# Work/24_channels/oauth_link.py — sketch
from fastapi import FastAPI, Request, Response
from urllib.parse import urlencode
import secrets

app = FastAPI()
PENDING = {}                    # in-mem; production: redis

@app.get("/link/google/start")
async def start_link(adk_user_id: str):
    state = secrets.token_urlsafe(16)
    PENDING[state] = adk_user_id
    params = {
        "client_id": "...",
        "redirect_uri": "https://my-bot.run.app/link/google/callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "state": state,
        "access_type": "offline",
    }
    return Response(status_code=302, headers={"location": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"})

@app.get("/link/google/callback")
async def callback(code: str, state: str):
    adk_user_id = PENDING.pop(state, None)
    if not adk_user_id:
        return {"error": "bad state"}
    # Exchange code for tokens, write to link table, write into user state...
    return {"linked": adk_user_id}
```

## State scoping recap (from module 04)

| Prefix | Lifetime | Use for channel bots |
|---|---|---|
| (none) | This session | This thread's transient state |
| `user:` | Across all sessions for this `user_id` | Preferences, name, OAuth link reference |
| `app:` | Across all users | Shared config, public data |
| `temp:` | Single invocation | Cache within one turn |

For channel bots, the most common moves:

- Write `user:name`, `user:locale`, `user:timezone` on first interaction (one-time onboarding).
- Write `user:auth.provider`, `user:auth.linked_at` once OAuth completes.
- Tools look up refresh tokens out-of-band (link table) using `user_id` (not from state — too sensitive to keep there).

## Per-channel vs per-user OAuth

Some channels (Slack workspace install) already give you a workspace-level bot token + sometimes per-user tokens. Don't re-link if the channel already gave you the auth:

- **Slack workspace install** with `users:read` scope → bot can read Slack profiles. No re-link.
- **Slack user token** (per-user OAuth) → if you need `chat:write:user` to post AS the user.
- **Google Chat** with service account → bot acts as itself.
- **Google Chat with OAuth** → bot can use OAuth to call Google APIs on user's behalf.

Pick the minimum. Every additional scope is a security review.

> 🚀 **In Production**
>
> Refresh tokens never expire (unless revoked) and grant long-lived access. Treat them like passwords — KMS encryption, audit log on read, rotate any token whose use looks anomalous (geo, time-of-day). A leaked refresh token is a persistent compromise.

> ❓ **Ask the student:** "Why don't we store the OAuth refresh token directly in ADK session state (`user:refresh_token`)?"
>
> (Answer: ADK state is serialized into session storage — sometimes Postgres, sometimes JSON exports. Refresh tokens demand stronger isolation: dedicated table, encrypted at rest with KMS, audit logging on access. State is the wrong container.)

> 🛠 **Have the student run:** sketch out (don't implement) the identity linking flow for their case — what's the bot doing, does it need scenario A/B/C, what would the link table look like? 5-min whiteboard exercise.

[← Prev: 07_AmbientAgentsAsChannels](07_AmbientAgentsAsChannels.md)  [↑ Map](../../MAP.md)  [Next: 09_HandlingMultimedia →](09_HandlingMultimedia.md)
