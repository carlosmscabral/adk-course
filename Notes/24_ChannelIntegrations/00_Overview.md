---
module: 24_ChannelIntegrations
page: 00_Overview
title: Channel Integrations — Slack, Chat, Discord, ambient triggers
estimated_minutes: 15
prereqs: [23_FrontendIntegration/00, 21_ApiSurface/00]
concepts: [webhook, channel_adapter, channel_user_mapping, background_ack, ambient_agent]
icon: 🗺
in_production: true
detours_suggested: [Slack_Bots, GoogleChat_Apps]
---

[← Prev: 23_FrontendIntegration/14_MiniDrill](../23_FrontendIntegration/14_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WebhookToRunnerPattern →](01_WebhookToRunnerPattern.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 00 Overview

# 🗺 Module 24 — Channel Integrations

Module 23 was the browser. This module is **everything else**: Slack, Google Chat, Discord, WhatsApp, email, Pub/Sub triggers. Different surfaces, *same backbone*. Every channel boils down to one universal adapter:

```
   webhook in  →  parse → build user_id+session_id → invoke Runner → respond
```

Once you've written it for one channel, the rest are 80% the same code with a different signature scheme and a different "post message" call.

## 🎯 What you'll walk away knowing

- The **webhook → Runner adapter** pattern (the universal piece).
- How chat platforms force you to **ACK quickly** and how to do real work in the background.
- Slack bot, Google Chat app, Discord — each in one focused page.
- A sketch for **WhatsApp / email** — same pattern, different doorways.
- **Ambient agents** — Pub/Sub triggers ADK, ADK posts back to a channel.
- Mapping **channel user → ADK user_id**, and what state lives where.
- How to handle **multimedia** (voice notes, images, files) from chat platforms.

## 📋 Prereqs

- 23 (you understand how *some* client speaks to ADK; this generalizes).
- 21 (ADK's runtime surface — `Runner.run_async`, sessions).
- 16 (security — signature verification, secret management).
- Helpful: 13 (Plugins — ambient agent webhooks land here).

## ⏱ Time

- **Total**: ~4 hours over 2 sessions.
- Each channel page (03–05) is ~25 min. Skip ones that aren't relevant to your work.

## 🧪 Sample anchor

This module dissects **`ambient-expense-agent`** at `/home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/`. It's a Pub/Sub-triggered ADK agent that processes expense reports and posts approval requests back to a frontend. The "channel" is Pub/Sub, but the adapter pattern is identical to Slack/Discord — webhook in, Runner invoked, response posted back.

## The mental picture

```
   Slack / GChat / Discord / WhatsApp / Email / Pub/Sub
                            │
                            ▼
                ┌───────────────────────┐
                │  webhook handler      │
                │   (the universal      │
                │    adapter)           │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   ADK Runner / Agent  │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Post back to channel│
                └───────────────────────┘
```

Full figure at [_figures/webhook_to_runner.txt](_figures/webhook_to_runner.txt).

## 🛣 Plan

1. **01 WebhookToRunnerPattern** — the universal adapter, step by step
2. **02 LongRunningOnChat** — quick ACK + background work + thread updates
3. **03 SlackBot** 🌐 — Events API, slash commands, threading
4. **04 GoogleChatApp** 🌐 — Chat Apps, message↔Runner mapping, IAM
5. **05 DiscordBot** 🌐 — Discord interactions API
6. **06 WhatsAppEmail** — sketch only; pattern repeats
7. **07 AmbientAgentsAsChannels** — Pub/Sub-triggered ADK → posting back
8. **08 AuthAndPerUserSession** — channel user → ADK user_id mapping
9. **09 HandlingMultimedia** — voice notes, images, files from chat
10. **10 DissectingSample** — `ambient-expense-agent` end-to-end
11. **11 InProduction** — consolidated checklist
12. **12 KnowledgeCheck** — 7 questions
13. **13 MiniDrill** — build a Slack-or-Discord adapter

After this module: → **Capstone (Module 99)** or back to whichever channel matters for your work.

> 🤖 **Tutor:** the student may only care about one channel (Slack OR Chat OR Discord). Validate up front and skip the ones they don't need. The universal pattern in page 01 is non-negotiable; the platform pages are choose-your-own.

[← Prev: 23_FrontendIntegration/14_MiniDrill](../23_FrontendIntegration/14_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WebhookToRunnerPattern →](01_WebhookToRunnerPattern.md)
