---
module: 08_MCP
page: 03_Transports
title: MCP transports — stdio, HTTP-SSE, Streamable-HTTP
estimated_minutes: 20
prereqs: [08_MCP/02]
concepts: [StdioConnectionParams, SseConnectionParams, StreamableHTTPConnectionParams, StdioServerParameters]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 08_MCP/02_MCPToolset](02_MCPToolset.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/04_LifecycleManagement →](04_LifecycleManagement.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 03 Transports

# 🧠 Three transports, one decision

ADK ships three connection-params classes. Same MCP underneath; different wire mechanics:

| Transport         | Class                              | Use when                                                |
| ----------------- | ---------------------------------- | ------------------------------------------------------- |
| stdio             | `StdioConnectionParams`            | Local subprocess. CLI-style MCP servers (`uvx ...`).    |
| HTTP-SSE          | `SseConnectionParams`              | Long-lived event stream over HTTP. Legacy / push-heavy. |
| Streamable-HTTP   | `StreamableHTTPConnectionParams`   | Modern HTTP transport. The default you should pick.     |

## stdio — subprocess on the same machine

```python
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=["ant-intl-antom-mcp"],
            env={"API_KEY": os.getenv("API_KEY")},
        ),
    ),
)
```

ADK launches the subprocess on first call and pipes JSON-RPC over stdin/stdout. This is the pattern in `antom-payment/`. Good for dev, good for tools that *must* be local (filesystem, sensitive keys you'd rather not put in an HTTP header).

> ⚠️ **Gotcha** — every agent process spawns its own subprocess. If you run 100 concurrent agent invocations, you have 100 subprocesses. Scale with HTTP transports instead.

## HTTP-SSE — legacy long-lived stream

```python
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams

MCPToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse",
        headers={"Authorization": "Bearer ..."},
        timeout=5.0,
        sse_read_timeout=300.0,
    ),
)
```

SSE keeps an HTTP connection open and pushes events server→client. Older MCP servers use this. Two timeouts: connect (`timeout`) and read (`sse_read_timeout`).

## Streamable-HTTP — the modern default

```python
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8080/mcp",
        headers={"X-Api-Key": os.getenv("API_KEY")},
    ),
)
```

This is what `currency-agent` and `travel-planner-google-maps-mcp` use. Modern HTTP semantics, optional streaming, plays nicely with load balancers. **Pick this for new code unless you have a reason not to.**

## Decision tree

```
                       Need MCP server?
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
   Server must run                       Server already
   on the same box?                      runs on a host?
            │                                   │
           yes                                  no
            │                                   │
           Stdio                  ┌─────────────┴─────────────┐
                                  │                           │
                          Server's docs say                 default
                          "use SSE endpoint"?               (modern)
                                  │                           │
                                 yes                         Streamable-HTTP
                                  │
                                 SSE
```

> ❓ **Ask the student:** their company's internal MCP server runs in a Kubernetes pod with a Service in front. Which transport? (Streamable-HTTP — they get a stable URL, the LB can balance multiple replicas, no subprocess per agent.)

> 🚀 **In Production**
>
> For HTTP transports, **always set a timeout**. The default 5 s for connect is usually fine, but the long read timeouts (5 min on SSE) can hide a stuck server for minutes. Pair with `on_tool_error_callback` to surface the failure quickly.

[← Prev: 08_MCP/02_MCPToolset](02_MCPToolset.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/04_LifecycleManagement →](04_LifecycleManagement.md)
