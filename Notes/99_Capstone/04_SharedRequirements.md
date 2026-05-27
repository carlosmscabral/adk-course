---
module: 99_Capstone
page: 04_SharedRequirements
title: Shared requirements (all tracks)
estimated_minutes: 20
prereqs: [99_Capstone/00]
concepts: [requirements, rubric, shared-baseline]
icon: 🏁
in_production: true
---

[← Prev: 99_Capstone/03_TrackC_PersonalKnowledgeHub]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/04A_DissectingACapstone →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 04 Shared Requirements

# 🏁 Shared requirements — the floor

Regardless of track, your capstone MUST satisfy all of the below. These are also the grading rubric in `09_MiniDrill.yml`.

## Composition

- [ ] **≥3 agents composed** — via `sub_agents` (transfer pattern) OR via a `WorkflowAgent` graph.
- [ ] **≥2 tools** — `FunctionTool`, `LongRunningFunctionTool`, `AgentTool`, or `McpToolset`. At least ONE must NOT be a built-in (`google_search`, `load_memory`, etc.).

## State and memory

- [ ] **Persistent state** — `DatabaseSessionService` or `SqliteSessionService`. NOT `InMemorySessionService` (use it only during development).
- [ ] **Memory service** — `VertexAiMemoryBankService`, `VertexAiRagMemoryService`, or `InMemoryMemoryService` (acceptable only with a clear "swap to Vertex for prod" note in README).

## Tests

- [ ] **≥5 eval cases** in an `EvalSet`.
- [ ] At least 2 distinct evaluator types (e.g., `LlmAsJudge` + `FinalResponseMatchV2Evaluator` / metric key `final_response_match_v2`).
- [ ] `adk eval` runs and reports.

## Cross-cutting

- [ ] **≥1 plugin** — built-in (`LoggingPlugin`, `ReflectAndRetryToolPlugin`, `ContextFilterPlugin`, `GlobalInstructionPlugin`, `BigQueryAgentAnalyticsPlugin`) OR a custom subclass of `BasePlugin`.
- [ ] **≥2 callbacks** across `before/after_model`, `before/after_tool`, `before/after_agent`, `on_*_error`. At least one MUST be a guardrail (input validation, output filtering, budget enforcement, etc.).

## Interface

- [ ] **A2A** — `to_a2a(root)` produces a running server and a valid `AgentCard`. A `RemoteA2aAgent` client can call it.

## Observability

- [ ] **OpenTelemetry tracing** — spans flowing to a backend (Cloud Trace in prod; Jaeger/console exporter acceptable for the demo). At least one invocation produces ≥8 spans.

## Documentation

- [ ] **README** with:
  - Architecture diagram (ASCII art OR linked image).
  - "How to run" — ≤3 commands.
  - "How to extend" — a worked example of adding one new sub-agent or tool in ≤20 lines.
  - "Eval results" — paste from `adk eval` (or screenshot).
  - "Limitations / next steps" — honest list of what's NOT done.

## Self-review against module 20

- [ ] In one paragraph in the README, answer: "Why ADK for this app — and where would a competing framework have been just as good or better?"
  - This forces nuance. Reflexive "ADK best" is **not** acceptable.

## What does NOT count

- A repo with all the pieces but no eval cases.
- A repo where `adk run` works but `to_a2a` was never tested.
- A repo where the README says "TODO: add memory" — the memory must actually work.
- A repo where the OpenTelemetry export is configured but the spans were never observed in a backend.

## How to measure yourself

Use `06_SelfReviewChecklist.md` as a pre-flight checklist. Walk through it before declaring done.

> ⚠️ **Gotcha:** the temptation is to cut evals or A2A "for time." Don't. Those are the two pieces that prove your agent works **for someone other than you**. A capstone with great agents and no evals is a science experiment, not a product.

> 🛠 **Have the student run:** their checklist progress as a percent every day of the build. Aim for 30% by end of Day 2, 60% by Day 3, 90% by Day 4.

[← Prev: 99_Capstone/03_TrackC_PersonalKnowledgeHub]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/04A_DissectingACapstone →]
