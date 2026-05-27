---
module: Detours
page: Grounding
title: Grounding — Search, Enterprise Search, and Agentic RAG
estimated_minutes: 30
icon: ☁️
prereqs: []
concepts: [google_search_tool, vertex_ai_search, enterprise_search, agentic_rag, citations, attribution, freshness, governance]
---

[← Back to: 10A_EmbeddingsVectorSearch, 10B_RAGPipeline, 17_AdvancedModels]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Grounding

> 🧭 **Optional, but read this before you build any "answer from a knowledge base" agent.** The three grounding strategies look interchangeable from outside and are wildly different in operations, cost, and answer quality. Pick the wrong one and you'll rebuild the wrong half. ~30 min.

---

## ☁️ 1. The three grounding strategies

```
                  ┌─ Google Search Grounding ─┐
   query  ──► Gemini   (built-in, public web)  ──► answer + web citations
                  └────────────────────────────┘

                  ┌─ Vertex AI Enterprise Search ─┐
   query  ──► Gemini   (managed corpus on GCS/BQ)  ──► answer + doc citations
                  └────────────────────────────────┘

                  ┌─ Agentic RAG (your pipeline) ─┐
   query  ──► retriever → reranker → Gemini       ──► answer + your citations
                  └────────────────────────────────┘
```

| strategy           | corpus                     | who owns ingestion | when it shines                          |
|--------------------|----------------------------|--------------------|-----------------------------------------|
| Google Search      | public web                 | Google             | "today's news", general factual lookup  |
| Enterprise Search  | your docs in GCS/BQ/CMS    | Vertex (managed)   | "our internal kb", "our policy docs"    |
| Agentic RAG        | your vectors anywhere      | you                | custom retrieval, hybrid search, ACLs   |

These are not mutually exclusive — production agents often combine two (Enterprise Search for primary, Google Search as fallback for current events).

---

## ☁️ 2. Google Search Grounding — `google_search` tool

The simplest. Pass the built-in tool, Gemini decides when to query, returns answer with citations to web pages.

```python
# Work/grounded_agent.py
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model="gemini-2.5-flash",
    name="researcher",
    instruction=(
        "Answer questions using up-to-date web sources. "
        "Always cite the URLs you used."
    ),
    tools=[google_search],
)
```

Gemini Live Search rephrases the user's question, runs it on Google, ingests top results, synthesizes an answer, and attaches `groundingMetadata.groundingChunks[*].web.uri` citations to the response.

**Strengths:** zero infra, current to today, broad. **Weaknesses:** can't restrict to trusted sources, results vary by region, no offline/airgap, no ACL — anything indexed by Google is in scope. **Cost model:** per-grounded-call surcharge on top of model tokens.

**Constraint:** on **Gemini 1.x** models, `google_search` cannot be combined with other tools on the same agent — the tool raises `ValueError('Google search tool cannot be used with other tools in Gemini 1.x.')`. On **Gemini 2.x**, ADK no longer raises the in-process error, but the Gemini API itself still rejects mixing built-in search with function-calling tools in a single call — set `bypass_multi_tools_limit=True` so ADK wraps the search in a sub-agent under the hood. `bypass_multi_tools_limit=True` doesn't lift the in-tool `ValueError` on Gemini 1.x — that check is unconditional. Instead, ADK's agent layer detects the flag (`llm_agent.py:149-155`) and wraps the search tool in a dedicated search sub-agent (`GoogleSearchAgentTool`) via `create_google_search_agent(model)` so it can coexist with function-calling tools. Works on both 1.x and 2.x — the Gemini API still won't accept built-in search alongside function-calling tools in a single call, so ADK delegates the search to a child agent. Source: `adk-python/src/google/adk/tools/google_search_tool.py:74-78` (the 1.x raise) and `:42` (the `bypass_multi_tools_limit` flag).

---

## ☁️ 3. Vertex AI Enterprise Search — managed corpus grounding

You hand Vertex a bucket / BigQuery dataset / Confluence connection. Vertex chunks, embeds, indexes, and exposes a search endpoint. Gemini grounds against that.

```python
# Work/enterprise_agent.py
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

search_tool = VertexAiSearchTool(
    data_store_id=(
        "projects/PROJECT/locations/global/collections/default_collection/"
        "dataStores/my-policy-docs_1234567890"
    ),
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="policy_bot",
    instruction=(
        "Answer questions about company policies using the policy data store. "
        "Quote the specific document and section."
    ),
    tools=[search_tool],
)
```

