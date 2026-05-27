---
module: 20_FrameworkComparison
page: 03_CrewAI
title: CrewAI — role-based "teams of agents"
estimated_minutes: 20
prereqs: [20_FrameworkComparison/02]
concepts: [CrewAI, Agent, Task, Crew, roles]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/02_LangChainAndLangGraph]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/04_AutoGen →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 03 CrewAI

# 🧠 CrewAI

**CrewAI** (João Moura, 2024-) pioneered the "role-based crew" metaphor: you describe agents as **personas** (role, goal, backstory) and **tasks** (description, expected output). A `Crew` runs them in `sequential` or `hierarchical` process.

## Hello-world snippet

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

researcher = Agent(
    role="Research Analyst",
    goal="Find the latest news about {topic}",
    backstory="You're an experienced analyst skilled at sourcing reliable info.",
    tools=[SerperDevTool()],
    verbose=True,
)

writer = Agent(
    role="Tech Writer",
    goal="Write a 200-word brief on {topic}",
    backstory="You translate research into approachable prose.",
    verbose=True,
)

research_task = Task(
    description="Research the topic: {topic}",
    expected_output="A bullet list of 5 facts with sources.",
    agent=researcher,
)

write_task = Task(
    description="Using the research, write the brief.",
    expected_output="A 200-word article.",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

result = crew.kickoff(inputs={"topic": "ADK 2.0"})
print(result)
```

## How multi-agent works

CrewAI is **role-as-prompt-template**. Each agent's "role", "goal", and "backstory" are stitched into the system prompt. The `Crew.process`:

- `Process.sequential` — tasks run in order; each task's output is appended to the next task's context.
- `Process.hierarchical` — a manager agent (extra LLM call) delegates to workers and aggregates.

## Tools

`from crewai_tools import ...` for built-ins (web search, file IO, vector retrieval). Custom tools subclass `BaseTool` or wrap a function. Schema generation is similar to ADK's `FunctionTool` (signature + docstring → JSON schema).

## Where CrewAI shines vs ADK

- **Onboarding for prompt engineers.** "Define a role" is the whole mental model. No async, no `Event`, no `InvocationContext`.
- **Templated tasks.** `{topic}` substitution is built-in and idiomatic — feels natural for content workflows.
- **Heavy out-of-the-box opinions.** A `Crew` "just works" with reasonable defaults.

## Where ADK beats CrewAI

- **Production primitives.** ADK has eval suites, A2A protocol, MCP first-class, observability, code-exec sandboxes — CrewAI has most of these only via plugins (some not at all).
- **Multi-LLM provider depth.** ADK supports Vertex Gemini, Claude, Gemma, LiteLLM, OpenAI, Apigee. CrewAI supports many but with less first-party rigor.
- **Graph workflows.** CrewAI's `hierarchical` is a single pattern; ADK gives you a full DAG.
- **State / session model.** CrewAI's "memory" is bolt-on (short_term, long_term via plugins); ADK has services first-class.
- **Streaming.** ADK has Live API + bidi streaming. CrewAI is request/response.

## When to pick CrewAI

- Team of prompt engineers (not Python engineers).
- Content / research / report generation workflows.
- Fast prototypes where "team of personas" maps cleanly to the domain.
- You want the lowest possible barrier to "running multi-agent."

## When to NOT pick CrewAI

- You need MCP, A2A, deep evals, sandboxed code exec, streaming, or GCP-native deployment.
- Your workflow is graph-shaped (not sequential / hierarchical).
- Cost matters — `hierarchical` mode is wasteful (extra manager LLM calls).

> ⚠️ **Gotcha:** CrewAI's role/goal/backstory all become system prompt text. Long backstories burn tokens on every call. Keep them short.

> ❓ **Ask the student:** "If your stakeholder said 'build me a research crew that outputs a weekly digest' — which framework would you reach for in week 1, and which would you migrate to in month 6?" *(Reasonable answer: CrewAI for week 1, ADK for month 6 — because by then you need evals, observability, and probably MCP-served data.)*

[← Prev: 20_FrameworkComparison/02_LangChainAndLangGraph]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/04_AutoGen →]
