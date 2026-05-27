---
module: 10B_RAGPipeline
page: 06_DissectingRAGSample
title: 🔎 Dissecting the RAG sample — line by line
estimated_minutes: 40
prereqs: [10B_RAGPipeline/05]
concepts: [sample-walkthrough, VertexAiRagRetrieval, prepare_corpus_and_data, citation-prompt]
icon: 🔎
in_production: false
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/05_RAGIntoADK] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/07_InProduction →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 06 Dissecting the RAG sample

---

## 🔎 What we're reading

Real files. Open each one and follow along:

```
/home/carloscabral/study/adk-samples/python/agents/RAG/
├── rag/
│   ├── agent.py                                       # 77 lines — the agent
│   ├── prompts.py                                     # citation instructions
│   ├── shared_libraries/
│   │   └── prepare_corpus_and_data.py                 # one-time setup
│   ├── app_utils/                                     # deploy + telemetry
│   ├── tracing.py
│   └── agent_engine_app.py
├── eval/
├── deployment/
└── tests/
```

The sample is a thin agent over `VertexAiRagRetrieval` + a one-shot setup script that builds a corpus from a single PDF (Alphabet's 10-K).

## 🔎 Trace the 7-stage loop through the sample

| Stage (from page 01) | Where in the sample |
|---|---|
| 1. Ingest | `prepare_corpus_and_data.py:86-97` — `download_pdf_from_url` |
| 2. Chunk | inside `rag.upload_file(...)` at `:104` — server-side |
| 3. Embed | inside `rag.upload_file` — uses corpus's `text-embedding-004` |
| 4. Store | inside `rag.upload_file` — managed `RagCorpus` |
| 5. Retrieve | `agent.py:47-62` — `VertexAiRagRetrieval` |
| 6. Augment | implicit — the tool result is in the LLM's context |
| 7. Generate | `agent.py:66-71` — the `Agent` itself, with `prompts.py` |

**Stages 2-4 collapse into one server-side call.** That's the managed shortcut.

## 🔎 `agent.py` walkthrough

```python
# lines 22-26 — imports
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from openinference.instrumentation import using_session
from vertexai.preview import rag
```

`VertexAiRagRetrieval` is the ADK wrapper around RAG Engine. `openinference` is Arize tracing — covered in module 15 (Observability).

```python
# lines 34-37 — GCP init
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-east1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
```

Note `us-east1` — RAG Engine has region constraints. Use what your corpus uses.

```python
# lines 45-63 — conditional tool wiring
rag_corpus = os.environ.get("RAG_CORPUS")
if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description=...,
        rag_resources=[rag.RagResource(rag_corpus=rag_corpus)],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)
```

If `RAG_CORPUS` env var is unset, the agent starts with **no retrieval tool**. This is a smart degradation pattern — agent still runs, just without docs. The setup script (below) writes the env var when the corpus is ready.

```python
# lines 66-71 — the agent
root_agent = Agent(
    model="gemini-2.5-flash",
    name="ask_rag_agent",
    instruction=return_instructions_root(),
    tools=tools,
)
```

`gemini-2.5-flash` — same default we recommend. Cheap + fast + capable enough for cited Q&A.

## 🔎 `prompts.py` — the citation discipline

The interesting block (lines 22-64):

> "Citation Format Instructions: When you provide an answer, you must also add one or more citations at the end of your answer... Use the retrieved chunk's `title` to reconstruct the reference..."

This is **why citations work in this sample**: the prompt is explicit and pedantic about format. The model doesn't volunteer citations — you ask, repeatedly. Adopt this pattern.

It also says: *"If you believe the user is just chatting and having casual conversation, don't use the retrieval tool."* This is the "tool selection discipline" we promised in page 05. The LLM is told when NOT to retrieve.

## 🔎 `prepare_corpus_and_data.py` walkthrough

The 3 functions worth reading carefully:

```python
# create_or_get_corpus  (lines 62-83)
def create_or_get_corpus():
    """Creates a new corpus or retrieves an existing one."""
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )
    existing_corpora = rag.list_corpora()
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            return existing_corpus
    return rag.create_corpus(...)
```

Idempotency by display-name lookup. Same pattern we used in 10A/04 for raw indexes. **Always do this.** Forgetting = N orphan corpora next time you run the script.

```python
# upload_pdf_to_corpus  (lines 100-124)
def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
    try:
        rag_file = rag.upload_file(...)
        return rag_file
    except ResourceExhausted as e:
        print(f"Error uploading file {display_name}: {e}")
        print("This is common for new Google Cloud projects.")
        print("Please see the 'Troubleshooting' section in the README.md...")
        return None
```

Explicit `ResourceExhausted` catch. Embedding-quota errors are common on new projects; the script *teaches* the user to fix it. Mirror this.

```python
# update_env_file  (lines 127-133)
def update_env_file(corpus_name, env_file_path):
    set_key(env_file_path, "RAG_CORPUS", corpus_name)
```

The bridge — the setup script writes `RAG_CORPUS=...` into `.env`, which the agent reads at startup. Clean separation between "build the corpus" and "use it."

## ⚠️ What this sample skips (your homework)

- **No re-embedding strategy** when the model changes. The corpus is locked to `text-embedding-004`.
- **No metadata filtering** — every chunk is global.
- **No eval** — recall isn't measured. We fix this in module 14.
- **No query rewriting** — the user's literal text is embedded. For ambiguous queries this misses.
- **No re-ranking** — top-10 chunks go straight in. A cross-encoder re-ranker would lift precision.

These are the items on the next-level RAG checklist. See `07_InProduction`.

> **🔍 Dissecting (secondary)**: `multiformat-hybrid-rag` — for the patterns this sample skips, study `/home/carloscabral/study/adk-samples/python/agents/multiformat-hybrid-rag/` next. It ships **hybrid retrieval** (semantic + BM25 fused via Reciprocal Rank Fusion on Vector Search 2.0), **multi-format ingestion** (PDF via Gemini multimodal, Office docs via LibreOffice, HTML/JSON/MD), **contextual chunking** (Gemini-generated per-chunk context prepended before embedding), and serves three interfaces (ADK chat, REST search, MCP server) from one Cloud Run service. Focus on `data_ingestion_pipeline/` for the ingest shape and `architecture.md` for the design rationale.

## ❓ Check

> ❓ **Ask the student:** "What single environment variable controls whether this sample becomes a useful agent vs a fallback chatbot?"
>
> Expected: `RAG_CORPUS`. Look at `agent.py:45-63` — the entire tool registration is gated on it.

## 🛠 Have the student run

> 🛠 If they have a billable project: actually run `prepare_corpus_and_data.py` (it takes ~5 min for the 10-K PDF), then `adk run` the agent and ask "What was Alphabet's 2025 revenue?". Trace the event stream — the tool call, the chunks returned, the cited answer.

## 🤖 Tutor

> The student should now be able to look at any RAG sample in the repo and trace the 7-stage loop. This is the actual exit skill of module 10B. The drill (page 09) tests it on their own data.

---

[← Prev: 10B_RAGPipeline/05_RAGIntoADK] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/07_InProduction →]
