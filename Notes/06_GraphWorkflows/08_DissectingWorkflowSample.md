---
module: 06_GraphWorkflows
page: 08_DissectingWorkflowSample
title: Dissecting workflow-concurrent_research_writer
estimated_minutes: 90
prereqs: [06_GraphWorkflows/07]
concepts: [Workflow, nested-workflows, list-fan-out, FunctionNode, route-fan-out]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/07_HumanInTheLoop]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/09_InProduction →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 08 Dissecting Workflow

## 🛠 The artifact

```
adk-samples/python/agents/workflow-concurrent_research_writer/
├── agent.py                  ← two Workflows + the root
├── main.py                   ← runner driver
├── prompts.py
├── tools.py
├── agent_nodes/
│   ├── research.py           ← LlmAgent (worker) + LlmAgent (distill)
│   └── publishing.py         ← LlmAgent (blog post writer)
└── function_nodes/
    ├── research.py           ← FunctionNodes: start, combine, save
    └── publishing.py         ← FunctionNodes: start_blog, router, post, shoutout
```

> ⚠️ **Sample version pin**: this sample's `pyproject.toml` declares `google-adk>=1.5.0,<2.0.0`. Its code uses the 1.x import paths (`from google.adk.agents.workflow.workflow_agent import WorkflowAgent`, etc.) — those modules do not exist in 2.0. The dissection below shows the **2.0 equivalent** using `google.adk.workflow.Workflow`. If you check out the sample on a 2.0 install, the imports will fail; treat the sample as a *shape reference*, not as runnable code on 2.0.

> 🛠 **Have the student open these files in tabs**, starting with `agent.py`. We'll walk top-down — but read the actual imports against the 2.0 framework source (`/home/carloscabral/study/adk-python/src/google/adk/workflow/__init__.py`), not against the sample's 1.x imports.

## 📁 `agent.py` — the orchestration (2.0 equivalent)

```python
from google.adk.workflow import Workflow, START

research_workflow = Workflow(
    name="research_workflow",
    edges=[
        (
            START,
            start_node,            # FunctionNode — yields list for fan-out
            research_worker_agent, # LlmAgent — runs once per list element
            distill_agent,         # LlmAgent — synthesize the merged Content
            save_node,             # FunctionNode — persist
        ),
    ],
)

# ... (blog_workflow definition — many edges, routes by post length, shoutouts)

root_agent = Workflow(
    name="root_agent",
    rerun_on_resume=True,
    edges=[(START, research_workflow, blog_workflow)],
)
```

Three layers:

1. **`research_workflow`** — linear: start → parallel research (via list yield) → distill → save.
2. **`blog_workflow`** — linear stem → dynamic routing by length → parallel shoutouts.
3. **`root_agent`** — composes the two as nodes. `Workflow` subclasses `BaseNode`, so workflows nest as nodes.

## 📁 `function_nodes/research.py`

```python
async def start_research_node(node_input):
    topic = str(node_input.parts[0].text if node_input.parts else "")
    yield Event(state={"topic": topic})           # save topic
    yield ["X", "LinkedIn", "Reddit", "Medium"]   # fan-out target list

async def combine_reports_node(node_input):
    # node_input is a Content with multiple parts (one per parallel worker).
    yield "\n\n---\n\n".join(p.text for p in node_input.parts if p.text)

async def save_report_node(node_input):
    yield Event(state={"research_report": node_input})  # persist
    yield ModelContent(parts=[Part.from_text(text=node_input)])  # show to user
```

Each `async def` is a generator. The `FunctionNode(...)` wrappers at the bottom of the file turn them into nodes. Note `rerun_on_resume=True` on `start_node` (cheap) vs `False` on `save_node` (avoid re-saving on resume).

## 📁 `agent_nodes/research.py`

```python
research_worker_agent = LlmAgent(
    name="research_worker_llm_agent",
    model="gemini-2.5-flash",
    instruction="Your sole task is to research the topic '{topic}' on the platform "
                "given as your input. Execute a search and summarize.",
    tools=[execute_search],
)
```

One agent, placed in the chain *after* a node that yields a list. The framework runs it once per element of that list — no public `ParallelWorker` wrapper required in 2.0. `{topic}` substitution reaches into state (saved by the start node) — same mechanic as `output_key` ↔ `{key}` from module 05.

## 📁 `function_nodes/publishing.py` (excerpt)

```python
async def length_router_node(node_input):
    n = len(node_input.split())
    route = "X" if n <= 100 else "LINKEDIN" if n <= 300 else "MEDIUM"
    yield node_input            # pass content along
    yield Event(route=route)    # signal which branch
```

This is the canonical conditional-routing node. The `route_changer` `FunctionNode` wraps it.

## 🧭 Trace one input through the whole graph

Input: `"The Future of AI in Education"` (250 words eventually).

```
[research_workflow]
  START
   │ Content(parts=[Part(text="The Future of AI in Education")])
   ▼
  start_node          (yields Event(state={topic: ...}); yields list of 4 platforms)
   │
   ▼  (fan-out, 4 parallel — framework dispatches once per list element)
  research_worker_agent (LlmAgent)
       │ ┌─ "X"        → worker runs → summary X
       │ ├─ "LinkedIn" → worker runs → summary LI
       │ ├─ "Reddit"   → worker runs → summary R
       │ └─ "Medium"   → worker runs → summary M
       ▼  (fan-in into one Content with 4 parts)
  distill_agent       (LLM synthesizes one report from 4 summaries)
   │
   ▼
  save_node           (writes Event(state={research_report: ...}); ModelContent to user)

[blog_workflow]
  START
   │ user-provided thesis
   ▼
  start_blog          (passthrough)
   │
   ▼
  generate_blog_post_agent  (writes the blog)
   │ blog text, say 250 words
   ▼
  route_changer       (250 words ≤ 300 → route="LINKEDIN")
   │
   ├─"X"────────▶ post_to_x         (untaken)
   ├─"LINKEDIN"─▶ post_to_linkedin  ← runs
   └─"MEDIUM"───▶ post_to_medium    (untaken)
                    │ after posting, yields routes for shoutouts
                    ▼
   ┌─"SHOUTOUT_X"─────▶ shoutout_to_x       (runs)
   └─"SHOUTOUT_REDDIT"▶ shoutout_to_reddit  (runs)
```

A linear 5-stage research stem, a 4-way fan-out, fan-in, then a blog stem with 1-of-3 routing and 2-of-3 shoutouts. ~30 nodes total. Templates could express the linear parts but not the routing.

## ❓ Comprehension checks

> ❓ **Ask the student:**
> 1. What does the framework do when an upstream node yields a list? (Answer: it dispatches the next node once per element, in parallel — no `ParallelWorker` import required in 2.0.)
> 2. Why does `start_node` write `topic` to state instead of just passing it as `node_input`?
> 3. The `route_changer` yields `node_input` *before* `Event(route=...)`. If you swapped the order, would it still work?

(Answers in this module's `AGENTS.md`.)

> 🤖 **Tutor:** if the student understands this sample, they understand graph workflows. Spend the time. The mini-drill is a fraction of this complexity.

---

[← Prev: 06_GraphWorkflows/07_HumanInTheLoop]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/09_InProduction →]
