---
module: 10A_EmbeddingsVectorSearch
page: 05_QueryingTheIndex
title: ☁️ Querying — find_neighbors
estimated_minutes: 25
prereqs: [10A_EmbeddingsVectorSearch/04]
concepts: [find_neighbors, num_neighbors, restricts, numeric_restricts, deployed_index_id]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/04_BuildingAnIndex] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/06_DissectingSample →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 05 Querying the index

---

## 🛠 The one call you actually use

```python
# Work/05_find_neighbors.py — run with: uv run python Work/05_find_neighbors.py
from google.cloud import aiplatform

aiplatform.init(project="YOUR-PROJECT", location="us-central1")
endpoint = aiplatform.MatchingEngineIndexEndpoint("projects/.../indexEndpoints/...")
query_embedding = [0.012, -0.034]  # 768 floats in real use; from embed_query(...)

response = endpoint.find_neighbors(
    deployed_index_id="adk_course_10a_deployed",
    queries=[query_embedding],          # list of vectors — batch friendly
    num_neighbors=5,
)
print(response)
```

```text
[[
    MatchNeighbor(id="doc_042", distance=0.812, ...),
    MatchNeighbor(id="doc_007", distance=0.788, ...),
    MatchNeighbor(id="doc_113", distance=0.756, ...),
    MatchNeighbor(id="doc_019", distance=0.731, ...),
    MatchNeighbor(id="doc_088", distance=0.704, ...),
]]
```

**Return shape**: list of lists. Outer list = one entry per query. Inner = top-k neighbors for that query.

## 📦 What's in a MatchNeighbor

- `id` — your `datapoint_id` (the string you upserted). **Use it to look up the original text in your own KV store** — Vector Search does NOT store the chunk text by default. Just the vector + metadata.
- `distance` — cosine distance (lower = closer for COSINE, higher = closer for DOT_PRODUCT — read the docs carefully).
- `restricts` / `crowding_tag` — echoed back if present.

> ⚠️ **Gotcha**
> Vector Search returns **IDs, not text**. You always need a side-store (BigQuery, Firestore, Cloud SQL, even a JSON file in dev) mapping `id → chunk_text`. The drill builds this side-store explicitly.

## 🧩 Metadata filtering with `restricts`

You can attach `restricts` (string tags) and `numeric_restricts` to each vector at upsert time, then filter at query time:

```python
# Work/05b_filtered_search.py — run with: uv run python Work/05b_filtered_search.py
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace, NumericNamespace,
)

response = endpoint.find_neighbors(
    deployed_index_id="adk_course_10a_deployed",
    queries=[query_embedding],
    num_neighbors=5,
    filter=[Namespace(name="topic", allow_tokens=["python"])],
    numeric_filter=[NumericNamespace(name="year", value_int=2026, op="GREATER_EQUAL")],
)
```

This is your replacement for SQL `WHERE` clauses inside the ANN search — done server-side, no extra round-trip.

> 🚀 **In Production**
> `restricts` are **declared at upsert time** — you cannot add a new metadata namespace to existing vectors without re-upserting them. Plan your filter schema before the first batch load.

## 🛠 End-to-end mini-call

```python
def search(query: str, k: int = 5) -> list[dict]:
    qry_vec = embed_query(query)                       # from page 02
    resp = endpoint.find_neighbors(
        deployed_index_id="adk_course_10a_deployed",
        queries=[qry_vec],
        num_neighbors=k,
    )
    hits = resp[0]
    return [
        {"id": h.id, "score": 1 - h.distance, "text": kv_store[h.id]}
        for h in hits
    ]
```

That's it. ~10 lines = a search engine.

## ⏱️ Latency tip

`num_neighbors` is the dominant latency knob after corpus size. Asking for `1000` instead of `10` is ~50% slower at 1M vectors. **Ask for what you need, not what you might need.**

## ❓ Check

> ❓ **Ask the student:** "Your retrieval is returning the right IDs but with wrong text in the final answer. Where do you look first?"
>
> Expected: the side-store / KV map from `id → chunk_text`. The vector match is correct; the lookup is wrong (stale, indexed during a re-chunk, etc.).

## 🛠 Have the student run

> 🛠 With their deployed index (or a mocked search function), query for `"How do Python decorators work?"` and inspect:
> 1. The 5 returned IDs.
> 2. The cosine scores — should be a smooth curve, not a cliff.
> 3. What happens with `num_neighbors=1` vs `num_neighbors=20`.

## 🤖 Tutor

> Drill the **id → text** lookup pattern hard. Half the bugs in RAG live in the side-store. The other half are task-type mismatches (page 02).

---

[← Prev: 10A_EmbeddingsVectorSearch/04_BuildingAnIndex] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/06_DissectingSample →]
