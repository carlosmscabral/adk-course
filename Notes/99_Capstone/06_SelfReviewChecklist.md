---
module: 99_Capstone
page: 06_SelfReviewChecklist
title: Self-review checklist — module by module
estimated_minutes: 20
prereqs: [99_Capstone/05]
concepts: [self-review, module-coverage]
icon: 🏁
in_production: true
---

[← Prev: 99_Capstone/05_BuildingPlan]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/07_InProduction →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 06 Self-Review Checklist

# 🏁 Self-review checklist — has every module's surface been exercised?

Walk this list when you think you're done. Each item must be **yes** with a pointer to where in your repo.

## Foundation

- [ ] **00 Setup** — repo has a `pyproject.toml` or `requirements.txt`; `adk` CLI works against it.
- [ ] **01 Foundations** — your README explains the agent loop your app exercises.
- [ ] **02 FirstAgent** — at least one `LlmAgent` with `model` + `instruction`.
- [ ] **03 Tools** — ≥2 tools wired; at least one is a `FunctionTool` with typed signature + docstring.
- [ ] **04 SessionsState** — at least 3 distinct state keys used; at least one uses a prefix (`user:`, `app:`, or `temp:`).

## Composition

- [ ] **05 MultiAgent** — at least one `sub_agents` relationship OR `transfer_to_agent` action observed.
- [ ] **06 GraphWorkflows** — at least one `WorkflowAgent` graph (if Track A) OR a clear justification for using sub_agents only (Tracks B/C).

## Production primitives

- [ ] **07 Callbacks** — ≥2 callbacks, ≥1 of them a guardrail.
- [ ] **08 MCP** — at least one `McpToolset` (mandatory for Tracks A and B; optional but encouraged for Track C).
- [ ] **09 Skills** — Track C only mandatory; Tracks A/B optional. If present, frontmatter + body in proper `.skill` files.
- [ ] **10 A2A** — `to_a2a(root)` runs; tested with `RemoteA2aAgent` client; AgentCard valid.

## GCP / data layer

- [ ] **10A Embeddings** — knowingly used somewhere (RAG, similarity search).
- [ ] **10B RAGPipeline** — at least one retrieval-augmented call.
- [ ] **10C BigQueryAgents** — optional unless your data domain is analytical; if applicable, used.

## Memory

- [ ] **11 Memory** — memory service wired; at least one cross-session recall demonstrated.

## Execution

- [ ] **12 CodeExecution** — Track B mandatory (`VertexAiCodeExecutor` or `ContainerCodeExecutor`). Tracks A/C only if your tools genuinely need code-exec.

## Cross-cutting

- [ ] **13 Plugins** — ≥1 plugin registered.
- [ ] **14 Evaluation** — `EvalSet` with ≥5 cases; `adk eval` runs and passes ≥80%.
- [ ] **15 Observability** — OpenTelemetry exporting; you've inspected at least one trace.
- [ ] **16 ProductionSecurity** — at least one of: input validation callback, output PII filter, sandbox for code-exec, auth check on a sensitive tool.

## Models

- [ ] **17 AdvancedModels** — you've consciously picked your model. If using multiple (mixing Gemini + Claude), document why.

## Streaming

- [ ] **18 StreamingLive** — at least the README explains whether your app would benefit from Live API; if Track A and you want extra credit, wire one streaming voice demo.

## Internals & comparison

- [ ] **19 Internals** — you can point at one place in your code where you needed to understand ADK internals to fix something (a callback's timing, an event's branch, a state-delta visibility).
- [ ] **20 FrameworkComparison** — README has the "why ADK / where competitors win" paragraph.

## Scoring

- 20-22 checkmarks (allowing 10C, 12, 18 as optional per-track): **excellent** — production-ready.
- 16-19: **good** — solid capstone, document the gaps in "limitations / next steps".
- <16: **revisit** — pick the 2 most-painful gaps and patch before declaring done.

> 🛠 **Have the student run:** literally check off each box with a file path next to it. If they can't name a file, the box is unchecked.

> ❓ **Ask the student:** "Which checkbox surprised you — either because you forgot about it or because it turned out to be more important than you thought?"

[← Prev: 99_Capstone/05_BuildingPlan]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/07_InProduction →]
