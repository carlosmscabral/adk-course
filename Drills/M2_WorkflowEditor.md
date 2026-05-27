---
module: Drills
page: M2_WorkflowEditor
title: Milestone M2 — Workflow Editor (legacy vs graph, side by side)
estimated_minutes: 720
prereqs: [00_Setup/last, 01_Foundations/last, 02_FirstAgent/last, 03_Tools/last, 04_SessionsState/last, 05_MultiAgent/11, 06_GraphWorkflows/11]
concepts: [SequentialAgent, ParallelAgent, LoopAgent, WorkflowAgent, dynamic-routing, side-by-side]
icon: 🏁
in_production: false
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/11_MiniDrill]  [↑ Map](../MAP.md)  [Next: 07_Callbacks/00_Overview →]

You are here: 🗺 Drills ▸ 🏁 M2 Workflow Editor

## 🏁 What you're building

A **research pipeline** that:

1. takes a topic from the user
2. plans 3 research angles
3. runs 3 researchers concurrently (one per angle)
4. drafts a unified article from the findings
5. reviews the draft — if the review score ≥ 8, ship it; otherwise send back to the writer (max 3 revisions)

You'll implement this pipeline **twice**:

- **Version A (legacy):** `SequentialAgent` containing a `ParallelAgent` (researchers) followed by a `LoopAgent` (writer + reviewer cycle).
- **Version B (graph):** a `WorkflowAgent` whose reviewer node yields `Event(route="REVISE")` to cycle back to the writer or `Event(route="APPROVE")` to exit.

Then write a short side-by-side comparison.

## 🎯 Goals

- Internalize that the two APIs can express overlapping shapes — but graphs handle dynamic exits natively while legacy needs hacks.
- Develop intuition for when the extra graph boilerplate pays off.
- Practice route-label discipline, `output_key` plumbing, and idempotent state writes.

## 📋 Prereqs

- Completed `Notes/00_Setup` through `Notes/06_GraphWorkflows` including both mini-drills.
- An LLM key (Gemini API or Vertex auth).
- Python ≥ 3.11, `google-adk` installed.

## ⏱ Time

**1.5 days** (~9-12 hours actual). Version A in ~3-4h, Version B in ~4-5h, comparison ~1-2h.

## 📐 Spec

### Common inputs/outputs (both versions)

- **Input:** a topic string (e.g., `"The economics of nuclear fusion R&D in 2026"`).
- **Output:** the final article string (≥ 300 words), plus the final reviewer score, plus the iteration count it took.

### Common sub-agents (you can share these between A and B)

| Agent | Model | Job | output_key |
|---|---|---|---|
| `planner` | `gemini-2.5-pro` | Take topic, propose 3 distinct angles as a JSON list | `angles` |
| `researcher` | `gemini-2.5-flash` | Take ONE angle, do `google_search`, return a 1-paragraph finding | (no output_key — runs N times in parallel, see below) |
| `writer` | `gemini-2.5-pro` | Take `{angles}` + `{findings}` (+ previous draft if revising) and produce a unified article | `draft` |
| `reviewer` | `gemini-2.5-pro` | Score the `{draft}` 1-10 and return `{"score": int, "feedback": str}` (use `output_schema=` from module 04 if you covered it; otherwise parse JSON) | `review` |

Researcher fan-out:

- **Version A** uses a `ParallelAgent` containing 3 fixed `researcher` instances, each with a different `instruction` that hard-codes "angle 1 of 3" / "angle 2 of 3" / "angle 3 of 3" and reads `state["angles"]`.
- **Version B** uses `ParallelWorker(researcher)` with the upstream planner-equivalent node yielding the list of 3 angles.

(That difference alone is instructive — graphs let you fan out on a dynamic list.)

### Version A — legacy templates

```
SequentialAgent (root)
├── planner                                  (LlmAgent)
├── ParallelAgent
│   ├── researcher_1                         (LlmAgent — reads angles[0])
│   ├── researcher_2                         (LlmAgent — reads angles[1])
│   └── researcher_3                         (LlmAgent — reads angles[2])
├── findings_combiner                        (LlmAgent — joins the 3 outputs into one state key 'findings')
└── LoopAgent  max_iterations=3
    ├── writer                               (LlmAgent — reads {angles}, {findings}, optionally {draft})
    └── reviewer                             (LlmAgent — scores; if ≥ 8, invokes exit_loop via a tool)
```

The reviewer must call the `exit_loop` built-in when the score is high enough. Otherwise the loop iterates until `max_iterations`. The final `draft` is what the user sees.

⚠ Constraint: the reviewer cannot dynamically send the draft to a *different* sub-agent in the legacy version — it can only exit or not exit. That's the legacy ceiling.

### Version B — graph workflow

