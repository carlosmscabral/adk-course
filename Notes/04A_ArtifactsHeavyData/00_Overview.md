---
module: 04A_ArtifactsHeavyData
page: 00_Overview
title: Artifacts & Heavy Data — getting bytes out of state
estimated_minutes: 10
prereqs: [04_SessionsState/08]
concepts: [ArtifactService, GcsArtifactService, multimodal, signed-urls]
icon: 🗺
in_production: false
detours_suggested: []
---

[← Prev: 04_SessionsState/10_MiniDrill](../04_SessionsState/14_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/01_WhyArtifacts →](01_WhyArtifacts.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 00 Overview

# 🗺 Module 04A — Artifacts & Heavy Data ☁️

In Module 04 we shoved everything into state. State is a dict — meant for kilobytes. The moment you need to hand around a PDF, a generated image, a podcast WAV, or a 12 MB CSV, state breaks: events bloat, sessions slow down, persistence backends cough. **Artifacts are the second store.** State for facts; artifacts for bytes.

## 🎯 Goals

By the end of this module you can:
- Decide between `state[...]` and `tool_context.save_artifact(...)` for any value.
- Wire `InMemoryArtifactService` for dev and `GcsArtifactService` for prod.
- Save and load binary artifacts from a tool, with explicit versioning.
- Choose between `inline_data` (bytes in the Part) and `file_data` (URI reference) on multimodal Parts.
- Hand a heavy file from one sub-agent to another by filename, not by bytes.
- Read `artifact_delta` off the event stream and reason about what the Runner persists.

## 📋 Prereqs

- Module 04 complete — you know what state is and why secrets do not belong in it.
- Module 03 complete — you can write a `FunctionTool` that takes `ToolContext`.
- A Google Cloud project with one GCS bucket you can write to, if you want to run the ☁️ pages live. Pages 03, 06, 07 are marked ☁️ and assume GCS access; the rest run on `InMemoryArtifactService`.

## ⏱ Estimated time

- **Total**: ~3 hours over 2 sessions
- The dissection page (`10_DissectingSample`) is the longest; budget 40 min for it.

## 🧪 Sample anchor

This module dissects [`brand-aligned-presentations`](../../../adk-samples/python/agents/brand-aligned-presentations/) — a multi-agent presentation builder that ingests user-uploaded text/images, hands GCS-backed `.pptx` files between sub-agents, and ships a real `GcsArtifactService` with a graceful `InMemoryArtifactService` fallback. It is the cleanest end-to-end artifact pattern in the samples repo.

> 🤖 **Tutor:** before the dissection page, confirm the student can `ls /home/carloscabral/study/adk-samples/python/agents/brand-aligned-presentations/`. The artifact-utils file is the core of that read-through.

## 🛣 Plan

1. **01 Why artifacts** — the state-vs-artifact decision tree.
2. **02 ArtifactService shape** — `BaseArtifactService`, `InMemoryArtifactService`, wiring into `App` / `Runner`.
3. **03 GcsArtifactService ☁️** — bucket setup, IAM, lifecycle policies.
4. **04 Save & load from tools** — `tool_context.save_artifact` / `load_artifact`, versioning, filenames.
5. **05 Multimodal Parts** — `inline_data` vs `file_data`, when to inline and when to reference.
6. **06 Video understanding ☁️** — Gemini video Parts, frame-rate tradeoffs, max length.
7. **07 Signed URLs & handoff ☁️** — pass URLs between sub-agents instead of bytes.
8. **08 `artifact_delta` in events** — how the Runner persists, how observability reads it.
9. **09 Heavy file between sub-agents** — uploader → reader by filename pattern.
10. **10 Dissecting `brand-aligned-presentations`** — trace one upload-and-edit turn.
11. **11 In Production** — GCS lifecycle, signed-URL TTL, PII in artifacts, cost.
12. **12 Knowledge Check** — 6 questions, tutor asks one at a time.
13. **13 Mini-Drill** — build a PDF-summariser agent with a real artifact roundtrip.

After this module: → **[04B Human-in-the-Loop](../4B_HumanInTheLoop/00_Overview.md)**, then Milestone **[M1 Conversation Server](../../Drills/M1_ConversationServer.md)**.

> 🤖 **Tutor:** the most common confusion in this module is "is this a state thing or an artifact thing?" Resolve it on page 01 and refer back relentlessly. Also: `GcsArtifactService` requires real GCP creds. If the student has none, skip 03/06/07 live runs but still walk the code; the patterns transfer to `FileArtifactService` (local disk) without rewriting application code.

---

[← Prev: 04_SessionsState/10_MiniDrill](../04_SessionsState/14_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/01_WhyArtifacts →](01_WhyArtifacts.md)
