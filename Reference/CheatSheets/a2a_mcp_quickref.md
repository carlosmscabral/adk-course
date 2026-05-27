# 📋 Cheat Sheet — A2A vs MCP quickref

The single most-confused topic in ADK. **A2A and MCP solve different problems in different directions.** Memorize the diagram before you start Module 10.

## ASCII — who talks to whom

```
                ┌──────────────────────────────────────────────────────┐
                │                                                      │
                │     ┌─────────────────┐                              │
                │     │ External caller │                              │
                │     │  (user, agent,  │                              │
                │     │   web app, …)   │                              │
                │     └────────┬────────┘                              │
                │              │                                       │
                │              │ A2A request (the WHOLE agent)         │
                │              │ ──────────────────────►               │
                │              ▼                                       │
                │     ╔═════════════════╗                              │
                │     ║                 ║                              │
                │     ║   Your ADK      ║                              │
                │     ║   AGENT         ║◄── A2A serves the agent      │
                │     ║                 ║       via to_a2a(agent)      │
                │     ║                 ║                              │
                │     ║  ┌───────────┐  ║                              │
                │     ║  │ tools=[…] │  ║                              │
                │     ║  └─────┬─────┘  ║                              │
                │     ║        │        ║                              │
                │     ╚════════╪════════╝                              │
                │              │                                       │
                │              │ MCP request (just ONE tool call)      │
                │              │ ──────────────────────►               │
                │              ▼                                       │
                │     ┌─────────────────┐                              │
                │     │  External MCP   │                              │
                │     │  server         │                              │
                │     │  (weather,      │                              │
                │     │   FS, Slack…)   │                              │
                │     └─────────────────┘                              │
                │                                                      │
                │     MCP brings TOOLS IN; A2A serves the AGENT OUT.   │
                │                                                      │
                └──────────────────────────────────────────────────────┘
```

## Side-by-side

| Dimension | **A2A (Agent-to-Agent)** | **MCP (Model Context Protocol)** |
|---|---|---|
| **Direction** | **OUTBOUND from your agent**: you expose your agent so others can reach in. | **INBOUND to your agent**: you reach out to pull tools from external servers. |
| **What's being exchanged** | Full agent invocations: a message goes in, the whole agent (with its tools, state, sub-agents) runs, a response comes out. | Individual tool calls: agent asks "call tool X with args Y," server runs it, returns the result. |
| **Primary ADK type IN** | `RemoteA2aAgent(agent_card=...)` — consume an external A2A agent as if it were a local sub-agent. `agent_card=` accepts a URL string, file path, or `AgentCard`. | `McpToolset(connection_params=...)` — consume external MCP server's tools as if they were local `FunctionTool`s. |
| **Primary ADK type OUT** | `to_a2a(root_agent)` — wrap your agent in an ASGI app, serve via uvicorn. | (None native — use FastMCP or the bare `mcp` SDK to author the server.) |
| **Discovery artifact** | `AgentCard` — JSON manifest describing the agent's capabilities, schemas, auth. Served at `/.well-known/agent-card.json` (modern canonical; legacy `/.well-known/agent.json` is the fallback if the a2a-sdk import fails). | Tools/resources/prompts list — fetched at handshake time from the MCP server. |
| **Transport** | HTTP (the A2A protocol over HTTP). | stdio (subprocess), SSE (server-sent events), Streamable-HTTP. |
| **Statefulness** | Session-aware — A2A sessions can persist across requests. | Mostly stateless per tool call (state lives in your ADK Session, not the MCP server). |
| **Auth surface** | A2A auth schemes in the AgentCard: `HTTPAuthSecurityScheme`, `APIKeySecurityScheme`, `OAuth2SecurityScheme`, `OpenIdConnectSecurityScheme`, `MutualTLSSecurityScheme`. Fields are snake_case (`bearer_format`, not `bearerFormat`). | MCP auth via the transport (HTTP headers, OAuth) plus `McpToolset(header_provider=...)` — a callable `(ReadonlyContext) -> dict[str,str]` that injects per-call headers. |
| **Typical use case** | Federate an existing agent into a larger system; expose your agent as a microservice. | Plug in third-party tools (filesystem, GitHub, Slack, custom) without re-implementing them. |
| **Don't use it for** | One-off tool calls. (That's MCP's job.) | Wrapping a whole conversational agent. (That's A2A's job.) |
| **Course module** | [Notes/10_A2A/](../../Notes/10_A2A/) | [Notes/08_MCP/](../../Notes/08_MCP/) |

## Code shape

### Expose your agent via A2A

```python
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import uvicorn

agent = LlmAgent(name="planner", model="gemini-2.5-flash", instruction="...")
app = to_a2a(agent)   # ASGI app
uvicorn.run(app, host="0.0.0.0", port=8000)
# AgentCard served at http://localhost:8000/.well-known/agent-card.json
# (legacy /.well-known/agent.json is only the fallback path if the a2a-sdk import fails)
```

### Consume an external A2A agent

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

booking_agent = RemoteA2aAgent(
    name="booking",
    agent_card="https://hotels.example.com/.well-known/agent-card.json",
    # agent_card= accepts: URL string, local file path, or an AgentCard object
)
# Use it like any other agent — drop into sub_agents=[…]
```

### Consume an external MCP server

```python
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters   # StdioServerParameters lives in the mcp SDK

toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        ),
    ),
)
agent = LlmAgent(name="fs", model="gemini-2.5-flash", instruction="...",
                 tools=[toolset])
```

### Serve your own MCP server (with FastMCP)

```python
from fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool
def get_weather(city: str) -> dict:
    """Get the current weather for a city."""
    return {"temp": 22, "city": city}

if __name__ == "__main__":
    mcp.run()   # speaks stdio MCP by default
```

## Common confusions

- **"I want to call another agent — should I use A2A or MCP?"** → A2A. The other agent runs end-to-end on its side. MCP would only give you one of its tools, not its reasoning.
- **"I want to add Google Maps to my agent."** → MCP. There is an existing Google Maps MCP server. Pull it in with `McpToolset`.
- **"Can I do both?"** → Yes, that's the M3 milestone drill: your agent serves itself via A2A while reaching out via MCP for tools.
- **`RemoteA2aAgent` is treated as an agent**, not a tool — drop into `sub_agents=[…]`, not `tools=[…]`. The parent's LLM picks it via `description=` the same way it picks any sub-agent.

## Where it's covered in the course

- MCP module: [Notes/08_MCP/](../../Notes/08_MCP/)
- A2A module: [Notes/10_A2A/](../../Notes/10_A2A/)
- The explicit comparison page: [Notes/10_A2A/04_A2A_vs_MCP](../../Notes/10_A2A/04_A2A_vs_MCP.md)
- FastMCP detour: [Notes/Detours/FastMCP.md](../../Notes/Detours/FastMCP.md)
- Milestone that integrates both: [Drills/M3_FederatedPlanner.md](../../Drills/M3_FederatedPlanner.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
