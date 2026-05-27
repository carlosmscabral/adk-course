---
module: 04A_ArtifactsHeavyData
page: 08_ArtifactDeltaInEvents
title: artifact_delta on Events — how the Runner persists
estimated_minutes: 15
prereqs: [04A_ArtifactsHeavyData/04]
concepts: [artifact_delta, EventActions, audit-log, observability]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/07_SignedUrlsHandoff](07_SignedUrlsHandoff.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/09_HeavyFileBetweenSubAgents →](09_HeavyFileBetweenSubAgents.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 08 artifact_delta in events

# 🧠 `artifact_delta` — the audit trail for bytes

In Module 04 you learned that state writes ride on `state_delta` inside `EventActions`. Artifacts have the same shape: every save records an `artifact_delta` on the tool-result event. That delta is **all** the session persists about the artifact — just `{filename: version}`. The bytes live in the artifact service; the event tells you *which* bytes (by name + version) the agent wrote, in event order.

## 🧠 The field

```python
# from google.adk.events.event_actions:
class EventActions(BaseModel):
    state_delta: dict[str, Any]       = Field(default_factory=dict)
    artifact_delta: dict[str, int]    = Field(default_factory=dict)  # filename → version
    transfer_to_agent: str | None     = None
    escalate: bool | None             = None
    skip_summarization: bool | None   = None
    requested_auth_configs: dict[...] = Field(default_factory=dict)
```

`artifact_delta` is `dict[str, int]` — filename mapped to the version the save returned. Multiple saves in one tool call accumulate:

```python
# In a tool that saves two artifacts:
await tool_context.save_artifact("chart.png", chart_part)   # → 0
await tool_context.save_artifact("data.csv", csv_part)      # → 0

# The tool-result event ends up with:
# event.actions.artifact_delta == {"chart.png": 0, "data.csv": 0}
```

## 🛠 Reading deltas off the event stream

```python
# Work/08_read_deltas.py — run with: uv run python Work/08_read_deltas.py
import asyncio

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


async def save_two(tool_context: ToolContext) -> str:
    """Save two tiny artifacts, return their names."""
    a = types.Part(inline_data=types.Blob(data=b"alpha", mime_type="text/plain"))
    b = types.Part(inline_data=types.Blob(data=b"beta",  mime_type="text/plain"))
    va = await tool_context.save_artifact("a.txt", a)
    vb = await tool_context.save_artifact("b.txt", b)
    return f"a.txt v{va}, b.txt v{vb}"


agent = LlmAgent(name="dual", model="gemini-2.5-flash",
                 instruction="Call save_two when asked to save the pair.",
                 tools=[save_two])
app = App(root_agent=agent, name="dual_app")


async def main():
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="dual_app", user_id="carlos")
    msg = types.Content(role="user",
        parts=[types.Part(text="Save the pair please.")])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        # Print author + every kind of action delta we see
        if ev.actions:
            if ev.actions.artifact_delta:
                print(f"[{ev.author}] artifact_delta:", ev.actions.artifact_delta)
            if ev.actions.state_delta:
                print(f"[{ev.author}] state_delta:", ev.actions.state_delta)
        if ev.is_final_response() and ev.content:
            print(f"[{ev.author}] REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output:

```
[dual] artifact_delta: {'a.txt': 0, 'b.txt': 0}
[dual] REPLY: a.txt v0, b.txt v0
```

## 🧠 What the Runner does with the delta

1. The tool returns; ADK wraps the tool result in an `Event` whose `actions.artifact_delta` captures the saves.
2. The `Runner` appends the Event to the Session via the `SessionService` — the delta is now part of the immutable event log.
3. The artifact bytes themselves already live in the `ArtifactService` (different store, different SLA).
4. The next iteration of the agent loop can `load_artifact(name)` and the service returns the latest version — including writes from earlier events in the same session.

The delta is **not** the artifact. It is the **reference** to it that the audit log carries. If the artifact service loses bytes (bucket lifecycle deletes the object), the delta still tells you that on event N, agent X saved `report.pdf v3` — invaluable for diagnostics even after the bytes are gone.

## 🧠 How callbacks and plugins use it

- **Observability ([15 Observability](../15_Observability/)):** filter the event stream for `actions.artifact_delta` non-empty to log every write with the writing agent's name. Cheap; the data is right there.
- **Callbacks ([07 Callbacks](../07_Callbacks/)):** an `after_tool_callback` can inspect `tool_context._event_actions.artifact_delta` (or the equivalent on the context object) to react — e.g., kick off a virus scan, log a metric, replicate to a backup bucket.
- **Plugins ([13 Plugins](../13_Plugins/)):** a plugin that needs to surface artifact writes to a frontend (Module 23) reads the deltas off events as they stream.

## ⚠️ Don't conflate delta with bytes

- The delta carries `(filename, version)`. **It does not carry the bytes.** Sub-agents must call `load_artifact(filename, version=...)` to read.
- Replaying the event log via `Runner.rewind` (Module 04 page on rewind) replays the events — the bytes must still be present in the artifact service for `load_artifact` to succeed. If your lifecycle policy already deleted the artifact, the replay can read the delta but not the bytes.

## ❓ Quick check

> ❓ **Ask the student:** they see `artifact_delta={"chart.png": 3}` on an event. What does the `3` mean, and how would they recover the specific bytes that event referred to (even if `chart.png` has since been overwritten)? *(Expected: `3` is the version number — the fourth save of `chart.png` in this scope (versions start at 0). Recovery: `await load_artifact("chart.png", version=3)`. As long as the artifact service kept that version (no lifecycle delete), the original bytes come back.)*

> 🛠 **Have the student run:** the script. Then add a second turn that asks the agent to save the pair again. Confirm the next event shows `{'a.txt': 1, 'b.txt': 1}` — versions monotonically increment in the delta just like in the artifact store itself.

> **🚀 In Production**
>
> Treat `artifact_delta` as the canonical audit record of every byte your agent persisted. Wire your observability pipeline (Module 15) to extract these deltas into structured logs from day one. When something goes wrong six months later — "which agent wrote this file?" — the answer is one query away.

---

[← Prev: 04A_ArtifactsHeavyData/07_SignedUrlsHandoff](07_SignedUrlsHandoff.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/09_HeavyFileBetweenSubAgents →](09_HeavyFileBetweenSubAgents.md)
