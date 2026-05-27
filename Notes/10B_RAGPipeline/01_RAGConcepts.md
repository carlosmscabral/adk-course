---
module: 10B_RAGPipeline
page: 01_RAGConcepts
title: The RAG loop in 7 stages
estimated_minutes: 20
prereqs: [10B_RAGPipeline/00]
concepts: [ingest, chunk, embed, store, retrieve, augment, generate]
icon: 🧠
in_production: false
detours_suggested: [Detours/Grounding]
---

[← Prev: 10B_RAGPipeline/00_Overview] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/02_Chunking →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 01 RAG concepts

---

## 🧠 Why RAG exists

Three problems with vanilla LLMs:

1. **No fresh knowledge** — training cutoff. (Today's date is Wed May 27 2026; the model doesn't know what happened last week.)
2. **No private knowledge** — your internal docs were never in training data.
3. **No citations** — the model can't tell you where it got "facts" from.

RAG fixes all three by **retrieving relevant chunks at query time and stuffing them into the prompt**. No fine-tuning. The LLM stays generic; the data layer carries the domain knowledge.

## 🗺 The 7-stage loop

```
_figures/rag_pipeline.txt
```

```
  ingest → chunk → embed → store        (offline, once-per-doc)
                                ↓
  retrieve → augment → generate          (online, per-query)
```

| Stage | What | Where |
|---|---|---|
| 1. **Ingest** | Load raw docs (PDF, MD, HTML, ...) | Page 03 (hand-rolled) |
| 2. **Chunk** | Split into 200-2000 token pieces | Page 02 |
| 3. **Embed** | Each chunk → vector | 10A/02 |
| 4. **Store** | Vectors + IDs in a vector DB | 10A/04 |
| 5. **Retrieve** | Query → top-k chunks | 10A/05 |
| 6. **Augment** | Stuff chunks into the prompt | Page 03 |
| 7. **Generate** | LLM produces an answer with cites | Page 03 |

Stages 1-4 are **offline ingest**. Stages 5-7 are **online query**. Most failures happen at the boundary — chunks drifted, model changed, query embedded with wrong task type.

## ⚖️ When NOT to use RAG

- The knowledge fits in the prompt (< ~50k tokens). Just stuff it. Use context caching (covered in 17).
- The knowledge is stable + critical → fine-tune.
- You need reasoning over the *whole* corpus (not retrieve top-k) → graph traversal, not RAG.

But for "answer questions over a large corpus you control" — RAG is the default.

> 🧭 If you're choosing between Search Grounding, Enterprise Search, and Agentic RAG, take Detour [[Detours/Grounding]] — back in ~15 min.

## 🚀 What RAG buys you (vs fine-tune)

| | RAG | Fine-tune |
|---|---|---|
| Freshness | Just re-ingest | Re-train |
| Citations | Free (you have the chunks) | Hard |
| Per-tenant data | Easy (one corpus per tenant) | Hard |
| Cost | Embed once + query-time retrieval | $$$$ + GPU time |
| Latency | +20-100ms retrieval | None |

## ❓ Check

> ❓ **Ask the student:** "Why do we need stage 2 (chunking)? Why not embed whole documents?"
>
> Expected: (1) embedding models have token limits (e.g. ~3k for text-embedding-005); (2) a whole-doc vector loses precision — averaging over many topics — so retrieval gets fuzzy; (3) the LLM at query time has finite context, so we want to inject precise relevant pieces, not entire docs.

## 🛠 Have the student trace

> 🛠 For the question "What's the capital of France?", trace which stage(s) of the loop run **per query** (5,6,7) vs **once** (1,2,3,4). Reinforce the offline-vs-online split.

## 🤖 Tutor

> The loop diagram is the spine of this module. Make sure the student can draw it from memory before moving on. Tape it above their desk if needed. Every subsequent page slots into one of these 7 boxes.

---

[← Prev: 10B_RAGPipeline/00_Overview] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/02_Chunking →]
