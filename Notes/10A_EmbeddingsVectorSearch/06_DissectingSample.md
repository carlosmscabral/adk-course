---
module: 10A_EmbeddingsVectorSearch
page: 06_DissectingSample
title: 🔎 Dissecting the RAG sample
estimated_minutes: 30
prereqs: [10A_EmbeddingsVectorSearch/05]
concepts: [VertexAiRagRetrieval, RagCorpus, sample-walkthrough]
icon: 🔎
in_production: false
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/05_QueryingTheIndex] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/07_InProduction →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 06 Dissecting the RAG sample

---

## 🔎 What we're reading

Open these in your editor and follow along:

- `/home/carloscabral/study/adk-samples/python/agents/RAG/rag/agent.py`
- `/home/carloscabral/study/adk-samples/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py`
- `/home/carloscabral/study/adk-samples/python/agents/RAG/rag/prompts.py`

This sample uses the **managed shortcut** — `VertexAiRagRetrieval` and `RagCorpus` (the higher-level Vertex AI RAG Engine API). It does **not** call `MatchingEngineIndex` directly. That's a teaching moment — we'll surface where the Vector Search primitives live underneath.

## 🧭 Walkthrough — `agent.py`

```python
# lines 22-26 — the retrieval tool import
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from vertexai.preview import rag
```

ADK ships a first-class retrieval tool wrapper. You give it `rag_corpus` resource names and it becomes a `FunctionTool` the LLM can call.

```python
# lines 46-63 — wiring the tool
rag_corpus = os.environ.get("RAG_CORPUS")
if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description="Use this tool to retrieve documentation ...",
        rag_resources=[rag.RagResource(rag_corpus=rag_corpus)],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)
```

Three knobs you should recognize from pages 02-05:

- `similarity_top_k=10` — same as `num_neighbors` in page 05.
- `vector_distance_threshold=0.6` — drop matches further than this. Cuts noise.
- `rag_resources` — the managed equivalent of "this Index, deployed here".

## ⚠️ Where's the task-type setting?

**It isn't surfaced in this sample.** That's because `RagCorpus` defaults to `RETRIEVAL_DOCUMENT` at upload time and `RETRIEVAL_QUERY` at query time — the managed API hides the gotcha by enforcing the right pairing. **This is exactly why people reach for the managed API.**

If you peek at `prepare_corpus_and_data.py:64-66`:

```python
embedding_model_config = rag.EmbeddingModelConfig(
    publisher_model="publishers/google/models/text-embedding-004"
)
```

Embedding model is pinned at corpus creation. Re-embedding later means recreating the corpus.

## 🔎 Walkthrough — `prepare_corpus_and_data.py`

This is a one-shot setup script. The pattern:

1. `create_or_get_corpus()` — idempotent: lists corpora, matches by display name (lines 62-83). Same pattern we used in page 04 for raw indexes.
2. `download_pdf_from_url(...)` — pulls Alphabet's 10-K (lines 86-97).
3. `upload_pdf_to_corpus(...)` — `rag.upload_file(...)` does chunking + embedding + indexing in one call (lines 100-124). The managed shortcut is *very* short.
4. `update_env_file(...)` — writes `RAG_CORPUS=projects/.../ragCorpora/...` so `agent.py` can pick it up.

> 🚀 **In Production**
> Notice the `ResourceExhausted` catch at line 112 — embedding quota is the most common failure on new projects. The error message in the sample even points the user at the README's troubleshooting section. **Adopt this pattern in your own setup scripts.**

## 🧭 What the sample skips (your homework)

- No metadata `restricts` — every chunk is searchable; no per-tenant or per-topic filtering.
- No re-embedding strategy when the model changes (corpus would need to be recreated).
- No eval — recall and precision are not measured. Module 14 fixes this.
- One-corpus assumption. Real systems often have per-tenant or per-topic corpora.

## ❓ Check

> ❓ **Ask the student:** "If I want to add metadata filtering (e.g. `topic=python`) to this sample, what's the smallest change?"
>
> Expected: switch from `RagCorpus` to a raw `MatchingEngineIndex` + the page-05 `restricts` pattern — OR use `RagCorpus` with `rag.RagRetrievalConfig` filters if supported in your SDK version. Either way, you trade some simplicity for the filter knob.

## 🛠 Have the student run

> 🛠 Open the sample's `agent.py` and trace **one query** through:
> 1. User says "what was Alphabet's 2025 revenue?"
> 2. LLM decides to call `retrieve_rag_documentation`.
> 3. `VertexAiRagRetrieval` embeds the query and calls `rag.retrieval_query(...)` under the hood.
> 4. Top-10 chunks returned.
> 5. LLM gets the chunks as the tool result, drafts an answer with citations (see `prompts.py:39-58`).

## 🤖 Tutor

> The teaching-moment: this sample is what you write when you **want to ship**. Pages 02-05 are what you write when you **want to learn**. Both are valid. Once the student has both, they can make the call per project.

---

[← Prev: 10A_EmbeddingsVectorSearch/05_QueryingTheIndex] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/07_InProduction →]
