---
module: 04A_ArtifactsHeavyData
page: 03_GcsArtifactService
title: GcsArtifactService — bucket, IAM, lifecycle ☁️
estimated_minutes: 25
prereqs: [04A_ArtifactsHeavyData/02]
concepts: [GcsArtifactService, IAM, lifecycle-policy, blob-naming]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/02_ArtifactServiceShape](02_ArtifactServiceShape.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/04_SaveAndLoadFromTools →](04_SaveAndLoadFromTools.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 03 GcsArtifactService ☁️

# ☁️ `GcsArtifactService` — the production swap

`GcsArtifactService` is `InMemoryArtifactService` with a GCS bucket behind it. The interface is identical; your tool code is identical; only the wiring at `App` startup changes. This page is the GCP-specific setup: bucket, IAM, lifecycle.

## ☁️ One-time bucket setup

```bash
# pick a name; bucket names are GLOBALLY unique
export BUCKET=adk-artifacts-$(gcloud config get-value project)
export REGION=us-central1

gcloud storage buckets create gs://$BUCKET \
    --location=$REGION \
    --uniform-bucket-level-access \
    --public-access-prevention
```

Three flags worth defending:
- `--location=us-central1` — a **single-region** bucket is cheapest and lowest-latency when your Cloud Run / Agent Engine workload is in the same region. Multi-region only if your traffic genuinely spans continents.
- `--uniform-bucket-level-access` — turns off per-object ACLs. IAM only. Less rope to hang yourself with.
- `--public-access-prevention` — refuses any policy that would make the bucket world-readable. **Artifacts often contain PII**; this is a guardrail against an accidental "Allow allUsers" later.

## ☁️ IAM — least privilege

The service account your agent runs as (Cloud Run / Agent Engine / GKE) needs one role on this bucket:

```bash
gcloud storage buckets add-iam-policy-binding gs://$BUCKET \
    --member="serviceAccount:agent-runtime@$PROJECT.iam.gserviceaccount.com" \
    --role="roles/storage.objectUser"
```

`storage.objectUser` covers read, write, delete on objects (no bucket-level changes). Do **not** grant `roles/storage.admin` to the agent's SA — if an agent goes rogue you do not want it deleting the bucket itself. (Module 16 cross-references this.)

## ☁️ Lifecycle policy — the cost lever

Without a lifecycle policy, every artifact version every user ever saved sits in GCS forever. That is your bill. Set a TTL appropriate to your domain — 30 days for ephemeral generated assets, 365 days for compliance-relevant uploads, never-delete for legal holds.

```bash
cat > /tmp/lifecycle.json <<'EOF'
{
  "rule": [
    {"action": {"type": "Delete"},
     "condition": {"age": 30, "matchesPrefix": ["temp/"]}},
    {"action": {"type": "Delete"},
     "condition": {"age": 365}}
  ]
}
EOF

gcloud storage buckets update gs://$BUCKET --lifecycle-file=/tmp/lifecycle.json
```

## ☁️ Wiring it into the App

```python
# Work/03_gcs_artifact.py — run with: uv run python Work/03_gcs_artifact.py
import os, asyncio

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types


async def save_note(text: str, tool_context: ToolContext) -> str:
    """Save text as note.txt; returns the artifact version."""
    part = types.Part(inline_data=types.Blob(
        data=text.encode("utf-8"), mime_type="text/plain"))
    return f"Saved version {await tool_context.save_artifact('note.txt', part)}."


def make_artifact_service():
    bucket = os.environ.get("GCS_BUCKET_NAME")
    if bucket:
        try:
            return GcsArtifactService(bucket_name=bucket)
        except Exception as e:
            print(f"[warn] GCS init failed ({e}); falling back to InMemory.")
    return InMemoryArtifactService()


root_agent = LlmAgent(name="note_taker", model="gemini-2.5-flash",
                     instruction="Call save_note on user-provided text.",
                     tools=[save_note])
app = App(root_agent=root_agent, name="note_app")


async def main():
    runner = Runner(app=app,
                    session_service=InMemorySessionService(),
                    artifact_service=make_artifact_service())
    session = await runner.session_service.create_session(
        app_name="note_app", user_id="carlos")
    msg = types.Content(role="user",
        parts=[types.Part(text="Save this: ship by Friday.")])
    async for ev in runner.run_async(
        user_id="carlos", session_id=session.id, new_message=msg):
        if ev.actions and ev.actions.artifact_delta:
            print("DELTA:", ev.actions.artifact_delta)
        if ev.is_final_response() and ev.content:
            print("REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Run with the env var set, and your note lands in GCS:

```
$ export GCS_BUCKET_NAME=adk-artifacts-my-proj
$ uv run python Work/03_gcs_artifact.py
DELTA: {'note.txt': 0}
REPLY: Saved version 0.

$ gcloud storage ls gs://adk-artifacts-my-proj/note_app/carlos/<session>/note.txt/
gs://adk-artifacts-my-proj/note_app/carlos/<session>/note.txt/0
```

## 🧠 The blob naming scheme

`GcsArtifactService` writes objects at:

```
{bucket}/{app_name}/{user_id}/{session_id}/{filename}/{version}
{bucket}/{app_name}/{user_id}/user/{filename}/{version}     ← if filename starts with "user:"
```

The version is the last segment — every save bumps it. `load_artifact(filename, version=None)` returns the latest; `load_artifact(filename, version=2)` pins.

## ⚠️ Common stumbles

- **Authentication.** Locally, run `gcloud auth application-default login` once. On Cloud Run / Agent Engine the SA is automatic. If you see `DefaultCredentialsError`, that is what is missing.
- **Bucket in the wrong region.** Bucket and compute should match for cost and latency. Cross-region GCS reads quietly add hundreds of ms per artifact load.
- **Mid-run rotation.** Swapping bucket names between deployments orphans every old artifact still referenced by live sessions. Pick one bucket per environment and stick with it; migrate via copy, not switchover.

## ❓ Quick check

> ❓ **Ask the student:** if I `save_artifact("report.pdf", part)` three times in a row, how many GCS objects exist, and which one does `load_artifact("report.pdf")` return? *(Expected: three objects — `.../report.pdf/0`, `.../1`, `.../2`. The bare `load_artifact` returns version 2, the latest. To pin: `load_artifact("report.pdf", version=0)`.)*

> 🛠 **Have the student do this:** if they have a GCP project, create a bucket per the recipe above and run the script. If not, run with `GCS_BUCKET_NAME` unset and confirm the fallback message + InMemory works.

> **🚀 In Production**
>
> A bucket without a lifecycle policy will eat your budget alive — old artifact versions from churn-deleted users accumulate forever. Set a TTL **on day one**, even an optimistically long one like 365 days; tightening later is one command, but reconstructing what should have been deleted is impossible. Forward link: [22 Deployment Models](../22_DeploymentModels/03_AgentEngine.md) for which bucket lives in which deployment shape, and [11 In Production](11_InProduction.md) for the full cost/PII checklist.

---

[← Prev: 04A_ArtifactsHeavyData/02_ArtifactServiceShape](02_ArtifactServiceShape.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/04_SaveAndLoadFromTools →](04_SaveAndLoadFromTools.md)
