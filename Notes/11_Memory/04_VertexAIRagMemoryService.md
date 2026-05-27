---
module: 11_Memory
page: 04_VertexAIRagMemoryService
title: VertexAiRagMemoryService — bring your own index
estimated_minutes: 25
prereqs: [11_Memory/03, 10A_EmbeddingsVectorSearch/00, 10B_RAGPipeline/00]
concepts: [VertexAiRagMemoryService, RAG corpus, Vector Search, chunking control]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/03_VertexAIMemoryBank]  [↑ Map](../../MAP.md)  [Next: 11_Memory/05_LoadMemoryTool →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 04 VertexAI RAG Memory

# ☁️ RAG-backed memory: when you want the controls

`VertexAiRagMemoryService` is the other managed option. Instead of letting Memory Bank summarize, you point it at a **Vector Search index** you already built (see `10A_EmbeddingsVectorSearch` and `10B_RAGPipeline`) and the service stores past conversation chunks as documents in that corpus.

```python
from google.adk.memory import VertexAiRagMemoryService
from google.adk.runners import Runner

memory_service = VertexAiRagMemoryService(
    rag_corpus="projects/.../locations/.../ragCorpora/12345",
    similarity_top_k=10,
    vector_distance_threshold=0.5,  # tighter than the framework default (10) per vertex_ai_rag_memory_service.py:99
)

runner = Runner(
    app_name="prod-app",
    agent=agent,
    memory_service=memory_service,
)
```

## When to prefer this over Memory Bank

Pick `VertexAiRagMemoryService` when:

- You already have a RAG corpus from 10B and you want chat history retrievable next to your docs (one substrate, one retriever).
- You need control over chunking, embeddings model, and top-k retrieval.
- You want **deterministic** "remember this exact text" semantics — not Memory Bank's distillation.
- You want to debug retrieval with Vector Search's existing tooling.

Pick `VertexAiMemoryBankService` when:

- You want a turnkey "personalization" memory and don't want to operate an index.
- You want the framework to decide what's worth remembering.

## What you give up

You give up automatic summarization. Past turns get indexed roughly verbatim (modulo whatever chunking your pipeline applies). That's good for recall, bad for token cost over time — you pay LLM context for past chat fragments instead of distilled facts.

## Cross-link with 10A/10B

> 🧭 If the student is fuzzy on "what's an index, what's a corpus, what gets embedded": pause here and walk through `10B_RAGPipeline/02_RagCorpusVsIndex.md` (or whichever page covers the corpus → index relationship in 10B). Don't re-explain it inline.

> ❓ **Ask the student:** "You want both: factual recall of past chats AND a hand-curated PDF corpus. One service, or two?" *(Expected: one — same `VertexAiRagMemoryService` pointed at a corpus that holds both. But ingestion is two pipelines.)*

> **🚀 In Production**
>
> RAG-backed memory has the same cost-creep failure mode as a RAG corpus: it grows linearly in chats. Set an ingestion filter (only store turns where `add_events_to_memory` is called explicitly) and a retention policy on the corpus.

---

[← Prev: 11_Memory/03_VertexAIMemoryBank]  [↑ Map](../../MAP.md)  [Next: 11_Memory/05_LoadMemoryTool →]
