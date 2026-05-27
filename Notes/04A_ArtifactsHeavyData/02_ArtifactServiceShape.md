---
module: 04A_ArtifactsHeavyData
page: 02_ArtifactServiceShape
title: ArtifactService shape — the interface and the dev implementation
estimated_minutes: 20
prereqs: [04A_ArtifactsHeavyData/01]
concepts: [BaseArtifactService, InMemoryArtifactService, Runner-wiring, App-wiring]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/01_WhyArtifacts](01_WhyArtifacts.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/03_GcsArtifactService →](03_GcsArtifactService.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 02 ArtifactService shape

# 🛠 The `BaseArtifactService` interface

ADK's artifact API is two halves: a service interface (`BaseArtifactService`) you wire into the `App` / `Runner`, and a convenience wrapper on `ToolContext` (next page). The service is what actually stores the bytes; pick the right one for your environment.

## 🧠 The interface (engine-first)

`google.adk.artifacts.BaseArtifactService` is an `ABC` with five async methods you almost never call yourself, but should recognise:

```python
class BaseArtifactService(ABC):
    async def save_artifact(*, app_name, user_id, filename,
                            artifact, session_id=None,
                            custom_metadata=None) -> int: ...
    async def load_artifact(*, app_name, user_id, filename,
                            session_id=None, version=None) -> types.Part | None: ...
    async def list_artifact_keys(*, app_name, user_id, session_id=None) -> list[str]: ...
    async def delete_artifact(*, app_name, user_id, filename, session_id=None) -> None: ...
    async def list_versions(*, app_name, user_id, filename, session_id=None) -> list[int]: ...
```

Note the **scoping keys**: `app_name`, `user_id`, `session_id`. If `session_id` is `None`, the artifact is **user-scoped** — visible across all of that user's sessions. With a `session_id`, it is **session-scoped** — lives and dies with the conversation. (Same model as `user:` vs no-prefix state.) The `filename` parameter is the artifact key. If it starts with `"user:"`, the service treats it as user-scoped regardless of `session_id`.

## 🛠 Three shipped implementations

| Class | Backing store | Use for |
|---|---|---|
| `InMemoryArtifactService` | Process-local dict | dev, tests, notebooks |
| `FileArtifactService` | Local filesystem dir | dev with persistence, single-host runs |
| `GcsArtifactService` | Google Cloud Storage bucket | production (page 03) |

All three are drop-in interchangeable — your tool code never changes, only the service you hand to the `App`.

## 🛠 Wiring it — `InMemoryArtifactService` end-to-end

```python
# Work/02_inmemory_artifact.py — run with: uv run python Work/02_inmemory_artifact.py
import asyncio

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


async def save_note(text: str, tool_context: ToolContext) -> str:
    """Save the text as a UTF-8 artifact named note.txt and return the version."""
    part = types.Part(inline_data=types.Blob(
        data=text.encode("utf-8"), mime_type="text/plain"))
    version = await tool_context.save_artifact("note.txt", part)
    return f"Saved note.txt version {version}."


root_agent = LlmAgent(
    name="note_taker",
    model="gemini-2.5-flash",
    instruction="When the user gives you text to remember, call save_note.",
    tools=[save_note],
)

app = App(root_agent=root_agent, name="note_app")


async def main() -> None:
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
    )
    session = await session_service.create_session(
        app_name="note_app", user_id="carlos")
    msg = types.Content(role="user",
        parts=[types.Part(text="Save this: meet the auditor at 3pm Friday.")])
    async for event in runner.run_async(
        user_id="carlos", session_id=session.id, new_message=msg):
        if event.actions and event.actions.artifact_delta:
            print("ARTIFACT_DELTA:", event.actions.artifact_delta)
        if event.is_final_response() and event.content:
            print("REPLY:", event.content.parts[0].text)

    keys = await artifact_service.list_artifact_keys(
        app_name="note_app", user_id="carlos", session_id=session.id)
    print("STORED:", keys)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (the LLM phrasing varies; the delta + STORED lines are the load-bearing ones):

```
ARTIFACT_DELTA: {'note.txt': 0}
REPLY: Saved note.txt version 0.
STORED: ['note.txt']
```

## 🧠 What just happened

1. The tool called `tool_context.save_artifact("note.txt", part)`.
2. `ToolContext` forwarded to `artifact_service.save_artifact(...)` with the app/user/session scope.
3. `InMemoryArtifactService` stored the bytes in a process-local dict, returned `version=0`.
4. The Runner attached `artifact_delta={"note.txt": 0}` to the tool-result event (we'll dissect this on page 08).
5. After the run, `list_artifact_keys(...)` returns the filename — proving it landed in the store.

## ⚠️ The two gotchas

- **Forgetting to pass `artifact_service=` to `Runner`.** Symptom: `ValueError: Artifact service is not initialized.` when your tool calls `save_artifact`. ADK does not default to an in-memory service — you must wire one explicitly.
- **Using `InMemoryArtifactService` in any deployment.** Process death = total artifact loss. Acceptable for tests and the `adk web` dev loop; never for prod. Page 03 swaps it for `GcsArtifactService`.

## ❓ Quick check

> ❓ **Ask the student:** what is the difference between `app_name`, `user_id`, and `session_id` as artifact-service scope keys? *(Expected: `app_name` namespaces everything; `user_id` scopes to one human across sessions; `session_id`, when present, scopes to one conversation. Pass `session_id=None` (or use a `"user:"`-prefixed filename) for user-scoped artifacts that survive across conversations.)*

> 🛠 **Have the student run:** the script above. Then add a SECOND turn (`"Save this: bring the deck."`) and confirm the next `ARTIFACT_DELTA` is `{'note.txt': 1}` — versions increment per filename.

> **🚀 In Production**
>
> `InMemoryArtifactService` is for dev only. The standard prod swap is `GcsArtifactService` (next page) for GCP, or `FileArtifactService` on a persistent volume for single-host deployments. Picking the right backend at the App level means tool code never changes — that is the whole point of the abstraction.

---

[← Prev: 04A_ArtifactsHeavyData/01_WhyArtifacts](01_WhyArtifacts.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/03_GcsArtifactService →](03_GcsArtifactService.md)
