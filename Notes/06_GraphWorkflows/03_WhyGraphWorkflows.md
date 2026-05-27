---
module: 06_GraphWorkflows
page: 03_WhyGraphWorkflows
title: Why graphs — what templates can't express
estimated_minutes: 15
prereqs: [06_GraphWorkflows/02]
concepts: [conditional-routing, joins, HITL, retries, observability]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/02_LegacyMixed]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/04_GraphIntro →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 03 Why Graphs

## 🧠 The four template ceilings

### 1. Conditional routing per-node

Templates run children unconditionally. Graphs let an edge carry a **route label**: "go to X only if this condition matches."

```
templates:                     graph:
  Sequential[A, B]               A ──▶ B                (always)
                                 A ──"happy"──▶ B       (only if route=happy)
                                 A ──"sad"───▶ C        (only if route=sad)
```

### 2. Joins

A `ParallelAgent` joins **all** children before continuing. Graphs let you express partial joins (k-of-n), waterfalls, and join-on-first-completion.

### 3. Retries per node

In templates, a child failure aborts the parent. Graphs let you declare `RetryConfig` per node (we'll see this in Internals / module 19) so a flaky network call retries 3x with backoff without burning the whole workflow.

### 4. HITL pauses

You cannot pause a `SequentialAgent` mid-pipeline to wait for human input. Graphs natively support `RequestInput` events that suspend execution; a separate API resumes from the suspension point. (This is the **Resume/Cancel** feature new in 2.0.)

## 🧠 The conceptual upgrade

| | templates (1.x style) | graphs (2.0 primary) |
|---|---|---|
| Composition by | nested tree | named nodes + edges |
| Routing | implicit (next sibling) | explicit edges with route labels |
| Async | hidden | first-class (each node yields events) |
| Branches | only `LlmAgent.sub_agents` decides | edges + route labels per node |
| Cycles | only `LoopAgent` with counter | any cycle, with budget caps |
| HITL | not supported | first-class via `RequestInput` |
| Visual editing | n/a | exportable to/from Visual Builder (NEW) |
| Observability | one span per child | one span per *node* (every step visible) |

## 🧠 When *not* to reach for graphs

If your problem is "do A then B then C" — `SequentialAgent` is shorter and clearer. The graph API costs ~3-5 more lines of boilerplate per node; it pays back when you need any of the four ceiling-breakers above.

Rule of thumb: if you're nesting 3+ template levels OR adding a callback "just to skip a step", switch to graphs.

> 🚀 **In Production**
>
> The strongest reason to choose graphs is observability. Every node is its own span in your trace. Templates lump children together. When a 7-step pipeline breaks at step 4, graphs tell you where in 1 click; templates make you binary-search.

> ❓ **Ask the student:** in their own application, which of the 4 ceilings would they hit first?

---

[← Prev: 06_GraphWorkflows/02_LegacyMixed]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/04_GraphIntro →]
