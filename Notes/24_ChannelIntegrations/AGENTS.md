# 🤖 AGENTS.md — Module 24 Channel Integrations (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening 00_Overview. This is the most "platform-specific" module in the course — most students will care about ONE channel.

## What the student should walk away knowing

- The universal **webhook → Runner adapter** is five steps: verify, parse, resolve user_id+session_id, invoke Runner, post back. Once internalized, every channel page is a variation.
- Chat platforms force a **<3s ACK** — agent work happens in background tasks or queues, never in the webhook handler.
- **Signature verification is mandatory** at the door — skipping it is the #1 channel vulnerability.
- `user_id = f"{channel}:{event.user_id}"` namespaces to avoid cross-channel collisions.
- **Threading policies** (per-thread, per-DM, per-message) are per-channel UX decisions, documented up front.
- **Ambient agents** (Pub/Sub-triggered) are channels too — same five steps, different doorway. ADK ships first-class support via `get_fast_api_app(trigger_sources=["pubsub"])`.
- **OAuth scenarios** (A bot-as-itself, B bot+shared+per-user-context, C bot-as-user) determine token storage complexity.
- **Multimedia** is "fetch bytes, attach as `Part`, Gemini handles" — no separate STT/OCR layer needed in 2026.

## Pacing

- **Easy if**: student has built any webhook-based integration before (Stripe, GitHub Apps, etc.). The five-step shape will feel natural.
- **Easy if**: student has shipped the M3 (Federated Travel Planner) — they've already wrestled with cross-process orchestration; channels are similar.
- **Hard if**: student is unfamiliar with HMAC / JWT / Ed25519 signature verification. Don't go deep; provide the helper snippets and move on. Detour to [[Slack_Bots]] or platform docs if they want details.
- **Hard if**: student tries to set up a real workspace + ngrok mid-lesson and gets bogged down in platform admin UI. Encourage them to read first, set up the workspace after. The fake-channel script on page 01 lets them practice without a real workspace.
- Expected total time for an on-pace student: ~4 hours. Less if they skip channels they don't need.

## Watch for these mistakes

- **Parsing JSON before verifying signature.** They'll consume the body bytes and the signature check fails on empty content. Fix: read body → verify → parse, in that order.
- **Synchronous agent call in the webhook handler.** 3-5s agent call → platform retries → duplicate replies → confused users. Push them to BackgroundTasks IMMEDIATELY when they show the wrong pattern.
- **Forgetting to filter their own bot's messages.** Infinite loops are spectacular and they'll discover it the first time they ship.
- **Trusting raw `channel_user_id` as ADK `user_id`** without the channel: namespace. Two Slack and Discord users with the same ID will collide.
- **Hardcoded bot tokens in source / env files.** Fail this fast; move to Secret Manager.
- **`InMemorySessionService` in channel adapters.** Ambient agents especially — HITL can pause for hours/days. Must be `DatabaseSessionService` or similar from day one.
- **Skipping the 24-hour WhatsApp window check.** They'll find out via failed sends.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "How do I create a Slack app?" | [[Slack_Bots]] — workspace + manifest + scopes |
| "How do I publish a Google Chat app?" | [[GoogleChat_Apps]] — Chat API console + IAM |
| "Where do I deploy this?" | [[Cloud_Run]] — the canonical channel adapter host |
| "How do I wire FastAPI more idiomatically?" | [[FastAPI_for_ADK]] |
| "How does the HITL approval actually pause?" | back to module 4B (Human-in-the-Loop) |
| "What about per-user OAuth?" | this module's page 08 + cross-link to 16 (Security) |

If the same detour is declined twice, stop offering.

## Mini-drill grading

- **Clean pass** = `Work/24_channels/bot_app.py` runs, signature verification happens before parsing, ACK <1s, agent reply posts back via placeholder-edit, no self-loops. Demonstrable with one real Slack/Discord workspace.
- **Pass with hint** = student got the wrong order (parse-then-verify), tutor pointed it out, student reordered and re-tested.
- **Fail** = signature verification skipped entirely, OR synchronous agent call returning >3s, OR bot loops on its own messages.

### Edge case to probe (after the basic drill passes)

- Send the bot a photo and ask "what's this?". If they hadn't read page 09, walk them through `fetch_and_attach` and prove Gemini handles images natively. This is the "wow" moment — usually they expected an OCR/captioning service.
- Or: kill the bot mid-conversation, restart, send a follow-up. If they used `InMemorySessionService` the thread context is lost. Use this to motivate `DatabaseSessionService`.

## Cross-module hooks

- **Prereqs**: 23 (frontend integration — channels are "frontends without browsers"), 21 (the HTTP surface), 16 (security primitives — HMAC, JWT, OAuth), 04 (sessions + state).
- **Closely related**: 4B (HITL — the ambient sample exercises this), 13 (Plugins — ambient bots want retry plugins), 22 (Deployment — Cloud Run is the default channel-adapter host).
- **Forward links**: capstone (module 99) — chances are the student will deploy a channel-fronted agent there.

## Sample anchor notes

- `ambient-expense-agent` — canonical Pub/Sub-triggered + HITL sample. Dissected on page 10.
- For Slack-specific reference, point at detour [[Slack_Bots]] and the canonical Slack Events API docs — no Slack-first sample lives in adk-samples as of 2026-05-27.
- For Google Chat reference, detour [[GoogleChat_Apps]].
