---
module: 08_MCP
page: 07_InProduction
title: MCP in production — auth, retries, version pinning, observability
estimated_minutes: 20
prereqs: [08_MCP/06]
concepts: [retry, circuit_breaker, auth, version_pin, observability]
icon: 🚀
in_production: true
detours_suggested: [PY_logging]
---

[← Prev: 08_MCP/06_DissectingSample](06_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/08_KnowledgeCheck →](08_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 07 In Production

# 🚀 Production checklist for MCP

## Retry + circuit-break with callbacks

MCP server failure should not equal agent failure for transient errors:

```python
async def retry_mcp_tool(tool, args, ctx, error):
    n = ctx.state.get("temp:mcp_retries", 0)
    if n >= 2:
        return {"error": "upstream_unavailable", "tool": tool.name}
    ctx.state["temp:mcp_retries"] = n + 1
    return None  # propagate this attempt; agent loop will retry
```

Wired as `on_tool_error_callback`. Combine with a `before_tool_callback` that opens the circuit when `temp:mcp_failures` exceeds a threshold.

## Auth: per-request tokens beat baked-in secrets

In `antom-payment/`, secrets live in subprocess env — fine because the subprocess is the trust boundary. For HTTP MCP servers, **never bake long-lived keys** into the agent process. The real ADK hook is `MCPToolset(header_provider=...)` — a callable that takes a `ReadonlyContext` and returns a dict of headers, evaluated on every MCP call (see `mcp_toolset.py:112-114` and the merge logic in `mcp_tool.py:386-398`):

```python
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

def per_user_headers(ctx):
    # ctx is a ReadonlyContext; reach the live session state via the invocation ctx.
    token = ctx._invocation_context.session.state.get("user:access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://mcp.example.com/v3/mcp"),
    header_provider=per_user_headers,
)
```

Each MCP call carries the right user's token, not your service account's blanket access. `MCPTool` merges these on top of any `auth_credential`-derived headers for that request — see `mcp_tool.py:386-398`. (There is no `tool_context.headers` attribute; the framework owns the wire-format headers.)

## Pin MCP server versions

The MCP server's tool list IS your contract. Pin versions:

```python
StdioServerParameters(command="uvx", args=["ant-intl-antom-mcp==1.4.2"])
```

```python
StreamableHTTPConnectionParams(url="https://mcp.example.com/v3/mcp")  # v3 in path
```

Without pinning, the upstream changes a tool signature and your agent silently produces wrong outputs.

## Log MCP latencies separately from LLM latencies

Two failure modes hide in your trace if you don't separate them:

- **Slow LLM** — model latency. Cure: smaller model, prompt caching.
- **Slow MCP** — upstream latency. Cure: cache the call result, add a circuit breaker.

The minimal pattern, in an `after_tool_callback`:

```python
import time, logging

def log_mcp_latency(tool, args, ctx, result):
    start = ctx.state.pop("temp:tool_start", None)
    if start and isinstance(tool, MCPTool):
        elapsed_ms = (time.monotonic() - start) * 1000
        logging.info("mcp.call name=%s ms=%.0f", tool.name, elapsed_ms)
    return None  # passthrough

def time_tool_start(tool, args, ctx):
    ctx.state["temp:tool_start"] = time.monotonic()
    return None
```

In a real deployment, ship to your tracing backend ([[15_Observability/00_Overview]]).

## Lifecycle (recap)

- **Scripts:** let `Runner.close()` walk the agent tree — it calls `await toolset.close()` on each toolset for you (`runners.py:2094-2144`). `MCPToolset` is not an async context manager.
- **Servers:** open at startup; rely on the auto-built `Runner`'s shutdown — or, for belt-and-braces, call `await toolset.close()` in `to_a2a(..., lifespan=...)`.
- **Tests:** mock the toolset, don't spin a real subprocess in CI unless you have to.

## Cross-link

- For retries-as-policy, see [[07_Callbacks/10_InProduction]].
- For deeper FastMCP server patterns (middleware, auth, mounting), take [[FastMCP]].
- For exposing your agent OVER A2A while it consumes MCP behind, that's the [[10_A2A/00_Overview]] story — and the M3 milestone drill combines both.

> 🤖 **Tutor:** if the student's prod plan is "I'll run the MCP server inline", redirect them to the two-process pattern. Inline = fate-shared crashes.

[← Prev: 08_MCP/06_DissectingSample](06_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/08_KnowledgeCheck →](08_KnowledgeCheck.yml)
