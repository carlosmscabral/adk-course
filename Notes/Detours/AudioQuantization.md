---
module: Detours
page: AudioQuantization
title: Audio quantization — bit depth, sample rate, and what breaks ASR
estimated_minutes: 20
prereqs: []
concepts: [bit-depth, dynamic-range, quantization-noise, Nyquist, formants, ASR-degradation]
icon: 🔉
---

[← Triggered from: 18_StreamingLive/04_AudioIO]  [↑ Map](../MAP.md)

You are here: 🗺 Detours ▸ Audio Quantization

> 🧭 **This is optional.** Take it if "why not 8 kHz, why not 8-bit, why not MP3?" feels unanswered. 20 min. Comes back to module 18.

## Bit depth ≈ dynamic range

Each sample is `N` bits, so it can represent `2^N` distinct amplitude levels. The ratio between the loudest and quietest representable sound is the **dynamic range**, ~6 dB per bit.

| Bits | Levels | Dynamic range | Sound |
|------|--------|---------------|-------|
| 8 | 256 | ~48 dB | Hissy, audible quantization noise (like a cheap intercom) |
| 16 | 65,536 | ~96 dB | Indistinguishable from analog for voice and music |
| 24 | 16,777,216 | ~144 dB | Studio recording headroom; overkill for playback |
| 32f | float | ~1500 dB equivalent | DSP intermediate; never on the wire |

**16-bit is the sweet spot.** 8-bit is acceptable only for low-fi voice (μ-law improves it perceptually but it's still bad for ML).

### Why 8-bit sounds bad

With only 256 levels, the gap between adjacent samples is large. Quiet passages (where samples cluster near zero) round to one of a handful of nearby integers, producing audible "quantization noise" — a constant low-level hiss. ASR models trained on 16-bit data see 8-bit input as if it had a permanent noise floor.

## Sample rate ≈ frequency ceiling

**Nyquist's theorem:** sampling at `R` Hz can represent frequencies up to `R/2` Hz. Anything above that **aliases** — folds back as a lower frequency and corrupts the signal. To prevent aliasing, audio is low-pass filtered before sampling.

| Sample rate | Max frequency | What it captures |
|-------------|---------------|------------------|
| 8 kHz | 4 kHz | Telephone band; loses upper formants of /s/, /f/, /ʃ/ |
| 16 kHz | 8 kHz | All voice formants; standard for ML speech |
| 24 kHz | 12 kHz | All voice + some upper harmonics for nicer TTS |
| 44.1 kHz | ~22 kHz | Full human hearing range; CD quality |

### Why 8 kHz sounds bad for TTS

Human speech has **formants** (vocal tract resonances) up to ~7 kHz, and fricatives like /s/ and /f/ have most of their energy in the 4-8 kHz band. An 8 kHz sample rate cuts at 4 kHz — so you lose the "sharpness" of consonants. TTS at 8 kHz sounds dull and muffled, like an old phone call. The model can still synthesize words, but listeners report it as "robotic" or "low quality."

### Why 16 kHz is the floor for ASR

Modern ASR models (including the one fronting Gemini Live) are trained on 16 kHz speech corpora. Feeding them 8 kHz audio works but accuracy drops several percentage points, especially on fricative-heavy languages (English, German). Upsampling 8 kHz → 16 kHz with `scipy.signal.resample_poly` doesn't recover the lost frequencies — it just adds zeros above 4 kHz.

## Lossy compression and what it breaks

| Codec | Bitrate | What it ruins |
|-------|---------|---------------|
| Opus voice 16 kbps | tiny | Subtle prosody; otherwise nearly transparent for voice |
| Opus voice 32 kbps | very small | Nothing noticeable |
| MP3 64 kbps | small | Mid-frequency artifacts; pre-roll silence |
| MP3 128 kbps | medium | Almost transparent for voice |
| μ-law 8 kHz | small | Bandwidth-limited (no upper formants), 8-bit-equivalent dynamic range |

**ASR-relevant:** Opus is generally safe down to 16 kbps. MP3 sometimes adds artifacts in the 1-3 kHz band that confuse models trained on PCM. **If you have a choice, send PCM.**

### "Codec mismatch" — the silent ASR killer

If your audio pipeline encodes voice as MP3 32 kbps for storage then decodes it back to PCM for the model, you've introduced lossy artifacts the model never saw at training. Symptom: ASR accuracy degrades a few percent for no obvious reason. Fix: keep PCM through the whole inference pipeline.

## Trade-off matrix

| Use case | Rate | Bits | Codec |
|----------|------|------|-------|
| Live API to Gemini | 16 kHz | 16 | PCM |
| Live API from Gemini | 24 kHz | 16 | PCM |
| Voicemail storage | 8-16 kHz | 16 | Opus |
| Podcast distribution | 44.1 kHz | 16 | Opus 64 / AAC 96 |
| Telephony (legacy) | 8 kHz | 8 | μ-law |
| Studio source | 48 kHz | 24 | uncompressed WAV |

## 🧪 Mini-exercise

Take a 16 kHz / 16-bit clip and degrade it three ways. Listen to each.

```python
import sounddevice as sd, numpy as np
from scipy.signal import resample_poly

# record 3s of you saying "she sells seashells by the seashore"
clip = sd.rec(3 * 16000, samplerate=16000, channels=1, dtype="int16")
sd.wait()
clip = clip[:, 0]

# (a) drop to 8-bit, then back to 16-bit
clip_8bit = ((clip >> 8).astype(np.int8).astype(np.int16) << 8)

# (b) downsample 16 kHz -> 8 kHz, then back to 16 kHz
clip_8k = resample_poly(clip, up=1, down=2).astype(np.int16)
clip_8k_back = resample_poly(clip_8k, up=2, down=1).astype(np.int16)

# (c) both
clip_both = ((clip_8k_back >> 8).astype(np.int8).astype(np.int16) << 8)

for name, arr, rate in [
    ("original", clip, 16000),
    ("8-bit",    clip_8bit, 16000),
    ("8 kHz",    clip_8k_back, 16000),
    ("both",     clip_both, 16000),
]:
    print(name); sd.play(arr, rate); sd.wait()
```

What you should hear:
- **Original**: clean.
- **8-bit**: constant hiss in quiet moments.
- **8 kHz**: muffled; the /s/ and /sh/ sounds lose their fizz.
- **Both**: telephone-from-1995.

Now imagine asking Live to transcribe these. The original works; the rest get progressively worse.

## Back to module 18

- The PCM 16 kHz / 16-bit input the API asks for is the **lowest config you can use without losing accuracy.** Don't try to "save bandwidth" with 8 kHz or 8-bit. The 256 kbps you'd save is nothing; the accuracy you'd lose matters.
- Output at 24 kHz from native-audio models exists because TTS sounds noticeably better with 12 kHz of frequency headroom vs 8 kHz of 16 kHz output.

[← Back: 18_StreamingLive/04_AudioIO](../18_StreamingLive/04_AudioIO.md)  [↑ Map](../MAP.md)
