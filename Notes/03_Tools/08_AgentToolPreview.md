---
module: 03_Tools
page: 08_AgentToolPreview
title: AgentTool — call an agent like a tool (preview)
estimated_minutes: 10
prereqs: [03_Tools/07]
concepts: [AgentTool, composition, multi-agent-preview]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/07_ToolLimitations](07_ToolLimitations.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/09_LongRunningTool →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 08 AgentTool (preview)

# 🧠 `AgentTool` — preview only

This page is a **30-second teaser**. Module 05 is the deep dive.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

# A specialist sub-agent
websearch_agent = LlmAgent(
    name="websearch",
    model="gemini-2.5-flash",
    instruction="Search the web for the given query and summarize.",
    tools=[google_search],
)

# A coordinator that uses the sub-agent as if it were a tool
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction="Delegate web research to the `websearch` tool.",
    tools=[AgentTool(agent=websearch_agent)],
)
```

## 🧠 What's happening

The coordinator's LLM sees `websearch` as a tool — with the schema "takes a query, returns a summary." When it calls the tool, ADK actually **runs the sub-agent**, passing the query as the initial message, and returns the sub-agent's final reply as the tool result.

It's still the agent loop — just with another agent loop nested inside one of the tool calls.

## 🧠 Why preview here?

Because the *shape* is the lesson: from the coordinator's perspective, `AgentTool` is **just a tool**. It joins the `tools=[…]` list, has a name, a description, and a schema. Modules 05 and 06 explore *when* to compose this way (vs. SequentialAgent, ParallelAgent, Workflow), but the building block is right here.

## 🧠 Real-sample anchor

`academic-research` uses exactly this pattern:

```python
# from adk-samples/.../academic_research/agent.py
academic_coordinator = LlmAgent(
    name="academic_coordinator",
    model=MODEL,
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=academic_websearch_agent),
        AgentTool(agent=academic_newresearch_agent),
    ],
)
```

Two sub-agents, each wrapped as a tool. The coordinator picks which to call based on the user's question.

> ❓ **Ask the student:** when the coordinator calls `AgentTool(agent=websearch_agent)`, does the sub-agent share the coordinator's Session?
> *(Expected: technically the sub-agent runs inside the parent's invocation context — Module 05 walks through this carefully. For now: same Session, but events from the sub-agent are clearly labeled with the sub-agent's name.)*

> 🛠 **Have the student do this:** read [`academic-research/academic_research/agent.py`](../../../adk-samples/python/agents/academic-research/academic_research/agent.py) and identify each `AgentTool(...)` call. Don't worry about *why* yet — just notice the pattern. They'll meet it again, intentionally, in Module 05.

> 🤖 **Tutor:** keep this short. The point is recognition, not mastery. If the student wants to play with it now, encourage them — but don't slow Foundation Track here.

---

[← Prev: 03_Tools/07_ToolLimitations](07_ToolLimitations.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/09_LongRunningTool →]
