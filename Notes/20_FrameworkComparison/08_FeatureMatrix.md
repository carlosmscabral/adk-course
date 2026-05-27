---
module: 20_FrameworkComparison
page: 08_FeatureMatrix
title: The big feature matrix
estimated_minutes: 20
prereqs: [20_FrameworkComparison/07]
concepts: [feature-matrix, comparison]
icon: 🗺
in_production: true
---

[← Prev: 20_FrameworkComparison/07_LettaMemGPT]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/09_ChoosingAFramework →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 08 Feature Matrix

# 🗺 The big matrix

`★★★` first-class · `★★` supported · `★` minimal · `-` absent · `~` complicated

| Feature | ADK 2.0 | LangGraph | CrewAI | AutoGen / AG2 | OAI Agents | Pydantic AI | Letta |
|---|---|---|---|---|---|---|---|
| **Multi-agent** | ★★★ (sub_agents + Workflow) | ★★★ (StateGraph) | ★★★ (Crew) | ★★★ (group chat) | ★★ (handoffs) | ★ (tools only) | ★★ (multi but single-first) |
| **Graph workflows** | ★★★ | ★★★ | - | ★ (Selector) | - | - | - |
| **Sequential / linear pipeline** | ★★★ (SequentialAgent) | ★★ | ★★★ | ★★ | ★★ | ★ | - |
| **Tools (function schema)** | ★★★ | ★★★ | ★★ | ★★ | ★★ | ★★★ | ★★ |
| **MCP** | ★★★ (MCPToolset) | ★★ (community) | ★★ (community) | ★★ (community) | ★★ | ★ | ★ |
| **A2A protocol** | ★★★ (to_a2a, RemoteA2aAgent) | - | - | - | - | - | - |
| **Streaming text** | ★★★ | ★★ | ★ | ★★ | ★★ | ★★ | ★★ |
| **Bidi voice/video (Live)** | ★★★ (Gemini Live) | - | - | - | - | - | - |
| **Persistent state / sessions** | ★★★ (4 services) | ★★ (checkpointer) | ★ (memory plugin) | ★ | ★ (Responses thread) | ★ (deps) | ★★★ |
| **Long-term memory** | ★★★ (Vertex Memory Bank, RAG) | ★★ | ★ | ★ | ★ | - | ★★★ |
| **Evals built-in** | ★★★ (AgentEvaluator, EvalSet, judges) | ★★ (LangSmith ecosystem) | ★ | ★ | ★ | ★ | ★ |
| **Observability / OTel** | ★★★ (telemetry/) | ★★ (LangSmith) | ★ | ★ | ★ | ★ | ★ |
| **Code execution sandbox** | ★★★ (5 executors) | ~ (DIY) | ★ | ★★ (Docker exec) | ★ (Code Interpreter) | - | - |
| **Vendor neutrality (LLMs)** | ★★★ (Gemini/Claude/Gemma/LiteLLM/OpenAI/Apigee) | ★★★ | ★★★ | ★★★ | ★ (OAI-first) | ★★ | ★★ |
| **Provider lock-in risk** | ★★ (GCP-friendly) | ★ (low) | ★ (low) | ★ (low) | ★★★ (high) | ★ (low) | ★★ (Letta backend) |
| **Plugins / cross-cutting hooks** | ★★★ (Plugin base) | ★★ (callbacks) | ★★ | ★★ | ★ (guardrails) | ★ | ★ |
| **Skills / capability packaging** | ★★★ (Skills feature, new in 2.0) | ★ | ★ | - | - | - | - |
| **CLI tooling** | ★★★ (`adk run/eval/web/create/deploy`) | ★★ (langgraph CLI) | ★ | ★ | - | ★ | ★★ |
| **Visual builder** | ★★ (ADK Visual Builder, new) | ★★ (LangGraph Studio) | - | - | - | - | - |
| **License** | Apache 2.0 | MIT | MIT | Apache 2.0 (AG2) / MIT (autogen-core) | MIT | MIT | Apache 2.0 |
| **GA maturity (May 2026)** | 2.0 GA (May 2026) | stable, frequent minor | stable | split (AG2 vs core) | stable | stable | stable |

## How to read the matrix

A row with `★★★` for ADK and `-` for others is a **moat** (e.g., A2A, Live, Skills). A row where ADK is `★★` and competitors are `★★★` is a **trade-off** (e.g., vendor neutrality: ADK works with many providers but is GCP-friendly).

## The honest summary

- **If you score "multi-agent + workflows + MCP + A2A + GCP + evals + observability"**, ADK wins decisively.
- **If you score "portability + ecosystem + content + tutorials"**, LangChain/LangGraph win.
- **If you score "fastest TTRA (time to running agent)"**, CrewAI or OAI Agents win.
- **If you score "long-term memory above all"**, Letta wins.
- **If you score "typed output rigor"**, Pydantic AI wins.

> 🚀 **In Production**
>
> A matrix freezes a moment. The shape of these frameworks changes month-to-month. Treat this as **a snapshot for orientation**, not a contract. Before betting a project, re-verify the rows that matter to you.

> 🛠 **Have the student run:** pick the 3 rows most relevant to their current project. Rank the top 3 frameworks by those rows only. See if the ranking matches their gut.

[← Prev: 20_FrameworkComparison/07_LettaMemGPT]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/09_ChoosingAFramework →]
