---
module: 12_CodeExecution
page: 07_DissectingSample
title: Dissecting the data-science analytics sub-agent
estimated_minutes: 30
prereqs: [12_CodeExecution/04]
concepts: [sample read-through, VertexAiCodeExecutor in practice, stateful=True]
icon: 🧪
in_production: false
detours_suggested: []
---

[← Prev: 12_CodeExecution/06_AgentEngineSandbox]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/08_InProduction →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 07 Dissecting data-science

# 🧪 A real `VertexAiCodeExecutor` in the wild

Sample: `/home/carloscabral/study/adk-samples/python/agents/data-science/`

The root agent is a multi-agent system. Among its sub-agents, `analytics_agent` is the one that actually executes Python. Open it:

```
data-science/
└── data_science/
    ├── agent.py                       ← root multi-agent
    └── sub_agents/
        ├── alloydb/                   ← NL2SQL on AlloyDB
        ├── analytics/
        │   └── agent.py               ← THE code-executor agent
        ├── bigquery/                  ← NL2SQL on BQ
        └── bqml/                      ← ML on BQ
```

### Read the file: `sub_agents/analytics/agent.py`

```python
from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor

from .prompts import return_instructions_analytics

analytics_agent = Agent(
    model=os.getenv("ANALYTICS_AGENT_MODEL", ""),
    name="analytics_agent",
    instruction=return_instructions_analytics(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)
```

Three things to notice and have the student name:

1. **`code_executor=` is attached at the agent level**, not on a tool. That's the shape — code execution is *not* a tool, it's a parallel mechanism the agent has.
2. **`stateful=True`** — the Vertex kernel persists across calls in one session. That's why an analytics flow can do `df = pd.read_csv(...)` once and then chain `.groupby(...)` queries.
3. **`optimize_data_file=True`** — uploaded data artifacts stay attached to the sandbox. No re-upload per call.

### How it slots into the bigger multi-agent

The root agent (in `data_science/agent.py`) doesn't execute code itself — it has tools that call sub-agents:

```python
from .tools import call_alloydb_agent, call_analytics_agent, call_bigquery_agent
```

The user asks "what's the average flight delay by airline?", root routes to `bigquery_agent` (NL2SQL → returns a DataFrame summary), then to `analytics_agent` (NL2Py → executes pandas to compute the aggregate or plot).

### Trace it conceptually

```
   user: "Plot average flight delay by airline."
        │
        ▼
   root_agent ──→ tool: call_bigquery_agent(...)
        │              │
        │              ▼
        │         bigquery_agent runs NL2SQL → returns small CSV artifact
        │
        ▼
   root_agent ──→ tool: call_analytics_agent(<dataframe>, "plot delay by airline")
                       │
                       ▼
                  analytics_agent:
                    LLM emits executable_code(language=python, code="...")
                       │
                       ▼
                    VertexAiCodeExecutor runs in Vertex sandbox
                       │
                       ▼
                    returns chart artifact + summary text
                       │
                       ▼
   root_agent integrates and replies to the user.
```

> ❓ **Ask the student:** "Why is code execution wired to a *sub-agent* instead of the root?" *(Expected: separation of concerns. Root orchestrates; analytics_agent specializes in 'execute Python on tabular data'. The sandbox blast radius is narrower; the prompt to the analytics agent is specialized to the task.)*

> 🤖 **Tutor:** Have the student trace one event from `examples/` in the sample (if present) and find the `executable_code` part. Seeing it on the wire makes the rest of the module click.

---

[← Prev: 12_CodeExecution/06_AgentEngineSandbox]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/08_InProduction →]
