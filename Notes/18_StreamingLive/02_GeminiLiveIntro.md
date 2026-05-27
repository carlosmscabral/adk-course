---
module: 18_StreamingLive
page: 02_GeminiLiveIntro
title: The Gemini Live API — what it is, what ADK wraps
estimated_minutes: 25
prereqs: [18_StreamingLive/01]
concepts: [Live-API, RunConfig, StreamingMode, response_modalities, native-audio, half-cascade]
icon: 🎙
in_production: true
detours_suggested: [gRPC]
---

[← Prev: 18_StreamingLive/01_StreamingFundamentals]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/03_TextStreaming →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 02 Live API Intro

## What "Live" means

The **Gemini Live API** is a single long-lived **bidirectional** session between your client and a Gemini model. Both sides can send at any moment.

- **Inputs**: text, audio (PCM), images, video frames.
- **Outputs**: text and/or audio.
- **Transport**: gRPC bidirectional streaming over HTTP/2 (the Google SDK can also do WebSockets in some clients). If gRPC is hand-wavy, take [[gRPC]] (20 min).

Compare with the request/response model you've used so far:

| | run_async (request/response, streamed reply) | run_live (bidi session) |
|---|---|---|
| Lifetime | One turn | Many turns, one session |
| Client → server during a turn | Only at start | Anytime (interrupt, push audio) |
| Server → client during a turn | Streaming partials | Streaming partials |
| Default modality | Text | Text or audio |
| Backend | Standard generate | Live API endpoint |

## Two model families

ADK's bidi-demo highlights the distinction (see `bidi-demo/app/main.py:105-156`):

- **Native audio** models (e.g. `gemini-2.5-flash-native-audio-preview-12-2025`, `gemini-live-2.5-flash-native-audio`): speech-to-speech end-to-end. **Audio response modality only.** Support proactivity, affective dialog, transcription.
- **Half-cascade** models (e.g. `gemini-2.0-flash-live`): TTS is bolted on. **Text response modality is faster** for non-voice use. Audio is also supported but goes through a cascade.

Pick native audio when you want natural prosody and barge-in. Pick half-cascade when you want lowest-latency text or when the native model isn't available in your region.

## The wrapper: `Runner.run_live(...)`

ADK exposes the Live session through one async iterator:

```python
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode

queue = LiveRequestQueue()
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],   # or ["TEXT"]
)

async for event in runner.run_live(
    user_id="u", session_id="s",
    live_request_queue=queue,
    run_config=run_config,
):
    ...   # same Event shape you already know
```

`LiveRequestQueue` is the **upstream pipe**. You call `queue.send_content(content)` for text turns and `queue.send_realtime(blob)` for audio/image chunks. The Runner reads from this queue and shoves into the Live session for you.

## `RunConfig` — the dials

The dials you'll actually touch:

```python
RunConfig(
    streaming_mode=StreamingMode.BIDI,         # required for Live
    response_modalities=["AUDIO"],             # or ["TEXT"]
    input_audio_transcription=types.AudioTranscriptionConfig(),    # ASR transcript of user
    output_audio_transcription=types.AudioTranscriptionConfig(),   # transcript of model TTS
    session_resumption=types.SessionResumptionConfig(transparent=True),
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
        )
    ),
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck"),
        ),
        language_code="en-US",
    ),
)
```

The full reference is in `bidi-demo/app/main.py:115-145` and `realtime-conversational-agent/server/main.py:41-63`.

> 🚀 **In Production**
>
> Always set `session_resumption=types.SessionResumptionConfig(...)` even in dev. Live sessions die on transient network blips. Without resumption, your user starts the conversation over. With it, the SDK auto-reconnects and replays the resume token. Free win.

> ❓ **Ask the student:** "If you ask a half-cascade model for an `AUDIO` response, does it work?" (Yes, but TTS is generated post-hoc and latency is higher. For voice UX, pick native audio.)

> 🛠 **Have the student run** `python -c "from google.adk.agents.run_config import RunConfig, StreamingMode; print(StreamingMode.__members__)"` to see the available modes (`NONE`, `SSE`, `BIDI`).

[← Prev: 18_StreamingLive/01_StreamingFundamentals]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/03_TextStreaming →]
