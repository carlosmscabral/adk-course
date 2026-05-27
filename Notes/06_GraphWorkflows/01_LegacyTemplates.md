---
module: 06_GraphWorkflows
page: 01_LegacyTemplates
title: Legacy workflow templates — Sequential, Parallel, Loop
estimated_minutes: 25
prereqs: [06_GraphWorkflows/00, 05_MultiAgent/06]
concepts: [SequentialAgent, ParallelAgent, LoopAgent, exit_loop, max_iterations]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/00_Overview]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/02_LegacyMixed →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 01 Legacy Templates

## 🧠 The three templates

All three live in `google.adk.agents` and pre-date the 2.0 graph API. They are **fully supported** in 2.0 and still the right tool for many linear/forked/looped pipelines.

```python
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
```

### SequentialAgent — recap

Runs children in declared order. We covered it in [`05_MultiAgent/06`](../05_MultiAgent/06_SequentialAgent.md).

### ParallelAgent — concurrent children

```python
from google.adk.agents import ParallelAgent

drafters = ParallelAgent(
    name="parallel_drafters",
    sub_agents=[creative_writer, focused_writer],   # both run at once
)
```

Each child runs **concurrently** and writes its own `output_key` to state. After all children finish, the parent's invocation returns. Downstream agents see *both* keys.

```
                 ┌───────────────────┐
                 │ ParallelAgent     │
       ┌─────────┤                   ├─────────┐
       ▼         └───────────────────┘         ▼
  ┌────────┐                              ┌────────┐
  │child_a │   (run concurrently)         │child_b │
  └───┬────┘                              └────┬───┘
      │ writes state['a']                      │ writes state['b']
      └─────────────┬──────────────────────────┘
                    ▼
              both keys available to next agent
```

⚠️ **Watch for state collisions.** If two parallel children write the same `output_key`, the result is non-deterministic. Always give them distinct keys.

### LoopAgent — repeat until exit

```python
from google.adk.agents import LoopAgent

revise_until_good = LoopAgent(
    name="revise_loop",
    sub_agents=[draft_agent, critique_agent],  # one iteration runs both
    max_iterations=5,
)
```

Each iteration runs all children once. The loop exits when:

1. `max_iterations` is hit, **or**
2. Any child or tool sets `tool_context.actions.escalate = True` (or invokes the built-in `exit_loop` tool).

```python
from google.adk.tools import exit_loop
```

`exit_loop` is the conventional way the critic signals "score is high enough, we're done."

## 🛠 Minimal `exit_loop` pattern

```python
from google.adk.tools import exit_loop, FunctionTool

def maybe_exit(score: int, tool_context) -> str:
    """Call this when the score is >= 8 to stop the loop."""
    if score >= 8:
        return exit_loop(tool_context=tool_context)
    return f"Score {score} too low; iterate."

critique_agent = LlmAgent(
    name="critique",
    instruction="Rate the draft 1-10. If >=8, call maybe_exit. Otherwise return suggestions.",
    tools=[FunctionTool(maybe_exit)],
)
```

> 🛠 **Have the student run** a 3-iteration loop and confirm `session.state` keeps the latest draft each turn (the loop doesn't reset state between iterations).

## 🧠 The "infinite loop" guard

Always set `max_iterations`. Even if your exit logic is "obvious", real LLMs surprise you. Treat `max_iterations` as a budget cap, not a debugging tool.

## 🧠 When templates are *enough*

These three templates compose: a `SequentialAgent` can contain a `LoopAgent` which contains a `ParallelAgent`. That covers a surprising range of pipelines without ever touching the graph API. We'll see exactly that on the next page.

> 🚀 **In Production**
>
> If your team prefers code review by reading top-to-bottom, templates often win — they read like nested function calls. Reach for the graph API only when the structure stops fitting (dynamic routing, complex joins, HITL).

> ❓ **Ask the student:** which template would you use to "generate 3 candidates and pick the best"? (Parallel → Sequential with a picker.)

---

[← Prev: 06_GraphWorkflows/00_Overview]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/02_LegacyMixed →]
