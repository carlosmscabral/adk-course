---
module: 20_FrameworkComparison
page: 02_LangChainAndLangGraph
title: LangChain & LangGraph
estimated_minutes: 25
prereqs: [20_FrameworkComparison/01]
concepts: [LangChain, LangGraph, StateGraph, chains]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/01_TheLandscape]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/03_CrewAI →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 02 LangChain & LangGraph

# 🧠 LangChain & LangGraph

**LangChain** is the OG agent-adjacent library (2022). **LangGraph** (2024) is the same team's "do orchestration properly" sequel built on top.

## LangChain in one paragraph

A toolbox: model wrappers (`ChatOpenAI`, `ChatAnthropic`, …), prompt templates, output parsers, retrievers, the `@tool` decorator, memory adapters, chains (`LCEL` — LangChain Expression Language). The agent pattern is mostly **the deprecated `AgentExecutor`** plus `create_react_agent` / `create_openai_tools_agent`. Mature for retrieval, integrations, and tool wrapping.

## LangGraph in one paragraph

A state-machine orchestrator. You define a **graph of nodes** (each a Python fn or LLM call) and **edges** (conditional or unconditional). Shared state is a typed pydantic-or-typeddict object that nodes return partial updates for. Multi-agent = nodes that each wrap an LLM call. Built on LangChain primitives, but conceptually replaces `AgentExecutor`.

## Hello-world snippet (LangGraph)

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class State(TypedDict):
    question: str
    answer: str

def think(state: State) -> dict:
    llm = ChatOpenAI(model="gpt-4o")
    return {"answer": llm.invoke(state["question"]).content}

graph = StateGraph(State)
graph.add_node("think", think)
graph.set_entry_point("think")
graph.add_edge("think", END)
app = graph.compile()

print(app.invoke({"question": "What is 7*8?"}))
```

## Tools in LangChain

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two ints."""
    return a + b

# bind to a chat model
model = ChatOpenAI(model="gpt-4o").bind_tools([add])
```

The `@tool` decorator generates a JSON-schema description from the function signature + docstring — **same idea as ADK's `FunctionTool`**, slightly different shape.

## Multi-agent in LangGraph

Two patterns:

1. **Supervisor**: one "router" node decides which sub-agent node runs next.
2. **Network/swarm**: nodes can hand off to each other via shared state flags.

The official prebuilt is `langgraph.prebuilt.create_react_agent` and the `langgraph-supervisor` library.

## Where ADK beats LangGraph

- **MCP first-class** (LangGraph has community adapters; ADK has built-in `MCPToolset`).
- **A2A protocol** (LangGraph has none).
- **GCP integration** (Vertex AI, BigQuery, Cloud Run — native in ADK).
- **Graph workflows feel more first-class in ADK 2.0** (Workflow nodes have first-party retry, parallel, dynamic scheduling; LangGraph leaves more to the user).
- **Evals built in** (ADK ships `AgentEvaluator`; LangGraph delegates to LangSmith).
- **Code execution sandboxes** — ADK has 5 (Container, Vertex, GKE, Engine, Unsafe Local); LangGraph has none built in.

## Where LangGraph beats ADK

- **Ecosystem breadth.** LangChain has hundreds of integrations (vector DBs, document loaders, retrievers) that LangGraph inherits. ADK has fewer.
- **Cloud neutrality.** LangGraph is Cloud-agnostic by design. ADK is GCP-first.
- **Community & content.** Tutorials, courses, books — LangChain/LangGraph have a multi-year head start.
- **LangSmith** for tracing/evals is more mature than ADK's OTel integration, and arguably easier to onboard.

> 🚀 **In Production**
>
> LangChain churns. Treat any LangChain/LangGraph code older than 6 months with suspicion — the imports may have moved (`langchain` → `langchain_core` → `langchain_community` etc.). Pin versions aggressively.

> 🛠 **Have the student run:** read [LangGraph's "multi-agent collaboration" guide](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/) (if accessible) and compare its supervisor-pattern code to ADK's `Workflow` + sub_agents. The mental model overlap is high; the API ceremony differs.

> ❓ **Ask the student:** "If you had to migrate an ADK Workflow to LangGraph in a day, what would you change first?" *(Answer: replace `sub_agents` with `StateGraph` nodes + a typed State dict, port tools to `@tool`, replace `MCPToolset` with LangChain MCP adapters.)*

[← Prev: 20_FrameworkComparison/01_TheLandscape]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/03_CrewAI →]
