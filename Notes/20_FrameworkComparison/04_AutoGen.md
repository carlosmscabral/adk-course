---
module: 20_FrameworkComparison
page: 04_AutoGen
title: AutoGen / AG2 — conversational multi-agent
estimated_minutes: 20
prereqs: [20_FrameworkComparison/03]
concepts: [AutoGen, AG2, group-chat, conversational-agents]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/03_CrewAI]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/05_OpenAIAgentsSDK →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 04 AutoGen

# 🧠 AutoGen (and AG2)

**AutoGen** started at Microsoft Research as the "agents talk to each other in chat" framework. After a community split in 2024, the active fork is **AG2** (`pip install autogen-agentchat` / `pip install ag2`). The original Microsoft `autogen-core` is also being maintained as a more event-driven runtime.

For this course's purposes, treat them as one ecosystem with two flavors: the **AgentChat layer** (conversational, the original UX) and the **Core layer** (lower-level event-driven runtime).

## Hello-world snippet (AgentChat)

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

model = OpenAIChatCompletionClient(model="gpt-4o")

writer = AssistantAgent("writer", model_client=model,
                        system_message="Draft the document.")
critic = AssistantAgent("critic", model_client=model,
                        system_message="Critique the draft. Say APPROVE when done.")

team = RoundRobinGroupChat(
    [writer, critic],
    termination_condition=TextMentionTermination("APPROVE"),
)

import asyncio
result = asyncio.run(team.run(task="Write a 100-word product brief about X."))
print(result)
```

## How multi-agent works

The metaphor is **a group chat**. Agents take turns speaking; a `Team` (`RoundRobinGroupChat`, `SelectorGroupChat`) decides whose turn it is. Termination conditions (textual mentions, max turns, etc.) end the chat.

This is fundamentally different from ADK's **structured `sub_agents` + workflow**: in AutoGen, the conversation IS the orchestration. In ADK, the workflow is explicit and the conversation is a side effect.

## Tools

`AssistantAgent` can be given tools (functions). The pattern is similar to others — signature + docstring → schema, agent decides when to invoke.

## Where AutoGen shines vs ADK

- **Conversational debugging.** You can read the chat log and see exactly what each agent said. Great for prompt iteration.
- **Research lineage.** Many papers prototype here.
- **Selector group chat.** A built-in pattern where an LLM selects the next speaker — emergent routing without a router node.

## Where ADK beats AutoGen

- **Structured workflows.** ADK's graph + sub_agent split makes "this happens before that" trivial; AutoGen needs careful termination conditions or chat order.
- **GCP / cloud integration.** AutoGen is provider-neutral but cloud-agnostic; no native Vertex tooling.
- **A2A protocol.** AutoGen has none.
- **MCP.** AutoGen has only community-built adapters; ADK has `MCPToolset`.
- **Evals.** ADK has first-class eval suites; AutoGen has community contribs.
- **Maturity.** The 2024 fork (AG2 vs autogen-core) means a single dependency choice is destabilizing; ADK's GA is a single supported track.

## When to pick AutoGen

- You're doing chat-emergent multi-agent research.
- You want a transparent "conversation log" as the primary artifact.
- You're already invested in the Microsoft ecosystem and want first-party support there.

## When NOT to

- You need a deterministic workflow with clear handoff points.
- You're shipping to production on GCP.
- You need A2A or MCP.

> ⚠️ **Gotcha:** the AutoGen vs AG2 vs autogen-core split is real and ongoing in 2026. Always check which fork the docs/tutorial you're reading targets — APIs are similar but not identical.

> ❓ **Ask the student:** "Compare AutoGen's `RoundRobinGroupChat` to ADK's `SequentialAgent`. What's the same? What's different?" *(Same: deterministic order. Different: AutoGen runs in a chat metaphor with termination conditions; ADK's `SequentialAgent` is a hard pipeline; ADK's `Workflow` graph is closer to AutoGen's `SelectorGroupChat` semantics.)*

[← Prev: 20_FrameworkComparison/03_CrewAI]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/05_OpenAIAgentsSDK →]
