---
module: 24_ChannelIntegrations
page: 07_AmbientAgentsAsChannels
title: Ambient agents — Pub/Sub-triggered ADK, posting back to a channel
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/02, 13_Plugins/00]
concepts: [ambient_agent, pubsub_trigger, trigger_sources, cloud_run_pubsub, fan_out_to_channel]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 06_WhatsAppEmail](06_WhatsAppEmail.md)  [↑ Map](../../MAP.md)  [Next: 08_AuthAndPerUserSession →](08_AuthAndPerUserSession.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 07 Ambient Agents As Channels

# 🛠 The agent that fires itself

So far every channel page has the same shape: *user* speaks → agent responds. **Ambient agents flip it**: an event fires (Pub/Sub message, BigQuery row, calendar trigger, scheduled cron) → agent runs → agent posts a message into a channel.

The user didn't ask. The agent decided to tell them. This is the 2026 "AI as a notification" pattern.

## ADK's Pub/Sub trigger

ADK 2.0 ships first-class Pub/Sub triggers via `get_fast_api_app(trigger_sources=["pubsub"])`. The framework registers `POST /trigger/pubsub` automatically. Pub/Sub push deliveries land there, ADK parses the envelope, constructs a session keyed by subscription name, and invokes your agent with the message body as the user input.

```python
# Work/24_channels/ambient_app.py — run with: uv run uvicorn Work.24_channels.ambient_app:app --port 8080
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,
    trigger_sources=["pubsub"],          # opt in to /trigger/pubsub
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```

That's the entire backend. ADK handles webhook → Runner. You write the agent + the "post-back" tool the agent uses to write into a channel.

## The agent shape

```python
# Work/24_channels/expense_agent/agent.py — the agent that lives next to ambient_app.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
import os, httpx

async def post_to_slack(message: str, tool_context: ToolContext) -> dict:
    """Send `message` to the team Slack channel."""
    channel = os.environ["SLACK_OPS_CHANNEL"]
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
            json={"channel": channel, "text": message},
        )
    return {"ok": r.json().get("ok", False)}

root_agent = Agent(
    name="expense_reviewer",
    model="gemini-2.5-flash",
    instruction=(
        "You receive expense report JSON via Pub/Sub. Review it. "
        "If anything looks off (amount > 500, missing receipt, vague description), "
        "post a summary + your concern to Slack via post_to_slack."
    ),
    tools=[FunctionTool(post_to_slack)],
)
```

The agent reads the Pub/Sub message (delivered as the user input), decides what to do, and uses a tool to write to the channel.

## Wire the trigger

```bash
# 1. Create a Pub/Sub topic and subscription
gcloud pubsub topics create expense-reports
gcloud pubsub subscriptions create review \
  --topic=expense-reports \
  --push-endpoint="https://my-agent-xyz.run.app/trigger/pubsub" \
  --push-auth-service-account=pubsub-pusher@my-project.iam.gserviceaccount.com

# 2. Grant the pusher SA the right to invoke Cloud Run
gcloud run services add-iam-policy-binding my-agent \
  --region=us-central1 \
  --member=serviceAccount:pubsub-pusher@my-project.iam.gserviceaccount.com \
  --role=roles/run.invoker

# 3. Publish a test message
gcloud pubsub topics publish expense-reports \
  --message='{"amount": 750, "vendor": "Hotel X", "description": "trip"}'
```

The push delivery hits `/trigger/pubsub`, ADK invokes `expense_reviewer`, the agent decides "amount over 500", calls `post_to_slack(...)`, and a message appears in your Slack ops channel — **without** a user typing anything.

## Session keying for ambient agents

ADK uses the **Pub/Sub subscription name** as the session `user_id` by default. That's per-subscription, which means:

- All deliveries on the `review` subscription share state.
- If you want per-event isolation, generate a per-message session_id (e.g., from the Pub/Sub `messageId`).
- If you want per-tenant isolation (one subscription per tenant), let ADK's default carry through.

Look at `ambient-expense-agent`'s `fast_api_app.py` for the normalize-subscription-name pattern — it strips `projects/.../subscriptions/` prefix so `user_id` is just `review` instead of the full resource path. We dissect this in page 10.

## Composition — channels in, channels out

This composes beautifully with the rest of the module:

- **Slack inbound** (page 03) — user asks a question.
- **Pub/Sub inbound** (this page) — system triggers a check.
- Both feed the same agent.
- Agent's `post_to_slack` tool posts back regardless of trigger source.

```
   Slack message  ────┐
                      ├──► same agent ──► post_to_slack ──► Slack
   Pub/Sub trigger ───┘                 ─► post_to_email ──► Email
                                        ─► post_to_gchat ──► Google Chat
```

The agent doesn't care how it was triggered.

## Cross-references

- [13 Plugins](../13_Plugins/) — `ReflectAndRetryToolPlugin` is useful for ambient agents that must be reliable.
- [Module 22 Deployment](../22_DeploymentModels/) — Cloud Run + Pub/Sub is the canonical ambient deployment.
- [Sample dissection (page 10)](10_DissectingSample.md) — `ambient-expense-agent` is exactly this pattern, end-to-end.

> 🚀 **In Production**
>
> Pub/Sub at-least-once delivery means your agent **will** see duplicate messages. Either: (a) make your post-back idempotent (de-dupe by message id in state), or (b) ACK quickly *before* doing work and rely on the next page's persistent session for resume. Don't assume exactly-once.

> ❓ **Ask the student:** "What's the auth chain that lets Pub/Sub call your private Cloud Run service?"
>
> (Answer: Pub/Sub uses a *push auth service account*; that SA needs `roles/run.invoker` on the Cloud Run service; Cloud Run verifies the SA's OIDC token at the door. The bash snippet shows all three steps.)

> 🛠 **Have the student run:** locally — POST a fake Pub/Sub envelope to `localhost:8080/trigger/pubsub` with `curl -X POST ... -d '{"message": {"data": "..."}}'`. Watch the agent fire and (if Slack creds are set) post.

[← Prev: 06_WhatsAppEmail](06_WhatsAppEmail.md)  [↑ Map](../../MAP.md)  [Next: 08_AuthAndPerUserSession →](08_AuthAndPerUserSession.md)
