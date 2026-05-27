---
module: 03_Tools
page: 07_ToolLimitations
title: Tool limitations — single-instance & mutually-exclusive constraints
estimated_minutes: 15
prereqs: [03_Tools/05, 03_Tools/06]
concepts: [tool-constraints, single-instance, bypass_multi_tools_limit, McpToolset-gotchas]
icon: ⚠️
in_production: true
detours_suggested: []
---

[← Prev: 03_Tools/06_ComputerUse](06_ComputerUse.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/08_AgentToolPreview →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 07 Tool limitations

# ⚠️ Tool limitations — the things `tools=[…]` won't let you do

Not every tool is composable. A few built-ins and toolsets reserve the **entire** tool slot of an agent. Pile them on top of others and you get a runtime error — or worse, silent misbehavior. Learn the list now so you don't burn 30 minutes debugging a one-line constraint.

## ⚠️ The "one-tool-only" club

Three real constraints in ADK 2.0 source:

### 1. `google_search` on Gemini 1.x

```python
# from adk-python/src/google/adk/tools/google_search_tool.py
if is_gemini_1_model(llm_request.model):
    if llm_request.config.tools:
        raise ValueError(
            'Google search tool cannot be used with other tools in Gemini 1.x.'
        )
```

On Gemini 2.x it composes fine. On Gemini 1.x — sole tool only. Same for `VertexAiSearchTool`. Both ship a `bypass_multi_tools_limit=False` kwarg as an escape hatch you almost never need.

### 2. `EnterpriseWebSearchTool` — same rule

```python
# from adk-python/src/google/adk/tools/enterprise_search_tool.py
'Enterprise Web Search tool cannot be used with other tools in ...'
```

Plan accordingly: if you want enterprise search + your own tools, split into sub-agents and use `transfer_to_agent` / `AgentTool` (Module 05).

### 3. Vertex AI RAG retrieval — recommended single-tool pattern

`VertexAiRagRetrieval` (the Vertex AI RAG **Engine** managed-retrieval tool) is a model-side grounding tool. Unlike `google_search` / `EnterpriseWebSearchTool` / `VertexAiSearchTool`, **ADK 2.0 ships no runtime guard** for it — `vertex_ai_rag_retrieval.py` has no `raise ValueError(...)` on tool composition. But on Gemini 2.x the tool injects a `types.Retrieval(vertex_rag_store=...)` config into `llm_request.config.tools`, which can collide with other model-side grounding tools and confuse the planner. **Treat "RAG-as-sole-tool on its agent" as the recommended pattern**, not a hard constraint: wrap it in a dedicated sub-agent, then expose that sub-agent to your coordinator via `AgentTool`.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.retrieval import VertexAiRagRetrieval

# Sub-agent: RAG-only (its single tool)
rag_agent = LlmAgent(
    name="rag",
    model="gemini-2.5-flash",
    instruction="Answer using the retrieved passages.",
    tools=[VertexAiRagRetrieval(
        name="corpus_retrieval",
        description="Searches the configured Vertex AI RAG corpora for relevant passages.",
        rag_corpora=["projects/.../ragCorpora/123"],
    )],
)

# Coordinator: composes RAG-as-tool alongside whatever else
coordinator = LlmAgent(
    name="root",
    model="gemini-2.5-flash",
    instruction="Use the `rag` tool for company-doc questions; otherwise answer directly.",
    tools=[AgentTool(agent=rag_agent), my_other_tool],   # legal — RAG is one level down
)
```

This is exactly the pattern `adk-samples/python/agents/RAG/` uses.

## ⚠️ `McpToolset` gotchas

`McpToolset` is composable — you can run two of them, plus FunctionTools, plus AgentTools. But:

* **Connection lifecycle.** The toolset holds an open transport (stdio or SSE). If your server crashes mid-conversation, tools 404 silently and the LLM hallucinates results. Wrap it in a callback that pings the server before tool dispatch.
* **Discovery on init.** Tools are listed at startup. If the server adds a tool later, the agent doesn't see it until you rebuild the toolset (or call `await toolset.reload()` where supported).
* **Tool-name collisions.** Two MCP servers exposing `search` will collide. Pass `tool_filter=` or namespace via a `tool_name_prefix` if your server supports it. Module 08 covers both.

## ⚠️ Practical tool-count limits

There's no hard cap on `tools=[…]`, but Gemini's tool-selection accuracy degrades sharply past **~15-20 tools**. Symptoms: the model calls the wrong tool, hallucinates a tool name, or asks the user to disambiguate.

Mitigations (in order of leverage):

1. **Split into sub-agents** (Module 05). Each gets ≤10 tools.
2. **Use `transfer_to_agent`** for explicit routing.
3. **Use a coordinator + `AgentTool`** wrappers — the coordinator picks a sub-agent (short list), the sub-agent picks a tool (short list).
4. **Last resort**: dynamic tool filtering via `tool_filter` on toolsets, or per-turn `before_model_callback` that prunes irrelevant tools.

## 🧠 How to discover a new limitation

You'll meet new ones as ADK ships new built-ins. Three places to look:

1. **The docs page** for that tool at https://adk.dev/ — limitations are usually under a "Constraints" or "Caveats" subheading.
2. **The runtime error.** ADK raises `ValueError(...)` with the exact rule (see the `google_search_tool.py` snippet above). Read the message; don't `except Exception: pass`.
3. **The source.** `grep -rn "cannot be used with\|sole tool\|must be the only" adk-python/src/google/adk/tools/` surfaces the current list in <1 second. The truth lives here, not in your blog post from last year.

> **🚀 In Production**
>
> When you stack a forbidden tool combo, the failure mode is **whichever request hits production first**. Catch it in CI: write a startup smoke test that instantiates the agent and runs a no-op turn (e.g., `"hello"`). If the configuration is illegal, the `ValueError` fires immediately — long before your first real user.

> ❓ **Ask the student:** you want an agent that does both BigQuery analytics AND Vertex AI RAG over the same docs corpus. Should you put both tools on one agent?
> *(Expected: not recommended — `VertexAiRagRetrieval` injects a model-side grounding config that collides poorly with other model-side tools, so the safe pattern is: RAG sub-agent and BigQuery sub-agent, wired into a coordinator via `AgentTool`, route in the coordinator's instruction. ADK 2.0 won't raise — but the planner will misbehave under load.)*

> 🛠 **Have the student do this:** run `grep -rn "cannot be used with\|sole tool\|bypass_multi_tools_limit" /home/carloscabral/study/adk-python/src/google/adk/tools/` and read every match. Three to five hits is the current list of "one-tool" constraints. This grep is your living source of truth.

> 🤖 **Tutor:** if the student asks "what about my MCP server's auth tokens timing out mid-session?" — that's a real Module 08 topic. Note it on the parking lot and keep moving.

---

[← Prev: 03_Tools/06_ComputerUse](06_ComputerUse.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/08_AgentToolPreview →]
