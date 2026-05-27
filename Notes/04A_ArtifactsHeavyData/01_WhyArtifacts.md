---
module: 04A_ArtifactsHeavyData
page: 01_WhyArtifacts
title: Why artifacts — when state is the wrong store
estimated_minutes: 15
prereqs: [04A_ArtifactsHeavyData/00, 04_SessionsState/08]
concepts: [state-vs-artifact, binary, large-blob, cross-agent-handoff]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/02_ArtifactServiceShape →](02_ArtifactServiceShape.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 01 Why artifacts

# 🧠 Why artifacts

State is a dict. ADK serialises it on every event. Stuffing a 4 MB image into `state["screenshot"]` works **once**, then your event log has a 4 MB row in it forever, your `DatabaseSessionService` queries get slow, and your `VertexAiSessionService` quotas start screaming. Artifacts are the second store: bytes live in a blob backend (memory, local disk, GCS); the session only holds a tiny `(filename, version)` reference on the event.

## 🧠 The decision tree

```
                Is the value...
                      │
        ┌─────────────┴──────────────┐
        ▼                            ▼
   small + structured           large or binary
   (≤ ~1 KB, JSON-friendly)     (PDF, image, audio, video,
        │                        big CSV, multi-MB text)
        ▼                            │
     STATE                           ▼
     state["key"] = value         ARTIFACT
                                  tool_context.save_artifact(
                                      "name.ext", types.Part(...)
                                  )
```

Three examples:

```python
# 1. Small + structured → state
tool_context.state["last_query"] = "whales"
tool_context.state["user:name"]  = "Carlos"
tool_context.state["app:rate"]   = 100
```

```python
# 2. Generated image → artifact
img_part = types.Part(inline_data=types.Blob(data=png_bytes, mime_type="image/png"))
version = await tool_context.save_artifact("chart_q1.png", img_part)
tool_context.state["latest_chart"] = "chart_q1.png"   # ← state stores the HANDLE
```

```python
# 3. User-uploaded PDF the next sub-agent will summarise → artifact
pdf_part = types.Part(inline_data=types.Blob(data=pdf_bytes, mime_type="application/pdf"))
await tool_context.save_artifact("uploaded_report.pdf", pdf_part)
# A downstream agent reads it by name:
part = await tool_context.load_artifact("uploaded_report.pdf")
```

## 🧠 The rule

If the value would make a JSON dump painful to read, or if it is bytes — it is an artifact, not state. **State holds names and small facts; artifacts hold the heavy thing those names point at.** This is the same split as a database row holding a `s3://...` URL instead of the file itself.

## ⚠️ The four canonical reasons to reach for an artifact

1. **Binary data** — PDFs, PNGs, MP3s, MP4s. Non-string bytes never go in state.
2. **Large data** — anything past a few KB. State writes show up on every event; large state means heavy events means slow Runner.
3. **Multimodal context for the LLM** — Gemini accepts image / audio / video / PDF Parts. Those Parts live as artifacts; you reference them on the next prompt.
4. **Cross-agent handoff of bytes** — sub-agent A produces a file, sub-agent B consumes it. The clean handoff is a filename in state pointing at an artifact, not the bytes themselves.

## ❓ Self-check

> ❓ **Ask the student:** for each value below, pick state or artifact:
> 1. The user's preferred timezone string.
> 2. A 3 MB JPEG the user just uploaded.
> 3. The filename of the chart the last sub-agent saved.
> 4. The transcript of a 45-minute meeting recording, stored as a 200 KB text blob.
> 5. The raw bytes of that meeting recording (MP3, 12 MB).
>
> *(Expected: 1 state — `user:`. 2 artifact. 3 state — a tiny string. 4 borderline; 200 KB of text is heavy enough to be artifact — file_data is cleaner. 5 artifact, no question.)*

> 🛠 **Have the student do this:** open their Module 04 mini-drill `Work/remember_name.py`. Ask: which writes would migrate to artifacts? *(Answer: none — every value is a short string. Good. This module is about everything that does **not** fit that pattern.)*

> **🚀 In Production**
>
> The "I'll just put it in state, just for now" anti-pattern is how production agents end up with multi-megabyte session rows that take 8 seconds to load. Catch it in code review: any tool that writes `state[key] = <something that isn't a short string / number / small dict>` deserves a hard look. The standard mitigation is to introduce an artifact wrapper *before* the value grows.

---

[← Prev: 04A_ArtifactsHeavyData/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/02_ArtifactServiceShape →](02_ArtifactServiceShape.md)
