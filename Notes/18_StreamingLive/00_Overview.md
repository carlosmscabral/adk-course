---
module: 18_StreamingLive
page: 00_Overview
title: Streaming and Live — text tokens, bidi voice, the whole wire
estimated_minutes: 30
prereqs: [02_FirstAgent/04, 07_Callbacks/01]
concepts: [run_async, run_live, LiveRequestQueue, RunConfig, bidirectional-streaming, PCM, WebSocket, gRPC]
icon: 🎙
in_production: true
detours_suggested: [PY_async, PY_generators, WebSockets, AudioEncoding, AudioQuantization, gRPC, ProtocolBuffers]
---

[← Prev: 17_AdvancedModels/(last)]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/01_StreamingFundamentals →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 00 Overview

## 🎙 What this module is

The deepest hands-on module in the course. You will build, byte-by-byte:

1. **Text token streaming** with `runner.run_async()` — partial events, an async-for loop, an SSE wrapper.
2. **Bidirectional voice** with `runner.run_live()` — mic in, speaker out, barge-in, the `LiveRequestQueue`.
3. **The wire underneath** — what PCM actually looks like, why Live uses gRPC, when WebSockets are good enough.

5 days. About 8-10 hours active.

## Prereqs

- Module 02 (you can build and run an `LlmAgent`).
- Module 07 (callbacks — you understand the event loop ADK presents you).
- Comfortable with `async`/`await`. If not, `[[PY_async]]` first.
- Comfortable with async generators (`async for`, `yield`). If not, `[[PY_generators]]`.

## Hardware

- A **working microphone** for `12_MiniDrill_VoiceLive`. USB headset is best; built-in laptop mic is fine.
- Speakers / headphones for output.
- If no mic: skip drill 12 and do drill 13 (SSE web) instead. The tutor will check.

> 🤖 **Tutor:** before page 04 (AudioIO), run a sanity check: `python -c "import sounddevice as sd; print(sd.query_devices())"`. If it errors, install `sudo apt install libportaudio2` (Linux) and `uv add sounddevice`. If the student has no input device, branch the curriculum: do all text/SSE pages, skip 04/06/07/12, still do the dissection page 08.

## Sample anchors

- `/home/carloscabral/study/adk-samples/python/agents/bidi-demo/` — the canonical reference. FastAPI + WebSocket + ADK Live wiring.
- `/home/carloscabral/study/adk-samples/python/agents/realtime-conversational-agent/` — same pattern with a Next.js client, video input, transcription.

## The sub-pages

| # | Page | What |
|---|------|------|
| 01 | StreamingFundamentals | async iterators, partial vs final, backpressure |
| 02 | GeminiLiveIntro | What the Live API is. `RunConfig`, modalities |
| 03 | TextStreaming | Token-by-token printing. SSE wire format |
| 04 | AudioIO | Mic capture and playback with `sounddevice`. PCM rates |
| 05 | StreamingTools | `LongRunningFunctionTool` and tools that yield progress |
| 06 | VideoInput | Webcam/screen capture into Live |
| 07 | LiveProductionPatterns | Barge-in, VAD, latency budgets, reconnection |
| 08 | DissectingLiveSample | Read `bidi-demo/` end-to-end |
| 09 | InProduction | Token cost, partial-output safety, session limits |

Then the three trailing files:

- `10_KnowledgeCheck.yml` — 7 questions
- `11_MiniDrill_TextStream.yml` — CLI that prints tokens with timestamps
- `12_MiniDrill_VoiceLive.yml` — mic → agent → speaker, with barge-in
- `13_MiniDrill_SSEWeb.yml` — FastAPI SSE endpoint + tiny HTML client

## The arc

By the end you should be able to look at the `bidi-demo` `main.py` and *predict* what every line does before reading it. That's the goal.

[← Prev: 17_AdvancedModels/(last)]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/01_StreamingFundamentals →]
