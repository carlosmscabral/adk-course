---
module: 10_A2A
page: 04_ConsumeWithRemoteA2aAgent
title: Consuming a remote agent with RemoteA2aAgent
estimated_minutes: 25
prereqs: [10_A2A/03]
concepts: [RemoteA2aAgent, agent_card, sub_agent, A2AClient, context_id]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10_A2A/03_ServeWithToA2a](03_ServeWithToA2a.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/05_A2A_vs_MCP →](05_A2A_vs_MCP.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 04 Consume with RemoteA2aAgent

# 🛠 `RemoteA2aAgent` — drop a remote agent into your agent tree

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

currency = RemoteA2aAgent(
    name="currency",
    description="Currency conversion agent.",
    agent_card="http://localhost:10000/.well-known/agent.json",
)
```

`RemoteA2aAgent` is a `BaseAgent` subclass. From the rest of your code's perspective, **it is an agent.** You can:

- Use it as a `sub_agent` in an `LlmAgent`.
- Pass it to an `AgentTool` (Module 05).
- Slot it into a `SequentialAgent` / `ParallelAgent` / `WorkflowAgent`.

## Three ways to specify the remote

```python
# (1) URL to the agent.json
RemoteA2aAgent(name="x", agent_card="https://example.com/.well-known/agent.json")

# (2) Path to a local agent.json file
RemoteA2aAgent(name="x", agent_card="./remote_cards/x.json")

# (3) Pre-built AgentCard object
from a2a.types import AgentCard
card = AgentCard(...)
RemoteA2aAgent(name="x", agent_card=card)
```

URL is the most common. File is useful for offline / dev. Object is useful for tests.

## Using it as a sub-agent

```python
from google.adk import Agent

planner = Agent(
    model="gemini-2.5-flash",
    name="planner",
    instruction=(
        "Use the currency sub-agent for FX conversions and the "
        "weather sub-agent for forecasts."
    ),
    sub_agents=[
        RemoteA2aAgent(
            name="currency",
            agent_card="http://localhost:10000/.well-known/agent.json",
        ),
        RemoteA2aAgent(
            name="weather",
            agent_card="http://weather.internal/.well-known/agent.json",
        ),
    ],
)
```

When `planner` `transfer_to_agent("currency")`, the call goes over the wire to the currency server. The parent agent doesn't know (or care) that the child is remote.

## What happens under the hood

1. First use → `RemoteA2aAgent` fetches the AgentCard.
2. Builds an `A2AClient` against the card's `url`.
3. Each user message → `client.send_message(...)`.
4. Returns a `Task` object → ADK adapts it into events the parent agent sees.
5. The remote's `context_id` is captured into session state so multi-turn works.

## Multi-turn / context propagation

```python
# First turn:
send_message(text="how much is 100 USD?")
# → response Task carries a context_id

# Second turn (in the same session):
send_message(text="in EUR", context_id=stored_context_id)
# → server resumes the same conversation
```

ADK threads `context_id` automatically when you use the agent as a sub-agent. If you call the A2A client directly (like `test_client.py` does), you manage it yourself.

## Timeouts and HTTP clients

```python
RemoteA2aAgent(
    name="x",
    agent_card=URL,
    timeout=30.0,                    # HTTP timeout in seconds
    httpx_client=my_shared_client,   # optional shared client
)
```

For a server with many remotes, share one `httpx.AsyncClient` across them to pool connections.

> 🛠 **Have the student run:** spawn the currency agent on port 10000 (from page 03). In another script, create a `RemoteA2aAgent(name="cc", agent_card="http://localhost:10000/.well-known/agent.json")` and use it as the sole sub-agent of a parent `Agent`. Ask "convert 50 USD to JPY". Confirm the round-trip works.

> ⚠️ **Gotcha** — `RemoteA2aAgent` resolves the card lazily on first use. If the server is down at startup, you find out at first request. Pair with an `on_tool_error_callback` for graceful UX.

> 🚀 **In Production**
>
> Pin the URL to a specific version path (`/v1/...`). When the remote rolls out a v2, you update your URL deliberately rather than discovering breakage in prod. See `07_InProduction.md`.

[← Prev: 10_A2A/03_ServeWithToA2a](03_ServeWithToA2a.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/05_A2A_vs_MCP →](05_A2A_vs_MCP.md)
