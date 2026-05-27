---
module: 05_MultiAgent
page: 08_DissectingAgentTool
title: Quick read — financial-advisor's AgentTool stack
estimated_minutes: 30
prereqs: [05_MultiAgent/07]
concepts: [AgentTool, coordinator-pattern, contrast-with-sub_agents]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 05_MultiAgent/07_DissectingLlmAuditor]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/08A_LangGraphAgent →](08A_LangGraphAgent.md)

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 08 Dissecting AgentTool

## 🛠 The artifact

```
adk-samples/python/agents/financial-advisor/
└── financial_advisor/
    ├── agent.py                          ← root: LlmAgent with 4 AgentTools
    ├── prompt.py
    └── sub_agents/
        ├── data_analyst/agent.py         ← LlmAgent + google_search
        ├── trading_analyst/agent.py
        ├── execution_analyst/agent.py
        └── risk_analyst/agent.py
```

## 📁 The root — `financial_advisor/agent.py`

```python
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from . import prompt
from .sub_agents.data_analyst import data_analyst_agent
from .sub_agents.execution_analyst import execution_analyst_agent
from .sub_agents.risk_analyst import risk_analyst_agent
from .sub_agents.trading_analyst import trading_analyst_agent

MODEL = "gemini-2.5-pro"

financial_coordinator = LlmAgent(
    name="financial_coordinator",
    model=MODEL,
    description="guide users through a structured process...",
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=trading_analyst_agent),
        AgentTool(agent=execution_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)

root_agent = financial_coordinator
```

## 🧠 Contrast with llm-auditor

| | `llm-auditor` | `financial-advisor` |
|---|---|---|
| Root type | `SequentialAgent` | `LlmAgent` |
| Children passed as | `sub_agents=[...]` | `tools=[AgentTool(agent=...)]` |
| Order | Fixed (critic → reviser) | LLM-driven (coordinator decides) |
| Cursor behavior | Moves to each child | Stays on coordinator; tools return strings |
| User-visible author | Each child speaks directly | Only the coordinator speaks |

The financial coordinator can call `data_analyst` to fetch a quote, *then* call `trading_analyst` with that quote, *then* call `risk_analyst`, and finally synthesize a unified recommendation. With `sub_agents=` and `transfer_to_agent`, the cursor would jump to one specialist and the orchestration would dissolve.

## 📁 One specialist — `sub_agents/data_analyst/agent.py`

```python
from google.adk import Agent
from google.adk.tools import google_search
from . import prompt

MODEL = "gemini-2.5-pro"

data_analyst_agent = Agent(
    model=MODEL,
    name="data_analyst_agent",
    instruction=prompt.DATA_ANALYST_PROMPT,
    output_key="market_data_analysis_output",
    tools=[google_search],
)
```

A vanilla `LlmAgent` with its own tools. The fact that it's wrapped as `AgentTool(agent=data_analyst_agent)` upstream doesn't change anything in *this* file — it remains usable standalone (you could `adk run` it directly).

**That portability is the AgentTool's superpower.** Same agent, two contexts: standalone or wrapped.

## 🧠 The output_key here is for `Session`, not for the parent

`data_analyst_agent` writes `output_key="market_data_analysis_output"`. The coordinator's instruction can reference `{market_data_analysis_output}` to grab it. So we have **both** signaling channels at once: the AgentTool's return value (immediate, conversational) **and** state-keyed output (durable, multi-step).

## ❓ Comprehension checks

> ❓ **Ask the student:**
> 1. If you wrapped `critic_agent` from llm-auditor as an `AgentTool` under a new coordinator, what would change about the user experience?
> 2. In financial-advisor, who controls call order — the coordinator's LLM or framework code?
> 3. Why is `data_analyst_agent` still useful as a standalone agent even though it lives inside `financial-advisor`?

---

[← Prev: 05_MultiAgent/07_DissectingLlmAuditor]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/08A_LangGraphAgent →](08A_LangGraphAgent.md)
