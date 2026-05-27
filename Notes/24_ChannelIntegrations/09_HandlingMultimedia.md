---
module: 24_ChannelIntegrations
page: 09_HandlingMultimedia
title: Handling multimedia — voice notes, images, files from chat
estimated_minutes: 25
prereqs: [24_ChannelIntegrations/03, 04A_Artifacts/00]
concepts: [voice_note, image_upload, file_download, ArtifactService, transcription, Part_inline_data]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 08_AuthAndPerUserSession](08_AuthAndPerUserSession.md)  [↑ Map](../../MAP.md)  [Next: 10_DissectingSample →](10_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 24 Channel Integrations ▸ 09 Handling Multimedia

# 🛠 When the user sends a photo, a voice note, a PDF

Chat platforms deliver multimedia as either:

- An **inline blob** in the webhook body (small, base64-encoded — rare for big files).
- A **download URL + auth token** that you fetch separately (the common case).

Your adapter's job is: fetch the bytes, attach them as a `Part` to the user message, let Gemini handle it natively. Gemini 2.5 understands images, PDFs, and audio without explicit transcription.

## The shape

```python
# Work/24_channels/multimedia_adapter.py
import httpx
from google.genai import types

async def fetch_and_attach(file_url: str, mime_type: str, auth_token: str | None = None) -> types.Part:
    """Download a file from a channel CDN and wrap it as a genai Part."""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    async with httpx.AsyncClient() as client:
        r = await client.get(file_url, headers=headers, follow_redirects=True)
        r.raise_for_status()
    return types.Part(inline_data=types.Blob(mime_type=mime_type, data=r.content))

# Then in the adapter:
text_part = types.Part(text=event["text"])
file_part = await fetch_and_attach(event["file_url"], event["file_mime"], slack_token)
msg = types.Content(role="user", parts=[text_part, file_part])
# runner.run_async(... new_message=msg)
```

That's it. Gemini sees both the text and the file in one message. For a photo + "what's in this?", the model captions it. For an audio file + "transcribe", it transcribes. For a PDF + "summarize", it summarizes.

## Per-channel specifics

### Slack — files in messages

When a user uploads a file, the message event includes a `files: [...]` array. Each entry has:

```json
{
  "id": "F0123",
  "url_private": "https://files.slack.com/files-pri/T0.../F0123/photo.jpg",
  "mimetype": "image/jpeg",
  "filetype": "jpg",
  "size": 245631
}
```

Fetch `url_private` with `Authorization: Bearer <SLACK_BOT_TOKEN>`. Without the token, Slack returns the file's HTML viewer page instead of the bytes (a classic foot-gun).

```python
# Inside the Slack adapter from page 03:
file_parts = []
for f in event.get("files", []):
    if f["size"] > 20_000_000:  # 20MB cap
        continue
    file_parts.append(await fetch_and_attach(f["url_private"], f["mimetype"], SLACK_BOT_TOKEN))
msg = types.Content(role="user", parts=[types.Part(text=event["text"])] + file_parts)
```

### Google Chat — attachments

Chat messages include `attachment: [...]`. Each has a `downloadUri` or `attachmentDataRef.resourceName`. Use the Chat API to fetch:

```python
attachment_data = chat_service.media().download_media(
    resourceName=attachment["attachmentDataRef"]["resourceName"]
).execute()
```

### Discord — attachments

Discord message payloads have `attachments: [{url, content_type, size, ...}]`. URLs are public-but-obscure; fetch without auth.

### WhatsApp — media messages

WhatsApp text messages with media have `value.messages[0].image.id` (or `audio.id`, `document.id`). Use the WhatsApp Graph API to retrieve the URL, then fetch:

```python
# Step 1: get URL
r = await client.get(f"https://graph.facebook.com/v18.0/{media_id}",
                     headers={"Authorization": f"Bearer {WA_TOKEN}"})
media_url = r.json()["url"]
# Step 2: fetch with the same token
r = await client.get(media_url, headers={"Authorization": f"Bearer {WA_TOKEN}"})
```

Two requests; you can't shortcut.

## Voice notes — transcription is automatic

Gemini handles audio natively. Send the bytes as `audio/ogg` (Slack/WhatsApp voice notes) or `audio/mp4` or `audio/wav` — no separate Speech-to-Text call needed:

```python
# Work/24_channels/voice_note.py — sketch
voice_part = await fetch_and_attach(slack_audio_url, "audio/ogg", SLACK_BOT_TOKEN)
msg = types.Content(role="user", parts=[
    types.Part(text="Transcribe and summarize the audio."),
    voice_part,
])
```

For long audio (>1 min), the cost adds up — but the *latency* is similar to text+image. Test with real samples before assuming.

## When to persist via ArtifactService

If the same file is referenced across multiple turns, push it to `ArtifactService` so you don't re-fetch every turn:

```python
# Save once
await artifact_service.save_artifact(
    app_name="bot", user_id=user_id, session_id=session_id,
    filename="user_photo.jpg",
    artifact=file_part,
)
# Tools can later load it by name
```

For one-shot ("what's in this photo?" → reply → done), inline is fine. For "OK now compare this to the one I sent yesterday", artifacts win. See [04A Artifacts & Heavy Data](../04A_ArtifactsHeavyData/) for the deep dive.

## Sending media back

Most agents reply with text only. If you need to *send* an image back:

- **Slack**: `files.upload` with `channels` + `thread_ts`.
- **Google Chat**: attach a card with an image element.
- **Discord**: `multipart/form-data` POST on the interaction follow-up.
- **WhatsApp**: `type: "image"` + `image.link` URL.

For agent-generated images (Imagen, Genmedia), upload the bytes to a CDN/GCS first, then send the public URL — most platforms prefer URLs over uploads for >1MB.

> 🚀 **In Production**
>
> Always cap file size at the door (Slack default Pro tier: 1GB per file, but you don't want a 1GB voice note in your Gemini context window). Soft cap at 20-50MB; reject early with a friendly "file too large" message. Sending oversized inline data to Gemini fails with a 400 — *catch and message gracefully*.

> ❓ **Ask the student:** "Why do we attach the file as an inline `Part` instead of putting it in `ArtifactService` immediately?"
>
> (Answer: artifacts persist into session storage. For one-shot photo+question, that's wasted I/O. Persist when you'll reuse; pass inline when it's a turn-local question. The decision is per-use, not per-file.)

> 🛠 **Have the student run:** if they have a real Slack bot — DM it a photo with "what's this?". Watch the agent describe it. Then send a voice note: "what did I say?". No STT plumbing required.

[← Prev: 08_AuthAndPerUserSession](08_AuthAndPerUserSession.md)  [↑ Map](../../MAP.md)  [Next: 10_DissectingSample →](10_DissectingSample.md)