```
START
  │  topic
  ▼
planner_node                  (FunctionNode wraps planner LlmAgent OR directly an LlmAgent node)
  │  yields the 3 angles as a list  (Event(state={"angles": ...}); yield ["a1","a2","a3"])
  ▼
ParallelWorker(researcher)    (fan-out by list)
  │  joins 3 findings into one Content
  ▼
findings_combiner             (LlmAgent — writes state["findings"])
  │
  ▼
writer                        (LlmAgent — reads {angles}, {findings}, optionally {draft})
  │
  ▼
reviewer_node                 (FunctionNode that runs the reviewer LlmAgent and inspects the score)
  │
  ├──"REVISE"──▶ writer       (cycle, max 3 trips)
  └──"APPROVE"──▶ done_node   (publish final draft to user)
```

The reviewer_node:

```python
async def reviewer_node(node_input):
    # Run an internal LlmAgent or parse the JSON the upstream reviewer emitted.
    result = ... # {"score": 7, "feedback": "..."}
    iterations = ctx.state.get("review_count", 0) + 1
    yield Event(state={"review_count": iterations, "last_review": result})
    if result["score"] >= 8 or iterations >= 3:
        yield ModelContent(parts=[Part.from_text(text=ctx.state["draft"])])
        yield Event(route="APPROVE")
    else:
        yield Event(route="REVISE")
```

Note the **explicit budget guard** (`iterations >= 3`) — graphs don't auto-cap cycles.

### Required logs

- **Version A:** print which loop iteration is running.
- **Version B:** print the route decision at each reviewer turn ("REVISE → iteration 2" / "APPROVE → done").

## ✅ Verification rubric

Run both versions against the same topic: `"The economics of nuclear fusion R&D in 2026"`.

| Check | Pass criterion |
|---|---|
| Both produce an article | Final stdout contains a non-empty string ≥ 300 words. |
| Both terminate | No process hangs. Both finish in ≤ 4 reviewer iterations. |
| Comparable quality | A spot-read says both articles are coherent and on-topic (not identical — that's expected). |
| Graph logs routing | Version B prints "REVISE" or "APPROVE" at each reviewer turn. |
| Side-by-side written | A `M2_comparison.md` file you write (200-400 words) covering: lines-of-code per version, observability differences, where each version was awkward, when you'd reach for each. |

Place outputs at:

```
Work/M2/
├── workflow_legacy.py      ← Version A
├── workflow_graph.py       ← Version B
├── article_legacy.txt
├── article_graph.txt
└── M2_comparison.md
```

## 🌟 Stretch goals

1. **HITL gate.** Insert a `RequestInput` node in Version B between writer and reviewer asking the user "approve auto-revision? y/n" — if no, escalate immediately.
2. **Adaptive parallelism.** In Version B, have the planner yield a *variable* number of angles (3-5) based on topic complexity. Watch the `ParallelWorker` fan out to the right count.
3. **Per-node retries** (forward to module 19). Wrap `researcher` with a `RetryConfig` in the graph version that retries 2x on transient errors.
4. **Comparison plot.** Time both versions on 5 topics, plot wall-clock per iteration. Graphs have slightly more orchestration overhead; quantify it.

## 🤖 Tutor notes

- **Don't let the student skip Version A.** The pain of writing the loop with a tool-based exit teaches them why graphs are nicer. Skipping it loses the lesson.
- **The `findings_combiner` LlmAgent is a kludge in Version A.** With `ParallelAgent`, parallel children write distinct `output_key`s; combining them into one `findings` string requires an extra LLM call. Version B can do this in a `FunctionNode` (no LLM needed). Point this out.
- **Watch for state-key drift.** `draft` in Version A's loop accumulates across iterations; `draft` in Version B's cycle does too — but the reviewer must NOT overwrite `draft`, only score it. Common bug.
- **If the student's `exit_loop` doesn't fire**, they probably forgot to wrap a function as a `FunctionTool` and pass it to the reviewer's `tools=[...]`. The LLM can only call functions it can see.
- **The point of the comparison doc** isn't to declare a winner. Both APIs ship in 2.0 for a reason. The student should articulate the trade-off in their own words.

## ❓ Self-check questions

> ❓ **Ask the student before they start coding:**
> 1. In Version A, what stops the LoopAgent if the reviewer is too generous?
> 2. In Version B, where do you enforce the 3-revision cap?
> 3. If you swap `gemini-2.5-pro` for `gemini-2.5-flash` on the writer, what likely degrades? (Output structure, length adherence, instruction-following on long contexts.)

> ❓ **After they finish:**
> 1. Which version was easier to debug when something went wrong?
> 2. Which version's code was easier to read top-to-bottom?
> 3. If you had to add "if the article mentions stock prices, also call a compliance check agent," which version would you reach for?

---

[← Prev: 06_GraphWorkflows/11_MiniDrill]  [↑ Map](../MAP.md)  [Next: 07_Callbacks/00_Overview →]
