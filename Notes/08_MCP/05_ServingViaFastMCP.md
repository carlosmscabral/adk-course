---
module: 08_MCP
page: 05_ServingViaFastMCP
title: Serving your tools via FastMCP
estimated_minutes: 25
prereqs: [08_MCP/04]
concepts: [FastMCP, mcp.tool, transport, http server]
icon: 🛠
in_production: true
detours_suggested: [FastMCP]
---

[← Prev: 08_MCP/04_LifecycleManagement](04_LifecycleManagement.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/06_DissectingSample →](06_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 05 Serving via FastMCP

# 🛠 Publishing your own MCP server

ADK consumes MCP. It does not bundle a server framework. The community standard — and what every official sample uses — is **FastMCP**: a decorator-based, one-file way to ship a server.

```bash
pip install fastmcp httpx
```

## The 12-line server

This is essentially `currency-agent/mcp-server/server.py`, stripped to its bones.

```python
# weather_server.py
import asyncio
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather Server 🌤")

@mcp.tool()
def fetch_weather(city: str) -> dict:
    """Return a mock weather report for the given city.

    Args:
        city: The city name to look up.

    Returns:
        A dict with city, temp_c, and condition fields.
    """
    return {"city": city, "temp_c": 21, "condition": "sunny"}

if __name__ == "__main__":
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
        )
    )
```

Run it:

```bash
python weather_server.py
# [INFO]: 🚀 MCP server started on port 8080
```

## What the decorator does

`@mcp.tool()` reflects the function signature into the MCP schema. **The docstring becomes the tool description** — same contract you learned with `FunctionTool` in Module 03. The argument types become the JSON-schema parameters.

If you've used FastAPI, this will feel identical. (FastMCP is by the same author.)

## Resources and prompts

`FastMCP` supports the other two MCP primitives too:

```python
@mcp.resource("file://greetings/{name}")
def greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.prompt("summarize")
def summarize_prompt(topic: str) -> str:
    return f"Write a 3-sentence summary of: {topic}"
```

The ADK client surfaces all three through `MCPToolset`'s discovery.

## Wiring the agent

```python
from google.adk import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

agent = Agent(
    model="gemini-2.5-flash",
    name="weather_buddy",
    instruction="Answer weather questions using the fetch_weather tool.",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://localhost:8080/mcp",
            )
        )
    ],
)
```

Two processes, talking MCP over HTTP. You can now reuse `weather_server.py` from any number of agents (or any other MCP client).

## Other transports

```python
asyncio.run(mcp.run_async(transport="http", ...))   # streamable-http
asyncio.run(mcp.run_async(transport="sse", ...))    # legacy SSE
asyncio.run(mcp.run_async(transport="stdio"))       # CLI-style
```

For a CLI-style server (`uvx your-pkg`), `transport="stdio"` is what you want.

> 🛠 **Have the student run:** copy `weather_server.py`, run it, point an `MCPToolset` at it, ask the agent "what's the weather in Tokyo?" Verify the mock response surfaces.

> 🧭 **If the student looks stuck:** suggest detour [[FastMCP]] for the deep dive (auth, middleware, mounting, sub-apps).

> 🚀 **In Production**
>
> Put `httpx` requests inside `@mcp.tool()` functions behind `httpx.AsyncClient` not `httpx.get` — FastMCP supports async tools and you'll need that throughput. Add a `/healthz` route via `mcp.custom_route(...)` so your LB can health-check the process.

[← Prev: 08_MCP/04_LifecycleManagement](04_LifecycleManagement.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/06_DissectingSample →](06_DissectingSample.md)