**Strengths:** Vertex handles chunking/embeddings/ranking/refresh, supports OCR for scanned PDFs, integrates with Workspace ACLs (Drive permissions respected at query time), citations point to your documents. **Weaknesses:** opinionated ranking, less control over hybrid search, latency higher than a local vector DB, GCP-only. **Cost model:** per-query + per-document indexed.

The natural choice for "make our SharePoint searchable for an agent." If you don't need exotic retrieval, this is the path of least resistance.

---

## ☁️ 4. Agentic RAG — your pipeline, your control

You implement retrieval as one or more tools, Gemini calls them like any function.

```python
# Work/rag_agent.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def search_docs(query: str, top_k: int = 5) -> list[dict]:
    """Search the internal docs index. Returns top_k chunks with metadata."""
    # your embedding lookup, hybrid (BM25 + dense), filters, ACL check
    vec = embed(query)
    hits = vector_index.search(vec, top_k=top_k, filter={"acl": current_user_groups()})
    return [
        {"text": h.text, "title": h.title, "url": h.url, "score": h.score}
        for h in hits
    ]

def rerank(query: str, chunks: list[dict]) -> list[dict]:
    """Re-rank candidates with a cross-encoder for higher precision."""
    return cross_encoder.rerank(query, chunks)[:3]

root_agent = Agent(
    model="gemini-2.5-flash",
    name="rag_agent",
    instruction=(
        "For factual questions, first call search_docs, then rerank, "
        "then answer ONLY from the returned chunks. Include url and title "
        "as citations. If chunks don't cover the question, say so."
    ),
    tools=[FunctionTool(search_docs), FunctionTool(rerank)],
)
```

**Strengths:** you own retrieval — hybrid (lexical + dense), per-tenant ACLs, custom filters, freshness SLAs, multi-corpus routing, reranking experiments. **Weaknesses:** you maintain the whole pipeline: embeddings, index, refresh, eval, monitoring. **Cost model:** your infra + embedding tokens + model tokens.

Pick this when Enterprise Search isn't flexible enough — typically when you have row-level ACLs, multi-tenant data, or want to experiment with retrieval algorithms. Module `10B_RAGPipeline` walks an end-to-end build.

---

## ☁️ 5. Citations and attribution — three different shapes

The three strategies produce three different citation formats, which matters for your UI and for grounding-faithfulness evals.

**Google Search:** attached to the response as `grounding_metadata`:

```python
async for ev in runner.run_async(...):
    if ev.grounding_metadata:
        for c in ev.grounding_metadata.grounding_chunks:
            print(c.web.uri, c.web.title)
```

Citations span ranges in the answer text — you can highlight per-sentence "this came from URL X."

**Enterprise Search:** similar `grounding_metadata`, but `c.retrieved_context.uri` points at a `gs://` or document URI in your data store. Spans also per-sentence.

**Agentic RAG:** no automatic citations — you instruct the model to include them and parse them out of the answer text. Less reliable; pair with an `after_model_callback` that checks citations against the chunks you retrieved (catches hallucinated URLs).

For high-stakes use cases (legal, medical), Enterprise Search wins on auditability — Google manages the chain of custody. Agentic RAG wins when you need answers like "and ONLY users with role X should see this."

---

## ☁️ 6. Wiring decision — the 30-second flowchart

```
  Q: Is the source the public web?
     yes ──► google_search        (on Gemini 1.x: cannot combine with other tools; on 2.x: ADK no longer raises, but the Gemini API still rejects mixing built-in search with function-calling tools in a single call — set `bypass_multi_tools_limit=True` so ADK wraps the search in a sub-agent under the hood)
     no  ──► continue

  Q: Are docs in GCS / BigQuery / Drive / SharePoint, with standard ACLs?
     yes ──► VertexAiSearchTool   (data store on those sources)
     no  ──► continue

  Q: Do you need hybrid search, custom ranking, row-level filters, or non-GCS sources?
     yes ──► Agentic RAG (your FunctionTools)
     no  ──► reconsider Enterprise Search; it's almost always cheaper to operate.
```

Modules that ground out from this detour:

- **10A_EmbeddingsVectorSearch** — internals of dense retrieval that underpins Agentic RAG.
- **10B_RAGPipeline** — end-to-end Agentic RAG build.
- **17_AdvancedModels** — when to swap models (Pro for synthesis, Flash for retrieval); model affects all three strategies.

