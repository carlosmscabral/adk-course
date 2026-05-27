---
module: Detours
page: AudioEncoding
title: Audio encoding — PCM, μ-law, Opus, MP3 and why Live picks PCM
estimated_minutes: 20
prereqs: []
concepts: [PCM, sample-rate, mono-stereo, mu-law, Opus, MP3, raw-bytes]
icon: 🔊
---

[← Triggered from: 18_StreamingLive/04_AudioIO]  [↑ Map](../MAP.md)

You are here: 🗺 Detours ▸ Audio Encoding

> 🧭 **This is optional.** Take it if "PCM 16 kHz mono int16" feels like magic words. 20 min. Comes back to module 18.

## PCM — the simplest digital audio

**Pulse-Code Modulation.** A stream of numeric samples of air pressure, taken N times per second. To play audio you need to know three things:

1. **Sample rate** (Hz): how often you sample. 16,000 = 16 kHz.
2. **Bit depth**: bits per sample. 16 = each sample is a `int16` in -32768..32767.
3. **Channels**: 1 = mono, 2 = stereo (left, right interleaved sample by sample).

That's literally it. No header, no metadata. Just samples.

```python
>>> import numpy as np
>>> # 1 second of 440 Hz sine wave, 16 kHz mono, int16
>>> rate = 16000
>>> t = np.arange(rate) / rate
>>> wave = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
>>> raw = wave.tobytes()
>>> len(raw)   # 16000 samples × 2 bytes
32000
```

That `raw` bytes object IS the wire format Gemini Live wants. No `.wav` header, no nothing — just `wave.tobytes()`.

## Sample rates you'll meet

| Hz | Use | Why |
|----|-----|-----|
| 8000 | Telephony (μ-law) | Voice band only, 1960s legacy |
| 16000 | **Speech ML, Live API input** | Captures all voice formants; small |
| 22050 | Older TTS | Half of CD rate; obsolete |
| 24000 | **Gemini Live API output** | Slightly more headroom for prosody |
| 44100 | CD audio, music | Captures up to 22 kHz (human limit) |
| 48000 | Video, pro audio | Aligns better with video frame rates |

Use the rate the model wants. Downsampling is OK; upsampling adds no information.

## Bit depth, briefly

`int16` (16-bit) is the standard for raw PCM. Dynamic range: 96 dB — more than enough for voice. `int24` and `float32` exist for studio work; ignore them for ML/voice.

`int8` (8-bit) sounds harsh and hissy — not used for modern voice. See [[AudioQuantization]] for the deep dive.

## Mono vs stereo

Stereo doubles the data and adds no information for a single speaker into a single mic. **Always mono** for speech ML unless you have a specific reason (beamforming, source separation, music).

## μ-law (telephony)

**μ-law** is 8-bit non-linear PCM at 8 kHz, used by classic phone systems. It compresses quiet sounds more than loud ones — a perceptual win over linear 8-bit. Still bad for ML compared to 16 kHz linear PCM.

Live doesn't take μ-law. If your input is from a phone gateway (Twilio etc.), you'll decode μ-law to 16-bit and resample to 16 kHz before sending.

## Opus / MP3 (lossy, for storage and broadcast)

- **Opus**: state of the art for voice and music; ~16-32 kbps for voice. Used by Discord, WebRTC, every modern voice app.
- **MP3**: ancient, lossy, music-oriented. ~64-128 kbps. Encoder priming silence at the start of the stream (~1152 samples) plus a bit-reservoir scheme that makes byte-aligned chunking lossy — both bad for low-latency streaming.

Both involve encode/decode steps. **Live wants raw PCM specifically because the server doesn't have to decode** — every millisecond of decode is a millisecond of latency in a voice-driven UX.

## Why Live wants raw PCM (the actual reason)

1. **Zero decode latency.** The server can pipe bytes straight to the model frontend.
2. **No frame-boundary games.** PCM has no concept of a frame; you can send 200 ms or 47 ms, the server doesn't care.
3. **Lossless.** No artifacts that might confuse the ASR.
4. **Implementations are trivial.** Every audio library can produce int16 PCM.

The cost is bandwidth — 16 kHz × 16-bit mono = **256 kbps**. Compare with Opus voice at ~24 kbps (~10× smaller). But 256 kbps fits in any home connection, and you're saving 30-100 ms of round-trip per chunk by not encoding/decoding.

## Show me the bytes

```python
>>> wave[:5]
array([    0,  9802, 17889, 22989, 24028], dtype=int16)
>>> raw[:10]
b'\x00\x00J&\xe1E\xcdY\xdc^'
```

Each pair of bytes is one int16, little-endian. `\x00\x00` = 0, `J&` = 0x264a = 9802, etc.

## 🧪 Mini-exercise

```python
# rec.py — record 3s of audio and write a .wav, inspect with hexdump
import sounddevice as sd, numpy as np, wave

rate = 16000
data = sd.rec(3 * rate, samplerate=rate, channels=1, dtype="int16")
sd.wait()

with wave.open("rec.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
    f.writeframes(data.tobytes())
```

Then:
```bash
$ hexdump -C rec.wav | head -3
00000000  52 49 46 46 24 78 00 00  57 41 56 45 66 6d 74 20  |RIFF$x...WAVE fmt |
00000010  10 00 00 00 01 00 01 00  80 3e 00 00 00 7d 00 00  |.........>...}..|
00000020  02 00 10 00 64 61 74 61  00 78 00 00 ...
```

`RIFF` + `WAVE` is the .wav header. After offset 0x2c, you're looking at raw int16 PCM — the bytes you'd send to Live. Try `hexdump -s 44 -C rec.wav | head` to see just the PCM.

## Back to module 18

- The `sounddevice` callback in `04_AudioIO` produces `float32` in [-1, 1] and we multiplied by 32767 to make it `int16`. Now you know why both steps are necessary: `float32` is the API's natural shape; `int16` PCM is what Live wants on the wire.
- The output side reads model-emitted `audio/pcm` blobs and writes them straight to an `OutputStream(dtype="int16")`. No decode. That's the point.

[← Back: 18_StreamingLive/04_AudioIO](../18_StreamingLive/04_AudioIO.md)  [↑ Map](../MAP.md)
