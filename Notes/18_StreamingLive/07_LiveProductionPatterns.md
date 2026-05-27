---
module: 18_StreamingLive
page: 07_LiveProductionPatterns
title: Live production patterns — barge-in, VAD, latency, reconnection
estimated_minutes: 30
prereqs: [18_StreamingLive/04, 18_StreamingLive/02]
concepts: [barge-in, VAD, AutomaticActivityDetection, session_resumption, p50, p99]
icon: 🚀
in_production: true
---

[← Prev: 18_StreamingLive/06_VideoInput]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/08_DissectingLiveSample →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 07 Production Patterns

## Barge-in — the single most user-visible thing

Barge-in: the user starts talking while the model is talking. The expected behavior:

1. Model **stops** producing audio immediately.
2. Currently-playing audio is **cut**, not allowed to drain.
3. Model listens, then responds to the *new* input.

Server side, the Live API tells you with `event.interrupted == True`. From `realtime-conversational-agent/server/main.py:82-93`:

```python
async for event in live_events:
    message = {
        "interrupted": event.interrupted or False,
        ...
    }
    if message["interrupted"]:
        await websocket.send_text(json.dumps(message))
```

Client side, your audio player has to honor it:

```python
# pseudo-code
def on_event(evt):
    if evt.get("interrupted"):
        audio_player.clear_buffer()    # drop the queue
        return                          # do NOT play more
    # else append new audio chunks
```

See `_figures/barge_in.txt`:

```
T0  user speaks  ─────╮
                      |  VAD: start-of-speech
T1  model speaking      ──────────╮
T2                                X  event.interrupted = True
T3  client clears audio buffer; model listens
T4  model produces a NEW turn ──────────►
```

## VAD — who decides "user is talking"?

**Voice Activity Detection.** Two options:

1. **Server-side automatic VAD** (default). You set sensitivity:

   ```python
   realtime_input_config=types.RealtimeInputConfig(
       automatic_activity_detection=types.AutomaticActivityDetection(
           start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
           end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
           prefix_padding_ms=0,
           silence_duration_ms=0,
       ),
   )
   ```

   `LOW` start-sensitivity = the model needs a confident speech signal before it triggers. Reduces false-positives from background noise.

2. **Manual VAD.** You send `activity_start` and `activity_end` signals yourself based on your own client-side VAD (e.g. WebRTC VAD). More work, more control. Use when you need to gate on a wake word or push-to-talk.

> 🚀 **In Production**
>
> In noisy environments (factory floor, kitchen) automatic VAD over-triggers. Switch to push-to-talk + manual `activity_start`/`activity_end`. The UX is worth it.

## Latency budgeting — P50 vs P99

Track these per-session:

| Metric | What | P50 target | P99 target |
|--------|------|-----------|-----------|
| Time to first audio (TTFA) | mic stop → first model audio byte | < 800 ms | < 1500 ms |
| Time to first text token (TTFT) | user msg sent → first text event | < 400 ms | < 1200 ms |
| Round-trip turn | mic stop → end-of-model-turn | depends on length | n/a |

**P99 matters more than P50 for voice UX.** A 5% chance of a 3-second pause feels broken to every user. A 50% chance of 600 ms feels fine.

Where the latency comes from:
- Network (~30-100 ms) → unfixable, pick a closer region.
- Server-side VAD silence-detection (~200-500 ms) → tune `silence_duration_ms` lower if responsiveness > false-positives.
- Model inference (~300-800 ms first token) → pick the smaller model if you can.

## Reconnection on transient gRPC errors

Live sessions die. WiFi blip, server restart, transient `UNAVAILABLE`. The fix is **session resumption** — the server hands you a resume token, you reconnect and present it, you continue where you left off.

```python
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    session_resumption=types.SessionResumptionConfig(transparent=True),
    # ...
)
```

`transparent=True` makes the SDK retry+resume automatically on retryable errors. `transparent=False` surfaces the disconnection to your code and you decide. For most apps, `transparent=True` is right.

Even with resumption, *some* audio in flight is lost. Your client should keep a small ring buffer of the last ~3 seconds of model audio and replay it on resume — the model knows what it said but the user might have missed it.

> ⚠️ **Gotcha:** Live sessions have a **hard cap** on duration (typically 10-15 minutes for half-cascade, longer for some configurations). Plan to either summarize-and-reset at ~80% of the cap, or to gracefully tear down and start a fresh session with prior context loaded from your session store.

> ❓ **Ask the student:** "If your client doesn't honor `interrupted`, what's the user's experience?" (The model finishes its previous sentence over the top of the user's new question. Feels like a phone call with a 2-second delay — terrible.)

[← Prev: 18_StreamingLive/06_VideoInput]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/08_DissectingLiveSample →]
