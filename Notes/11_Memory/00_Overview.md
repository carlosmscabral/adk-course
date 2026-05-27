---
module: 11_Memory
page: 00_Overview
title: Memory — beyond one session
estimated_minutes: 10
prereqs: [04_SessionsState/02, 10A_EmbeddingsVectorSearch/00, 10B_RAGPipeline/00]
concepts: [memory-service, cross-session, load_memory, Memory Bank, Rag-backed memory]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/last]  [↑ Map](../../MAP.md)  [Next: 11_Memory/01_SessionVsStateVsMemory →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 00 Overview

# 🧠 Module 11 — Memory

## What you'll learn

- Where memory sits relative to session and state (three lifetimes).
- The three `MemoryService` implementations and when each is the right call.
- How the built-in `load_memory` and `PreloadMemoryTool` tools surface memory to the LLM.
- How to wire `add_session_to_memory()` into an `after_agent_callback`.
- The two production failure modes nobody warns you about: memory bloat and PII leak.

## Prereqs

- **04 SessionsState** — you must understand `session.state`, the four prefixes, and state delta events. Memory is the *next* lifetime up.
- **10A Embeddings & Vector Search** — `VertexAiRagMemoryService` is backed by a Vector Search index. We won't re-explain embeddings here.
- **10B RAG Pipeline** — same; if RAG-backed memory feels unclear, take a half-day in 10B first.

## Time budget

≈ 2 days. Reading + the mini-drill once with `VertexAiMemoryBankService` and once with `VertexAiRagMemoryService`.

## Sample anchor

`/home/carloscabral/study/adk-samples/python/agents/memory-bank/` — a tiny weather/time agent wired to Vertex AI Memory Bank via `PreloadMemoryTool` and a `generate_memories_callback`. We dissect this in `06_DissectingMemoryBank.md`.

> **🚀 In Production**: `memory-bank` is **the** canonical Memory Bank example. Read `app/agent.py` for the `PreloadMemoryTool()` + `after_agent_callback → add_session_to_memory()` shape; the dissection lives at [[11_Memory/06_DissectingMemoryBank]]. Same sample is the App-wiring anchor in [[1A_AppAndRunner/08_DissectingSample]].

## Module map

| Page | Topic |
|------|-------|
| 01 | Session vs State vs Memory — the three lifetimes |
| 02 | `InMemoryMemoryService` (dev only) |
| 03 | `VertexAiMemoryBankService` (managed, auto-summarized) |
| 04 | `VertexAiRagMemoryService` (you bring the index) |
| 05 | The `load_memory` / `PreloadMemoryTool` built-ins |
| 06 | Dissecting `memory-bank` sample |
| 07 | In Production |
| 08 | Knowledge Check |
| 09 | Mini Drill |

> 🤖 **Tutor:** This module is short on lines, long on conceptual reorientation. The student often confuses "the session has state" with "the agent has memory". The single biggest payoff of this module is making the student fluent in switching between the three lifetimes. Lean on the figure in `_figures/memory_lifetimes.txt`.

---

[← Prev: 10C_BigQueryAgents/last]  [↑ Map](../../MAP.md)  [Next: 11_Memory/01_SessionVsStateVsMemory →]
