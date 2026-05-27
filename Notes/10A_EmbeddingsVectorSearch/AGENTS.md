# AGENTS.md — Module 10A Embeddings & Vector Search (teaching notes for the AI tutor)

## What the student should walk away knowing

- An embedding is a fixed-length dense vector representing meaning; cosine for text.
- Vertex AI text embedding models (`text-embedding-005` as default for 768 dims).
- `RETRIEVAL_QUERY` vs `RETRIEVAL_DOCUMENT` — the asymmetric-task-type pattern, the #1 gotcha.
- Vector Search has two resources: `MatchingEngineIndex` (storage) and `MatchingEngineIndexEndpoint` (serving).
- TreeAH (ANN, scalable) vs BruteForce (exact, slow). When to pick which.
- `find_neighbors` returns IDs, not text — you always need a side-store.
- Index deploy takes 20-40 minutes. Plan around it.
- Re-embedding cost when models change is real; pin the model and tag vectors.

## ☁️ Pre-flight (do NOT skip)

Before drilling, verify the student has:

- A billable GCP project (`gcloud config get-value project`).
- ADC set up (`gcloud auth application-default print-access-token`).
- Vertex AI API enabled (`gcloud services list --enabled | grep aiplatform`).
- A region pinned (default us-central1).

If any of these fail, **stop and fix**. The whole module is wired around real GCP calls (or a documented mock).

## 💸 Cost concern

This module touches the embedding API (cheap) and Vector Search (an idle endpoint costs $X/month). Tell the student:

> "Delete the endpoint when you're done with the drill. `endpoint.undeploy_index(...)` and `endpoint.delete()`. Don't be the engineer paying for an idle index six months from now."

The drill defaults to a `--mock` flag for exactly this reason.

## Pacing

- **Easy if** the student already knows what an embedding is (e.g., did the interview-prep practice on cosine similarity): blast through 01-02, slow down on 03-04 (the resource model is unfamiliar even to ML folks).
- **Hard if** the student hasn't seen vector math: linger on page 01, run the cosine snippet by hand 2-3 times, *then* move on.

Tell them upfront: "There's a 20-40 min deploy step. We'll start it, then read page 06 (sample dissection) while it runs."

## Watch for these mistakes

- Mixing task types — by far the most common. Audit their code: are there two distinct embed functions or one?
- Trying to query the Index instead of the Endpoint. The error message is unhelpful — recognize it.
- Forgetting to undeploy after the drill (cost).
- Asking for `num_neighbors=1000` when they need 10 (latency).
- Storing chunk text inside `restricts` (it's metadata, not a payload). Use a side-store.

## When to suggest a detour

- Student fuzzy on vector math: link them to the interview-prep cosine practice (they likely already did it).
- Student asks "how does TreeAH actually work?": this is a rabbit hole. Park it as "module 19 Internals" optional reading. Don't derail 10A.
- Student asks about embeddings for images/audio: out of scope here — point them at the Vertex AI multimodal embedding docs as a self-study link.

## Mini-drill grading

- **Pass** = both configs run, side-by-side output shows that asymmetric (correct) retrieves visibly more on-topic results for at least 2/3 sample questions.
- **Fail** = student got cosine wrong, embedded one at a time (quota smell), or didn't actually contrast the two task-type configurations.
- **Edge probe**: ask "what would happen if you embedded *queries* as RETRIEVAL_DOCUMENT but kept docs as RETRIEVAL_DOCUMENT?" — answer: symmetric similarity (both same type), recall hit smaller than full mismatch but still measurable.

## Cross-link reminders

- 10A is foundational for 10B (RAG) and 11 (Memory).
- Pages 04-05 link forward to 10B/03 (hand-rolled RAG).
- Page 07 (In Production) references module 14 (Evaluation) for the recall@k eval setup.
