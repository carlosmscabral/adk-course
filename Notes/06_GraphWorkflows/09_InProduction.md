---
module: 06_GraphWorkflows
page: 09_InProduction
title: Graph workflows in production
estimated_minutes: 20
prereqs: [06_GraphWorkflows/08]
concepts: [per-node-observability, cycle-budgets, idempotence, visual-builder]
icon: 🚀
in_production: true
detours_suggested: [VisualBuilder]
---

[← Prev: 06_GraphWorkflows/08_DissectingWorkflowSample]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/10_KnowledgeCheck →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 09 In Production

## 🚀 Per-node observability is the killer feature

Every node yields events. In your tracing stack (OpenTelemetry, Cloud Trace, Langfuse — module 15) each node becomes a span. A failing workflow shows you exactly which node failed, what input it received, what state was at the time, how long it took.

**Templates lump children together**; graphs decompose them. When you're paged at 2am about a research pipeline that's misbehaving, this is the difference between a 5-minute fix and a 5-hour bisect.

## 🚀 Cycles MUST terminate

The graph API doesn't enforce a budget cap on cycles. You must add one:

```python
edges=[
    (START, planner, writer, reviewer),
    (reviewer, writer, "REVISE"),     # cycle
    (reviewer, done,   "APPROVE"),    # exit
]
```

The reviewer must *eventually* yield `Event(route="APPROVE")`. Defend with:

- A counter in state — increment per iteration, force APPROVE after N.
- A timeout on the workflow invocation.
- An `escalate` action that bubbles up.

A graph with a cycle and no exit is a billing event waiting to happen.

## 🚀 Parallel nodes must be idempotent

A node that mutates state while running in parallel with another mutating node creates races. Standard mitigations:

- Each parallel worker writes to its **own** state key (use a worker ID).
- Use a join/distill node to merge after the parallel fan-in (the canonical sample pattern).
- Mark parallel nodes `rerun_on_resume=False` if they have any side effect.

## 🚀 `rerun_on_resume` per node, not just the workflow

Set it deliberately:

| Node kind | `rerun_on_resume` |
|---|---|
| Cheap pure function (router, parser) | `True` |
| LLM call (expensive) | `False` |
| External API call (paid) | `False` |
| State write (idempotent) | `True` is OK if truly idempotent |
| Save-to-DB | `False` |

## 🚀 Route labels as constants

```python
class Routes:
    REVISE  = "REVISE"
    APPROVE = "APPROVE"
    REJECT  = "REJECT"

edges = [
    (reviewer, writer, Routes.REVISE),
    (reviewer, done,   Routes.APPROVE),
    (reviewer, escalate, Routes.REJECT),
]
```

This catches typos at edit time, not at runtime.

## 🚀 Nested workflows are normal

Don't fear a 5-edge `Workflow` becoming a node inside a larger one. The runtime nests cleanly (`Workflow` is a `BaseNode`), traces stay attributed to the inner nodes, and reasoning about each piece in isolation gets easier. `workflow-concurrent_research_writer` does this with research + blog inside root.

## 🚀 The Visual Builder (NEW 2.0)

ADK 2.0 ships a visual graph editor that exports to / imports from `Workflow` definitions. For design-by-PM workflows or for sharing the *shape* with non-coders, it can replace hand-written `edges=[]`. We dedicate [[VisualBuilder]] to this when authored.

## 🚀 Checklist before deploying a graph

- [ ] Every cycle has at least one exit route reachable in bounded iterations.
- [ ] Every parallel node has a unique state-key namespace (no two write the same key).
- [ ] `rerun_on_resume` is set deliberately per node (not left default).
- [ ] Route labels are constants, not magic strings.
- [ ] Long-running workflows use a durable `SessionService` (`DatabaseSessionService` or `VertexAiSessionService`).
- [ ] Trace export is enabled — you'll need per-node spans the first time something breaks.

> 🤖 **Tutor:** when the student finishes the mini-drill, ask them to walk the checklist for their drill graph. Even a 3-node drill teaches the habit.

---

[← Prev: 06_GraphWorkflows/08_DissectingWorkflowSample]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/10_KnowledgeCheck →]
