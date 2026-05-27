---
module: 04A_ArtifactsHeavyData
page: 09_HeavyFileBetweenSubAgents
title: Heavy-file handoff between sub-agents
estimated_minutes: 25
prereqs: [04A_ArtifactsHeavyData/04, 05_MultiAgent/05]
concepts: [sub-agent-handoff, output_key, filename-as-handle, SequentialAgent]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/08_ArtifactDeltaInEvents](08_ArtifactDeltaInEvents.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/10_DissectingSample →](10_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 09 Heavy file between sub-agents

# 🛠 The canonical pattern: filename in state, bytes in artifact

You learned in [05/05 Sharing State Across Agents](../05_MultiAgent/05_SharingStateAcrossAgents.md) that all sub-agents share one Session. Combine that with the artifact store: the handoff between sub-agents is a **short filename string in state** (or via `output_key=`), with the bytes living in the artifact service.

```
┌──────────────────┐   output_key="report_file"   ┌──────────────────┐
│   uploader       │──────────────────────────────▶│   summariser     │
│                  │  state["report_file"]         │                  │
│ save_artifact    │  = "report.pdf"               │ load_artifact    │
│ ("report.pdf",   │                               │ ("report.pdf")   │
│  pdf_part)       │                               │                  │
└────────┬─────────┘                               └─────────┬────────┘
         │ bytes                                             │ bytes
         ▼                                                   ▲
   ┌──────────────────────────────────────────────────────────────┐
   │              ArtifactService (Gcs / InMemory)                │
   │           {(app, user, session, "report.pdf"): bytes}        │
   └──────────────────────────────────────────────────────────────┘
```

## 🛠 Two sub-agents, one Sequential

```python
# Work/09_handoff.py — run with: uv run python Work/09_handoff.py
import asyncio

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


# ---- uploader: takes user text, saves it as report.md, returns the filename ----
async def stash_text(text: str, tool_context: ToolContext) -> str:
    """Save the given text as report.md, returns its filename."""
    part = types.Part(inline_data=types.Blob(
        data=text.encode("utf-8"), mime_type="text/markdown"))
    await tool_context.save_artifact("report.md", part)
    return "report.md"


uploader = LlmAgent(
    name="uploader", model="gemini-2.5-flash",
    instruction=(
        "The user will give you content. Call stash_text on it. "
        "Reply ONLY with the filename returned by the tool."
    ),
    tools=[stash_text],
    output_key="report_file",     # ← reply (the filename) → state['report_file']
)


# ---- summariser: reads the filename from state, loads bytes, summarises ----
async def fetch_text(filename: str, tool_context: ToolContext) -> str:
    """Load the named artifact and return its text content."""
    part = await tool_context.load_artifact(filename)
    if part is None:
        return f"(no artifact named {filename})"
    return part.inline_data.data.decode("utf-8")


summariser = LlmAgent(
    name="summariser", model="gemini-2.5-flash",
    instruction=(
        "The filename of the report is {report_file}. "
        "Call fetch_text on it, then give a one-sentence summary."
    ),
    tools=[fetch_text],
)


pipeline = SequentialAgent(
    name="report_pipeline", sub_agents=[uploader, summariser])
app = App(root_agent=pipeline, name="handoff_app")


async def main():
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="handoff_app", user_id="carlos")
    msg = types.Content(role="user", parts=[types.Part(text=(
        "Save and summarise:\n\n"
        "Q1 revenue grew 14% YoY led by enterprise renewals."
    ))])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        if ev.actions and ev.actions.artifact_delta:
            print(f"[{ev.author}] artifact_delta:", ev.actions.artifact_delta)
        if ev.actions and ev.actions.state_delta:
            print(f"[{ev.author}] state_delta:", ev.actions.state_delta)
        if ev.is_final_response() and ev.content:
            print(f"[{ev.author}] FINAL:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (LLM phrasing varies; structurally):

```
[uploader] artifact_delta: {'report.md': 0}
[uploader] state_delta: {'report_file': 'report.md'}
[summariser] FINAL: Q1 revenue rose 14% YoY, driven by enterprise renewals.
```

## 🧠 Why this works

- The uploader saves bytes via the artifact service — the session gets a tiny `artifact_delta`.
- `output_key="report_file"` writes the uploader's last reply text (`"report.md"`) into `state['report_file']`.
- The summariser's instruction template `{report_file}` interpolates that string. The LLM sees the literal filename.
- The summariser's `fetch_text` tool calls `load_artifact(filename)` — the SAME artifact service the uploader wrote to (shared via the App), and the bytes come back.

State is **the dependency graph between sub-agents**; the artifact service is **the heavy-data plane**. They are decoupled but coordinated through the event log.

## 🧠 Variant: user-scoped handoff across sessions

For an asset the user should see again next session — say, a profile photo or a saved template:

```python
await tool_context.save_artifact("user:profile.jpg", part)
# Next session of the same user, a different sub-agent:
part = await tool_context.load_artifact("user:profile.jpg")
```

Same pattern, just a `"user:"`-prefixed filename to escape the session-scope. (Same logic as `user:` state keys.)

## ⚠️ Three failure modes

1. **Both sub-agents use different `app_name` strings** when constructing their own Runners. Artifacts are scoped by `app_name`; mismatched apps → empty `load_artifact`. Fix: use one `App` / `Runner` for the whole pipeline (as in the script above). Multi-Runner setups are a Module 22 / 23 concern.
2. **The uploader does not write the filename to a known state key.** Without `output_key=` or an explicit `state_delta`, the downstream agent does not know what filename to ask for. The prompt template `{report_file}` errors at substitution time.
3. **Saving the bytes to state instead of to the artifact service.** Defeats the whole point. Module 04's `state_delta` would hold the megabytes; the audit log balloons; persistence backends slow down. Page 01's decision tree is your guide.

## ❓ Quick check

> ❓ **Ask the student:** they swap `SequentialAgent` for `ParallelAgent` and the summariser starts failing. Why? *(Expected: with `ParallelAgent` both sub-agents run simultaneously — the summariser tries to `load_artifact("report.md")` before the uploader has saved it. The artifact-handoff pattern requires temporal ordering, so `SequentialAgent` or an explicit dependency edge in a graph workflow ([Module 06](../06_GraphWorkflows/)).)*

> 🛠 **Have the student run:** the script. Then add a SECOND user message in the same session asking the summariser to re-summarise. Confirm no new `artifact_delta` appears — the artifact is already there, only `load_artifact` runs. The artifact persists across turns within the session for free.

> **🚀 In Production**
>
> Treat the filename as the **contract** between sub-agents. Document which sub-agent writes which artifact (the way you would document a function's return type). When the contract is implicit, refactors break silently — the producer renames the artifact, the consumer still asks for the old name, `load_artifact` returns `None`, the LLM hallucinates a recovery. Forward link: [Module 19 / Internals](../19_Internals/) traces the artifact-write path in the framework source.

---

[← Prev: 04A_ArtifactsHeavyData/08_ArtifactDeltaInEvents](08_ArtifactDeltaInEvents.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/10_DissectingSample →](10_DissectingSample.md)
