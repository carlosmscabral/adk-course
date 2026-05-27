---
module: 05_MultiAgent
page: 08A_LangGraphAgent
title: LangGraphAgent — wrap a LangGraph workflow as an ADK agent
estimated_minutes: 20
prereqs: [05_MultiAgent/08]
concepts: [LangGraphAgent, BaseAgent, langgraph interop, CompiledGraph, thread_id]
icon: 🧠
in_production: false
detours_suggested: [LangGraph]
---

[← Prev: 05_MultiAgent/08_DissectingAgentTool](08_DissectingAgentTool.md)  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/09_InProduction →](09_InProduction.md)

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 08A LangGraphAgent

---

## 🧠 What it is

`LangGraphAgent` is an ADK-native `BaseAgent` subclass that wraps a compiled LangGraph `CompiledGraph` and exposes it as a regular ADK agent. From the runner's perspective it behaves like any other agent: one invocation in, an `Event` out. Inside, LangGraph is doing the actual work — nodes, edges, conditional routing, the LangGraph checkpointer for memory if you wired one.

It lives in `google.adk.agents.langgraph_agent` and is **not** re-exported from `google.adk.agents` top-level — import the path explicitly.

## 🛠 When you'd reach for it

- You already have a LangGraph workflow (some team built it last quarter) and you want it inside an ADK app without rewriting.
- You want LangGraph's specific control flow (e.g. its conditional edges + persistence story) inside a larger ADK graph or `sub_agents` tree.
- You are migrating *from* LangGraph *to* ADK and need a step where both coexist.

If you are starting fresh, prefer ADK's own graph `WorkflowAgent` (module 06) — same shape, no extra dependency, full ADK callback surface.

## 🛠 Runnable example

```python
"""Wrap a one-node LangGraph as an ADK agent. Requires:
    pip install google-adk[extensions] langgraph langchain-core
"""
import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from typing import TypedDict, Annotated
from operator import add

from google.adk.agents.langgraph_agent import LangGraphAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

class S(TypedDict):
    messages: Annotated[list, add]

def echo_node(state: S) -> S:
    last = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"langgraph saw: {last}")]}

builder = StateGraph(S)
builder.add_node("echo", echo_node)
builder.set_entry_point("echo")
builder.add_edge("echo", END)
graph = builder.compile()

root = LangGraphAgent(
    name="lg_agent",
    graph=graph,
    instruction="Echo what the user said with a prefix.",
)

async def main():
    runner = InMemoryRunner(agent=root, app_name="lg_demo")
    sess = await runner.session_service.create_session(app_name="lg_demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(text="hello")])
    async for ev in runner.run_async(user_id="u", session_id=sess.id, new_message=msg):
        if ev.is_final_response():
            print(ev.content.parts[0].text)

asyncio.run(main())
# → langgraph saw: hello
```

The `instruction=` is injected as a `SystemMessage` only on the **first** invocation against an empty graph state; subsequent turns rely on the LangGraph checkpointer (if any) or the ADK event history.

## ⚠️ Gotchas

- The class docstring says *"Currently a concept implementation."* That is upstream's own caveat — surface is small (`graph`, `instruction`, `name`) and likely to evolve.
- State models differ: LangGraph carries its own `state` dict per `thread_id`; ADK has `session.state`. They are **not** synchronised. Pick one as the source of truth.
- ADK's `before_model_callback` / `after_model_callback` (module 07) fire on ADK's `LlmAgent`s. They do **not** see the model calls that happen inside the LangGraph nodes. If you need uniform observability across both, hook at the LangGraph layer.

> 🚀 **In Production**
>
> The thread isolation key is `ctx.session.id` (see `_run_async_impl` line 71 of `langgraph_agent.py`). If you reuse a session across users, LangGraph's checkpointer will leak state between them. Always create a fresh session per (user, conversation). Pair with the resume / cancel discipline from module 02.

---

[← Prev: 05_MultiAgent/08_DissectingAgentTool](08_DissectingAgentTool.md)  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/09_InProduction →](09_InProduction.md)

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 08A LangGraphAgent
