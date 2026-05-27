---
drill: M5_Capstone
title: Milestone 5 — Capstone (final integration)
estimated_minutes: 1800
prereqs: [99_Capstone/00, 99_Capstone/04]
icon: 🏁
---

[← Prev: M4_AuditorWithEvals]  [↑ Drills](./)  [Capstone Overview](../Notes/99_Capstone/00_Overview.md)

# 🏁 Milestone 5 — Capstone

The final integration. **The course exit ticket.**

Full spec, building plan, and grading rubric live in:
- **[Notes/99_Capstone/00_Overview.md](../Notes/99_Capstone/00_Overview.md)** — start here.
- **[Notes/99_Capstone/04_SharedRequirements.md](../Notes/99_Capstone/04_SharedRequirements.md)** — the floor every track must satisfy.
- **[Notes/99_Capstone/09_MiniDrill.yml](../Notes/99_Capstone/09_MiniDrill.yml)** — the verification rubric the tutor uses to grade.

## Pick one track

| Track | Theme | Headline tech |
|---|---|---|
| **[A — Research Assistant](../Notes/99_Capstone/01_TrackA_ResearchAssistant.md)** | Multi-agent research + critique loop | Graph workflow + MCP doc store + A2A |
| **[B — Code Reviewer](../Notes/99_Capstone/02_TrackB_CodeReviewer.md)** | Diff-aware reviewer with test sandbox | sub_agents + VertexAiCodeExecutor + GitHub webhook |
| **[C — Personal Knowledge Hub](../Notes/99_Capstone/03_TrackC_PersonalKnowledgeHub.md)** | Lifelong-memory note-taker | Memory Bank + RAG + Skills packaging |

## Shared requirements (floor — every track)

- **Composition**: ≥3 agents via `sub_agents` OR `WorkflowAgent` graph.
- **Tools**: ≥2 (at least 1 not a built-in).
- **Persistent state**: `DatabaseSessionService` or `SqliteSessionService`.
- **Memory service**: Vertex Memory Bank, Vertex RAG, or InMemory (with prod-swap note).
- **Evals**: ≥5 cases in an `EvalSet`; ≥2 evaluator types.
- **Plugins**: ≥1 plugin registered.
- **Callbacks**: ≥2 callbacks; ≥1 must be a guardrail.
- **A2A**: `to_a2a(root)` + verified `RemoteA2aAgent` client round-trip.
- **Observability**: OpenTelemetry exporting (Cloud Trace / Jaeger / console); ≥8 spans visible per invocation.
- **README**: architecture diagram, run commands (≤3), extension example (≤20 lines), eval results, limitations, and a **"why ADK / where competitors win"** paragraph (module 20 self-review).

## Time

**5 days.** See [Notes/99_Capstone/05_BuildingPlan.md](../Notes/99_Capstone/05_BuildingPlan.md) for the day-by-day sequence.

## Pass criteria (from the rubric)

- ≥18 of the YAML rubric items pass.
- Track-specific headlines (workflow critic loop / sandboxed code-exec / Skills + dual memory) work.
- Student answers ≥3 post-submit probes coherently:
  - "Show me a Cloud Trace span tree for one invocation."
  - "Run `adk eval` live. Why does case X fail?"
  - "Add one new sub-agent in <20 lines without touching others."
  - "If you had one more day, what one feature would you add and what would you cut?"

## When you pass

You're done. Read [Notes/99_Capstone/07_InProduction.md](../Notes/99_Capstone/07_InProduction.md) and pick option A (ship it), B (iterate weekly), C (postmortem), or D (open-source).

Set the 6-month tickle out loud.

[← Prev: M4_AuditorWithEvals]  [↑ Drills](./)  [Capstone Overview](../Notes/99_Capstone/00_Overview.md)
