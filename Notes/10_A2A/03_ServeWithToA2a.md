---
module: 10_A2A
page: 03_ServeWithToA2a
title: Serving an ADK agent with to_a2a()
estimated_minutes: 25
prereqs: [10_A2A/02]
concepts: [to_a2a, Starlette, uvicorn, lifespan, port]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10_A2A/02_AgentCard](02_AgentCard.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/04_ConsumeWithRemoteA2aAgent →](04_ConsumeWithRemoteA2aAgent.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 03 Serve with to_a2a

# 🛠 `to_a2a` — your agent in one line

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(root_agent, port=10000)
```

Done. `a2a_app` is a [Starlette](https://www.starlette.io/) ASGI app with:

- `GET /.well-known/agent.json` returning the auto-built AgentCard.
- `POST /` accepting JSON-RPC messages (`message/send`, `task/get`, …).
- SSE streaming for long-running tasks.

## Signature

```python
def to_a2a(
    agent: BaseAgent,
    *,
    host: str = "localhost",
    port: int = 8000,
    protocol: str = "http",
    agent_card: AgentCard | str | None = None,
    push_config_store: PushNotificationConfigStore | None = None,
    task_store: TaskStore | None = None,
    runner: Runner | None = None,
    lifespan: Callable | None = None,
    agent_executor_factory: Callable | None = None,
) -> Starlette: ...
```

Most callers only set `port` (and maybe `host="0.0.0.0"` when running in a container).

## Running it

```bash
# from a separate terminal
uvicorn my_module:a2a_app --host localhost --port 10000
```

Or, if you'd rather embed the run:

```python
import uvicorn
if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=10000)
```

## What's wired by default

- An **in-memory `TaskStore`** holds task state across messages (so multi-turn works in one process).
- An **in-memory `PushNotificationConfigStore`** captures push-notification subscriptions.
- A **default `Runner`** is created using in-memory session, memory, and artifact services.

For production you swap these out via the `to_a2a(...)` kwargs:

```python
to_a2a(
    agent,
    port=10000,
    task_store=DatabaseTaskStore(...),
    runner=Runner(
        app_name="currency",
        agent=agent,
        session_service=DatabaseSessionService(...),
    ),
    lifespan=my_lifespan,
)
```

## Lifespan hook (the production handle)

When your agent has resources to open/close (MCP toolsets, DB pools), use `lifespan`:

```python
from contextlib import asynccontextmanager

toolset = MCPToolset(connection_params=...)
agent = Agent(model="gemini-2.5-flash", tools=[toolset])

@asynccontextmanager
async def lifespan(app):
    # startup
    yield
    # shutdown — MCPToolset is NOT an async context manager; use .close()
    await toolset.close()

a2a_app = to_a2a(agent, port=10000, lifespan=lifespan)
```

This is the same pattern from `08_MCP/04_LifecycleManagement` — bring it here when your agent has an MCPToolset.

## Override the AgentCard

```python
a2a_app = to_a2a(agent, agent_card=my_custom_card)            # pre-built object
a2a_app = to_a2a(agent, agent_card="path/to/agent_card.json")  # JSON file
```

When you need control beyond what auto-build gives you.

## CLI alternative — `adk api_server --a2a`

ADK ships a CLI:

```bash
adk api_server --a2a path/to/agents_dir
```

This serves every agent in a directory, each at `/<agent-name>/.well-known/agent.json`. You hand-author an `agent.json` per agent. Use this when you have a fleet to expose.

> 🛠 **Have the student run:** copy the currency agent's `to_a2a(root_agent, port=10000)` snippet, save as `my_agent.py`, run `uvicorn my_agent:a2a_app --port 10000`. Hit `localhost:10000/.well-known/agent.json` with curl.

> ⚠️ **Gotcha** — `to_a2a()` returns a Starlette app; running `python my_agent.py` without `uvicorn` does nothing. You must run an ASGI server.

> 🚀 **In Production**
>
> The default in-memory stores are dev-only. **Always** swap in persistent stores for production — otherwise a restart drops all in-flight tasks and session state. We cover the swap in `07_InProduction.md`.

[← Prev: 10_A2A/02_AgentCard](02_AgentCard.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/04_ConsumeWithRemoteA2aAgent →](04_ConsumeWithRemoteA2aAgent.md)
