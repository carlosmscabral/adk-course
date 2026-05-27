# AGENTS.md — Module 18 Streaming & Live (teaching notes for the AI tutor)

## What the student should walk away knowing

- `runner.run_async(...)` returns an **async iterator** of events; partials carry deltas, final carries `turn_complete`.
- Backpressure: awaiting inside the loop slows the producer. Fan slow work out to a queue.
- `runner.run_live(...)` + `LiveRequestQueue` + `RunConfig(streaming_mode=BIDI)` is the whole bidi voice/video story. Everything else is wiring.
- Audio shape: **input PCM 16k mono int16**, **output PCM 24k mono int16**. No container, no compression.
- Native-audio models only emit AUDIO. Half-cascade can do TEXT or AUDIO.
- Barge-in is detected via `event.interrupted`; client MUST drop queued playback.
- Live sessions have time caps; always enable `session_resumption(transparent=True)`.
- You cannot filter what you've already streamed. Front-load guardrails in `before_model_callback`.

## Pacing

- **5 days, ~8-10 hours active.** This is the deepest module.
- **Easy if:** student already writes asyncio servers and has touched WebSockets. They'll fly through 01-03.
- **Hard if:** student is shaky on `async`/`await` and async generators. Detour to `[[PY_async]]` then `[[PY_generators]]` BEFORE page 01, not during.
- **Especially hard if:** their dev box has no working mic. See "Pre-flight check" below.

## Pre-flight check (do before page 04)

Run together:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

- ✅ At least one device shows `(N in, M out)` with `N > 0`: continue.
- ❌ `OSError: PortAudio library not found`: install system lib.
  - Debian/Ubuntu: `sudo apt install libportaudio2`
  - macOS: `brew install portaudio`
  - then `uv add sounddevice numpy`
- ❌ No input devices visible at all: branch the curriculum.
  - Skip pages 04 (AudioIO), 06 (VideoInput where audio is required), 07 (LiveProductionPatterns audio sections), and drill 12.
  - Still do pages 01, 02, 03, 05, 08, 09 + drills 11, 13.
  - The student will lack hands-on voice experience but will understand the architecture.

## Watch for these mistakes

- **Awaiting slow I/O inside the run_async loop.** Will silently double or triple TTFT. Have them measure with timestamps.
- **Collecting `runner.run_async(...)` into a list with `list(...)`.** TypeError — it's async. The whole point is iteration.
- **Forgetting `\n\n` in SSE.** Tokens "appear all at once at the end." See drill 13 tutor notes.
- **Sending float32 to Live instead of int16.** Symptom: model says "I'm having trouble hearing you" or worse, garbled audio in. The `(x * 32767).astype(np.int16)` step is non-negotiable.
- **Ignoring `event.interrupted`.** Symptom: model keeps talking over the user. Re-check page 07.
- **Reading `event.content.parts[0].text` without guarding `event.content is None`.** `turn_complete`-only events have no content. AttributeError.
- **Hardcoding `gemini-2.0-flash` for Live.** Live API requires Live-compatible model IDs (see the bidi-demo README for the current list).
- **Running `main.py` from the wrong directory.** The bidi-demo specifically needs `cd app/` first — `ModuleNotFoundError: google_search_agent`. Note in the dissection page.

## When to suggest a detour

- Student asks "why `async for`?" → suggest `[[PY_async]]` then `[[PY_generators]]`.
- Student asks "WebSockets vs SSE?" → suggest `[[WebSockets]]`.
- Student asks "why raw PCM and not MP3?" → suggest `[[AudioEncoding]]`.
- Student asks "is 16 kHz really enough for voice?" → suggest `[[AudioQuantization]]`.
- Student asks "what's gRPC actually doing?" → suggest `[[gRPC]]`.
- Student asks "what's protobuf?" → suggest `[[ProtocolBuffers]]`.
- Student asks "how do I deploy this?" → defer to Module 16 (ProductionSecurity) and the bidi-demo README's Cloud Run / Agent Engine sections.

## Three mini-drills

Module 18 is the **only** module in the course with multiple mini-drill files (`11_MiniDrill_TextStream.yml`, `12_MiniDrill_VoiceLive.yml`, `13_MiniDrill_SSEWeb.yml`). The three slices — token-stream, bidi voice/Live, browser SSE — are independent enough in surface area (asyncio iterator vs. `LiveRequestQueue` + PCM vs. HTTP framing) that one combined drill would either be a 90-minute marathon or skip two of the three. The tutor should offer them sequentially in numeric order, but the student can skip any one (e.g. drill 12 if the pre-flight mic check failed) without breaking the others.

## Mini-drill grading

- **Drill 11 (TextStream)**: pass = three distinct chunk timestamps + one FINAL. If they only see one chunk, ask for a longer reply (5 paragraphs) — the chunk count depends on response length.
- **Drill 12 (VoiceLive)**: pass = audible roundtrip + barge-in cuts within ~250 ms. If barge-in lags > 1 s, check that they're clearing the play queue (not just stopping new appends) AND skipping audio events until the next user turn.
- **Drill 13 (SSEWeb)**: pass = browser shows progressive text + DevTools EventStream tab populated. If "all at once," check the `\n\n` and `media_type`.

## Sample anchors used

- `/home/carloscabral/study/adk-samples/python/agents/bidi-demo/app/main.py` (lines referenced explicitly in page 08)
- `/home/carloscabral/study/adk-samples/python/agents/realtime-conversational-agent/server/main.py` (lines 41-63 for RunConfig, 82-93 for interrupt handling)
- `/home/carloscabral/study/adk-samples/python/agents/bidi-demo/agent_engine/test.py` (Agent Engine bidi client pattern)
