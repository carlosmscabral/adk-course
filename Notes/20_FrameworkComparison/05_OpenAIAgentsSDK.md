---
module: 20_FrameworkComparison
page: 05_OpenAIAgentsSDK
title: OpenAI Agents SDK — slim, OAI-shaped
estimated_minutes: 15
prereqs: [20_FrameworkComparison/04]
concepts: [OpenAI-Agents, Handoffs, Guardrails, Tools]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/04_AutoGen]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/06_PydanticAI →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 05 OpenAI Agents SDK

# 🧠 OpenAI Agents SDK

OpenAI's official agent framework (2025-). Successor to `Swarm`. Deliberately **narrow** in surface — four primitives: **Agent**, **Tool**, **Handoff**, **Guardrail**.

## Hello-world snippet

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}."

assistant = Agent(
    name="Weather agent",
    instructions="Help users with weather questions.",
    tools=[get_weather],
)

result = Runner.run_sync(assistant, "What's the weather in Tokyo?")
print(result.final_output)
```

## Multi-agent — "handoffs"

```python
from agents import Agent, handoff

researcher = Agent(name="Researcher", instructions="Find facts.")
writer = Agent(
    name="Writer",
    instructions="Write briefs. Hand off to Researcher if you need facts.",
    handoffs=[handoff(researcher)],
)
```

`handoff(agent)` is registered as a tool; when the model "calls" it, control passes. Same idea as ADK's `transfer_to_agent`.

## Guardrails

Pre-call and post-call validators. Pre = "is this user input safe to process"; Post = "is this output safe to return." Returns a boolean + optional reason; failure short-circuits the run.

## Where the OAI SDK shines vs ADK

- **Tightness.** The whole SDK fits in your head — Agent, Tool, Handoff, Guardrail. ADK has more concepts.
- **OpenAI-native.** Built-in vision, audio, structured outputs, file search — all wire up directly to OAI's Responses API.
- **Hosted tool execution.** OAI hosts the tool runtime when you use the Responses API server-side.

## Where ADK beats OAI Agents

- **Multi-provider.** ADK uses Gemini, Claude, Gemma, LiteLLM, OpenAI, Apigee. OAI SDK is OpenAI-first by design; non-OpenAI providers are second-class.
- **Workflow graphs.** OAI SDK has handoffs (linear chain) but no DAG. ADK has full graph workflows.
- **MCP.** ADK first-class; OAI Agents has it but as one option among many.
- **A2A.** ADK has it as a protocol; OAI SDK doesn't.
- **Evals & sandboxes.** ADK has more.
- **Memory services.** ADK has Memory Bank / RAG / InMemory; OAI Agents leans on the Responses API's `previous_response_id` (conversation continuity, not curated memory).

## When to pick OAI Agents

- You're committed to OpenAI models and want the least friction.
- You want a small surface area to teach a team.
- You're using OpenAI's Responses API for hosted tool exec.

## When NOT to

- You need multi-provider, multi-region, or non-OpenAI guarantees.
- You need graphs, deep evals, sandboxes, or A2A.

> ⚠️ **Gotcha:** OAI's `Runner.run_sync` is sync-blocking. If your app is async-heavy, use `await Runner.run(...)` instead.

> ❓ **Ask the student:** "What ADK feature is 'handoffs' equivalent to?" *(Answer: `transfer_to_agent` action — see the `agent_transfer` processor in `AutoFlow` from module 19/08.)*

[← Prev: 20_FrameworkComparison/04_AutoGen]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/06_PydanticAI →]
