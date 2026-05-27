---
module: 23_FrontendIntegration
page: 09_FileUploadFlow
title: File upload — multipart from browser to ArtifactService
estimated_minutes: 20
prereqs: [23_FrontendIntegration/05, 04A_Artifacts/01]
concepts: [multipart, ArtifactService, signed_url, GCS_direct, file_size_limits]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 08_StreamingPartialResults](08_StreamingPartialResults.md)  [↑ Map](../../MAP.md)  [Next: 10_OptimisticUI →](10_OptimisticUI.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 09 File Upload Flow

# 🛠 Two upload paths — pick by file size

A user drops a PDF on your chat input. You need that PDF visible to the agent as an **artifact**, addressable by name from any tool. Two patterns; the size of the file decides.

## Path A — small files (<10 MB), through your backend

The browser POSTs multipart; your FastAPI handler reads bytes; you write to `ArtifactService`. Then you call the Runner with a message referencing the artifact name.

```html
<!-- Work/frontend/upload_min.html -->
<input type="file" id="file">
<button id="send">Upload + Ask</button>
<script>
  document.getElementById("send").onclick = async () => {
    const f = document.getElementById("file").files[0];
    const form = new FormData();
    form.append("file", f);
    form.append("user_id", "u1");
    form.append("session_id", "s1");
    form.append("prompt", "Summarize the attached doc.");
    const r = await fetch("/upload_and_run", { method: "POST", body: form });
    console.log(await r.json());
  };
</script>
```

```python
# Work/23_frontend/upload_server.py — run with: uv run uvicorn Work.23_frontend.upload_server:app --port 8000
from fastapi import FastAPI, UploadFile, Form
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types as genai_types

agent = Agent(name="doc_agent", model="gemini-2.5-flash", instruction="summarize what's attached")

artifact_service = InMemoryArtifactService()
runner = InMemoryRunner(
    app_name="doc_agent", agent=agent, artifact_service=artifact_service
)
app = FastAPI()

@app.post("/upload_and_run")
async def upload_and_run(
    file: UploadFile,
    user_id: str = Form(...),
    session_id: str = Form(...),
    prompt: str = Form(...),
):
    data = await file.read()
    session = await runner.session_service.get_session(
        app_name="doc_agent", user_id=user_id, session_id=session_id
    ) or await runner.session_service.create_session(
        app_name="doc_agent", user_id=user_id, session_id=session_id
    )
    # save artifact — name it after the original filename
    artifact_part = genai_types.Part(
        inline_data=genai_types.Blob(mime_type=file.content_type, data=data)
    )
    version = await artifact_service.save_artifact(
        app_name="doc_agent",
        user_id=user_id,
        session_id=session.id,
        filename=file.filename,
        artifact=artifact_part,
    )
    # send a message that references the file inline
    msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"{prompt}\n\nFile: {file.filename}"), artifact_part],
    )
    out = []
    async for ev in runner.run_async(user_id=user_id, session_id=session.id, new_message=msg):
        if ev.content:
            for p in ev.content.parts:
                if p.text:
                    out.append(p.text)
    return {"filename": file.filename, "version": version, "reply": "".join(out)}
```

**Pros:** simple, one round-trip from the user's perspective. **Cons:** files traverse your backend → memory pressure, request body limits.

Cross-reference: [04A Artifacts & Heavy Data](../04A_Artifacts/) covers `ArtifactService` types (`InMemory`, `GcsArtifactService`) and versioning semantics in depth.

## Path B — large files, direct to GCS via signed URL

For files >10 MB, you don't want them touching your backend at all. Pattern:

1. Browser asks backend for a **signed upload URL** (your backend mints it against GCS).
2. Browser PUTs the file directly to GCS.
3. Browser tells the backend the file is uploaded; backend constructs an artifact reference (URI, not bytes) and runs the agent.

```python
# Work/23_frontend/signed_url_server.py
from fastapi import FastAPI
from google.cloud import storage
from datetime import timedelta

app = FastAPI()
bucket = storage.Client().bucket("my-uploads")

@app.post("/upload_url")
async def upload_url(filename: str, content_type: str):
    blob = bucket.blob(f"uploads/{filename}")
    url = blob.generate_signed_url(
        version="v4", expiration=timedelta(minutes=15),
        method="PUT", content_type=content_type,
    )
    return {"url": url, "gcs_uri": f"gs://my-uploads/uploads/{filename}"}
```

```javascript
// Work/frontend/upload_signed.js
async function uploadLarge(file, prompt) {
  const meta = await fetch("/upload_url", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({filename: file.name, content_type: file.type}),
  }).then(r => r.json());

  await fetch(meta.url, {
    method: "PUT",
    headers: {"Content-Type": file.type},
    body: file,
  });

  // tell backend to run with the artifact reference
  return fetch("/run_with_gcs", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({gcs_uri: meta.gcs_uri, prompt}),
  });
}
```

The agent side then loads the file via `GcsArtifactService` or reads `gs://...` directly. Gemini supports `Part.file_data(file_uri="gs://...")` for direct GCS reads — no bytes through your backend.

## Validation rules

- **MIME allow-list.** Don't blindly trust `file.type` — sniff content or restrict by extension.
- **Size cap.** FastAPI: configure max body size (or use streaming uploads).
- **Virus scan.** For untrusted users, run uploads through Cloud Storage virus scan / a sandbox before letting an agent touch them.

> 🚀 **In Production**
>
> Path A's biggest failure mode: a user uploads a 500 MB PDF, your FastAPI worker reads it into memory, OOMs, kills the request, frontend retries, repeat. **Always** set a request body limit + reject early with a 413. Better: route >10 MB through Path B unconditionally.

> ❓ **Ask the student:** "Why is Path B's signed URL `PUT` instead of `POST`?"
>
> (Answer: GCS signed URLs use HTTP verbs that match S3-style object semantics — `PUT` = create/replace one object. POST is for multipart form uploads to a different style of endpoint.)

> 🛠 **Have the student run:** the Path A server with a tiny `.txt` file. Watch it round-trip. Then upload a 50 MB file and observe FastAPI's response time / memory — sets up why Path B exists.

[← Prev: 08_StreamingPartialResults](08_StreamingPartialResults.md)  [↑ Map](../../MAP.md)  [Next: 10_OptimisticUI →](10_OptimisticUI.md)
