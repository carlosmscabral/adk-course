---
module: 1A_AppAndRunner
page: 04_WiringResumability
title: Wiring `resumability_config` on the App
estimated_minutes: 15
prereqs: [1A_AppAndRunner/01]
concepts: [ResumabilityConfig, resume, cancel, long-running-tools, idempotency]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 03_AppStateBoundary](03_AppStateBoundary.md)  [↑ Map](../../MAP.md)  [Next: 05_WiringContextCache →](05_WiringContextCache.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 04 Wiring Resumability

# 🛠 Wiring `resumability_config` on the App

Resumability is the 2.0 feature that lets an agent **pause** mid-invocation (typically on a long-running tool waiting for human approval) and **resume** later — possibly in a different process. It is opt-in, and it is opted in at the `App` level.

> 🤖 **Tutor:** this page only covers *wiring* — flipping the bit on the App. The full mechanism (`Runner.resume()`, `LongRunningFunctionTool` semantics, the at-least-once contract, the failure modes) is taught in [Module 4B Human-in-the-Loop & Resume/Cancel](../4B_HumanInTheLoop/). This page is the contract that lets 4B exist.

## 🛠 The one-liner

```python
# Work/1A_resumability_wiring.py
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps._configs import ResumabilityConfig

agent = LlmAgent(name="approver", model="gemini-2.5-flash", instruction="Be brief.")

app = App(
    name="approval_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
```

That is the whole API today. `ResumabilityConfig` has a single field: `is_resumable: bool` (default `False`). Set it to `True` and every agent in the app becomes resumable.

## 🧠 What "resumable" actually changes

Three things flip on:

1. **`LongRunningFunctionTool` calls are checkpointable.** When the LLM emits a tool call to a long-running function, the Runner persists the pending tool-call event to the Session service and *yields control* back to the caller. The caller can shut the process down. Later, calling `runner.resume(...)` with the function response continues from that point.
2. **The session service holds the pause state.** Resumability requires a *persistent* session service (`DatabaseSessionService`, `VertexAiSessionService`, `SqliteSessionService`). `InMemorySessionService` works for testing but loses state on process restart — defeating the point.
3. **At-least-once semantics.** When you `resume()`, ADK guarantees the resumed step runs *at least* once. It may run more than once on retries. Your long-running tool **must be idempotent** — e.g., write the result keyed by a stable ID so a re-run is a no-op.

## 🧠 What the App-level config does NOT change

- It does not make plain `LlmAgent.run_async` magically resumable across `KeyboardInterrupt`. Crash mid-streaming and the partial event is lost. Resumability only kicks in at *long-running tool boundaries*.
- It does not make tools idempotent for you. That is your job.
- It does not enable `Runner.cancel()` — cancellation is always available; it is a different mechanism from resume.

## 🛠 Sketch — resumable approval loop (full impl in Module 4B)

```python
# Work/1A_resumability_sketch.py — preview only; the real script is in Module 4B
import asyncio
import uuid
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps._configs import ResumabilityConfig
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools import LongRunningFunctionTool

def request_human_approval(action: str) -> dict:
    """Ask a human to approve an action. Long-running."""
    return {"status": "pending", "action": action}

agent = LlmAgent(
    name="approver",
    model="gemini-2.5-flash",
    instruction="When asked to do anything risky, call request_human_approval.",
    tools=[LongRunningFunctionTool(func=request_human_approval)],
)

app = App(
    name="approval_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

runner = Runner(
    app=app,
    session_service=DatabaseSessionService(db_url="sqlite:///sessions.db"),
)

# Module 4B shows the actual `await runner.resume(...)` continuation.
```

The pieces you can see today: `ResumabilityConfig(is_resumable=True)` on the App, a `LongRunningFunctionTool` on the agent, a persistent session service. The Runner picks up `resumability_config` from the App automatically (see [01_AppVsRunnerVsAgent](01_AppVsRunnerVsAgent.md) — `Runner.__init__` reads `self.resumability_config = app.resumability_config`).

> ❓ **Ask the student:** "If I set `resumability_config=ResumabilityConfig(is_resumable=True)` but keep `InMemorySessionService`, does resume work?"
> *(Expected: no — or rather, it 'works' within one process but not across restarts, which is the whole point. The session service is where the pause checkpoint lives; in-memory means the checkpoint dies with the process.)*

## 🚀 In Production

> **🚀 In Production**
>
> Resumability is an `@experimental` feature in ADK 2.0 today (see `from ..utils.feature_decorator import experimental` on the `ResumabilityConfig` class). The API surface and the at-least-once semantics are stable enough for human-approval flows, but check [Notes/Updates/](../Updates/) for the next release delta before pinning a critical workflow on it. The standard mitigation for "I need real durable execution today and can't tolerate API churn" is to combine ADK's resumability with [Temporal or Dapr workflows](../4B_HumanInTheLoop/08_DurableExecution.md) — let ADK handle the agent loop, let Temporal handle the durability.

> 🛠 **Have the student run:** `python -c "from google.adk.apps._configs import ResumabilityConfig; print(ResumabilityConfig(is_resumable=True))"`. Confirm the import path works and the Pydantic repr prints `is_resumable=True`. Just verifying the wiring before they move on.

---

[← Prev: 03_AppStateBoundary](03_AppStateBoundary.md)  [↑ Map](../../MAP.md)  [Next: 05_WiringContextCache →](05_WiringContextCache.md)
