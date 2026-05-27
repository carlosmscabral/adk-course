---
module: 04A_ArtifactsHeavyData
page: 10_DissectingSample
title: Dissecting brand-aligned-presentations — artifacts end-to-end
estimated_minutes: 40
prereqs: [04A_ArtifactsHeavyData/09]
concepts: [GcsArtifactService, save_artifact, load_artifact, fallback-pattern]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/09_HeavyFileBetweenSubAgents](09_HeavyFileBetweenSubAgents.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/11_InProduction →](11_InProduction.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 10 Dissecting brand-aligned-presentations

# 🔬 Dissecting `brand-aligned-presentations`

> 🤖 **Tutor:** open the sample's directory in the student's editor. We trace **how a user-uploaded text file becomes a final downloadable `.pptx`**, with every artifact hop pointed out. Do not paste big code blocks — point at file:line and ask the student to read.

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/brand-aligned-presentations/`

## Why this sample

`brand-aligned-presentations` is a multi-agent presentation builder. The user uploads a text brief and an optional PowerPoint template; the system synthesises an outline (sub-agent), drafts each slide (sub-agent), generates visuals (sub-agent), then writes out a `.pptx`. **Every step exchanges either a user-uploaded artifact or a generated one.** It is the cleanest end-to-end artifact pattern in the samples repo: real `GcsArtifactService` wiring, `InMemoryArtifactService` fallback, `tool_context.save_artifact` + `load_artifact` calls in production-quality tools.

## What we will trace

By the end of this read-through the student should be able to:

- Point at the `GcsArtifactService` / `InMemoryArtifactService` fallback ladder in `agent.py`.
- Point at the four canonical artifact operations (`list`, `load`, `save`, `read_text`) in `artifact_utils.py`.
- Explain why `save_presentation` writes to BOTH the artifact store AND optionally to a separate GCS bucket.
- Distinguish what flows through `state` versus what flows through artifacts in one full turn.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/brand-aligned-presentations/presentation_agent/` and confirm the `tools/`, `sub_agents/`, `shared_libraries/`, `agent.py` layout before we walk it.

## File-by-file walkthrough

### `presentation_agent/agent.py` — the App wiring (lines 112-164)

This is the load-bearing block. The student should read lines 112-139:

```python
# Configure Artifact Service (GCS or In-Memory)
artifact_service = None
if GCS_BUCKET_NAME:
    try:
        gcs_client = get_gcs_client()
        if gcs_client:
            gcs_client.get_bucket(GCS_BUCKET_NAME)
            artifact_service = GcsArtifactService(bucket_name=GCS_BUCKET_NAME)
            ...
    except Exception as e:
        get_logger("agent").warning(f"Failed to initialize GcsArtifactService: {e}")
        get_logger("agent").warning("Falling back to InMemoryArtifactService.")
        artifact_service = InMemoryArtifactService()
else:
    get_logger("agent").info("GCS_BUCKET_NAME not set. Using InMemoryArtifactService.")
    artifact_service = InMemoryArtifactService()
```

Note three things:

1. **GCS first, in-memory fallback.** Production-grade: if the bucket is missing, misconfigured, or auth fails, the agent still boots — degraded but functional. This is the pattern from our page 03.
2. The bucket existence check (`get_bucket(...)`) runs at startup, not lazily on the first save. Fail fast.
3. The service is passed to `Runner(... artifact_service=artifact_service, ...)` on line 162 — same wiring you wrote on page 02.

> ❓ **Ask the student:** "Why is `InMemoryArtifactService()` an acceptable fallback for a presentation builder in development, but catastrophic in production?" *(Expected: the process is the storage; restart = lose every user's uploads. Fine for `adk web` dev loop, never for Cloud Run cold-restarts.)*

### `presentation_agent/tools/artifact_utils.py` — the four canonical ops

This file is **the** artifact playbook. Have the student read it top-to-bottom (it is small — ~330 lines).

- **`list_available_artifacts(tool_context)`** (lines 36-42) — wraps `tool_context.list_artifacts()`. Returns filenames so the LLM can decide which to load.
- **`get_artifact_as_local_path(tool_context, artifact_name)`** (lines 45-88) — calls `tool_context.load_artifact(name)`, handles `None` with a 2-second retry (cloud propagation lag), then writes bytes to a temp file. Returns the path so a non-async sub-process (the `.pptx` library) can read it.
- **`save_presentation(tool_context, new_artifact_name, local_path, gcs_bucket_name)`** (lines 136-191) — reads a generated `.pptx` from local disk, builds a `Part(inline_data=Blob(data=bytes, mime_type="application/...presentation"))`, calls `tool_context.save_artifact(...)`, **and** optionally uploads to a separate bucket as a backup.
- **`read_file_content(tool_context, artifact_name)`** (lines 280-302) — loads a text artifact, returns its decoded content as a string (with a graceful `UnicodeDecodeError` branch).

The shape is consistent: every tool that takes a filename takes a `ToolContext` and routes through it. No tool ever opens the artifact service directly.

> ❓ **Ask the student:** "Why does `save_presentation` save to both the artifact service AND a user-named GCS bucket?" *(Expected: the artifact store is internal — its layout uses the framework's `{app}/{user}/{session}/...` scheme, which is not user-friendly. The optional named-bucket upload gives the human a clean `gs://my-bucket/my-deck.pptx` URL they can share. Two stores, two purposes.)*

### `presentation_agent/sub_agents/synthesizer/agent.py:349`

```python
artifact = await tool_context.load_artifact(...)
... artifact.inline_data.data ...
```

The synthesiser sub-agent loads an artifact written by an earlier sub-agent and reads `.inline_data.data` — exactly the pattern from our page 09. This is the cross-sub-agent handoff in real code.

> 🛠 **Have the student grep** the sample: `grep -rn "save_artifact\|load_artifact" presentation_agent/`. Count the calls. The artifact API is small but used everywhere.

## Trace one turn end-to-end

User uploads `brief.txt` via the frontend; types "Build a 5-slide deck from this."

```
1.  Frontend → ADK API: new_message with Part(inline_data=Blob(data=brief.txt bytes,
                                                               mime_type="text/plain"))
2.  Runner receives event → ADK's frontend layer typically auto-saves the inline_data
    Part as an artifact (filename like "brief.txt"). artifact_delta records it.
3.  root agent ("presentation_expert_agent") sees the user request and
    routes to sub-agent tools.
4.  outline_specialist sub-agent calls read_file_content("brief.txt") → 
    load_artifact → bytes → str → drafts the outline.
5.  save_deck_spec writes the structured deck plan into state["current_deck_spec"]
    (small JSON, fits in state).
6.  batch_slide_writer reads {current_deck_spec} from state, drafts each slide.
7.  visual_generator (if needed) generates an image, saves it via
    save_artifact("chart_q1.png", img_part) → artifact_delta = {"chart_q1.png": 0}.
8.  presentation_orchestrator builds the .pptx locally, calls
    save_presentation("MyDeck.pptx", local_path, gcs_bucket_name="user-bucket").
9.  save_artifact("MyDeck.pptx", pptx_part) → artifact_delta = {"MyDeck.pptx": 0}.
10. Final reply: "Your deck is ready: MyDeck.pptx".
11. Frontend reads the latest artifact_delta and offers a download link.
```

Two things to internalise:

- **State and artifacts coexist.** The deck spec (small JSON) lives in state for cheap, prompt-templated reuse. The slide images and the final `.pptx` (heavy bytes) live in artifacts.
- **The Runner's event stream is the audit trail.** Every artifact write produces an `artifact_delta`. Six months later, "which agent generated chart_q1.png for this session?" is answerable.

> 🛠 **Have the student run:** the sample locally if they can. Otherwise, walk the trace above on paper while pointing at the code that implements each step.

## Module concepts present in this sample

| Module concept | Where in the sample |
|---|---|
| `GcsArtifactService` with fallback | `presentation_agent/agent.py:112-139` |
| `tool_context.save_artifact` | `presentation_agent/tools/artifact_utils.py:162` |
| `tool_context.load_artifact` | `presentation_agent/tools/artifact_utils.py:57, 286` |
| `tool_context.list_artifacts` | `presentation_agent/tools/artifact_utils.py:39` |
| `Part(inline_data=Blob(data=..., mime_type=...))` | `presentation_agent/tools/artifact_utils.py:156-161` |
| Cross-agent handoff by filename | `presentation_agent/sub_agents/synthesizer/agent.py:349` |
| State vs artifact split (`state` for `current_deck_spec`, artifact for `.pptx`) | `tools/artifact_utils.py:215` (state) vs `tools/artifact_utils.py:162` (artifact) |
| Separate user-named GCS bucket for friendly download URLs | `tools/artifact_utils.py:169-186` |

---

[← Prev: 04A_ArtifactsHeavyData/09_HeavyFileBetweenSubAgents](09_HeavyFileBetweenSubAgents.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/11_InProduction →](11_InProduction.md)
