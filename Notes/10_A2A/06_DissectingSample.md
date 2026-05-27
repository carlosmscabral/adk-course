---
module: 10_A2A
page: 06_DissectingSample
title: Dissecting currency-agent — A2A serve + MCP consume + A2A client
estimated_minutes: 30
prereqs: [10_A2A/05]
concepts: [to_a2a, A2AClient, A2ACardResolver, test_client, McpToolset]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 10_A2A/05_A2A_vs_MCP](05_A2A_vs_MCP.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/07_InProduction →](07_InProduction.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 06 Dissecting Sample

# 🧠 The full stack in one repo

> 🛠 **Have the student run:** open `/home/carloscabral/study/adk-samples/python/agents/currency-agent/` and read these three files side by side: `mcp-server/server.py`, `currency_agent/agent.py`, `currency_agent/test_client.py`.

The repo runs three processes:

```
    MCP server (port 8080)  ◄── HTTP/MCP ──  ADK agent (port 10000)  ◄── HTTP/A2A ──  test_client
    fastmcp + Frankfurter                    LlmAgent + McpToolset                    a2a-sdk
```

## File 1 — `mcp-server/server.py` (already covered in Module 08)

Skim review:

```python
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
    asyncio.run(mcp.run_async(transport="http", host="0.0.0.0", port=os.getenv("PORT", "8080")))
```

A FastMCP server. One tool. Runs at `http://localhost:8080/mcp`.

## File 2 — `currency_agent/agent.py` (the A2A server)

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

SYSTEM_INSTRUCTION = (
    "You are a specialized assistant for currency conversions. "
    "Your sole purpose is to use the 'get_exchange_rate' tool to answer "
    "questions about currency exchange rates. "
    "If the user asks about anything other than currency conversion or "
    "exchange rates, politely state that you cannot help with that topic..."
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="currency_agent",
    description="An agent that can help with currency conversions",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp"),
            )
        )
    ],
)

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10000)
```

Two things stacked in 25 lines:

- **MCP in back:** the `McpToolset` points at the FastMCP server.
- **A2A in front:** `to_a2a(root_agent, port=10000)` exposes the whole agent.

Started via:

```bash
uvicorn currency_agent.agent:a2a_app --host localhost --port 10000
```

After it boots, the AgentCard is live at `http://localhost:10000/.well-known/agent-card.json`. The card's `skills` list is auto-built and will include `get_exchange_rate` (because the McpToolset's tools are reflected up into the card).

## File 3 — `currency_agent/test_client.py` (the A2A client)

This file uses the **raw `a2a-sdk` Python client**, not `RemoteA2aAgent`. Either works; the SDK is lower-level and shows the moving parts.

```python
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

async def main():
    async with httpx.AsyncClient() as httpx_client:
        # Step 1: fetch the AgentCard
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=AGENT_URL)
        agent_card = await resolver.get_agent_card()

        # Step 2: build a client against that card
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        # Step 3: send a message
        payload = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "how much is 100 USD in CAD?"}],
                "messageId": uuid4().hex,
            },
        }
        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        response = await client.send_message(request)
        print(response.root.model_dump_json(exclude_none=True))
```

Walk-through:

- **`A2ACardResolver`** fetches `/.well-known/agent-card.json`. Returns an `AgentCard`.
- **`A2AClient(httpx_client=..., agent_card=...)`** wraps the RPC URL from the card.
- **`SendMessageRequest`** carries a `MessageSendParams` carrying the user message. The `messageId` is a uuid so the server can dedupe.
- The response is a `SendMessageResponse` whose `.root` is either a success (`Task`) or an error.

The `test_client.py` file then does a **multi-turn** test: it sends "how much is 100 USD?" first; the agent returns `task.status.state == TaskState.input_required`; the client sends "in GBP" with the same `context_id`. That round-trips through the agent's session state.

## What you've now learned end-to-end

1. **MCP** (Module 08): how the agent picks up its `get_exchange_rate` tool.
2. **Callbacks** (Module 07): you could add `after_tool_callback` to log every FX lookup.
3. **A2A** (this module): how external callers reach the agent.

This is the production triad. M3 (next milestone) layers Skills (Module 09) on top.

[← Prev: 10_A2A/05_A2A_vs_MCP](05_A2A_vs_MCP.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/07_InProduction →](07_InProduction.md)
