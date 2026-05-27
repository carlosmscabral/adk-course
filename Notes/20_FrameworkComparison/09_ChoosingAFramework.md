---
module: 20_FrameworkComparison
page: 09_ChoosingAFramework
title: Choosing a framework — decision flowchart
estimated_minutes: 20
prereqs: [20_FrameworkComparison/08]
concepts: [decision-making, trade-offs]
icon: 🚀
in_production: true
---

[← Prev: 20_FrameworkComparison/08_FeatureMatrix]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/10_DissectingSample →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 09 Choosing a Framework

# 🚀 Choosing a framework

See `_figures/decision_flowchart.txt` for the ASCII flowchart.

## The 5 questions, in order

### 1. Where will this run?

- **Google Cloud** (Vertex AI, BigQuery, GKE, Agent Engine): **ADK** is the obvious fit. The GCP integrations (BigQuery analytics, Vertex Memory Bank, Vertex AI Code Executor, Agent Engine deployment) are first-party.
- **AWS / Azure / hybrid**: tossup between **ADK** (still works fine — it's just Python + HTTPS) and **LangGraph** (most portable state-graph). Choose by your team's familiarity.
- **On-prem / air-gapped / regulated**: **LangGraph** with self-hosted models is the safest. ADK works but you'll re-build the GCP-shaped pieces.

### 2. What's the multi-agent style?

- **Graph / fan-out / fan-in**: **ADK Workflow** or **LangGraph StateGraph**. (ADK has the additional advantage of treating an LlmAgent and a Workflow as the same primitive.)
- **Role-based "team of personas"**: **CrewAI** — lowest floor for prompt-engineer teams.
- **Conversational ("agents chat with each other")**: **AutoGen / AG2** — that's the metaphor.
- **Handoffs (linear chain of specialists)**: **OpenAI Agents SDK** if you're OAI-first; **ADK transfer_to_agent** otherwise.

### 3. Need MCP from day 1?

- **Yes**: ADK (first-class `McpToolset`).
- **No**: anything else works; ADK still has the smoothest MCP wiring.

### 4. Need A2A?

- **Yes**: only ADK has A2A first-class as of May 2026.
- **No**: doesn't constrain.

### 5. What's the dominant non-functional requirement?

- **Long-term memory** → Letta (or ADK + Vertex Memory Bank if you want the GCP stack).
- **Strict typed output** → Pydantic AI (or ADK with `output_schema` if you want the full agent runtime).
- **Lowest TTRA** → CrewAI or OAI Agents.
- **Evals from day 1** → ADK.
- **Observability** → ADK or LangGraph (with LangSmith).

## The "no wrong answer" defaults

If you can't pick:

- **Greenfield, GCP-shop, full stack**: ADK.
- **Greenfield, cloud-agnostic, mixed-team**: LangGraph.
- **Greenfield, content/research team**: CrewAI.
- **Greenfield, OAI-first product team**: OpenAI Agents SDK.

## Migration cost

You're not stuck. But each migration costs roughly:

| From → To | Effort |
|---|---|
| CrewAI → ADK | Medium (rewrite agents, port tools, rebuild tasks as workflow) |
| LangGraph → ADK | Low-medium (concepts map closely) |
| OAI Agents → ADK | Low (handoffs → transfer_to_agent; small surface) |
| Pydantic AI → ADK | Low (Pydantic AI is mostly leaf calls; embed inside ADK) |
| AutoGen → ADK | Medium-high (conversational → structured; rethink termination) |
| Letta → ADK | Medium-high (re-architect memory layer) |

> 🚀 **In Production**
>
> The most expensive framework choice isn't the wrong one — it's the **late** one. Decide early, build a thin spike in your top-2 candidates, pick within 1 sprint. The cost of staying undecided exceeds the cost of being wrong.

> 🛠 **Have the student run:** trace their current/upcoming project through the 5 questions. Land on a recommendation. Justify it in 3 sentences.

> ❓ **Ask the student:** "What's the framework you'd recommend AGAINST your default for one specific use case, and why?" *(Forces nuance; great signal of genuine understanding.)*

[← Prev: 20_FrameworkComparison/08_FeatureMatrix]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/10_DissectingSample →]