---

## ☁️ 7. Combining strategies

Real production agents often run two:

```python
from google.adk.agents import Agent, SequentialAgent

primary = Agent(
    model="gemini-2.5-flash",
    name="kb_first",
    instruction="Try Enterprise Search first.",
    tools=[VertexAiSearchTool(data_store_id="...")],
    output_key="kb_answer",
)

fallback = Agent(
    model="gemini-2.5-flash",
    name="web_fallback",
    instruction=(
        "If {kb_answer} says it could not answer, use google_search. "
        "Otherwise return {kb_answer} unchanged."
    ),
    tools=[google_search],
)

root_agent = SequentialAgent(name="grounded", sub_agents=[primary, fallback])
```

This pattern (KB-first, web-fallback) is one of the most common shapes in production agent systems. Pin a budget on the fallback (max one search) or your bill will surprise you.

> **🚀 In Production**
>
> Hallucination rate is roughly proportional to how much the model has to "fill in" gaps in retrieved context. Always (a) instruct strict grounding ("answer ONLY from sources"), (b) run a grounding-faithfulness eval (see `14_Evaluation/04_HallucinationsV1`), (c) display the citations in the UI so users can verify. Without all three, your "grounded" agent confidently hallucinates.

---

## 🌐 8. Freshness, governance, latency — the operational lens

| dimension     | Google Search          | Enterprise Search          | Agentic RAG                |
|---------------|------------------------|----------------------------|----------------------------|
| Freshness     | seconds (Google index) | minutes-hours (refresh job)| your choice (push-on-edit OK) |
| Governance    | none — public web      | Workspace ACL pass-through | yours — granular per row   |
| Latency       | +1-2 s (search call)   | +0.5-1 s                   | depends on your index      |
| Airgap        | no                     | no                         | yes                        |
| Audit log     | minimal                | Vertex audit log           | yours                      |
| Eval surface  | hard — moving corpus   | medium                     | easy — frozen index per eval set |

For regulated industries: **agentic RAG is usually the only option** because you need provable ACLs and reproducible eval against a frozen corpus.

---

## 🛠 Have the student try

Build three tiny agents over the same question and compare.

**Question:** "What is the current population of Tokyo?"

```python
# Variant 1: google_search
from google.adk.agents import Agent
from google.adk.tools import google_search

agent_a = Agent(model="gemini-2.5-flash", name="a", tools=[google_search],
                instruction="Cite the URL.")

# Variant 2: Enterprise Search — pre-create a data store with a few Wikipedia
# dumps about Japan cities, point at it
from google.adk.tools import VertexAiSearchTool
agent_b = Agent(model="gemini-2.5-flash", name="b",
                tools=[VertexAiSearchTool(data_store_id="...")],
                instruction="Cite the source document.")

# Variant 3: Agentic RAG — your own retriever (could be a stub returning a fixed snippet)
def lookup(q: str) -> list[dict]:
    return [{"text": "Tokyo population: 13.96M (2024 estimate).",
             "url": "https://example.com/tokyo.html"}]
from google.adk.tools import FunctionTool
agent_c = Agent(model="gemini-2.5-flash", name="c", tools=[FunctionTool(lookup)],
                instruction="Answer ONLY from lookup() output. Cite the url.")
```

Observe:

1. Variant A: live web answer, multiple citations, latency ~2 s.
2. Variant B: answer from your indexed corpus, latency ~1 s.
3. Variant C: deterministic answer keyed to the stub, latency <500 ms.

Now flip the question to "What is the population of Tokyo in 1750?" and watch each agent's behavior — A retrieves a paper, B says "not in corpus" if your dump didn't cover it, C confidently parrots the stub. The right answer depends on what "grounding" should mean for your product.

---

[← Back to: 10A_EmbeddingsVectorSearch](../10A_EmbeddingsVectorSearch/00_Overview.md) · [Back to: 10B_RAGPipeline](../10B_RAGPipeline/00_Overview.md) · [Back to: 17_AdvancedModels](../17_AdvancedModels/00_Overview.md)  [↑ Map](../../MAP.md)

**When you're done:** return to whichever module sent you. 10A/10B continue with the retrieval internals; 17 covers the model-side of grounding (which models to use for synthesis vs retrieval).
