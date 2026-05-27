---
module: 10B_RAGPipeline
page: 05_RAGIntoADK
title: 🛠 Wiring RAG into an ADK agent
estimated_minutes: 30
prereqs: [10B_RAGPipeline/04, 03_Tools/05]
concepts: [VertexAiRagRetrieval, FunctionTool, VertexAiRagMemoryService, load_memory]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/04_VertexAIRAGEngine] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/06_DissectingRAGSample →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 05 RAG into ADK

---

## 🛠 Two integration paths

| Path | Retrieval is... | When |
|---|---|---|
| (a) **`FunctionTool` wrapper** | An explicit tool the LLM calls | You want fine control; multi-corpus; conditional retrieve |
| (b) **`VertexAiRagMemoryService`** | Automatic — the runner injects relevant chunks | You want "just always retrieve context" |

You pick per agent. (a) is more common; (b) shines for chat agents with long-running context.

## ☁️ Path (a) — managed `VertexAiRagRetrieval`

ADK ships a first-class tool that wraps the RAG Engine query:

```python
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

ask_docs = VertexAiRagRetrieval(
    name="ask_docs",
    description="Search the Python docs corpus. Use for any Python language question.",
    rag_resources=[rag.RagResource(rag_corpus="projects/.../ragCorpora/...")],
    similarity_top_k=5,
    vector_distance_threshold=0.6,
)

agent = Agent(
    model="gemini-2.5-flash",
    name="docs_agent",
    instruction="Answer Python questions using ask_docs. Cite chunk IDs.",
    tools=[ask_docs],
)
```

**This is what the canonical RAG sample uses.** Dissected in page 06.

## 🛠 Path (a, alt) — your own `FunctionTool`

If you're on raw Vector Search (page 03 style), wrap your retriever yourself:

```python
from google.adk.tools import FunctionTool, ToolContext

def search_corpus(query: str, tool_context: ToolContext) -> dict:
    """Search the corpus for relevant chunks.

    Args:
        query: the user's natural-language question.

    Returns:
        dict with 'chunks' (list of {id, score, text}).
    """
    hits = retrieve(endpoint, deployed_id, query, side_store, k=5)
    return {"chunks": hits}

search_tool = FunctionTool(search_corpus)

agent = Agent(
    model="gemini-2.5-flash",
    name="docs_agent",
    instruction="Use search_corpus for any factual question. Cite chunk IDs.",
    tools=[search_tool],
)
```

The agent loop:

1. User asks a question.
2. LLM picks `search_corpus`, passes the query.
3. Your tool runs retrieve, returns `{chunks: [...]}`.
4. LLM gets the chunks as the tool result, writes a cited answer.

You control everything — re-ranking, hybrid retrieval, query rewriting can all be added inside the tool body.

## ☁️ Path (b) — `VertexAiRagMemoryService`

Memory services in ADK are **automatically consulted** by the runner — no explicit tool call needed. `VertexAiRagMemoryService` uses a RAG corpus as long-term memory.

```python
from google.adk.memory import VertexAiRagMemoryService
from google.adk.runners import Runner

memory_service = VertexAiRagMemoryService(
    rag_corpus="projects/.../ragCorpora/...",
    similarity_top_k=5,
)

runner = Runner(
    app_name="docs_app",
    agent=agent,
    memory_service=memory_service,
)
```

Now the runner pulls relevant chunks from the corpus into the prompt automatically. The agent doesn't need a search tool at all — but it also has less control over WHEN retrieval happens.

> 🧭 **Detour suggestion**
> Memory services are covered in depth in [11_Memory](../11_Memory/00_Overview.md). If you want to use `VertexAiRagMemoryService` seriously, finish 10B first (pipeline mechanics), then go to 11.

## ⚠️ The hybrid mistake

Don't wire **both** `VertexAiRagMemoryService` AND `VertexAiRagRetrieval` (or a FunctionTool that retrieves) pointing at the same corpus. You'll inject the same chunks twice — once from memory, once from the tool result — burning context and confusing the LLM. Pick one.

## 🚀 In Production

> **🚀 In Production**
> For most production RAG agents, path (a) with `VertexAiRagRetrieval` is the right pick. Path (b) is great for assistant-style apps where retrieval should always happen. Either way, log every retrieved chunk ID + final answer so you can debug "why did the model say X?" later.

## ❓ Check

> ❓ **Ask the student:** "Why is `VertexAiRagRetrieval` a tool the LLM can choose to call, rather than always-on?"
>
> Expected: chatty queries ("hi", "thanks") don't need retrieval — wasted call + wasted tokens. Making retrieval a tool lets the LLM decide. The sample's prompt (`prompts.py`) explicitly tells it: "if the user is just chatting, don't use the retrieval tool."

## 🛠 Have the student run

> 🛠 Wrap their page-03 hand-rolled retrieve in a `FunctionTool` and put it on an `Agent`. Have them chat with the agent and confirm it picks up the tool for factual questions and skips it for greetings. Then ALSO have them try the `VertexAiRagRetrieval` path with the same corpus.

## 🤖 Tutor

> Show both paths. Don't bias the student. The pick is project-dependent; what matters is they recognize when each shines.

---

[← Prev: 10B_RAGPipeline/04_VertexAIRAGEngine] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/06_DissectingRAGSample →]
