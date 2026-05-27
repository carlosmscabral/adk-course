---
module: 10A_EmbeddingsVectorSearch
page: 07_InProduction
title: 🚀 In Production — embeddings & vector search
estimated_minutes: 25
prereqs: [10A_EmbeddingsVectorSearch/06]
concepts: [task-type-asymmetry, model-versioning, quotas, recall-eval]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/06_DissectingSample] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/08_KnowledgeCheck →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 07 In Production

---

## 🚀 The five things that bite in prod

### 1. Task-type asymmetry (the #1 silent killer)

`RETRIEVAL_DOCUMENT` for stored chunks, `RETRIEVAL_QUERY` for user questions. Mismatch = ~10-30% recall drop, no error, no warning.

**Mitigation:**
- Centralize embedding through two functions (`embed_documents`, `embed_query`) — never call `get_embeddings` directly from agent code.
- Log the task type on every embedding call; alert if both query and doc use the same type for the same corpus.
- Eval (module 14) catches the regression but only if you have a baseline to compare to.

### 2. Model versioning = re-embed everything

Switching `text-embedding-005` → `text-embedding-large-exp-03-07` is **not** a config flip. The two models live in different geometric spaces. Vectors are incomparable across models.

**Mitigation:**
- Tag every vector with `model_version` in `restricts`.
- Migration playbook: stand up a **new** index, embed corpus with new model, dual-route queries to old + new, eval, cut over, delete old index.
- Budget the re-embed time *and* cost up front. 10M docs × $0.000025/1k chars × average chunk size = real money.

### 3. Quota — the first failure mode on new projects

Default quotas on a fresh GCP project:

- **Vector Search deployed indexes**: often 1-2.
- **Embedding RPM**: ~600 for `text-embedding-005`.
- **Embedding input chars/min**: ~250k.

A single batch ingest of 100k chunks will blow through this in minutes.

**Mitigation:**
- File quota increases **before** the first prod ingest. Lead time is days, not minutes.
- Build retry-with-backoff into your embedder; respect `429 Resource Exhausted`.

### 4. Endpoint cost — the thing that runs even when you sleep

`IndexEndpoint` is a deployed VM(s). It bills by-the-hour as long as it's up. **It does not auto-undeploy.**

**Mitigation:**
- Dev: `undeploy` after each session OR delete the endpoint entirely.
- Prod: pin `min_replica_count=1` only if you actually need 24/7 latency. Otherwise consider Vertex AI RAG Engine (managed, pay-per-query — covered in 10B/04).
- Alert on idle endpoints in non-prod projects.

### 5. ANN is approximate — measure it

TreeAH at default params recalls ~95-99% vs BruteForce. That last 1-5% includes some of the *most relevant* docs (similarity-by-similarity, the hardest to retrieve are the ones the ANN tree won't find).

**Mitigation:**
- Keep a small **BruteForce** companion index on a sampled subset (e.g. 10k vectors).
- Eval the prod TreeAH index against the BruteForce baseline weekly. Track `recall@10` and `MRR@10`.
- For high-stakes use (legal, medical), use BruteForce in prod even at cost — covered with examples in module 14.

## 🚀 The In-Production checklist

Before shipping a Vector Search-backed agent:

- [ ] Embedding model pinned in config; documented in runbook.
- [ ] Task types audited (search code for `task_type=` — both kinds present, used correctly).
- [ ] Quotas raised: embedding RPM, deployed indexes, embedding chars/min.
- [ ] Endpoint cost monitored; idle alerts set.
- [ ] Recall eval: TreeAH vs BruteForce baseline on a sample.
- [ ] Re-embed playbook documented (you *will* upgrade models).
- [ ] Side-store (id → chunk_text) backed up; consistency with index audited.
- [ ] Endpoint network mode: VPC peering or PSC for prod (not public).

## 🤖 Tutor

> Walk through the checklist with the student. For each item ask: "What would break if you skipped this?" Their answer is the real test of whether the module landed.

---

[← Prev: 10A_EmbeddingsVectorSearch/06_DissectingSample] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/08_KnowledgeCheck →]
