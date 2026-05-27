---
module: 20_FrameworkComparison
page: 06_PydanticAI
title: Pydantic AI — type-driven agents
estimated_minutes: 15
prereqs: [20_FrameworkComparison/05]
concepts: [PydanticAI, structured-output, type-safety]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/05_OpenAIAgentsSDK]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/07_LettaMemGPT →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 06 Pydantic AI

# 🧠 Pydantic AI

From the Pydantic team. Built around: **structured output is the point**, not the afterthought.

## Hello-world snippet

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class WeatherReport(BaseModel):
    city: str
    temperature_c: float
    description: str

agent = Agent(
    "openai:gpt-4o",
    output_type=WeatherReport,
    instructions="Return a WeatherReport for the requested city.",
    # NB: `system_prompt=` is the older kwarg and still accepted; `instructions=`
    # is the newer form (Pydantic AI 0.0.40+) and is the preferred way to pass
    # the system message. Verify against current pydantic-ai docs for your
    # installed version.
)

result = agent.run_sync("What's the weather in Tokyo?")
print(result.output)
# WeatherReport(city='Tokyo', temperature_c=22.0, description='Clear')
```

Notice: `output_type=WeatherReport` is the headline feature. The agent is contractually obligated to return a `WeatherReport`, with retries on schema-violation.

## Tools

Tools are typed Python functions registered with `@agent.tool` or `@agent.tool_plain`. Args use Python types; the runtime validates them with Pydantic.

```python
from pydantic_ai import Agent, RunContext

agent = Agent("openai:gpt-4o", deps_type=dict)

@agent.tool
def lookup(ctx: RunContext[dict], key: str) -> str:
    """Read from the dict dependency injected by deps."""
    return ctx.deps.get(key, "missing")
```

`deps_type` is a typed dependency injection — close to a typed `ToolContext`.

## Where Pydantic AI shines

- **Type-safe structured output.** If you need "this LLM call must return a `Customer`" with retries-on-failure, Pydantic AI is the cleanest API in the field.
- **Pydantic-native.** No translation layer if you already use Pydantic for your domain.
- **Testability.** Strong typing → easy mocks → reliable unit tests.

## Where ADK beats it

- **Multi-agent depth.** Pydantic AI has tool-using single agents that can call other agents; ADK has first-class sub_agents, workflows, transfers, A2A.
- **Production primitives.** ADK has memory services, sandboxes, MCP, evals, plugins, callbacks. Pydantic AI is leaner.
- **Provider breadth.** Both are multi-provider; ADK has more native integrations.
- **Streaming + Live.** ADK has bidi audio/video Live API; Pydantic AI is request/response (streaming text supported).

## When to pick Pydantic AI

- You want the LLM to act as a typed function returning a Pydantic model — and you want it bulletproof.
- You're already Pydantic-native.
- You don't need heavy multi-agent orchestration.

## When NOT to

- You need workflows, sandboxes, MCP/A2A, or GCP integration.

> 💡 **Synergy:** Pydantic AI and ADK can coexist. Use Pydantic AI for the leaf "extract this structured thing from text" calls inside an ADK agent's tool — and use ADK for the orchestration. The `output_schema` field on `LlmAgent` provides similar type-safety natively, but Pydantic AI's retry-on-violation is more aggressive.

> ❓ **Ask the student:** "ADK's `LlmAgent(output_schema=MyModel, ...)` does what's similar to Pydantic AI's `output_type=`. Where does ADK win, where does Pydantic AI?" *(ADK: wraps in a full agent runtime with tools/state. Pydantic AI: more rigorous about validation + retries on the output side.)*

[← Prev: 20_FrameworkComparison/05_OpenAIAgentsSDK]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/07_LettaMemGPT →]
