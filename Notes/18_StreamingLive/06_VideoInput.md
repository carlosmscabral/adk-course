---
module: 18_StreamingLive
page: 06_VideoInput
title: Video input — webcam / screen capture into Live
estimated_minutes: 25
prereqs: [18_StreamingLive/04]
concepts: [image-blob, frame-rate, base64, screen-capture]
icon: 🎙
in_production: true
detours_suggested: [gRPC]
---

[← Prev: 18_StreamingLive/05_StreamingTools]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/07_LiveProductionPatterns →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 06 Video Input

## Video in Live = a stream of image blobs

There is no separate "video" type in the Live API. You push **individual image frames** as `Blob`s of `image/jpeg` or `image/png`, and the model treats them as a temporal sequence. The cadence is up to you.

Typical settings:
- **1-2 frames per second** for a "tutor that watches your screen."
- **5-10 frames per second** if the model needs to track motion.
- Resolution: 640×480 to 1280×720. Higher is rarely worth the bandwidth or the per-frame cost.

> ⚠️ **Preview / availability note (2026-05):** native video support in Live is GA for image frames over the bidi channel. Continuous video-codec transport (H.264) is preview. The frame-as-blob pattern is the supported path; that's what `bidi-demo` and `realtime-conversational-agent` use.

## Wire format — same as audio, different MIME

From `bidi-demo/app/main.py:211-227`:

```python
# Decode base64 image data
image_data = base64.b64decode(json_message["data"])
mime_type = json_message.get("mimeType", "image/jpeg")

image_blob = types.Blob(mime_type=mime_type, data=image_data)
live_request_queue.send_realtime(image_blob)
```

A webcam frame and a microphone PCM chunk go through the same `send_realtime` call. The MIME type is the discriminator.

## Capturing a webcam frame in Python

```python
# webcam.py
import asyncio
import cv2
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

cam = cv2.VideoCapture(0)
live_q = LiveRequestQueue()

async def webcam_pump(fps: float = 2.0):
    interval = 1.0 / fps
    while True:
        ok, frame = cam.read()
        if not ok:
            await asyncio.sleep(interval); continue
        # encode to JPEG (~30 KB at 720p)
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            await asyncio.sleep(interval); continue
        blob = types.Blob(mime_type="image/jpeg", data=buf.tobytes())
        live_q.send_realtime(blob)
        await asyncio.sleep(interval)
```

For screen capture, swap `cv2.VideoCapture(0)` for `mss` (`pip install mss`):

```python
import mss, numpy as np
with mss.mss() as sct:
    img = np.array(sct.grab(sct.monitors[1]))   # primary monitor
    # then cv2.imencode(...) the same way
```

## Bandwidth math

At 2 fps, 30 KB per JPEG frame, you push **~60 KB/s** upstream. Plus audio at ~32 KB/s (16 kHz × 16-bit). Total ~95 KB/s — comfortably within any home connection.

If you go to 10 fps at higher quality you're at 300+ KB/s; check your egress costs on Cloud Run.

## Why gRPC under the hood matters

Bidirectional gRPC over HTTP/2 multiplexes streams on **one TCP connection**. Your audio chunks, image frames, and control messages share that connection in both directions with frame-level interleaving. That's why latency stays low even when you're pushing video. If "HTTP/2 multiplexing" feels vague, take [[gRPC]] (20 min).

> 🚀 **In Production**
>
> Decide your fps based on the *task*, not your connection. A tutor watching code doesn't need 30 fps — 1 fps is fine, the screen barely changes. Charge yourself for every frame you send; native video tokens are not cheap.

> ❓ **Ask the student:** "Why send JPEG instead of raw RGB pixels?" (A 720p raw frame is ~2.7 MB. JPEG at quality 80 is ~30 KB. 90× smaller, indistinguishable to the model for most tasks.)

> 🧭 **If the student wants to understand the gRPC transport:** suggest detour [[gRPC]] then [[ProtocolBuffers]].

[← Prev: 18_StreamingLive/05_StreamingTools]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/07_LiveProductionPatterns →]
