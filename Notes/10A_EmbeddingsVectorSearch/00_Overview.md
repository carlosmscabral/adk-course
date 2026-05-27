---
module: 10A_EmbeddingsVectorSearch
page: 00_Overview
title: Embeddings & Vector Search — Overview
estimated_minutes: 15
prereqs: [03_Tools/05, 04_SessionsState/04]
concepts: [embeddings, vertex-ai, vector-search, RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, ANN]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 09_Skills/last] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 00 Overview

---

## 🧠 What you'll learn

- What an **embedding** is — a dense vector representing meaning.
- How to generate them with **Vertex AI text-embedding** models.
- How to store and query them in **Vertex AI Vector Search** (the managed ANN index).
- The single biggest gotcha: `RETRIEVAL_QUERY` vs `RETRIEVAL_DOCUMENT` task types.
- When to fall back to **BruteForce** (exact) over **TreeAH** (ANN).

This module is the **foundation** for 10B (RAG pipelines) and 11 (Memory). Build muscle here.

## 📦 Time

~3 days (concept pages + drill).

## ☁️ GCP prereqs — verify BEFORE you start

> 🛠 **Have the student run each of these and paste the output back:**

```bash
# 1. ADC configured?
gcloud auth application-default print-access-token | head -c 20 ; echo " ..."

# 2. Project set?
gcloud config get-value project

# 3. Region pinned (most embedding+VS regions are us-central1; pick one and stick)?
gcloud config get-value compute/region   # or set: gcloud config set compute/region us-central1

# 4. Required APIs enabled?
gcloud services list --enabled \
  --filter="name:(aiplatform.googleapis.com OR storage.googleapis.com)"
```

If any are missing:

```bash
gcloud services enable aiplatform.googleapis.com storage.googleapis.com
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

## 💸 Quotas to check upfront

Vertex AI Vector Search defaults are tight on new projects:

- **Vector Search index nodes** (often capped at 1-2 nodes — request more before drilling).
- **Embedding API requests/min** (default ~600 RPM for `text-embedding-005` — fine for the drill, painful in prod).

> ⚠️ **Gotcha**
> Index *deploy* takes 20-40 minutes. The drill mocks the index by default so you don't burn an hour waiting. Real deploy is covered in `04_BuildingAnIndex`.

## 🗺 Page order

| # | Page | What |
|---|---|---|
| 01 | `WhatIsAnEmbedding` | Vectors as meaning. 🧠 |
| 02 | `VertexAITextEmbeddings` | The SDK + task types. ☁️ |
| 03 | `VectorSearchIntro` | Indexes, endpoints, TreeAH vs BruteForce. ☁️ |
| 04 | `BuildingAnIndex` | Create → deploy → upsert. 🛠 |
| 05 | `QueryingTheIndex` | `find_neighbors`, `restricts`. 🛠 |
| 06 | `DissectingSample` | Walk through the RAG sample's retrieval code. 🔎 |
| 07 | `InProduction` | Task-type asymmetry, versioning, cost. 🚀 |
| 08 | `KnowledgeCheck` | 5 questions. ❓ |
| 09 | `MiniDrill` | 100 docs → index → query. 🛠 |

## 🤖 Tutor

> Open `00_Overview` aloud, verify GCP prereqs in order, then move to `01_WhatIsAnEmbedding`.
> If the student lacks a billable project, **stop here** — the rest of the module assumes it.

---

[← Prev: 09_Skills/last] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding →]
