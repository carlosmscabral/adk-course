# AGENTS.md — Module 10B RAG Pipeline (teaching notes for the AI tutor)

## What the student should walk away knowing

- The 7-stage RAG loop (ingest → chunk → embed → store → retrieve → augment → generate).
- Three chunking strategies (fixed / sentence / semantic) and their trade-offs.
- Hand-rolled RAG end-to-end using 10A's primitives.
- The managed shortcut — Vertex AI RAG Engine (`RagCorpus`, `rag.upload_file`, `rag.retrieval_query`).
- Two ADK integration paths: `VertexAiRagRetrieval` as a tool vs `VertexAiRagMemoryService` as automatic memory.
- The canonical RAG sample's structure and where each pipeline stage maps to code.
- Production concerns: re-embedding, freshness, evals, lost-in-middle, query rewriting, hybrid retrieval, re-ranking.

## Pacing

- **Easy if** they nailed the 10A drill (asymmetric task types worked first try): 1-2 cruise, slow on 03 (the hand-rolled glue is the workout).
- **Hard if** they skipped the 10A drill or are fuzzy on retrieval mechanics: send them back to 10A before continuing 10B.

This module is the longest in the GCP track (~4 days). The drill is intentionally meaty — a personal RAG agent over their own notes is genuinely useful, not throwaway.

## ☁️ GCP cost concern

The drill ingests hundreds of MD files. At `text-embedding-005` defaults that's well within free-tier quotas for a one-shot run, but warn the student:

> "Cache the vectors + side-store after the first ingest. Re-running the drill from scratch will re-embed and chew quota."

If they're using a Vertex AI Vector Search endpoint for this drill (vs the mock-in-memory path), **make them delete the endpoint** when done. RAG Engine corpora are cheaper to leave around but still cost something — `rag.delete_corpus(...)` when finished.

## Watch for these mistakes

- **The task-type sin again** — yes, repeatedly. If the student's recall feels off in 10B, first thing: audit task types.
- **Skipping page 03** — they'll want to jump to the managed shortcut. Don't let them.
- **Re-embedding on every run** — quota smell. Cache.
- **Citing chunk IDs but not file paths** — answers feel less trustworthy. Tag source_file in metadata.
- **Stuffing too many chunks in the prompt** — lost-in-middle. Top-3-5 usually plenty.
- **Forgetting tool-selection discipline** — agent retrieves for "hi". Tell it not to in the prompt.

## When to suggest a detour

- "What's an LLM context limit?" → quick aside, no formal detour.
- "How do I evaluate this?" → "module 14 Evaluation" — note the forward link.
- "How do I make retrieval automatic?" → page 05 path (b) + "see module 11 Memory."
- "What about multimodal retrieval (images)?" → out of scope; link Vertex AI multimodal embedding docs.

## Mini-drill grading

- **Pass** = list-vs-tuple answer is substantive AND cites at least one real .md file from the corpus.
- **Strong pass** = the chatty question ("hi") does NOT trigger a retrieval call (observable in event log).
- **Fail** = answers without citations, hallucinated file paths, or task-type mismatch.

## Cross-link reminders

- 10B is foundational for 11 (Memory uses similar retrieval mechanics).
- Page 05 references 11 Memory for `VertexAiRagMemoryService`.
- Page 07 references 14 Evaluation for recall@k metrics.
- The spiral curriculum (rule 8): the "research assistant" comes back in 14, 16, 99 — each adds a layer (eval, guardrails, full capstone).
