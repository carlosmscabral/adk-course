---
module: 21_AdkApiSurface
page: 01A_AdkRunUnderTheHood
title: adk run under the hood — argv to first event
estimated_minutes: 25
prereqs: [21_AdkApiSurface/01, 04_SessionsState/03]
concepts: [click, AgentLoader, _to_app, _setup_runner_context, run_interactively]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 01_AdkRunCli](01_AdkRunCli.md)  [↑ Map](../../MAP.md)  [Next: 01B_AdkWebUnderTheHood →](01B_AdkWebUnderTheHood.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 01A adk run internals

---

## 🔬 The actual call graph

`adk` is a `click` CLI. Type the command and control flows like this:

```
src/google/adk/cli/cli_tools_click.py
  @main.command("run")  def cli_run(...)
        │ resolves AGENT_PARENT_DIR + AGENT_NAME from argv
        │ resolves --session_service_uri / --artifact_service_uri into svc factories
        │
        ▼
src/google/adk/cli/cli.py
  async def run_cli(...)
        │ AgentLoader(agents_dir).load_agent(agent_name)       ← #1
        │ app = _to_app(loaded, app_name)                      ← #2
        │ runner = _setup_runner_context(app, ...)             ← #3
        │ session = await session_service.create_session(...)  ← #4
        │
        ▼
  async def run_interactively(runner, session, ...)
        │ while True:
        │   line = input("[user]: ")
        │   async for event in runner.run_async(...):          ← #5
        │     _print_event(event)
```

See [_figures/adk_run_lifecycle.txt](_figures/adk_run_lifecycle.txt) for the same picture as ASCII.

## 🔬 Step #1 — `AgentLoader` discovers the package

The loader does **dynamic import**, not source-code parsing.

```python
# what AgentLoader.load_agent(name) effectively does:
import importlib
mod = importlib.import_module(name)        # e.g. "research_assistant"
candidate = getattr(mod, "root_agent", None) or getattr(mod, "agent", None)
return candidate
```

That's why `__init__.py` must import `agent`: dynamic import only fires the package's `__init__.py`, not arbitrary sub-modules.

## 🔬 Step #2 — `_to_app(...)` normalises the surface

The loader can return three different things, all valid:

| What the loader returns | What `_to_app` does                             |
|-------------------------|-------------------------------------------------|
| `App(...)`              | pass-through                                     |
| `LlmAgent` (or `BaseAgent`) | wraps it: `App(name=app_name, root_agent=agent)` |
| anything else           | raises a `TypeError`                            |

The whole point: downstream code (the runner, the plugin manager) only knows about `App`. Bare-`Agent` is a convenience.

## 🔬 Step #3 — `_setup_runner_context` picks the services

This is the most flag-sensitive function in the CLI. It builds:

- **SessionService**: from `--session_service_uri`. No URI → `InMemorySessionService`. `sqlite:///x.db` → `DatabaseSessionService` (SQLAlchemy). `agentengine://...` → `VertexAiSessionService`. `memory://` is also accepted to force the in-memory service.
- **ArtifactService**: from `--artifact_service_uri`. No URI → `InMemoryArtifactService`. `gs://bucket` → `GcsArtifactService`. `file://<path>` writes to a local directory; `memory://` forces in-memory.
- **MemoryService**: `InMemoryMemoryService` unless an Agent-Engine URI was provided (then `VertexAiMemoryBankService`).
- **CredentialService**: in-memory by default.

Then it constructs the runner:

```python
runner = Runner(
    app=app,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
    credential_service=credential_service,
)
```

That `Runner` is the *same class* you built by hand in module 04. The CLI just discovers it.

## 🔬 Step #5 — `run_interactively` is a 20-line REPL

```python
# distilled — the actual function is in src/google/adk/cli/cli.py
async def run_interactively(runner, session, ...):
    while True:
        line = await aioconsole.ainput("[user]: ")
        if not line:
            continue
        content = types.Content(role="user", parts=[types.Part.from_text(line)])
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            _print_event(event)
        # if event.actions had pending function_calls (long-running tools),
        # prompt the human for the response
```

`_print_event` is the formatter — it walks `event.content.parts` and prints text vs function-call vs function-response with author labels.

> 🛠 **Have the student run:** open `src/google/adk/cli/cli.py` and find `run_interactively`. Have them count how many lines it is. The answer is *startling small* — the magic is the runner, not the CLI.

## 🐍 Detour suggestion

If `click.command`, `@click.option`, and `pass_context` look like Greek, take 20 min on Python's argparse / click ecosystem. The CLI surface is 100% click — once you can read a click group, you can extend `adk` itself.

## 🚀 In Production

> **🚀 In Production**
>
> The CLI's dynamic-import contract has one operational consequence: **package import side effects are part of your agent**. If `__init__.py` does `os.environ.setdefault(...)` or eagerly opens a DB connection, that fires the moment `adk run` starts — *before* the first user input. Keep `__init__.py` minimal: imports only.

> ❓ **Ask the student:** "If you change `agent.py` and re-type `adk run`, does the new code take effect?" *(Yes — every `adk run` invocation is a fresh process, fresh import. `adk web` is different — that's page 01B.)*

---

[← Prev: 01_AdkRunCli](01_AdkRunCli.md)  [↑ Map](../../MAP.md)  [Next: 01B_AdkWebUnderTheHood →](01B_AdkWebUnderTheHood.md)
