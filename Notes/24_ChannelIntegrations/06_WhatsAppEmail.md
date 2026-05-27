---
module: 24_ChannelIntegrations
page: 06_WhatsAppEmail
title: WhatsApp and Email — sketches, same pattern
estimated_minutes: 15
prereqs: [24_ChannelIntegrations/02]
concepts: [whatsapp_cloud_api, twilio, smtp, imap, ses_inbound]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 05_DiscordBot](05_DiscordBot.md)  [↑ Map](../../MAP.md)  [Next: 07_AmbientAgentsAsChannels →](07_AmbientAgentsAsChannels.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 06 WhatsApp Email

# 🛠 Two more doorways — same five steps

You've now seen Slack, Google Chat, Discord. WhatsApp and email are *less common* targets for ADK agents but the pattern is identical. This page is a sketch — short on code, long on "here's what changes".

## WhatsApp (Cloud API or Twilio)

**Doorway:** Meta's WhatsApp Cloud API or Twilio's WhatsApp wrapper.

| Step | What's different |
|---|---|
| Sig verify | Meta: HMAC-SHA256 with your app secret on `X-Hub-Signature-256`. Twilio: HMAC-SHA1 with your auth token. |
| Parse | Webhook JSON has `entry[].changes[].value.messages[]`. Text is at `value.messages[0].text.body`. |
| `user_id` | `f"wa:{phone_number}"` — phone numbers are stable. |
| `session_id` | Per-user (single thread per phone). WhatsApp doesn't have "threads". |
| Post back | `POST /messages` to the WhatsApp Cloud API endpoint with bearer token. |
| 3s ACK | Same — Meta retries with backoff. |

The ADK middle three steps are unchanged. Replace `slack_sdk` with `httpx` calls to Meta's graph endpoint, and the bot works.

```python
# Work/24_channels/wa_post.py — pattern shape only
import httpx, os
WA_TOKEN = os.environ["WHATSAPP_TOKEN"]
PHONE_ID = os.environ["WHATSAPP_PHONE_ID"]

async def wa_send(to_phone: str, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WA_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": text[:4096]},   # WhatsApp limit
            },
        )
```

### WhatsApp-specific gotchas

- **24-hour window:** you can only proactively message a user within 24h of their last message. After that, you need pre-approved message templates.
- **Phone-number-based identity** is leaky: a user changes phones, you "lose" them. Plan for re-auth flows.

## Email (Cloud Functions + SES inbound or IMAP polling)

**Doorway:** AWS SES inbound parses emails into S3+SNS; or Cloud Functions with Mailgun/SendGrid inbound; or you poll IMAP.

| Step | What's different |
|---|---|
| Sig verify | SES: verify SNS signature. Mailgun: HMAC on `timestamp + token`. IMAP: there's no webhook, you poll. |
| Parse | MIME parsing: `email.message.EmailMessage` from stdlib, walk `.iter_parts()` for text + attachments. |
| `user_id` | `f"email:{from_address}"`. |
| `session_id` | `In-Reply-To` / `References` headers = email thread. Or per-thread by subject hash. |
| Post back | SMTP send (`smtplib` or async via `aiosmtplib`) using same `Message-Id` chain to thread. |
| 3s ACK | SES requires <30s for SNS notification; comfortable. |

```python
# Work/24_channels/email_reply.py — pattern shape only
import smtplib
from email.message import EmailMessage

def reply_to(in_reply_to_message_id: str, to_addr: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = "agent@yourdomain.com"
    msg["To"] = to_addr
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg["In-Reply-To"] = in_reply_to_message_id
    msg["References"] = in_reply_to_message_id
    msg.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login("agent@yourdomain.com", "...")
        s.send_message(msg)
```

### Email-specific gotchas

- **No real-time:** users expect minute-scale latency, not chat-scale. Use [Pattern D from page 02](02_LongRunningOnChat.md) — long jobs are fine.
- **Thread loss:** if the user changes the subject, `References` chain may break. Defensive: hash the conversation thread on first sight and stash the canonical `session_id` in your own store keyed by user+subject prefix.
- **Spam filtering:** your agent's outbound mail must pass SPF/DKIM. Use a transactional ESP (SES, Postmark, SendGrid) — never raw SMTP from a Compute Engine VM.

## When to use this page vs a real implementation

This page is a **map**, not a how-to. When a student asks "can I do WhatsApp?", point here so they see *which* dial-tones change. The full WhatsApp Cloud API onboarding (Meta Business verification, phone number provisioning, approval queue) is a multi-day affair that doesn't belong in the course.

> 🚀 **In Production**
>
> Both channels share an under-appreciated risk: **outbound-rate limits**. WhatsApp throttles per-phone-per-day. SMTP providers throttle per-IP-per-hour. Your agent might happily generate 200 replies in a tight loop and you discover the limit by way of bounce notifications. Always add a per-channel send budget + alerting.

> ❓ **Ask the student:** "If a WhatsApp user replies 25 hours after your bot's last message, what limits your bot's reply?"
>
> (Answer: the 24-hour customer-service window has expired. Your only legal outbound is a pre-approved template message. Plan templates for the long-tail follow-ups your bot needs to send.)

> 🤖 **Tutor:** if the student isn't shipping a WhatsApp or email integration, skim this page in 5 min and move on. The pattern is the takeaway, not the code.

[← Prev: 05_DiscordBot](05_DiscordBot.md)  [↑ Map](../../MAP.md)  [Next: 07_AmbientAgentsAsChannels →](07_AmbientAgentsAsChannels.md)
