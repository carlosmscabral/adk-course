---
module: 19_Internals
page: 03_RunnerSource
title: Runner.run_async — top-level plumbing
estimated_minutes: 30
prereqs: [19_Internals/02]
concepts: [Runner, run_async, invocation_context, session_service]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/02_LlmAgentSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/04_SessionEventSource →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 03 Runner Source

# 🧠 Runner.run_async

File: `/home/carloscabral/study/adk-python/src/google/adk/runners.py`
Class: `Runner` — line **152**. `InMemoryRunner(Runner)` — line **2167**.

## What the Runner owns

Open the class to its `__init__` around line **190**. The runner holds:

- `agent` — your root `BaseAgent`
- `app` — the `App` wrapper (artifacts, plugins, resumability, compaction config)
- `session_service: BaseSessionService` — where events go
- `memory_service: BaseMemoryService`
- `artifact_service: BaseArtifactService`
- `credential_service: BaseCredentialService`
- `plugin_manager: PluginManager`
- `resumability_config`

These are the **only** singletons in a request. Everything else (`InvocationContext`, `ToolContext`, `CallbackContext`) is built fresh per call.

## `run_async` — line 914

```python
async def run_async(
    self,
    *,
    user_id: str,
    session_id: str,
    invocation_id: Optional[str] = None,
    new_message: Optional[types.Content] = None,
    state_delta: Optional[dict[str, Any]] = None,
    run_config: Optional[RunConfig] = None,
    yield_user_message: bool = False,
) -> AsyncGenerator[Event, None]:
```

The shape (paraphrased from lines 950-1100):

```
1. Fetch (or create) the Session from session_service.
2. Decide which agent runs:
     - LlmAgent root → wrap in a workflow node (build_node)
     - BaseNode root → run as graph
     - Other BaseAgent → trace + _run_with_trace path
3. Build an InvocationContext (session + plugins + new_message + state_delta).
4. Start a tracer span "invocation".
5. async for event in agent_to_run.run_async(ctx):
       session_service.append_event(session, event)  # persists state_delta!
       yield event
6. On end: cleanup toolsets, end span.
```

**Two non-obvious bits:**

- **Every LlmAgent root is wrapped as a node** (`build_node`) before running. The "legacy" direct path is gone; everything runs through the workflow scheduler now.
- **Events are appended inside the generator.** If a consumer stops iterating, persistence stops. This is why you should always `async for` to completion (or use `aclosing`).

## `_get_or_create_session` — line 807

If `session_id` doesn't exist, it's created. This is **why your first run with a fresh id "just works."** In prod you usually fetch the session yourself first to inspect.

## `rewind_async` — line 1114

The newer 2.0 surface: roll a session back to event index N, recomputing state and artifact deltas. Implementation: walk events, build inverse deltas (`_compute_state_delta_for_rewind` at line 1165 and `_compute_artifact_delta_for_rewind` at line 1199), append a rewind event.

## `run_live` — line 1519

The bidi/streaming twin of `run_async`. Different generator, same persistence rules.

## `InMemoryRunner` (line 2167)

```python
class InMemoryRunner(Runner):
    def __init__(self, agent, app_name="InMemoryRunner", ...):
        super().__init__(
            agent=agent, app=App(name=app_name, root_agent=agent),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
            ...
        )
```

This is "5 in-memory services in a trenchcoat." Great for tests and demos; **never** for prod (no persistence, no concurrency).

> 🚀 **In Production**
>
> Always inject your own `session_service` (Sqlite/Database/VertexAi) and `memory_service`. `InMemoryRunner` is for the REPL.

> 🛠 **Have the student run:** find line 914 in `runners.py` and read the first 50 lines of `run_async`. Ask them: "what happens if `new_message` and `invocation_id` are both None?" *(Answer: `ValueError` — see line 1031.)*

> ❓ **Ask the student:** "Why is `append_event` called inside the `async for`, not after?" *(Answer: streaming — every event must be persisted before the consumer sees it, so a crash mid-stream doesn't lose history.)*

[← Prev: 19_Internals/02_LlmAgentSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/04_SessionEventSource →]
