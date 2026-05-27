---
module: 99_Capstone
page: 01_TrackA_ResearchAssistant
title: Track A — Research Assistant
estimated_minutes: 30
prereqs: [99_Capstone/00]
concepts: [research-assistant, graph-workflow, A2A, MCP]
icon: 🛠
in_production: true
---

[← Prev: 99_Capstone/00_Overview]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/02_TrackB_CodeReviewer →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 01 Track A

# 🛠 Track A — Research Assistant

See `_figures/track_a.txt` for the architecture diagram.

## The pitch

A research assistant that ingests a question, **researches** it across the open web and a private doc store, **summarizes** with citations, and **critiques** its own draft before returning it. Exposed as an A2A service so other agents can consume it.

## The spec

### Agents (3 minimum — graph workflow)

1. **`Researcher`** (`LlmAgent`)
   - Tools: `google_search` (built-in) + `McpToolset` for a private doc store (your local `mcp-server-filesystem` over a `/docs/` dir is fine for the demo).
   - Output: a structured `ResearchPacket` (Pydantic) with `query`, `findings: list[Finding]`, where `Finding` has `text` + `source_url`.

2. **`Summarizer`** (`LlmAgent`)
   - Input: the `ResearchPacket`.
   - `output_schema=Summary` (Pydantic with `headline`, `body`, `sources: list[str]`).
   - Instruction: "Summarize in <=200 words. Every paragraph must cite at least one source."

3. **`Critic`** (`LlmAgent`)
   - Input: the `Summary`.
   - Tools: `google_search` (for fact-checking).
   - Output: either `APPROVED` (passes through the summary) or `REJECTED` + reasons (loops back to Summarizer with feedback in state).

### Workflow (graph)

```
researcher → summarizer ⇄ critic
                    │
                    └──→ END  (when critic returns APPROVED)
```

Use the `Workflow` graph primitive (exported as `google.adk.Workflow` from `google/adk/workflow/_workflow.py:148`). Define edges with triggers (Critic's `APPROVED` → END; `REJECTED` → back to Summarizer with state delta carrying the critique).

### Tools (≥2)

- **`google_search`** — built-in.
- **`McpToolset(StdioServerParameters("npx", ["-y", "@modelcontextprotocol/server-filesystem", "./docs/"]))`** — private docs.

### Persistent state

`SqliteSessionService(db_path="./capstone.db")` so a session survives restarts.

### Memory service

`VertexAiRagMemoryService` (production) OR `InMemoryMemoryService` with a periodic export script (demo). Capture every approved summary into memory keyed on the query.

### Eval cases (≥5)

Build an `EvalSet` with cases like:
- `q="What is ADK 2.0?"` → expect the summary to mention "Google", "Python", "agent framework".
- `q="Compare LangGraph and ADK."` → expect specific differentiators (A2A, MCP, GCP).
- Failure case: empty query → expect graceful error.
- Adversarial: a question whose answer requires the private doc store (verifies MCP plumbing).
- Long-tail: a multi-hop question forcing 2+ critique cycles.

Use `LlmAsJudge` for the open-ended ones, `FinalResponseMatchV2Evaluator` (metric key `final_response_match_v2`) for keyword ones, `TrajectoryEvaluator` for the multi-hop one.

### Plugins (≥1) and callbacks (≥2)

- `LoggingPlugin` for stdout JSON logs.
- Custom `before_model_callback` that enforces a per-invocation token budget (e.g., 5k tokens max).
- Custom `after_tool_callback` on the Summarizer that fails the response if no source URLs appear.

### A2A interface

`to_a2a(workflow_root)` and run on port 8080. Generate the `AgentCard` and verify with `RemoteA2aAgent` from a tiny client script.

### Observability

OpenTelemetry export to Cloud Trace (or a local Jaeger for the demo). Every invocation produces ≥10 spans; you should be able to point at one and explain what happened.

### README

In your project root, `README.md` must include:
- Architecture diagram (ASCII or PNG).
- "How to run" (3 commands max).
- "How to extend" (add a new sub-agent in ≤20 lines).
- "Eval results" pasted from `adk eval`.

### Self-review

Cross-check against the comparison flowchart from module 20: in 1 paragraph, why is ADK the right tool for THIS app? Be honest — if LangGraph would have been just as good, say so.

## Suggested file layout

```
capstone-research/
├── research_assistant/
│   ├── __init__.py
│   ├── agent.py              ← root + workflow definition
│   ├── sub_agents/
│   │   ├── researcher/agent.py
│   │   ├── summarizer/agent.py
│   │   └── critic/agent.py
│   ├── tools/
│   │   └── mcp_docs.py
│   ├── plugins/
│   │   └── budget.py
│   └── schemas.py
├── docs/                     ← MCP filesystem docs
├── tests/
│   └── eval_set.json
├── README.md
└── pyproject.toml
```

> 🚀 **In Production**
>
> The critic loop can run away. Cap it at `max_critic_cycles=3` in the workflow and emit a clear "could not satisfy critic" final message if exceeded. Untimely costs come from unbounded critique loops.

> 🛠 **Have the student run:** `mkdir capstone-research && cd capstone-research && adk create` then port the scaffold into the layout above.

[← Prev: 99_Capstone/00_Overview]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/02_TrackB_CodeReviewer →]
