---
module: 18_StreamingLive
page: 04_AudioIO
title: Audio I/O — mic in (16 kHz PCM), speaker out (24 kHz PCM)
estimated_minutes: 40
prereqs: [18_StreamingLive/02]
concepts: [PCM, sounddevice, sample-rate, mono, int16, callback-buffer]
icon: 🔊
in_production: true
detours_suggested: [AudioEncoding, AudioQuantization]
---

[← Prev: 18_StreamingLive/03_TextStreaming]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/05_StreamingTools →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 04 Audio I/O

## The shape of audio Live wants

- **Input (mic → Live):** PCM, 16-bit signed integer, **16 kHz mono**. MIME `audio/pcm;rate=16000`.
- **Output (Live → speaker):** PCM, 16-bit signed integer, **24 kHz mono** (typical for native-audio models).

That's it. No header, no container, no compression. Just raw little-endian int16 samples back-to-back.

Why raw PCM? **Lower latency.** No decoding step on the server, no MP3 frame alignment, no Opus packet boundary games. The trade-off is bandwidth (~256 kbps), which is fine for a single session and terrible for Spotify. If "why not MP3?" feels hand-wavy, take [[AudioEncoding]] (20 min).

## Sanity check the dev box

```bash
$ python -c "import sounddevice as sd; print(sd.query_devices())"
   0 HDA Intel PCH: ALC1220 Analog (hw:0,0), ALSA (2 in, 2 out)
>  1 default, ALSA (32 in, 32 out)
```

The `>` marks default input/output. If you don't see at least one device with `in > 0`, your mic isn't visible — fix that before going further.

> 🤖 **Tutor:** if `import sounddevice` fails, the missing piece is the system library, not the wheel. `sudo apt install libportaudio2` on Debian/Ubuntu; `brew install portaudio` on macOS. Then `uv add sounddevice numpy`.

## Capture: 200 ms chunks of int16 mono

```python
# mic_capture.py
import asyncio, queue
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000
CHUNK_MS    = 200
CHUNK_FRAMES = SAMPLE_RATE * CHUNK_MS // 1000   # 3200 samples

q = queue.Queue()  # thread-safe; sd uses a real OS thread

def on_audio(indata, frames, time_info, status):
    if status:
        print("[mic]", status)
    # indata is float32 in [-1, 1]; convert to int16
    pcm16 = (indata[:, 0] * 32767).astype(np.int16)
    q.put(pcm16.tobytes())

async def main():
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="float32", blocksize=CHUNK_FRAMES,
                        callback=on_audio):
        print("recording 3s...")
        await asyncio.sleep(3)
    # drain
    while not q.empty():
        chunk = q.get_nowait()
        print(f"{len(chunk)} bytes ({len(chunk)//2} samples)")

asyncio.run(main())
```

> ⚠️ **Gotcha:** `sd.InputStream` callbacks run on an audio thread, not the asyncio loop. **Never** `await` from inside `on_audio`. Push bytes into a queue and let an async consumer drain.

## Playback: write int16 to an OutputStream

```python
# speaker_play.py
import sounddevice as sd, numpy as np

PLAYBACK_RATE = 24000  # native-audio model output

def play_pcm_chunks(byte_chunks):
    with sd.OutputStream(samplerate=PLAYBACK_RATE, channels=1, dtype="int16") as out:
        for chunk in byte_chunks:
            samples = np.frombuffer(chunk, dtype=np.int16)
            out.write(samples)
```

For barge-in (page 07), you need to be able to **drop the queued buffer** mid-playback. Easiest pattern: keep your own `deque` of pending chunks, and on interruption clear it before the next write.

## Wiring mic into the Live queue

Combine the two:

```python
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

live_q = LiveRequestQueue()

async def mic_pump():
    while True:
        chunk = await asyncio.to_thread(q.get)  # blocks on the sync queue
        blob = types.Blob(mime_type="audio/pcm;rate=16000", data=chunk)
        live_q.send_realtime(blob)
```

`send_realtime` is the right call for streaming audio/image blobs. `send_content` is for whole text turns.

> 🚀 **In Production**
>
> Use 100-250 ms chunks. Smaller = jittery TTFT savings drowned by per-message overhead. Larger = audible lag in barge-in (the model can't react to audio it hasn't received yet).

> 🧭 **If the student wants to understand "why 16 kHz mono?":** suggest detour [[AudioEncoding]] then [[AudioQuantization]] (20 min each).

> ❓ **Ask the student:** "If the input stream callback raises an exception, what happens to the queue?" (The exception is logged to `status` and the stream silently stops feeding. Check the `status` flag every callback.)

[← Prev: 18_StreamingLive/03_TextStreaming]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/05_StreamingTools →]
