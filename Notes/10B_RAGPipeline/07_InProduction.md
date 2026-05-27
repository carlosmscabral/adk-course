---
module: 10B_RAGPipeline
page: 07_InProduction
title: 🚀 In Production — RAG pipelines
estimated_minutes: 30
prereqs: [10B_RAGPipeline/06]
concepts: [re-embedding, freshness, lost-in-middle, query-rewriting, hybrid-retrieval, re-ranking, precision-recall]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/06_DissectingRAGSample] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/08_KnowledgeCheck →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 07 In Production

---

## 🚀 The seven things that bite

### 1. Re-embedding when the model upgrades

Switching embedding models = vectors are incomparable. Plan it.

**Strategies:**
- **Lazy** — re-embed a chunk on next ingest/edit. Old chunks linger on old model. Cheap, slow convergence.
- **Eager** — recompute all vectors. Expensive but clean. Standard for major upgrades.
- **Dual-route** — stand up new index alongside old, query both, A/B for a week, cut over.

Always tag vectors with `model_version` (in `restricts` or in the side-store). Skipping this turns the migration into archaeology.

### 2. Freshness / staleness

Your corpus drifts. Wiki page edited. PDF replaced. Stale chunks return stale answers.

**Strategies:**
- TTL on chunks; re-ingest after expiry.
- Hash-based dedup (chunk text → hash; only re-embed if hash changed).
- Webhook from CMS / docs source → trigger re-embed.
- Document the cadence in the runbook ("docs re-indexed nightly at 02:00 UTC").

### 3. Evals (covered in depth in module 14)

You can't improve what you don't measure. Build a tiny eval set early.

Metrics:

| Metric | What it measures |
|---|---|
| **recall@k** | Did we retrieve the gold chunk in top-k? |
| **precision@k** | What fraction of top-k were relevant? |
| **MRR** | Mean Reciprocal Rank — was the gold chunk near the top? |
| **answer-correctness** | LLM-as-judge on final answer |
| **citation-faithfulness** | Are the cited chunks actually supporting the claim? |

Start with 20-30 golden questions. Grow over time. Re-run on every chunker/embedder/model change.

### 4. Lost-in-the-middle

```
_figures/lost_in_middle.txt
```

LLMs pay more attention to the **start** and **end** of long prompts. A relevant chunk stuffed in the middle of top-10 is ~25% less likely to be used than the same chunk at position 1 or 10.

**Mitigations:**
- Smaller top-k. If 3 is enough, don't use 10.
- **Re-rank** retrieved chunks so the highest-relevance ones land at the start.
- **Bracket** important chunks: put best at start AND at end of the context block.

### 5. Query rewriting

User asks: "What about the second one?" — referencing prior turn. Vanilla retrieval embeds that literal text — garbage in, garbage out.

Wire a tiny LLM step before retrieval:

```python
def rewrite_query(history: list[str], question: str) -> str:
    prompt = f"""Rewrite the user's question into a self-contained search query.
Context: {history[-3:]}
Question: {question}
Self-contained query:"""
    return llm.generate(prompt).strip()
```

Now retrieve on the rewritten query. This adds ~150ms but rescues turn-2+ queries.

### 6. Hybrid retrieval (vector + keyword)

Pure vector retrieval misses **exact-match** cases — error codes, function names, version numbers. "What does `KeyError: 0` mean?" lexical match nails it; semantic vector might miss.

**Hybrid** = vector retrieval ∪ BM25 / keyword search → re-rank ∪ → top-k.

Worth it when: domain has many high-cardinality identifiers (code, errors, IDs). Skip when: pure prose Q&A.

### 7. Re-ranking with a cross-encoder

Bi-encoder retrieval (what 10A taught) embeds each chunk and query separately. Fast, scalable. Loses fine-grained relevance signals.

**Cross-encoder** re-ranking: take top-N (e.g. 50) from the bi-encoder, then run a cross-encoder over each (query, chunk) pair to compute true relevance. Pick top-k (e.g. 5) for the prompt.

Cost: ~10ms per (query, chunk) pair = ~500ms extra at N=50. Worth it for high-stakes retrieval. Vertex AI has a ranking API for this — see the `discoveryengine` SDK.

## 🚀 The In-Production checklist

Before shipping a RAG agent:

- [ ] Eval set of ≥20 golden questions, baselined.
- [ ] `model_version` tagged on every vector / chunk.
- [ ] Re-embed playbook documented.
- [ ] Freshness strategy: TTL OR webhook OR scheduled re-ingest.
- [ ] Chunk size chosen via eval, not guess.
- [ ] `task_type` audit: query is RETRIEVAL_QUERY, doc is RETRIEVAL_DOCUMENT.
- [ ] Citations enforced in the system prompt (see RAG sample's `prompts.py`).
- [ ] Logging: every (query, retrieved_ids, final_answer) tuple is stored.
- [ ] Tool-selection discipline in prompt (don't retrieve for "hi").
- [ ] If using `VertexAiRagMemoryService` AND a retrieval tool — pick one.
- [ ] Query rewriting in place for chat agents (turn-2+ context).
- [ ] Re-ranking budget evaluated (often worth it at top-50 → top-5).

## 🤖 Tutor

> The student doesn't need to implement all of these. They need to **know they exist**. When they hit a recall problem in real life, this page is the diagnosis menu.

---

[← Prev: 10B_RAGPipeline/06_DissectingRAGSample] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/08_KnowledgeCheck →]
