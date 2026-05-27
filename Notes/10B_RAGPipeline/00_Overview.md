---
module: 10B_RAGPipeline
page: 00_Overview
title: RAG Pipeline — Overview
estimated_minutes: 20
prereqs: [10A_EmbeddingsVectorSearch/09]
concepts: [RAG, ingest, chunk, retrieve, augment, generate, VertexAiRagRetrieval]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/09_MiniDrill] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/01_RAGConcepts →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 00 Overview

---

## 🧠 What you'll build

A working **Retrieval-Augmented Generation** pipeline, two ways:

1. **Hand-rolled** — `pypdf` → chunks → `text-embedding-005` → Vertex AI Vector Search → top-k → Gemini. You see every wire.
2. **Managed (Vertex AI RAG Engine)** — `RagCorpus`, `rag.upload_file`, `rag.retrieval_query`. Two API calls. You ship.

Then wire both into an ADK agent.

## 📦 Time

~4 days (concept pages + drill ingesting your own notes).

## 🧭 Prereqs

- 10A (embeddings + Vector Search) — non-negotiable.
- 03 (FunctionTool) — you'll wrap retrieval as a tool.
- 04 (State) — chunks pass through `tool_context.state`.
- Same GCP setup as 10A: project, ADC, region, APIs enabled, quotas requested.

## 🔎 Sample anchors

- **Primary**: `/home/carloscabral/study/adk-samples/python/agents/RAG/` — the canonical RAG sample (uses `VertexAiRagRetrieval`).
- **Secondary**: `/home/carloscabral/study/adk-samples/python/agents/academic-research/` — multi-step retrieval-style agent.
- **For reference (skim only)**: `/home/carloscabral/study/adk-samples/python/agents/multiformat-hybrid-rag/` — a heavier production-flavored example with a separate ingest pipeline.

## 🗺 Page order

| # | Page | What |
|---|---|---|
| 01 | `RAGConcepts` | The 7-stage loop. 🧠 |
| 02 | `Chunking` | Fixed / sentence / semantic; overlap. 🧠 |
| 03 | `HandRolledRAG` | Glue everything from 10A. 🛠 |
| 04 | `VertexAIRAGEngine` | The managed shortcut. ☁️ |
| 05 | `RAGIntoADK` | FunctionTool vs `VertexAiRagMemoryService`. 🛠 |
| 06 | `DissectingRAGSample` | Full read of the RAG sample. 🔎 |
| 07 | `InProduction` | Re-embed, freshness, evals, lost-in-middle. 🚀 |
| 08 | `KnowledgeCheck` | 6 questions. ❓ |
| 09 | `MiniDrill` | RAG over your own notes folder. 🛠 |

## 🤖 Tutor

> Open `00_Overview` aloud, confirm 10A is complete (drill done, side-by-side worked), then 01.
> If the student is itching to ship: hint at page 04 — the managed path is short — but **do not** skip 03. They need to feel the wires once.

---

[← Prev: 10A_EmbeddingsVectorSearch/09_MiniDrill] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/01_RAGConcepts →]
