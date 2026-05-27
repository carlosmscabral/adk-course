---
module: 08_MCP
page: 06_DissectingSample
title: Dissecting antom-payment, currency-agent, travel-planner
estimated_minutes: 30
prereqs: [08_MCP/05]
concepts: [MCPToolset, StdioConnectionParams, StreamableHTTPConnectionParams, FastMCP]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 08_MCP/05_ServingViaFastMCP](05_ServingViaFastMCP.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/07_InProduction →](07_InProduction.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 06 Dissecting Sample

# 🧠 Three samples, three patterns

> 🛠 **Have the student run:** open all three in tabs.

## 1. antom-payment — stdio consumer (minimal)

File: `/home/carloscabral/study/adk-samples/python/agents/antom-payment/antom-payemnt-agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = Agent(
    name="antom_payment_agent",
    model="gemini-2.0-flash",
    instruction="You are an Antom payment agent...",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["ant-intl-antom-mcp"],
                    env={
                        "GATEWAY_URL": os.getenv("GATEWAY_URL"),
                        "CLIENT_ID": os.getenv("CLIENT_ID"),
                        # ...auth env vars...
                    },
                ),
            ),
        )
    ],
)
```

Walk-through:

- The MCP server is a CLI tool (`ant-intl-antom-mcp`) launched via `uvx` (a pip-runner).
- `args=[...]` is the rest of the CLI.
- `env={...}` is how secrets get into the subprocess — **not** in the agent's heap, and never in a prompt.

Production note: this agent doesn't manage lifecycle. Acceptable for `adk web` / `adk run` since the runner tears down the toolset on exit. For a server, you'd add the `lifespan` pattern from page 04.

## 2. currency-agent — both ends in one repo

The repo has TWO ADK-relevant files:

### Server: `currency-agent/mcp-server/server.py`

```python
import asyncio, logging, os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("Currency MCP Server 💵")

@mcp.tool()
def get_exchange_rate(currency_from="USD", currency_to="EUR", currency_date="latest"):
    """Use this to get current exchange rate."""
    response = httpx.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    asyncio.run(mcp.run_async(
        transport="http",
        host="0.0.0.0",
        port=os.getenv("PORT", "8080"),
    ))
```

A FastMCP server that wraps the public Frankfurter FX API. Note `transport="http"` = Streamable-HTTP; `host="0.0.0.0"` makes it Cloud Run-friendly.

### Client: `currency-agent/currency_agent/agent.py`

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.a2a.utils.agent_to_a2a import to_a2a

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="currency_agent",
    instruction="You are a specialized assistant for currency conversions...",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp"),
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=10000)
```

Two things to notice:

1. The MCPToolset's URL is **configurable via env** — you can point at localhost in dev, Cloud Run in prod.
2. `to_a2a(...)` exposes the whole agent over A2A (Module 10 preview). This is the canonical "agent as a service" stack: A2A in front, MCP in back.

## 3. travel-planner-google-maps-mcp — MCP + callbacks + skills

File: `/home/carloscabral/study/adk-samples/python/agents/travel-planner-google-maps-mcp/travel_planner_agent/agent.py`

```python
maps_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    )
)
```

Notice the auth pattern: the API key goes in a header, not in the URL. ADK passes the headers to the MCP transport, which threads them onto every JSON-RPC call.

The full agent also wires the MCP toolset *through a `SkillToolset`* (Module 09 preview):

```python
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[travel_skill],
    additional_tools=[maps_mcp_toolset],
)
root_agent = Agent(model='gemini-2.5-flash', ..., tools=[my_skill_toolset])
```

So the LLM sees skills + Maps tools through one unified toolset. That's the integration story this Track is teaching.

> ❓ **Ask the student:** in `currency-agent`, what would break if you started the agent before the MCP server? (Answer: nothing immediately — connection is lazy. First tool call fails. That's why warm-up callbacks exist.)

[← Prev: 08_MCP/05_ServingViaFastMCP](05_ServingViaFastMCP.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/07_InProduction →](07_InProduction.md)
