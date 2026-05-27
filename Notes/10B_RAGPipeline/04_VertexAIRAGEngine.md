---
module: 10B_RAGPipeline
page: 04_VertexAIRAGEngine
title: ☁️ Vertex AI RAG Engine — the managed shortcut
estimated_minutes: 25
prereqs: [10B_RAGPipeline/03]
concepts: [RagCorpus, rag.upload_file, rag.retrieval_query, RagVectorDbConfig, TransformationConfig]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/03_HandRolledRAG] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/05_RAGIntoADK →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 04 Vertex AI RAG Engine

---

## 🧠 Three things, one button

The hand-rolled pipeline does ingest+chunk+embed+index+retrieve. **RAG Engine collapses all of that.** You hand it files, it gives you `retrieval_query`. Internally it still uses Vector Search — you just don't manage the resources.

## ⚠️ GA vs preview surface

RAG Engine has graduated to GA. The import path is now `from vertexai import rag` (not `from vertexai.preview import rag`). Configuration moved from flat kwargs into nested config objects: `RagVectorDbConfig`, `RagEmbeddingModelConfig`, `VertexPredictionEndpoint`, `TransformationConfig`, `ChunkingConfig`. Code written against the preview namespace still runs today but is being retired — pin to GA.

## ☁️ Create a corpus

```python
# Work/04_rag_corpus.py — run with: uv run python Work/04_rag_corpus.py
import vertexai
from vertexai import rag
from vertexai.rag import (
    RagVectorDbConfig,
    RagEmbeddingModelConfig,
    VertexPredictionEndpoint,
)

vertexai.init(project="YOUR-PROJECT", location="us-central1")

backend_config = RagVectorDbConfig(
    rag_embedding_model_config=RagEmbeddingModelConfig(
        vertex_prediction_endpoint=VertexPredictionEndpoint(
            publisher_model="publishers/google/models/gemini-embedding-001",
        )
    )
)

corpus = rag.create_corpus(
    display_name="adk_course_10b_corpus",
    description="Course content",
    backend_config=backend_config,
)
print(corpus.name)
```

```text
projects/123/locations/us-central1/ragCorpora/4567890
```

Embedding model is **pinned at corpus creation**. Changing it = recreate the corpus. (Same constraint as the hand-rolled pipeline, just enforced.) The recommended default is `gemini-embedding-001` — see [10A/03](../10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding.md). The `text-embedding-004` family is deprecated 2026-01-14; old samples that hardcode it will keep running for now but should be migrated.

## ☁️ Upload files (chunking + embedding happen server-side)

```python
# Work/04b_rag_upload.py — run with: uv run python Work/04b_rag_upload.py
from vertexai import rag

rag_file = rag.upload_file(
    corpus_name=corpus.name,
    path="/local/path/to/doc.pdf",
    display_name="doc.pdf",
    description="Sample document",
)
print(rag_file.name)
```

```text
projects/123/locations/us-central1/ragCorpora/4567890/ragFiles/...
```

One call. The file is uploaded, chunked (server-side defaults — typically ~500 token chunks, configurable), embedded (`RETRIEVAL_DOCUMENT`), and indexed. **You don't see Vector Search resources** — they're managed for you.

Bulk import from GCS, now with explicit chunking config:

```python
# Work/04c_rag_import_gcs.py — run with: uv run python Work/04c_rag_import_gcs.py
from vertexai import rag
from vertexai.rag import TransformationConfig, ChunkingConfig

transformation_config = TransformationConfig(
    chunking_config=ChunkingConfig(
        chunk_size=512,
        chunk_overlap=100,
    )
)

rag.import_files(
    corpus_name=corpus.name,
    paths=["gs://my-bucket/docs/"],
    transformation_config=transformation_config,
)
```

Note the migration: the old top-level `chunk_size=` / `chunk_overlap=` kwargs are gone. Chunking lives under `TransformationConfig` — the same shape that will (per the GA docs) eventually carry other transformations.

## ☁️ Query

```python
# Work/04d_rag_query.py — run with: uv run python Work/04d_rag_query.py
from vertexai import rag

response = rag.retrieval_query(
    rag_resources=[rag.RagResource(rag_corpus=corpus.name)],
    text="What are decorators?",
    similarity_top_k=5,
    vector_distance_threshold=0.6,
)
for ctx in response.contexts.contexts:
    print(ctx.source_uri, "→", ctx.text[:80])
```

```text
doc.pdf → Decorators in Python are functions that take another function ...
doc.pdf → A decorator wraps a function, modifying its behavior without ...
...
```

`retrieval_query` returns `Context` objects with `source_uri` (your filename — citation is free) and `text` (chunk content). The task-type pairing is **handled internally** — RETRIEVAL_DOCUMENT at upload, RETRIEVAL_QUERY here.

## ⚖️ When to prefer RAG Engine over hand-rolled

| Pick **RAG Engine** when... | Pick **hand-rolled** when... |
|---|---|
| You want to ship in a week | You need a custom chunker |
| You don't need exotic metadata filters | You need to test exotic ANN params |
| Standard document types (PDF, MD, HTML, TXT) | Esoteric formats (your own protobuf) |
| Operational cost matters more than per-query cost | You have huge volume and need batch update |
| You want auto-handling of model versioning | You're already running Vector Search |

For 80% of teams, **RAG Engine is the right answer**. Knowing the hand-rolled version means you can debug when it goes wrong.

## ⚠️ The managed limitations

- **Chunk-size customization** is exposed via `TransformationConfig` but the set of transformations is still narrower than rolling your own.
- **Custom metadata filters** are limited compared to raw `restricts`.
- **Vector access** is closed — you can't pull out vectors and re-rank with your own model. (You can re-rank chunks with a re-rank model post-retrieval.)
- **Embedding model swap** = recreate corpus. The hand-rolled version has the same constraint, but here you can't do clever migrations (dual-write to two indexes).

## 🚀 In Production

> **🚀 In Production**
> Default to RAG Engine, and pin to the **GA surface** (`vertexai.rag`). The preview namespace (`vertexai.preview.rag`) is being retired; code written against it will break on upgrade. Concretely: use `backend_config=RagVectorDbConfig(...)` instead of `embedding_model_config=`, and `transformation_config=TransformationConfig(chunking_config=ChunkingConfig(...))` instead of flat `chunk_size=`/`chunk_overlap=` kwargs. Use `gemini-embedding-001` as the embedding model — `text-embedding-004` is deprecated 2026-01-14.
>
> Drop to raw Vector Search when an eval shows the managed defaults are limiting recall, OR when you need filter / re-ranking sophistication the managed API doesn't expose. The migration path is straightforward — you've already learned both APIs in 10A and 10B.

## ❓ Check

> ❓ **Ask the student:** "You're getting good answers from RAG Engine but you want to filter chunks by `region=EU` for a tenancy isolation requirement. What's your first move?"
>
> Expected: check the SDK version's `rag.RagRetrievalConfig` for filter support; if insufficient, fall back to raw Vector Search with `restricts` (covered in 10A/05).

## 🛠 Have the student run

> 🛠 Ingest the same PDF used in page 03 into a `RagCorpus`. Ask the same three questions. Compare answer quality vs the hand-rolled version. Note: managed defaults are usually competitive — sometimes better, because the server-side chunker is sophisticated.

## 🤖 Tutor

> Resist the urge to gush about how short this code is. The student should *earn* the shortcut by understanding what's underneath. They wrote ~80 lines in page 03; this is 6. The 6 are only readable because the 80 made sense.

---

[← Prev: 10B_RAGPipeline/03_HandRolledRAG] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/05_RAGIntoADK →]
