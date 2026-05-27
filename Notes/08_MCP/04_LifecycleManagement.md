---
module: 08_MCP
page: 04_LifecycleManagement
title: Lifecycle management — when MCP sessions open and close
estimated_minutes: 20
prereqs: [08_MCP/03]
concepts: [McpToolset, Runner auto-cleanup, toolset.close, session pooling]
icon: ⚠️
in_production: true
detours_suggested: [PY_async]
---

[← Prev: 08_MCP/03_Transports](03_Transports.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/05_ServingViaFastMCP →](05_ServingViaFastMCP.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 04 Lifecycle Management

# ⚠️ The lifecycle bug that catches everyone

`McpToolset` holds **open resources** — a subprocess (stdio), a streaming HTTP connection (SSE / Streamable-HTTP). They need to be closed.

```python
toolset = McpToolset(connection_params=...)

# At program exit, if you don't close toolset:
#   - stdio: a leaked subprocess
#   - http:  a leaked connection slot
```

## Two lifecycle patterns

### Pattern A — per-session (short-lived)

For a script that runs an agent once and exits, let the `Runner` close the toolset for you:

```python
async def main():
    toolset = McpToolset(connection_params=params)
    agent = Agent(model="gemini-2.5-flash", tools=[toolset])
    runner = InMemoryRunner(agent)
    try:
        async for event in runner.run_async(...):
            print(event)
    finally:
        await runner.close()   # walks the agent tree, closes every toolset
```

ADK's `Runner` DOES auto-manage your toolsets. `Runner.close()` calls
`_collect_toolset(agent)` to walk sub-agents and then `_cleanup_toolsets(...)`
to `await toolset.close()` on each one with a 10-second timeout (see
`runners.py:2094-2144`). The toolset's own docstring (`mcp_toolset.py:92`) says
"Cleanup is handled automatically by the agent framework." `McpToolset` does
**not** implement `__aenter__` / `__aexit__` — `async with McpToolset(...)`
will raise `AttributeError`.

If you need explicit teardown outside a `Runner` (e.g., a one-off script that
constructed the toolset directly), call `await toolset.close()` yourself.

### Pattern B — long-lived (server / persistent app)

For a long-running agent server (e.g., `to_a2a()` + uvicorn), open the toolset once and close it on shutdown. The standard hook is `to_a2a(..., lifespan=...)`:

```python
from contextlib import asynccontextmanager
from google.adk.a2a.utils.agent_to_a2a import to_a2a

toolset = McpToolset(connection_params=params)
agent = Agent(model="gemini-2.5-flash", tools=[toolset])

@asynccontextmanager
async def lifespan(app):
    # toolset opens lazily on first call; explicit warm-up optional
    yield
    await toolset.close()

app = to_a2a(agent, lifespan=lifespan)
```

The agent reuses the same MCP session across all incoming requests. Faster, fewer subprocesses, but you commit to clean teardown. (You can also rely on the auto-built `Runner` inside `to_a2a` to close the toolset when it shuts down — explicit `lifespan` cleanup is belt-and-braces.)

## What gets shared across calls

For Streamable-HTTP and SSE, the toolset reuses one HTTP connection. For stdio, the subprocess is reused too. **Concurrent tool calls share the session** — the MCP client serializes them on the wire, so you get no parallelism benefit from launching many at once.

If you need parallel MCP calls, run one toolset per concurrency lane (e.g., per-user) and cap the pool size.

## Common failure modes

| Symptom                                              | Cause                                              |
| ---------------------------------------------------- | -------------------------------------------------- |
| Hanging on shutdown                                  | Constructed `McpToolset` outside a `Runner` and never called `await toolset.close()`. |
| `AttributeError: __aenter__`                         | You tried `async with McpToolset(...)`. It is not an async context manager — use `Runner.close()` or `await toolset.close()`. |
| "subprocess died" mid-conversation                   | Stdio server crashed. Catch in `on_tool_error_callback`. |
| Slow first tool call                                 | Lazy connection. Warm up in `before_agent_callback`. |
| `RuntimeError: Event loop is closed`                 | Toolset cleanup running in a dead loop — wrong lifecycle. |

## Cleanup callback pattern

For a self-contained agent module that wants per-invocation churn instead of process-lifetime reuse:

```python
toolset = McpToolset(connection_params=...)

async def cleanup(callback_context):
    await toolset.close()

agent = Agent(
    model="gemini-2.5-flash",
    tools=[toolset],
    after_agent_callback=cleanup,  # closes on every invocation end
)
```

⚠️ This is fine for per-call lifecycle but creates churn. Prefer Pattern B for servers, and prefer letting `Runner.close()` handle it for scripts.

> 🛠 **Have the student run:** spawn a stdio toolset, call one tool, exit the process without ever calling `await runner.close()` (or `await toolset.close()`). Check `ps aux` for leftover children — there will be one. Now wrap the run in `try / finally: await runner.close()` and rerun. Gone.

> 🚀 **In Production**
>
> Inventory your toolsets. Each one is a resource. Servers should warm them up at startup, tear them down at shutdown, and emit metrics on session-open / session-close so you notice leaks before they leak.

[← Prev: 08_MCP/03_Transports](03_Transports.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/05_ServingViaFastMCP →](05_ServingViaFastMCP.md)
