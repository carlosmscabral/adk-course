---
module: 06_GraphWorkflows
page: 06_RoutingEdges
title: Routing edges — static vs dynamic
estimated_minutes: 25
prereqs: [06_GraphWorkflows/05]
concepts: [route-labels, Event-route, conditional-edges, fan-out-by-route]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/05_DefiningNodes]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/07_HumanInTheLoop →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 06 Routing Edges

## 🧠 Two edge styles

### Static (always-on)

The default. Whatever a node yields becomes the next node's input.

```python
edges=[(START, A, B)]    # A's output → B's input, always
```

### Dynamic (route-label)

A node yields `Event(route="X")` and the runtime picks edges whose **third tuple element** matches:

```python
edges=[
    (START, router_node),                # router_node is a FunctionNode
    (router_node, branch_a, "A"),        # taken when router yields Event(route="A")
    (router_node, branch_b, "B"),        # taken when router yields Event(route="B")
]
```

The third element is the **route label**. If the node doesn't yield a matching route, the edge isn't taken.

> ⚠️ Routing uses `Event(route=...)` from `google.adk.events`. The framework also has a graph-level `Edge` class (public, in `google.adk.workflow.__init__`) and a private `Event` page representation inside `_workflow.py` — when you write a node, you yield the public `google.adk.events.Event`, NOT the private one. Don't import `from google.adk.workflow._workflow import Event`; stick to the public surface.

## 🛠 The router function

```python
async def length_router_node(node_input: str):
    """Routes by word count."""
    blog_post = node_input
    n = len(blog_post.split())
    route = "X" if n <= 100 else "LINKEDIN" if n <= 300 else "MEDIUM"
    yield blog_post              # pass content along
    yield Event(route=route)     # signal the route
```

The node yields **two things**: the content (forwarded to whichever branch runs) and a route Event. Order doesn't strictly matter; convention is content first, route Event last.

## 🧠 Yielding multiple routes

`Event(route=["X", "Y"])` fires *both* edges — fan-out by route. From `function_nodes/publishing.py`:

```python
routes_for_shoutouts = ["SHOUTOUT_LINKEDIN", "SHOUTOUT_REDDIT"]
yield Event(route=routes_for_shoutouts)
```

After posting to platform X, the graph fans out shoutouts to LinkedIn and Reddit in parallel.

## 🧠 The shape, drawn

```
            ┌──────────────┐
            │ router_node  │  yields Event(route="LINKEDIN")
            └───┬──────┬───┘
                │      │
       route="X"│      │ route="LINKEDIN"
                │      │
                ▼      ▼
        ┌─────────┐  ┌──────────┐
        │ post_to │  │ post_to  │
        │   X     │  │ LinkedIn │   ← only this one runs (route matched)
        └─────────┘  └──────────┘

(route="MEDIUM" edge would exist too, untaken this run)
```

## 🛠 The blog-workflow chain — read it

From `workflow-concurrent_research_writer/agent.py`:

```python
from google.adk.workflow import Workflow, START

blog_workflow = Workflow(
    name="blog_workflow",
    edges=[
        # 1. Linear start: write the blog, then route by length.
        (START, start_blog, generate_blog_post_agent, route_changer),

        # 2. Route to one of three platforms (only one fires).
        (route_changer, post_to_x,        "X"),
        (route_changer, post_to_linkedin, "LINKEDIN"),
        (route_changer, post_to_medium,   "MEDIUM"),

        # 3. After posting, fan out shoutouts to the other platforms.
        (post_to_x,        shoutout_to_linkedin, "SHOUTOUT_LINKEDIN"),
        (post_to_x,        shoutout_to_reddit,   "SHOUTOUT_REDDIT"),
        (post_to_linkedin, shoutout_to_x,        "SHOUTOUT_X"),
        # ...etc
    ],
)
```

This shape — linear stem → dynamic branch → fan-out shoutouts — is impossible with the legacy templates. The graph lets you express it declaratively in ~15 lines.

## 🧠 Cycles

There is **no special syntax** for a cycle — just an edge that points to an earlier node:

```python
edges=[
    (START, planner, writer, reviewer),
    (reviewer, writer, "REVISE"),     # cycle: reviewer → writer if route=REVISE
    (reviewer, done,   "APPROVE"),    # exit
]
```

Cycles must terminate (always provide an "exit" route) and must have a budget cap to avoid runaway. Set the cap on the workflow level or use a counter in state.

> **🧭 See also**: `deep-search` — `/home/carloscabral/study/adk-samples/python/agents/deep-search/app/agent.py` is the canonical *reflect-loop* sample (plan → search → critique → revise, looping until the critic grades `pass`). Same cycle shape, with a real exit condition. Dissected end-to-end in [[23_FrontendIntegration/11_DissectingSample]].

## ⚠️ Common routing mistakes

1. **Forgetting to yield content before `Event(route=...)`** — the next node gets `None` input.
2. **Mistyping the route label** — "Linkedin" vs "LINKEDIN" silently drops the routing.
3. **No default edge** — if the node yields a route nobody listens for, the workflow halts at that node.

> 🚀 **In Production**
>
> Define route labels as **constants** at module top. Refer to them by name in both the node and the edges. Magic strings cause silent routing bugs.

> ❓ **Ask the student:** in the blog-workflow above, what's the absolute minimum number of nodes that fire for a 200-word post? (4 stem nodes + 1 platform-post + 2 shoutouts = 7.)

---

[← Prev: 06_GraphWorkflows/05_DefiningNodes]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/07_HumanInTheLoop →]
