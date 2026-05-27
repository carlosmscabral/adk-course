---
module: Detours
page: FastMCP
title: FastMCP — the decorator framework for MCP servers
estimated_minutes: 30
icon: 📡
prereqs: []
concepts: [FastMCP, mcp_tool, mcp_resource, mcp_prompt, stdio, sse, streamable_http]
---

[← Back to Map](../../MAP.md)

Triggered from: `08_MCP` (authoring a server you can plug into `McpToolset`).

> Take this detour the first time you need to *write* (not just consume) an MCP server. The raw `mcp` SDK works but is verbose; FastMCP is the FastAPI-style decorator layer that 90% of real-world servers use. ~30 min.

---

## 📡 1. Two SDKs, same protocol

```
  protocol:   MCP wire format (JSON-RPC over stdio/SSE/HTTP)
       ↑                ↑
  raw `mcp`        `fastmcp`
  (low-level,      (decorators,
   verbose)         batteries included)
```

The raw `mcp` Python SDK gives you handler classes, manual schema dicts, and explicit transport plumbing — useful if you need exotic behavior. **FastMCP** wraps that with decorators that look like FastAPI/Flask, infers schemas from type hints, and handles transport selection with a flag. ADK's `McpToolset` doesn't care which you used — it just speaks MCP.

---

## 📡 2. The 15-line server

```python
# weather_server.py
from datetime import datetime, timezone
from fastmcp import FastMCP

mcp = FastMCP("weather-server")

@mcp.tool
def now() -> str:
    """Return the current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()

@mcp.tool
def get_weather(city: str) -> dict:
    """Look up the current weather for a city."""
    return {"city": city, "temp_c": 22, "condition": "sunny"}

if __name__ == "__main__":
    mcp.run()    # stdio by default
```

`@mcp.tool` introspects the function — type hints become the JSON schema, the docstring becomes the description. Same contract as ADK's `FunctionTool`, which is not a coincidence (both target LLM consumers).

---

## 📡 3. The three MCP primitives

MCP isn't just tools. The protocol defines three resource types and FastMCP exposes each:

| primitive   | decorator          | what it is                                  | LLM sees it as       |
|-------------|--------------------|---------------------------------------------|----------------------|
| **Tool**    | `@mcp.tool`        | callable side-effecting function            | a tool to invoke     |
| **Resource**| `@mcp.resource`    | addressable read-only data (by URI)         | context to fetch     |
| **Prompt**  | `@mcp.prompt`      | parameterized prompt template               | a starter message    |

```python
@mcp.resource("config://app")
def app_config() -> str:
    """Static config the client can read on connect."""
    return open("config.yaml").read()

@mcp.prompt
def code_review(language: str, code: str) -> str:
    """Ask the model to review code in `language`."""
    return f"Review this {language} code:\n\n{code}"
```

Most ADK use cases want tools. Resources are useful when the client wants to *pre-load* context (RAG-ish); prompts standardize how downstream clients phrase requests.

---

## 📡 4. Transport — stdio, SSE, Streamable HTTP

```python
mcp.run()                                  # stdio (default; subprocess piping)
mcp.run(transport="sse", port=8000)        # legacy HTTP server-sent events
mcp.run(transport="http", port=8000)       # Streamable HTTP — newer HTTP streaming
```

(FastMCP 2.x renamed this to `transport="http"`; the old alias `"streamable-http"` is still accepted.)

Rule of thumb:

- **stdio** → local servers spawned per-process. Lowest overhead, no auth needed (the parent owns the subprocess).
- **http** → remote servers, multiple clients, behind a load balancer. The 2026 recommended HTTP transport (this is Streamable HTTP).
- **sse** → older HTTP option; only use if you must interop with pre-2025 clients.

ADK points at each one differently — `McpToolset` accepts a stdio command list or a URL.

---

## 📡 5. Auth and composition

**Per-request auth via headers** — pull them from the active HTTP request via the dependency helper:

```python
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP("secure-server")

@mcp.tool
def whoami() -> str:
    token = get_http_headers().get("authorization", "")
    return f"hello, holder of {token[:8]}..."
```

`get_http_headers()` (documented at gofastmcp.com/servers/context) reads from the current request and returns `{}` under stdio, so the same tool function is transport-agnostic. For HTTP transports, slot in any ASGI middleware (e.g., OAuth introspection, rate limiting) for boundary checks.

**Mounting** — one FastMCP can be hosted under another, so a single endpoint serves multiple logical servers. The signature is `root.mount(child, namespace=...)` — FastMCP composition namespaces **tool names**, not URL paths:

```python
root = FastMCP("root")
weather = FastMCP("weather")
root.mount(weather, namespace="weather")
root.run(transport="http", port=8000)
# Tools register under namespaced names: weather_get_weather, weather_now, ...
```

Useful when you have a fleet of small servers and want one process / one auth boundary.

---

## 📡 6. FastMCP vs raw `mcp` SDK — when each wins

| concern               | FastMCP                          | raw `mcp`                       |
|-----------------------|----------------------------------|----------------------------------|
| schema generation     | from type hints, automatic       | hand-write JSON schema dicts     |
| transport             | one flag                         | wire up `Server.run_stdio()` etc. |
| auth / middleware     | ASGI-style hooks                 | DIY                              |
| custom handlers       | escape hatches but lossy         | full control                     |
| typical LOC for a 3-tool server | ~30                    | ~150                             |

If you're not sure, start with FastMCP. You can drop into raw `mcp` for the one handler that needs it.

> **🚀 In Production**
>
> Tool *outputs* from any MCP server are untrusted input to your agent — a malicious or compromised server can stuff prompt-injection payloads into the response. Sanitize at the agent boundary (`after_tool_callback`) and prefer least-privilege tool sets. See [[PromptInjection]] section 2.

---

## 🛠 Have the student try

Write the 15-line server above into `weather_server.py`, then point ADK at it:

```python
# inside an ADK agent file
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters  # comes from the upstream `mcp` package

mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["weather_server.py"],
        ),
        timeout=10.0,
    ),
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="weather_agent",
    instruction="Use the weather tools to answer.",
    tools=[mcp_tools],
)
```

> ⚠️ `StdioServerParameters` is **not** exported by `google.adk.tools.mcp_tool` — see `google/adk/tools/mcp_tool/__init__.py` (only `SseConnectionParams`, `StdioConnectionParams`, `StreamableHTTPConnectionParams`, `MCPTool`, `McpToolset` and their alias forms are re-exported). Import `StdioServerParameters` from `mcp` directly.
>
> Passing a raw `StdioServerParameters` to `connection_params=` does work (`mcp_session_manager.py:200-204`, `mcp_toolset.py:99-105`), but the recommended pattern is to wrap it in `StdioConnectionParams(server_params=..., timeout=...)` so you get timeout control — `StdioServerParameters` alone has none.

Then ask the agent "what time is it?" and "what's the weather in NYC?" — you should see two distinct MCP tool invocations in the event stream. Confirm by adding a `print` inside `now()` / `get_weather()`.

Bonus: switch the server to `mcp.run(transport="http", port=8000)` and update the ADK side to point at `http://localhost:8000`. Notice the agent code didn't change.

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — likely `08_MCP/03_AuthoringServer` or `08_MCP/05_DissectingSample`.
