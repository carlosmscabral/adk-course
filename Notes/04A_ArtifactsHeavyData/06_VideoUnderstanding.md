---
module: 04A_ArtifactsHeavyData
page: 06_VideoUnderstanding
title: Video understanding — Gemini video Parts ☁️
estimated_minutes: 20
prereqs: [04A_ArtifactsHeavyData/05]
concepts: [video-part, frame-rate, max-length, VideoMetadata]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/05_MultimodalParts](05_MultimodalParts.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/07_SignedUrlsHandoff →](07_SignedUrlsHandoff.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 06 Video understanding ☁️

# ☁️ Video understanding with Gemini

Gemini 2.5 Flash and Pro accept video natively — you hand it an MP4 (inline or via GCS), it samples frames + audio and answers questions about the content. The artifact-store mechanics are the same as the previous page; the wrinkles are sampling rate, length limits, and where the bytes live.

## 🧠 The numbers worth memorising

- **Hard upper bound** on a single video Part: about **1 hour** with audio (≈ 2 hours without audio) at default 1 FPS sampling. Past that, split.
- **Inline size**: capped at the same ~20 MB total-request limit. In practice that is **a few seconds of video**. Anything real-world goes `file_data` from GCS.
- **Default frame sampling**: 1 frame per second + a sparse audio track. Plenty for narration, slow scenes, lecture recordings. Not enough for fast sports clips or rapid UI demos.
- **Bumping the frame rate** (via `video_metadata.fps`) costs proportionally more tokens. Default 1 FPS is the sweet spot for most content; go to 2-5 FPS only when motion matters.

## 🛠 A video Part — `file_data` from GCS

```python
# Work/06_video_understand.py — run with: uv run python Work/06_video_understand.py
import asyncio

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def main():
    video = types.Part(
        file_data=types.FileData(
            file_uri="gs://my-bucket/onboarding_walkthrough.mp4",
            mime_type="video/mp4",
        ),
        video_metadata=types.VideoMetadata(
            start_offset="0s",
            end_offset="180s",   # only the first 3 minutes
            fps=1.0,             # default; show explicitly for clarity
        ),
    )
    prompt = types.Part(text=(
        "Summarise the first 3 minutes of this walkthrough in 5 bullet points. "
        "Call out any UI clicks the narrator demonstrates."
    ))

    agent = LlmAgent(
        name="video_summariser", model="gemini-2.5-flash",
        instruction="You watch video walkthroughs and produce crisp summaries.",
    )
    app = App(root_agent=agent, name="video_app")
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="video_app", user_id="carlos")

    msg = types.Content(role="user", parts=[prompt, video])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        if ev.is_final_response() and ev.content:
            print("REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (depends on the video; structurally):

```
REPLY: - Narrator opens with the login screen and clicks "Sign in with Google".
       - Walks through the empty-state dashboard at 0:23.
       ...
```

## 🧠 The `VideoMetadata` knobs

```python
types.VideoMetadata(
    start_offset="0s",        # trim from the front
    end_offset="180s",        # trim from the back
    fps=1.0,                  # frames per second sampled
)
```

Three reasons to use them:

1. **`start_offset` / `end_offset`** — clip a long video to the segment you actually care about. Cheaper, faster, more focused answer.
2. **`fps`** — bump to 2–5 for fast-motion content; drop to 0.5 for slow, static content if you are pinching tokens.
3. **Combination** — `start=120s, end=180s, fps=2.0` is "the third minute, sampled twice per second" — perfect for "what happened around 2:30?" follow-ups without re-watching the whole thing.

## 🛠 Saving the video Part as an artifact for handoff

```python
# A sub-agent uploads + saves the reference
await tool_context.save_artifact("user:onboarding.mp4", types.Part(
    file_data=types.FileData(
        file_uri="gs://my-bucket/onboarding.mp4",
        mime_type="video/mp4",
    ),
))

# A different sub-agent loads the reference (no bytes copied)
part = await tool_context.load_artifact("user:onboarding.mp4")
# part.file_data.file_uri is the GCS path; Gemini fetches it on the next call.
```

This is the canonical heavy-handoff: bytes live in GCS, the artifact store holds a tiny reference, every agent reads by filename.

## ⚠️ Frame-rate vs cost tradeoff

At 1 FPS a 1-hour video samples 3,600 frames + an audio track — already ~hundreds of thousands of tokens. At 5 FPS the same video is 18,000 frames; you blow your context window and your bill. Default to 1 FPS, only escalate when the question explicitly depends on fast motion.

## ⚠️ Length and split strategy

For videos past the per-request limit, split into chunks (e.g., 20-minute segments) and process sequentially. A `SequentialAgent` over a list of chunk references, each emitting a partial summary with `output_key=`, gives you the whole-video answer in pieces. (Module 05's sub_agents pattern, but the values being passed are video Part references.)

## ❓ Quick check

> ❓ **Ask the student:** they have a 90-minute training recording, and the user is asking "what was the question someone asked during the Q&A?" How would they structure the call to minimise cost while still answering accurately? *(Expected: scrub to roughly where the Q&A starts (e.g., `start_offset="3600s"`), set a reasonable `end_offset`, keep `fps=1.0` since the relevant signal is in the audio. If unknown where Q&A starts, run a cheap first pass at `fps=0.5` to locate the segment, then a second focused call.)*

> 🛠 **Have the student do this:** if they have any MP4 in GCS, run the script with their URI and `end_offset="30s"` for cheapness. If not, walk the `VideoMetadata` constructor on paper — they need to recognise the knobs even if they cannot run it live today.

> **🚀 In Production**
>
> Videos in artifact stores age expensively. A 200 MB MP4 sitting in GCS for a year is one user's worth of storage cost. Lifecycle policies (page 03) matter twice as much for video. Also: **never** assume a user-uploaded video is safe. Always run it past a content-safety check before passing to the model — Module 16 covers the safety plugin pattern.

---

[← Prev: 04A_ArtifactsHeavyData/05_MultimodalParts](05_MultimodalParts.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/07_SignedUrlsHandoff →](07_SignedUrlsHandoff.md)
