---
module: 10A_EmbeddingsVectorSearch
page: 04_BuildingAnIndex
title: ☁️ Building & deploying an index
estimated_minutes: 40
prereqs: [10A_EmbeddingsVectorSearch/03]
concepts: [MatchingEngineIndex, MatchingEngineIndexEndpoint, batch-update, stream-update, GCS]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/03_VectorSearchIntro] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/05_QueryingTheIndex →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 04 Building an index

---

## 🛠 The four steps

```
1. create Index           (seconds)
2. create IndexEndpoint   (seconds)
3. deploy Index → Endpoint (20-40 min — the big wait)
4. upsert vectors          (batch or stream)
```

Then query. We do query in page 05.

## ☁️ Step 1 — create the Index

```python
# Work/04_create_index.py — run with: uv run python Work/04_create_index.py
from google.cloud import aiplatform

aiplatform.init(project="YOUR-PROJECT", location="us-central1")

index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name="adk-course-10a-index",
    dimensions=768,                          # match text-embedding-005
    approximate_neighbors_count=10,           # default top-k
    distance_measure_type="COSINE_DISTANCE",  # default for text
    leaf_node_embedding_count=500,
    leaf_nodes_to_search_percent=7,
    index_update_method="STREAM_UPDATE",      # or BATCH_UPDATE
)
print(index.resource_name)
```

```text
projects/123/locations/us-central1/indexes/45678...
```

`STREAM_UPDATE` — vectors are queryable within seconds of upsert. Higher per-vector cost.
`BATCH_UPDATE` — point at a GCS folder of JSON files; index ingests on schedule. Cheaper, lower freshness.

For BruteForce: `MatchingEngineIndex.create_brute_force_index(...)` — same args, no `leaf_node_*`.

## ☁️ Step 2 — create the Endpoint

```python
# Work/04b_create_endpoint.py — run with: uv run python Work/04b_create_endpoint.py
from google.cloud import aiplatform

aiplatform.init(project="YOUR-PROJECT", location="us-central1")

endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name="adk-course-10a-endpoint",
    public_endpoint_enabled=True,   # easiest for dev; lock down for prod
)
print(endpoint.resource_name)
```

For prod, prefer **VPC-peered** or **PSC** endpoints — never public.

## ☁️ Step 3 — deploy (grab a coffee)

```python
# Work/04c_deploy_index.py — run with: uv run python Work/04c_deploy_index.py
# Assumes `index` and `endpoint` are loaded by display_name (see the
# idempotent helper at the bottom of this page).
endpoint.deploy_index(
    index=index,
    deployed_index_id="adk_course_10a_deployed",
    min_replica_count=1,
    max_replica_count=1,
)
# blocks 20-40 minutes
```

> ⚠️ **Gotcha — the deploy wait**
> This is the single longest single operation in the course. Start it, switch to coffee + page 05 (the query API), come back. Your tutor should explicitly call out the wait.

## ☁️ Step 4 — upsert vectors

Two paths:

### Stream upsert (small batches, real-time)

```python
# Work/04d_stream_upsert.py — run with: uv run python Work/04d_stream_upsert.py
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace,
)

index.upsert_datapoints(
    datapoints=[
        {
            "datapoint_id": "doc_001",
            "feature_vector": [0.012, -0.034],   # 768 floats in real use
            "restricts": [{"namespace": "topic", "allow_list": ["python"]}],
        },
        # ... up to 1000 per call
    ]
)
```

`restricts` are **metadata filters** queried server-side — covered in page 05.

### Batch update (huge corpora)

1. Write your vectors to GCS as JSONL files. Each line:
   ```json
   {"id": "doc_001", "embedding": [0.012, ...], "restricts": [...]}
   ```
2. Call `index.update_embeddings(contents_delta_uri="gs://bucket/path/")`.
3. The index re-builds in the background (hours for millions of vectors).

> 🚀 **In Production**
> Use **batch** for the initial corpus load. Use **stream** for incremental updates (a new doc landed, re-embed and upsert the few chunks). Mixing modes is fine.

## 🛠 The full mini-script (skip the long wait)

If quota is the blocker, write the index code but **don't deploy**. Replace `endpoint.deploy_index(...).result()` with a print + sleep and proceed to mock the query. The drill page (09) documents both the real and the mocked path.

```python
def build_or_get_index(name: str, dims: int = 768) -> aiplatform.MatchingEngineIndex:
    """Idempotent: returns existing if display_name matches, else creates."""
    existing = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{name}"'
    )
    if existing:
        return existing[0]
    return aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=name,
        dimensions=dims,
        approximate_neighbors_count=10,
        distance_measure_type="COSINE_DISTANCE",
        index_update_method="STREAM_UPDATE",
    )
```

Idempotent helpers like this are crucial — you do not want to accidentally create five $X/month endpoints.

## ❓ Check

> ❓ **Ask the student:** "Why is `create_tree_ah_index` cheaper at query time than `create_brute_force_index` for a 1M-vector corpus?"
>
> Expected: TreeAH visits only a small percent of leaf nodes (configurable via `leaf_nodes_to_search_percent`), so query latency stays roughly log(N). BruteForce scans all N.

## 🛠 Tutor — explicit pause

> 🛠 **Have the student** start the `deploy_index` call now, then jump to page 05 (querying) while the deploy runs. Come back to page 04 after deploy completes to actually upsert.

## 🤖 Tutor

> The deploy-wait is unavoidable. Treat it as a natural break: the student can read pages 05 and 06 (sample dissection) while waiting. **Do not** have them write more code that depends on the index existing — wait for the deploy to finish.

---

[← Prev: 10A_EmbeddingsVectorSearch/03_VectorSearchIntro] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/05_QueryingTheIndex →]
