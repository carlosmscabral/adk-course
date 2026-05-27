---
module: Detours
page: VisualBuilder
title: ADK 2.0 Visual Builder — drag-and-drop graph authoring
estimated_minutes: 20
icon: 🗺
prereqs: []
concepts: [visual_builder, graph_workflow, round_trip, code_generation]
---

[← Back to Map](../../MAP.md)

Triggered from: `06_GraphWorkflows` (when a graph has >5 nodes and ASCII gets noisy), `99_Capstone` (communicating designs with non-engineers).

> Take this detour if you'd rather *draw* a workflow than type it — or if you need to hand a diagram to a stakeholder. The Visual Builder is bidirectional: drawings become code, code becomes drawings. ~20 min. (You can skim this if you only ever author by hand.)

---

## 🗺 1. What it is

ADK 2.0 ships a browser-based **Visual Builder** for the graph-workflow API (the same one you write by hand with `WorkflowAgent`). You drag nodes, connect edges, fill in properties on the right panel, hit *Export* — out comes Python that runs in the same runtime.

```
   ┌──────────────────────┐         ┌──────────────────────┐
   │   Visual Builder     │ export  │  Python file using   │
   │   (browser canvas)   ├────────►│  WorkflowAgent API   │
   │                      │         │                      │
   │                      │◄────────┤                      │
   └──────────────────────┘ import  └──────────────────────┘
```

Same surface as code — anything you draw is a thin wrapper around the same primitives covered in `06_GraphWorkflows`.

---

## 🗺 2. When it's worth opening

| situation                                          | visual builder? |
|----------------------------------------------------|-----------------|
| Sketching a new workflow with 3-10 nodes           | ✅ great        |
| Showing a non-engineer how the agent flows         | ✅ great        |
| Round-tripping (draw → tweak in code → re-import)  | ✅ supported    |
| Many small workflows of the same shape             | ❌ codegen / for-loop |
| Highly dynamic graphs (edges built at runtime)     | ❌ code only    |
| Diff-friendly history in PRs                       | ❌ code is better diffable |

Rule of thumb: **moderate complexity** is the sweet spot. Trivial → just code it. Deeply dynamic → can't be drawn.

---

## 🗺 3. How to open it

Per `https://adk.dev/` (snapshot 2026-05-27):

```bash
$ adk web                       # the dev UI we covered in [[a2UI]]
# In the UI, switch to the "Builder" tab.
# Or directly:
$ adk web --builder
```

The builder shares the dev-server process — same caveats apply (localhost only, no auth, dev-only). You select a target Python file; edits in the canvas sync to that file on save.

If your environment's builder UI is gated (some early-access tenants), skip to section 5 — drawing on paper and writing code by hand teaches the underlying model better anyway.

---

## 🗺 4. The round-trip

The killer feature is **bidirectional sync**:

```
1. Draw a 3-node graph in the UI         → save → writes pipeline.py
2. Open pipeline.py in your editor       → tweak a node's prompt
3. Re-open the Builder                   → it re-parses pipeline.py
4. Your edit shows up on the canvas
5. Drag a new edge                       → save → pipeline.py updates
```

This works because the Builder treats the code as the source of truth. It doesn't keep its own serialized format — it reads and writes the same `WorkflowAgent` Python that you'd write by hand. So `git diff` is meaningful, code review works, no `.builder.json` sidecar.

⚠️ One catch: **the parser is conservative**. Anything that isn't a recognized pattern (e.g., a node assembled via a helper function, or a comprehension over edges) becomes an opaque "custom code" block on the canvas — you can see it but not edit visually. Keep the drawable portion declarative.

---

## 🗺 5. What it generates (the API you're learning anyway)

Even if you never open the Builder, knowing what it spits out helps:

```python
# Equivalent to a 3-node Builder drawing: research → critique → revise
from google.adk.agents import WorkflowAgent, Agent

research = Agent(model="gemini-2.5-flash", name="research", instruction="...")
critique = Agent(model="gemini-2.5-flash", name="critique", instruction="...")
revise   = Agent(model="gemini-2.5-flash", name="revise",   instruction="...")

root_agent = WorkflowAgent(
    name="reviewer_pipeline",
    nodes=[research, critique, revise],
    edges=[
        ("research", "critique"),
        ("critique", "revise"),
    ],
)
```

A drawing of three boxes with two arrows produces this. That's it. The Builder is a viewer/editor for graphs of this shape — no magic.

> **🚀 In Production**
>
> Don't let the Builder be the *only* place a workflow lives. Commit the generated `.py` to git; review it like any other code. Treat the UI as a *productivity tool*, not a data store. If you'd be unhappy losing the canvas, you're using it wrong.

---

## 🛠 Have the student try

Sketch a 3-node graph on paper (or text), then write it as `WorkflowAgent` code from scratch — no UI required.

**The shape**: a researcher emits a draft; a fact-checker reads it; if the fact-checker flags an issue, route to a reviser, otherwise emit. (Conditional edge.)

```
       research
          │
          ▼
       fact-check
        /     \
   issue?     clean?
      │           │
      ▼           ▼
   revise      (done)
      │
      ▼
   (done)
```

Have the student write this as a `WorkflowAgent` with `nodes=[...]` and `edges=[...]`. Then if the Builder is available, **import that file** and confirm the canvas matches the drawing.

If the Builder isn't accessible, the exercise still works — the point is that "drawing" and "code" are isomorphic.

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — likely `06_GraphWorkflows/02_AuthoringGraphs` or `99_Capstone/03_DesignReview`.
