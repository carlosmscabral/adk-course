---
module: 04A_ArtifactsHeavyData
page: 04_SaveAndLoadFromTools
title: Save and load artifacts from a tool
estimated_minutes: 20
prereqs: [04A_ArtifactsHeavyData/02]
concepts: [tool_context, save_artifact, load_artifact, versioning]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/03_GcsArtifactService](03_GcsArtifactService.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/05_MultimodalParts →](05_MultimodalParts.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 04 Save & load from tools

# 🛠 Saving and loading from a tool

You met `ToolContext` in [Module 03 / FunctionTool](../03_Tools/02_FunctionTool.md) and used `tool_context.state[...]` in [Module 04 / Writing state from tools](../04_SessionsState/04_WritingStateFromTools.md). The artifact API is three sibling methods on the same object:

```python
await tool_context.save_artifact(filename, part)     # → int (the new version)
await tool_context.load_artifact(filename)            # → types.Part | None  (latest)
await tool_context.load_artifact(filename, version=2) # → types.Part | None  (pinned)
await tool_context.list_artifacts()                   # → list[str]
```

## 🛠 Round-trip in one script

```python
# Work/04_artifact_roundtrip.py — run with: uv run python Work/04_artifact_roundtrip.py
import asyncio

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


async def write_report(body: str, tool_context: ToolContext) -> str:
    """Save the body as report.md and return the version stored."""
    part = types.Part(inline_data=types.Blob(
        data=body.encode("utf-8"), mime_type="text/markdown"))
    v = await tool_context.save_artifact("report.md", part)
    return f"Wrote report.md v{v}."


async def read_report(tool_context: ToolContext) -> str:
    """Load report.md (latest version) and return its text."""
    part = await tool_context.load_artifact("report.md")
    if part is None:
        return "No report yet."
    return part.inline_data.data.decode("utf-8")


root_agent = LlmAgent(
    name="reporter", model="gemini-2.5-flash",
    instruction=(
        "If the user gives you content, call write_report. "
        "If the user asks for the latest report, call read_report and return it verbatim."
    ),
    tools=[write_report, read_report],
)
app = App(root_agent=root_agent, name="report_app")


async def main():
    sess = InMemorySessionService()
    arts = InMemoryArtifactService()
    runner = Runner(app=app, session_service=sess, artifact_service=arts)
    s = await sess.create_session(app_name="report_app", user_id="carlos")

    async def turn(text: str) -> None:
        msg = types.Content(role="user", parts=[types.Part(text=text)])
        async for ev in runner.run_async(
            user_id="carlos", session_id=s.id, new_message=msg):
            if ev.actions and ev.actions.artifact_delta:
                print("DELTA:", ev.actions.artifact_delta)
            if ev.is_final_response() and ev.content:
                print("REPLY:", ev.content.parts[0].text)

    await turn("Save this report: All systems nominal.")
    await turn("What's in the latest report?")


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output:

```
DELTA: {'report.md': 0}
REPLY: Wrote report.md v0.
REPLY: All systems nominal.
```

## 🧠 What ADK did under the hood

```
{{INCLUDE _figures/artifact_lifecycle.txt}}
```

The diagram lives at [_figures/artifact_lifecycle.txt](_figures/artifact_lifecycle.txt). Three things to internalise:

1. `save_artifact` returned an `int` — the version. Versions start at `0` and monotonically increment per filename per (user, session) scope.
2. The Runner attached `artifact_delta={"report.md": 0}` to the tool-result event. That delta is **all** the session persists about the artifact — bytes live in the backing service, not in the session.
3. `load_artifact` is a fresh read every call. The next turn's `read_report` fetched bytes from the artifact store, not from any in-memory cache.

## 🛠 Versioning in practice

```python
# Save three drafts; each call bumps the version
await tool_context.save_artifact("draft.md", v1)   # → 0
await tool_context.save_artifact("draft.md", v2)   # → 1
await tool_context.save_artifact("draft.md", v3)   # → 2

await tool_context.load_artifact("draft.md")               # latest → v3 bytes
await tool_context.load_artifact("draft.md", version=0)    # pinned → v1 bytes
```

Use pinned versions when you need reproducibility (eval traces, audit logs). Use the bare latest for the common case.

## ⚠️ Three failure modes

- **No `artifact_service` wired into the Runner.** `tool_context.save_artifact(...)` raises `ValueError: Artifact service is not initialized.` See page 02.
- **Returning the `Part` from the tool instead of saving it.** Tools should return small JSON-serializable strings/dicts to the LLM, not raw bytes. Save the artifact, then return its filename + version.
- **Forgetting that `load_artifact` returns `None` if the filename does not exist.** Always check `if part is None` before dereferencing `.inline_data.data`.

## 🧠 User-scoped artifacts

Pass a filename starting with `"user:"` to make the artifact visible across all that user's sessions (same pattern as `user:` state keys):

```python
await tool_context.save_artifact("user:profile_photo.jpg", part)
# Next session of the same user can: load_artifact("user:profile_photo.jpg")
```

Use this for per-user assets (profile photos, saved templates) that should outlive any one conversation.

## ❓ Quick check

> ❓ **Ask the student:** in the round-trip script above, what would happen if the first turn was `"What's in the latest report?"`? *(Expected: `read_report` returns `"No report yet."` because `load_artifact("report.md")` returns `None` when nothing has been saved. The agent should surface that politely rather than crash.)*

> 🛠 **Have the student run:** the script, then add a third turn `"Save: All systems still nominal."` followed by a fourth `"What's in the latest report?"`. Confirm the delta is `{'report.md': 1}` and the reply matches the second save — proves the latest-version semantic.

> **🚀 In Production**
>
> Tools that save artifacts should **return the filename and version as a string**, not the bytes. The LLM only ever needs the handle to refer to the artifact in subsequent turns. Returning raw bytes (or even a long Base64 string) blows up your event log and your token bill. Save → return `"saved as report.md v0"` → done.

---

[← Prev: 04A_ArtifactsHeavyData/03_GcsArtifactService](03_GcsArtifactService.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/05_MultimodalParts →](05_MultimodalParts.md)
