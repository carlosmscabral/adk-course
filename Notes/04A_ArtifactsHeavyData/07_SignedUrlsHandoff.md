---
module: 04A_ArtifactsHeavyData
page: 07_SignedUrlsHandoff
title: Signed URLs & cross-agent handoff ☁️
estimated_minutes: 25
prereqs: [04A_ArtifactsHeavyData/06]
concepts: [signed-url, V4-signing, TTL, sub-agent-handoff]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/06_VideoUnderstanding](06_VideoUnderstanding.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/08_ArtifactDeltaInEvents →](08_ArtifactDeltaInEvents.md)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 07 Signed URLs & handoff ☁️

# ☁️ Pass URLs between sub-agents, not bytes

We saw on page 04 that sub-agents share a session, so they can hand off by filename: agent A `save_artifact("report.pdf", part)`, agent B `load_artifact("report.pdf")`. That works **inside one runtime**. The moment your sub-agents live in different processes — an A2A remote agent, a Cloud Function tool, a browser frontend, a third party — there is no shared `artifact_service` to read from.

The standard pattern: **upload to GCS once, mint a short-lived signed URL, pass the URL.** Whoever has the URL has time-bounded access; nobody copies bytes around.

## 🧠 Signed URLs in 60 seconds

A V4-signed URL is a regular HTTPS URL with a signature query string. GCS validates the signature against the signing service account's key and serves the object — no GCP IAM check on the requester. Two knobs that matter:

- **`expiration`** — how long the URL is valid. Pass `datetime.timedelta(minutes=15)`. Default to short; refresh on demand.
- **`method`** — `"GET"` for downloads (most common), `"PUT"` for browser-direct uploads (skips your backend).

You need either a key file with `private_key`, or to run as a service account that can self-sign (Cloud Run / Agent Engine give you this automatically via the IAM Credentials API).

## 🛠 A tool that mints a download URL

```python
# Work/07_signed_url_tool.py — run with: uv run python Work/07_signed_url_tool.py
import asyncio
import datetime as dt

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types


_client = storage.Client()


async def mint_download_url(
    bucket: str, object_path: str, tool_context: ToolContext
) -> str:
    """Return a 15-minute signed download URL for gs://{bucket}/{object_path}."""
    blob = _client.bucket(bucket).blob(object_path)
    url = blob.generate_signed_url(
        version="v4",
        expiration=dt.timedelta(minutes=15),
        method="GET",
    )
    # Save the URL itself as a tiny artifact so downstream agents can read it
    part = types.Part(text=url)
    await tool_context.save_artifact(f"signed_url_{object_path.replace('/', '_')}.txt", part)
    return f"Signed URL ready (15-min TTL); saved as artifact."


root_agent = LlmAgent(
    name="url_minter", model="gemini-2.5-flash",
    instruction=(
        "When asked to share an object, call mint_download_url with the bucket "
        "and object path. Tell the user the URL has been prepared."
    ),
    tools=[mint_download_url],
)
app = App(root_agent=root_agent, name="url_app")


async def main():
    runner = Runner(app=app, session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService())
    s = await runner.session_service.create_session(
        app_name="url_app", user_id="carlos")
    msg = types.Content(role="user", parts=[types.Part(
        text="Mint a download URL for my-bucket / reports/Q1.pdf.")])
    async for ev in runner.run_async(
        user_id="carlos", session_id=s.id, new_message=msg):
        if ev.actions and ev.actions.artifact_delta:
            print("DELTA:", ev.actions.artifact_delta)
        if ev.is_final_response() and ev.content:
            print("REPLY:", ev.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output (assuming the bucket and object exist):

```
DELTA: {'signed_url_reports_Q1.pdf.txt': 0}
REPLY: Signed URL ready (15-min TTL); saved as artifact.
```

## 🛠 The cross-agent handoff pattern

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   uploader       │ writes  │   GCS bucket     │ reads   │  remote consumer │
│   sub-agent      │────────▶│   (private)      │◀────────│  (different proc │
│ - mint signed PUT│         │                  │         │   or sub-agent)  │
│ - return URL via │         └────────┬─────────┘         │ - GET via signed │
│   output_key=    │                  │                   │   URL            │
└──────────────────┘                  │                   └──────────────────┘
                                      │
                                      ▼
                       artifact_service holds the
                       (filename, version) reference;
                       state holds the URL string
                       (short-lived; do NOT log it)
```

Three rules for the handoff:

1. **TTL on the order of minutes**, not hours. The URL is functionally a bearer token — leaks = data exposure.
2. **Pass the URL via `output_key=` / state**, not as a tool return value the LLM might paraphrase. The exact string matters.
3. **Mint, do not store.** Generate fresh URLs per handoff; never persist URLs in state past the conversation. The artifact in the bucket is the source of truth; URLs are ephemeral access tickets.

## 🧠 Why this beats shipping bytes

- **Bandwidth**: bytes traverse the network once (uploader → GCS), not three times (uploader → orchestrator → consumer).
- **Memory**: no agent needs to hold the full payload; each just deals with a URL.
- **Auditability**: GCS access logs show every GET — you know exactly who pulled what when.
- **Decoupling**: the consumer can be a different process, an A2A peer (Module 10), a webhook callback (Module 24). All they need is HTTPS.

## ⚠️ Stumbles

- **Signing without a private key locally.** Plain `google.auth.default()` credentials cannot sign without an `iam.serviceAccounts.signBlob` call. On Cloud Run / Agent Engine this works automatically. Locally you may need a key file or `--impersonate-service-account` on `gcloud auth application-default login`.
- **Pasting the URL into logs.** Treat signed URLs like passwords. Module 15 covers redaction; the rule is: never log a URL with a `?X-Goog-Signature=` query string.
- **TTL too long.** A 24-hour URL that escapes your system stays exploitable for 24 hours. Default to ≤ 15 minutes; renew programmatically if the consumer needs more time.

## ❓ Quick check

> ❓ **Ask the student:** the orchestrator agent asks a remote A2A agent to summarise a 200 MB PDF the user uploaded. What flows across the A2A boundary? *(Expected: a signed URL — not the bytes, not even the artifact name in your local artifact service. The remote agent has no access to your `artifact_service`; the only common ground is HTTPS-fetchable GCS. Mint a 5-minute signed URL, pass it in the A2A payload, the remote agent GETs and reads.)*

> 🛠 **Have the student do this:** if they have a GCS object handy, run the script with their bucket/object. Inspect the saved artifact's text — confirm the URL has the `X-Goog-Signature` query string. Try the URL in a fresh browser; it should download once, and after 15 minutes return 403.

> **🚀 In Production**
>
> Signed URLs are convenient and dangerous — they bypass IAM by design. The mitigation triangle: (1) short TTL (≤ 15 min), (2) never log, (3) prefer PUT signed URLs for browser uploads so bytes never traverse your backend at all. See [SignedUrls_GCS detour](../Detours/SignedUrls_GCS.md) for the deep dive.

---

[← Prev: 04A_ArtifactsHeavyData/06_VideoUnderstanding](06_VideoUnderstanding.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/08_ArtifactDeltaInEvents →](08_ArtifactDeltaInEvents.md)
