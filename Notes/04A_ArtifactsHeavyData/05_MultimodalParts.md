---
module: 04A_ArtifactsHeavyData
page: 05_MultimodalParts
title: Multimodal Parts — inline_data vs file_data
estimated_minutes: 20
prereqs: [04A_ArtifactsHeavyData/04]
concepts: [inline_data, file_data, Blob, FileData, mime_type]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/04_SaveAndLoadFromTools](04_SaveAndLoadFromTools.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/06_VideoUnderstanding →](06_VideoUnderstanding.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 05 Multimodal Parts

# 🧠 `inline_data` vs `file_data`

A `genai.types.Part` carries the actual modality payload to Gemini. There are two ways to attach binary content: **inline** (bytes in the Part) and **referenced** (a URI the model fetches). Pick the right one or you waste either bandwidth or money.

## 🧠 The two shapes

```python
from google.genai import types

# Inline — bytes travel inside the request
inline = types.Part(inline_data=types.Blob(
    data=open("chart.png", "rb").read(),
    mime_type="image/png",
))

# Referenced — Gemini fetches by URI (GCS, https, etc.)
referenced = types.Part(file_data=types.FileData(
    file_uri="gs://my-bucket/uploads/long_video.mp4",
    mime_type="video/mp4",
))
```

Both produce one `Part` you can put in `Content(parts=[...])` or save as an artifact. The model sees the same modality either way; the wire format differs.

## 🧠 The rule

| Use **inline_data** when... | Use **file_data** when... |
|---|---|
| Payload ≤ ~10 MB | Payload > 10 MB |
| Asset is ephemeral (just-generated chart) | Asset lives in GCS / a URL anyway |
| You will not reuse the bytes across turns | You will reuse the same asset many times |
| Latency matters more than bandwidth | Bandwidth and request size matter more |

ADK's request budget is generous but not infinite. The Gemini API caps a single request around ~20 MB; long videos and big PDFs **must** go `file_data`. There is also no point base64-shipping a 50 MB MP4 over HTTP when Gemini's backend lives one hop from your GCS bucket.

## 🛠 Inline — generate, save, send

```python
# Work/05a_inline_image.py — run with: uv run python Work/05a_inline_image.py
import asyncio
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def main():
    # A 1x1 PNG we ship inline as a smoke test
    tiny_png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000a49444154789c63600000000200015df8b5a30000000049454e44ae426082"
    )
    img = types.Part(inline_data=types.Blob(data=tiny_png, mime_type="image/png"))
    prompt = types.Part(text="In one sentence: what colour is this pixel?")

    agent = LlmAgent(name="vision", model="gemini-2.5-flash",
                     instruction="Answer image questions concisely.")
    app = App(root_agent=agent, name="vision_app")
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="vision_app", user_id="carlos")

    msg = types.Content(role="user", parts=[prompt, img])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content:
            print("REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (varies, but mentions transparency / no colour because the pixel is transparent):

```
REPLY: That pixel is transparent — no visible colour.
```

## 🛠 Referenced — point at a GCS object

```python
# Work/05b_file_data.py — run with: uv run python Work/05b_file_data.py
import asyncio
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


async def main():
    # Assume gs://my-bucket/sample_invoice.pdf already exists
    pdf = types.Part(file_data=types.FileData(
        file_uri="gs://my-bucket/sample_invoice.pdf",
        mime_type="application/pdf",
    ))
    prompt = types.Part(text="What is the total on this invoice?")

    agent = LlmAgent(name="reader", model="gemini-2.5-flash",
                     instruction="Read the document and answer.")
    app = App(root_agent=agent, name="reader_app")
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="reader_app", user_id="carlos")

    msg = types.Content(role="user", parts=[prompt, pdf])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content:
            print("REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (depends on the PDF):

```
REPLY: The invoice total is $1,247.50.
```

The Gemini backend fetches the PDF from GCS directly — your process never has to hold the bytes, and the request stays a few hundred bytes instead of multi-MB.

## 🧠 Artifact storage of `file_data` Parts

When you `save_artifact(name, part)` where `part` carries `file_data`, the artifact service **records the URI reference, not the bytes**. The bytes already live at `file_uri`; storing them twice would be wasteful. (See `BaseArtifactService.save_artifact` docstring — it explicitly handles the `file_data` case.)

This is the foundation of the signed-URL handoff pattern (page 07): a tool uploads bytes to GCS, then saves a Part with `file_data` pointing at the upload. Downstream agents `load_artifact` and get the URI — no bytes ever sit in state or in the event stream.

> ⚠️ **Heads up — `GcsArtifactService` does NOT yet support `file_data`.** `gcs_artifact_service.py:232-236` raises `NotImplementedError("Saving artifact with file_data is not supported yet in GcsArtifactService.")`. Only `InMemoryArtifactService` and `FileArtifactService` walk the `is_artifact_ref` path today. So for the URI-reference pattern, wire `InMemoryArtifactService` or `FileArtifactService`; if you must use `GcsArtifactService`, save the bytes inline via `inline_data` instead. Track the GCS gap on upgrades — when it lands, the snippet on page 07 will work uniformly.

## ⚠️ Common stumbles

- **Wrong `mime_type`.** Gemini routes on MIME — `image/png` vs `application/pdf` vs `video/mp4` trigger different pipelines. Sniffing extension is not enough; set the MIME explicitly.
- **Inlining a giant file.** If the request fails with a body-size error, the file is too big to inline. Upload to GCS first, switch to `file_data`.
- **Forgetting that `file_uri` must be readable by the Gemini service account, not your process.** Public `https://` URLs work; `gs://` URLs require either uniform bucket-level access with the Vertex AI service agent granted read, or a signed URL. Page 07 covers signed URLs.

## ❓ Quick check

> ❓ **Ask the student:** the user uploads a 35 MB MP4 recording. Where do the bytes go, and how does Gemini see them? *(Expected: bytes go to GCS (upload from your process or via a signed URL). Build a `Part(file_data=FileData(file_uri="gs://...", mime_type="video/mp4"))` and put it in `Content(parts=[...])`. Gemini fetches directly. Inlining a 35 MB file would exceed the request size limit.)*

> 🛠 **Have the student do this:** sketch both `Part(...)` constructors from memory — `inline_data=types.Blob(data=..., mime_type=...)` vs `file_data=types.FileData(file_uri=..., mime_type=...)`. They will type these often; the muscle memory matters.

> **🚀 In Production**
>
> The 10 MB rule of thumb is conservative. If you have any doubt about the size — or if the same asset will be referenced more than once — go `file_data`. The cost difference (egress, request body bandwidth, retries that re-upload the bytes) compounds quickly at scale.

---

[← Prev: 04A_ArtifactsHeavyData/04_SaveAndLoadFromTools](04_SaveAndLoadFromTools.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/06_VideoUnderstanding →](06_VideoUnderstanding.md)
