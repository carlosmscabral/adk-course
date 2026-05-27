---
module: 10A_EmbeddingsVectorSearch
page: 03_VectorSearchIntro
title: ☁️ Vertex AI Vector Search — concepts
estimated_minutes: 20
prereqs: [10A_EmbeddingsVectorSearch/02]
concepts: [index, indexEndpoint, TreeAH, BruteForce, ANN, recall]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/04_BuildingAnIndex →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 03 Vector Search intro

---

## 🧠 Two resources, one mental model

Vertex AI Vector Search has **two GCP resources** you need to know:

```
_figures/vector_search_topology.txt
```

```
  Index           ───deploy───►   IndexEndpoint
  (the vectors)                   (serves queries)
```

- **Index** — stores your vectors + metadata. Has an algorithm config (TreeAH or BruteForce). Lives in a region.
- **IndexEndpoint** — a deployed serving instance. One endpoint can host multiple indexes (called "deployed indexes" — give each a deploy ID).

You build the Index once, deploy it once, then query through the Endpoint forever.

## ⚖️ TreeAH vs BruteForce

| | TreeAH (ANN) | BruteForce |
|---|---|---|
| Algorithm | Tree-based approximate nearest neighbor | Exact: scan every vector |
| Speed | ms at billions of vectors | linear in N |
| Recall | ~95-99% (configurable) | 100% |
| Use when | Default. Most production RAG. | Eval baselines; small N (<10k); legal/medical where missing one hurts |

The "AH" is "asymmetric hashing" — Google's proprietary ANN variant (similar idea to FAISS-IVF). Configurable: `leaf_node_embedding_count`, `leaf_nodes_to_search_percent` — higher = slower + better recall.

## ⚠️ When ANN is the *wrong* answer

- **Tiny N (<10k vectors)**: BruteForce is faster *and* exact. Don't pay the TreeAH overhead.
- **Hard recall guarantees** (legal discovery, medical retrieval): use BruteForce or run TreeAH + verify with BruteForce eval on a sample.
- **Streaming-heavy / few queries**: ANN index update cost may exceed query savings.

> 🚀 **In Production**
> Most teams run TreeAH for prod and a tiny BruteForce companion index on a sampled corpus for recall regression eval. We cover this in module 14 (Evaluation).

## 💸 The cost shape

You pay for:

1. **Index storage** — per GB-month of vectors.
2. **Endpoint serving** — per-node-hour while deployed. The endpoint runs even when no queries. **Undeploy or delete in dev**.
3. **Embedding API** (covered in 02) — separate line item.

Two-node `e2-standard-2` endpoint is ~$X/month idle. Cheap-but-not-free. For dev: deploy → drill → undeploy.

## ⏱️ Latencies you should expect

- Index *creation*: seconds.
- First *deploy*: **20-40 minutes**. (This catches everyone.)
- Subsequent deploys / re-deploys: ~10-15 min.
- Query: <50ms p50 at moderate scale.
- Stream upsert: visible to queries in seconds; batch upsert in minutes.

> ⚠️ **Gotcha**
> Your drill script *will* fail the first time if you don't account for the deploy wait. Use `index.deploy_index(...).result()` or poll explicitly — see page 04.

## ❓ Check

> ❓ **Ask the student:** "You have 5,000 product descriptions, queries are rare (~10/day), and you need exact recall for a legal-compliance use case. TreeAH or BruteForce?"
>
> Expected: BruteForce — small N + exact recall required + few queries = ANN gives you nothing.

## 🤖 Tutor

> Make the student internalize that **Index ≠ Endpoint**. They will at some point try to `find_neighbors` on an Index (the resource that just stores vectors) and get an error. Set them up for that error now.

---

[← Prev: 10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/04_BuildingAnIndex →]
