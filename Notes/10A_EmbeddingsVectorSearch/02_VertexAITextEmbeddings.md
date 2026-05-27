---
module: 10A_EmbeddingsVectorSearch
page: 02_VertexAITextEmbeddings
title: ☁️ Vertex AI text embeddings — the SDK
estimated_minutes: 30
prereqs: [10A_EmbeddingsVectorSearch/01]
concepts: [gemini-embedding-001, task-type, RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, batch-embedding]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/03_VectorSearchIntro →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 02 Vertex AI text embeddings

---

## ☁️ The model lineup (2026-05-27)

| Model | Dims | Notes |
|---|---|---|
| `gemini-embedding-001` | up to 3072 | **Current default for new work.** Matryoshka — truncate dims to fit cost. Supports `task_type`. |
| `text-multilingual-embedding-002` | 768 | 100+ languages. |
| `text-embedding-005` | 768 | Legacy. English + code. |
| `text-embedding-004` | 768 | **Deprecated 2026-01-14.** Widely supported by RAG Engine, but on the sunset path. |

> ⚠ **Model deprecation** — `text-embedding-004` was deprecated 2026-01-14 and `text-embedding-005` is legacy. For new work, use `gemini-embedding-001` (3072 dims, supports `task_type` parameter). Existing indexes are incompatible across embedding-model families — switching model requires re-embedding the entire corpus.

> 🚀 **In Production**
> Pin the model in config. Changing the model means **re-embedding the whole corpus** (vectors from different model families are not comparable). See `07_InProduction`.

## 🛠 Embedding a single string

```python
# Work/02_embed_one.py — run with: uv run python Work/02_embed_one.py
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput

vertexai.init(project="YOUR-PROJECT", location="us-central1")
model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

embeddings = model.get_embeddings([
    TextEmbeddingInput("Python is a programming language", task_type="RETRIEVAL_DOCUMENT"),
])
print(len(embeddings[0].values))
print(embeddings[0].values[:5])
```

```text
3072
[0.0234, -0.0119, 0.0573, 0.0411, 0.0188]
```

`get_embeddings` takes a **list** of `TextEmbeddingInput` and returns a parallel list. Always batch — single-string calls are the same per-call cost as 5-string calls.

## ⚠️ THE gotcha: task types

**This is the #1 mistake students make.** Vertex AI embeddings have a `task_type` parameter. Two text strings with identical content but different task types produce **different vectors**. The model literally tilts the embedding for the downstream task.

For RAG, you use exactly two:

| Task type | Use for |
|---|---|
| `RETRIEVAL_DOCUMENT` | Every chunk you store in the index. |
| `RETRIEVAL_QUERY` | The user's question at query time. |

Mix them up and **recall drops 10-30%**. The vectors are still close-ish (they're describing the same text), but you're comparing apples to slightly-different apples.

Other task types (worth knowing):

- `SEMANTIC_SIMILARITY` — both sides are "queries" (symmetric similarity).
- `CLASSIFICATION` / `CLUSTERING` — for downstream classifiers / k-means.
- `QUESTION_ANSWERING` / `FACT_VERIFICATION` — specialized retrieval variants.

> ⚠️ **Gotcha**
> The default if you omit `task_type` is `RETRIEVAL_QUERY` on some SDK versions and unset on others. **Always pass it explicitly.**

## 🛠 Right way — asymmetric embeddings

```python
# Work/02b_embed_asym.py — run with: uv run python Work/02b_embed_asym.py
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput

vertexai.init(project="YOUR-PROJECT", location="us-central1")
_MODEL = TextEmbeddingModel.from_pretrained("gemini-embedding-001")


def embed_documents(texts: list[str]) -> list[list[float]]:
    inputs = [TextEmbeddingInput(t, task_type="RETRIEVAL_DOCUMENT") for t in texts]
    return [e.values for e in _MODEL.get_embeddings(inputs)]


def embed_query(q: str) -> list[float]:
    inputs = [TextEmbeddingInput(q, task_type="RETRIEVAL_QUERY")]
    return _MODEL.get_embeddings(inputs)[0].values


if __name__ == "__main__":
    docs = embed_documents(["Python is a programming language"])
    print(len(docs), len(docs[0]))           # 1 3072
    print(len(embed_query("What is Python?")))  # 3072
```

Two functions. Two task types. **Wire them carefully.**

## 🛠 Have the student run

> 🛠 Have the student embed the same string with both task types and compute cosine between the two:
>
> ```python
> doc_vec = embed_documents(["What is Python?"])[0]
> qry_vec = embed_query("What is Python?")
> print(cos(doc_vec, qry_vec))  # < 1.0 — the model tilted both
> ```
>
> Typical result: ~0.85-0.92. Same text, different vectors.

## 💸 Cost & throughput

- Check the Vertex AI pricing page — `gemini-embedding-001` is priced per 1k input chars; rates differ from the legacy `text-embedding-*` family.
- Default 600 RPM, 250k input chars/min — request increase early.
- Batch up to **250 inputs per call** for the legacy `text-embedding-*` family; `gemini-embedding-001` currently caps batches lower — check the SDK error if you exceed it.

> 🚀 **In Production**
> A nightly batch job at 600 RPM gets you ~36M chars/hour. If you have a 10M-doc corpus, plan for hours-to-days of embed time, or request quota up front.

## ❓ Check

> ❓ **Ask the student:** "If I embed all my docs with `task_type='RETRIEVAL_QUERY'` and all my queries with `task_type='RETRIEVAL_QUERY'`, what happens?"
>
> Expected: retrieval *works* (both sides use the same projection) but recall is worse than the asymmetric setup; you've lost the model's asymmetric tilt that's optimized for query→doc matching.

## 🤖 Tutor

> The asymmetric-task-type thing is invisible until eval scores look weird. **Hammer it now.** The drill (page 09) explicitly compares both configurations so the student feels the difference.

---

[← Prev: 10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/03_VectorSearchIntro →]
