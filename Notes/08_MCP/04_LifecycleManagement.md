---
module: 08_MCP
page: 04_LifecycleManagement
title: Lifecycle management — when MCP sessions open and close
estimated_minutes: 20
prereqs: [08_MCP/03]
concepts: [MCPToolset, async context manager, __aexit__, session pooling]
icon: ⚠️
in_production: true
detours_suggested: [PY_async]
---

[← Prev: 08_MCP/03_Transports](03_Transports.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/05_ServingViaFastMCP →](05_ServingViaFastMCP.md)

You are here: 🗺 Integration Track ▸ 08 MCP ▸ 04 Lifecycle Management

# ⚠️ The lifecycle bug that catches everyone

`MCPToolset` holds **open resources** — a subprocess (stdio), a streaming HTTP connection (SSE / Streamable-HTTP). They need to be closed.

```python
toolset = MCPToolset(connection_params=...)

# At program exit, if you don't close toolset:
#   - stdio: a leaked subprocess
#   - http:  a leaked connection slot
```

## Two lifecycle patterns

### Pattern A — per-session (short-lived)

For a script that runs an agent once and exits, the cleanest pattern is an `async with`:

```python
async def main():
    async with MCPToolset(connection_params=params) as toolset:
        agent = Agent(model="gemini-2.5-flash", tools=[toolset])
        runner = InMemoryRunner(agent)
        async for event in runner.run_async(...):
            print(event)
    # toolset closed on exit
```

ADK's runner does NOT auto-manage your toolsets — that's your code's job.

### Pattern B — long-lived (server / persistent app)

For a long-running agent server (e.g., `to_a2a()` + uvicorn), open the toolset once and close it on shutdown. The standard hook is `to_a2a(..., lifespan=...)`:

```python
from contextlib import asynccontextmanager
from google.adk.a2a.utils.agent_to_a2a import to_a2a

toolset = MCPToolset(connection_params=params)
agent = Agent(model="gemini-2.5-flash", tools=[toolset])

@asynccontextmanager
async def lifespan(app):
    # toolset opens lazily on first call; explicit warm-up optional
    yield
    await toolset.__aexit__(None, None, None)

app = to_a2a(agent, lifespan=lifespan)
```

The agent reuses the same MCP session across all incoming requests. Faster, fewer subprocesses, but you commit to clean teardown.

## What gets shared across calls

For Streamable-HTTP and SSE, the toolset reuses one HTTP connection. For stdio, the subprocess is reused too. **Concurrent tool calls share the session** — the MCP client serializes them on the wire, so you get no parallelism benefit from launching many at once.

If you need parallel MCP calls, run one toolset per concurrency lane (e.g., per-user) and cap the pool size.

## Common failure modes

| Symptom                                              | Cause                                              |
| ---------------------------------------------------- | -------------------------------------------------- |
| Hanging on shutdown                                  | Forgot `await toolset.__aexit__(...)`.             |
| "subprocess died" mid-conversation                   | Stdio server crashed. Catch in `on_tool_error_callback`. |
| Slow first tool call                                 | Lazy connection. Warm up in `before_agent_callback`. |
| `RuntimeError: Event loop is closed`                 | Toolset cleanup running in a dead loop — wrong lifecycle. |

## Cleanup callback pattern

For a self-contained agent module:

```python
toolset = MCPToolset(connection_params=...)

async def cleanup(callback_context):
    await toolset.__aexit__(None, None, None)

agent = Agent(
    model="gemini-2.5-flash",
    tools=[toolset],
    after_agent_callback=cleanup,  # closes on every invocation end
)
```

⚠️ This is fine for per-call lifecycle but creates churn. Prefer Pattern B for servers.

> 🛠 **Have the student run:** spawn a stdio toolset, call one tool, exit without `__aexit__`. Check `ps aux` for leftover children — there will be one. Now wrap in `async with` and rerun. Gone.

> 🚀 **In Production**
>
> Inventory your toolsets. Each one is a resource. Servers should warm them up at startup, tear them down at shutdown, and emit metrics on session-open / session-close so you notice leaks before they leak.

[← Prev: 08_MCP/03_Transports](03_Transports.md)  [↑ Map](../../MAP.md)  [Next: 08_MCP/05_ServingViaFastMCP →](05_ServingViaFastMCP.md)
