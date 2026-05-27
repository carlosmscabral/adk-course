---
module: 20_FrameworkComparison
page: 01_TheLandscape
title: The landscape — one-page overview
estimated_minutes: 15
prereqs: [20_FrameworkComparison/00]
concepts: [framework-axes, multi-agent-styles]
icon: 🗺
in_production: false
---

[← Prev: 20_FrameworkComparison/00_Overview]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/02_LangChainAndLangGraph →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 01 The Landscape

# 🗺 The landscape

Open `_figures/landscape.txt` next to this page.

## The 7 axes I score frameworks on

1. **Multi-agent style.** How do agents collaborate? Role-based (CrewAI), chat-based (AutoGen), graph (LangGraph/ADK), handoff (OpenAI Agents).
2. **Tool model.** Function-schema (most), MCP (ADK first-class, others via adapter), provider-native (OAI tool-use, Gemini function-calling).
3. **Memory.** Stateless-by-default (LangChain) vs persistent-by-default (Letta) vs pluggable services (ADK).
4. **Observability.** Logs, traces, OpenTelemetry, managed (Vertex AI Agent Engine, AgentOps).
5. **Code execution.** Sandbox availability (ADK has 5 executor types; most others have one or none).
6. **Vendor neutrality.** Number of LLM providers supported out of the box.
7. **Maturity / GA.** Cadence of breaking changes, GitHub responsiveness.

## The framework-by-framework executive summary

| | One-line description |
|---|---|
| **ADK** | Google's batteries-included agent runtime. Graph + tree multi-agent, MCP, A2A, GCP-native. |
| **LangGraph** | State-graph orchestrator on top of LangChain's tool/integration ecosystem. The most portable graph. |
| **LangChain** | The original "chain" library. Still huge ecosystem, but most multi-agent work has moved to LangGraph. |
| **CrewAI** | Role-based "team of agents" with task scheduling. Lowest floor for non-engineers. |
| **AutoGen** | Conversational multi-agent (chat among models). Microsoft Research lineage. The AG2 community fork is the active one in 2026. |
| **OpenAI Agents SDK** | OAI's slim agent surface (Agents, Tools, Handoffs, Guardrails). Tight, OpenAI-shaped, narrow scope. |
| **Pydantic AI** | Strongly-typed structured-output-first. Pydantic-native. Excellent for "LLM as typed function." |
| **Letta / MemGPT** | Memory-first agent runtime (paper-pedigree). Hierarchical memory hot/cold tiers. |

## What the matrix shows

The ASCII matrix in the figure file ranks each framework on each axis (`★★★` = first-class, `-` = absent). A summary in words:

- **ADK wins on**: GCP integration, MCP-first, A2A, evals, code-exec variety.
- **LangGraph wins on**: portability, integration breadth, smoothest pure-Python state-graph.
- **CrewAI wins on**: time-to-first-running-agent for prompt engineers.
- **AutoGen wins on**: conversational research workflows (the chat metaphor).
- **OpenAI Agents wins on**: simplicity if you're all-in on OpenAI.
- **Pydantic AI wins on**: typed output rigor.
- **Letta wins on**: long-horizon memory.

## What the matrix HIDES

- **Documentation quality.** Roughly: ADK > LangGraph > Pydantic AI > OAI Agents > AutoGen > CrewAI > Letta.
- **Community size.** Roughly: LangChain > AutoGen > CrewAI > ADK > OAI Agents > Pydantic AI > Letta.
- **Breaking-change frequency.** Roughly the inverse of doc quality.

> ❓ **Ask the student:** "Which axis matters most for *your* current project — and why?" *(There's no right answer; this is the entry to the rest of the module.)*

> 🛠 **Have the student run:** scan the matrix in `_figures/landscape.txt`. Pick one row (their highest priority axis) and predict which framework wins it before reading on.

[← Prev: 20_FrameworkComparison/00_Overview]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/02_LangChainAndLangGraph →]
