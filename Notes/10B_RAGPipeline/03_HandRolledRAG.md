---
module: 10B_RAGPipeline
page: 03_HandRolledRAG
title: 🛠 Hand-rolled RAG end-to-end
estimated_minutes: 50
prereqs: [10B_RAGPipeline/02, 10A_EmbeddingsVectorSearch/05]
concepts: [pypdf, ingest, augment, prompt-stuffing, gemini-2.5-flash]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/02_Chunking] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/04_VertexAIRAGEngine →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 03 Hand-rolled RAG

---

## 🛠 What we're building

A standalone script — **no ADK yet** — that:

1. Loads a PDF.
2. Chunks it (sentence-aware from page 02).
3. Embeds chunks with `gemini-embedding-001` (`RETRIEVAL_DOCUMENT`).
4. Upserts to a Vertex AI Vector Search index (from 10A/04).
5. Accepts a question, embeds it (`RETRIEVAL_QUERY`).
6. Retrieves top-k, augments the prompt, calls Gemini, prints + cites.

Then in page 05 we wrap it into an ADK tool. **Glue first, agent after.**

## 📦 Imports

```python
from pypdf import PdfReader
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from google.cloud import aiplatform
from google.genai import Client
from google.genai.types import GenerateContentConfig
```

## ☁️ Step 1 — ingest

```python
def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)
```

A page extraction this naive misses headers/footers and tables. Production code uses `pypdf` + a layout parser or Document AI. For learning, this is fine.

## 🛠 Step 2 — chunk

Reuse `chunk_sentences` from page 02. Chunk size = 600 chars for this drill.

## ☁️ Step 3 — embed (asymmetric!)

```python
EMBED_MODEL = "gemini-embedding-001"  # text-embedding-004 deprecated 2026-01-14; -005 legacy

def embed_documents(texts: list[str]) -> list[list[float]]:
    model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
    inputs = [TextEmbeddingInput(t, task_type="RETRIEVAL_DOCUMENT") for t in texts]
    # Batch in groups of 250 (the model's max per-call).
    out: list[list[float]] = []
    for i in range(0, len(inputs), 250):
        batch = inputs[i : i + 250]
        out.extend(e.values for e in model.get_embeddings(batch))
    return out

def embed_query(q: str) -> list[float]:
    model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
    return model.get_embeddings(
        [TextEmbeddingInput(q, task_type="RETRIEVAL_QUERY")]
    )[0].values
```

> ⚠️ **Gotcha (you've been warned twice now)** — `RETRIEVAL_DOCUMENT` going in, `RETRIEVAL_QUERY` going out. Two functions. Different signatures. Don't merge them.

## ☁️ Step 4 — upsert

```python
def index_chunks(index, chunks: list[str], vectors: list[list[float]]) -> dict[str, str]:
    """Upsert vectors to Vector Search. Returns id→text side-store."""
    side_store = {}
    datapoints = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        doc_id = f"chunk_{i:05d}"
        side_store[doc_id] = chunk
        datapoints.append({"datapoint_id": doc_id, "feature_vector": vec})
    # In batches of 1000 (stream upsert limit).
    for i in range(0, len(datapoints), 1000):
        index.upsert_datapoints(datapoints=datapoints[i : i + 1000])
    return side_store
```

The **side-store** is just a dict here. In prod: BigQuery, Firestore, GCS JSON.

## ☁️ Step 5 — retrieve

```python
def retrieve(endpoint, deployed_id: str, query: str, side_store: dict, k: int = 5):
    qvec = embed_query(query)
    resp = endpoint.find_neighbors(
        deployed_index_id=deployed_id, queries=[qvec], num_neighbors=k,
    )
    return [
        {"id": h.id, "score": 1 - h.distance, "text": side_store[h.id]}
        for h in resp[0]
    ]
```

## 🛠 Step 6+7 — augment & generate

```python
PROMPT_TEMPLATE = """\
You are a precise documentation assistant. Answer the question using ONLY the
context below. Cite the chunk IDs in brackets [chunk_00042] inline after each
claim. If the context is insufficient, say so plainly.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

def answer(client: Client, question: str, hits: list[dict]) -> str:
    context = "\n\n".join(f"[{h['id']}] {h['text']}" for h in hits)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(temperature=0.1),
    )
    return resp.text
```

The whole pipeline:

```python
text       = load_pdf("docs/python_tutorial.pdf")
chunks     = chunk_sentences(text, max_chars=600)
vectors    = embed_documents(chunks)
side_store = index_chunks(index, chunks, vectors)
hits       = retrieve(endpoint, deployed_id, "what are decorators?", side_store, k=5)
print(answer(client, "what are decorators?", hits))
```

That's RAG. ~80 lines. No magic.

## ⚠️ Where this script will fail in prod

- No retry on transient 429s.
- Re-ingesting re-embeds everything (wasteful — track content hashes).
- No dedup (same chunk indexed twice = wasted vectors).
- Prompt-stuffing all 5 chunks may exceed context if chunks are large.
- No eval — you have no idea if retrieval is good.

We address each in `07_InProduction` and module 14 (Evaluation).

## ❓ Check

> ❓ **Ask the student:** "Walk me through what happens, in order, when a user asks a question to this script."
>
> Expected: embed query (RETRIEVAL_QUERY) → find_neighbors on endpoint → side-store lookup for text → format prompt template → Gemini call → print answer with chunk IDs in brackets.

## 🛠 Have the student run

> 🛠 Use the script above with a small PDF (the Python tutorial works great). Ask three questions: one whose answer is in one chunk, one whose answer spans two adjacent chunks, one that's NOT in the PDF. Observe the answers — the third should say "I don't know based on the provided context."

## 🤖 Tutor

> If the student rushes to page 04 (managed) without writing this script, **stop them**. The whole point of the engine-first track is they feel the wires once. They will thank you when they have to debug a managed pipeline later.

---

[← Prev: 10B_RAGPipeline/02_Chunking] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/04_VertexAIRAGEngine →]
