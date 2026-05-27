---
module: Detours
page: SignedUrls_GCS
title: GCS Signed URLs — direct upload without proxying through your agent
estimated_minutes: 25
icon: 🌐
prereqs: []
concepts: [signed_url_v4, TTL, content_type_binding, signer_identity, IAM_signBlob, direct_upload, resumable_upload]
---

[← Back to: 04A_ArtifactsHeavyData]  [↑ Map](../../MAP.md)

You are here: 🗺 Detours ▸ Signed URLs (GCS)

> 🧭 **Optional.** Take this if "the client uploads directly to GCS" sounds like magic. Signed URLs are the standard pattern for any agent that handles user files (PDFs, images, audio) — your agent should never proxy bytes. ~25 min.

---

## ☁️ 1. Why signed URLs exist

```
  Naive flow (don't):
  browser ──50 MB PDF──► your agent ──50 MB PDF──► GCS
                          (RAM/CPU)
                          (network egress)
                          (request timeout risk)

  Signed-URL flow:
  browser ──asks──► your agent ──"PUT here, ttl=10min"──► browser
  browser ──50 MB PDF directly──► GCS
  browser ──"done, here's the gs://"──► your agent
```

A **signed URL** is a long URL containing a cryptographic signature that GCS accepts as proof of authorization for a specific operation (usually `PUT`, sometimes `GET`), on a specific object, until a specific time. Anyone who holds the URL during the window can perform the operation — no Google login required.

Result: your agent process never touches the bytes. The browser uploads straight to GCS. Your handler stays small, fast, and free of multi-GB request bodies.

---

## ☁️ 2. V4 signing — the only flavor that matters in 2026

V2 signing is deprecated; V4 (AWS SigV4-compatible) is what you use. The Google Cloud Storage client picks V4 by default.

```python
# Work/sign_upload.py — run with: uv run python Work/sign_upload.py
from datetime import timedelta
from google.cloud import storage

client = storage.Client()
bucket = client.bucket("my-agent-uploads")
blob = bucket.blob("uploads/user_123/doc.pdf")

url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=15),
    method="PUT",
    content_type="application/pdf",  # client MUST send this exact header
)
print(url)
```

Hand `url` back to the browser. The browser then:

```javascript
await fetch(url, {
  method: "PUT",
  headers: { "Content-Type": "application/pdf" },
  body: pdfBlob,
});
```

If `Content-Type` doesn't match the signed value exactly, GCS rejects with `SignatureDoesNotMatch`. That binding is a feature: prevents callers from re-targeting an upload URL at a different content type.

---

## ☁️ 3. TTL — pick the smallest window that works

```
  upload PUT URLs:  5-15 min     enough time for a chunked upload
  download GET URLs: 1-24 hours  matches your UI's typical use
  long-lived URLs:  7 days max   absolute ceiling for V4
```

Defaults to aim for:
- **Single-shot upload from browser** → 10 min.
- **Resumable upload (multi-hour)** → use a resumable session URL (next section), not a long-lived signed URL.
- **Download links shared in chat / email** → 1 hour, regenerate on click if needed.

The signature carries the expiration; you cannot revoke a signed URL early. The traditional workaround is rotating the signer's key (which invalidates all outstanding URLs — nuclear option). For the `signBlob` path (no key file), the equivalent is removing the `roles/iam.serviceAccountTokenCreator` self-binding from the SA, which invalidates all *future* signing requests but leaves already-issued URLs valid until their TTL expires.

---

## ☁️ 4. Content-type binding and other locks

The signed URL pins:

- **HTTP method** (PUT, GET, DELETE, POST resumable-init).
- **Bucket + object name**.
- **Expiration timestamp**.
- **Optionally**: content-type, content-md5, x-goog-* headers.

Anything you pin must be reproduced exactly by the client. Anything you don't pin can be chosen by the client. Pin content-type for uploads — otherwise an attacker can upload an HTML file masquerading as a PDF and serve it back to other users.

```python
url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=10),
    method="PUT",
    content_type="image/png",
    headers={
        "x-goog-content-length-range": "0,10485760",  # cap at 10 MB
    },
)
```

The `x-goog-content-length-range` header is GCS-specific — caps the upload size at the gateway, before bytes hit your bucket.

---

## ☁️ 5. IAM — who can sign

Signing requires a private key associated with a service account. Two paths:

**A. Service account key file** (legacy; avoid in prod):
```python
client = storage.Client.from_service_account_json("sa-key.json")
# generate_signed_url() works directly — the key file holds the signing material
```

**B. ADC + `signBlob` API** (modern; what Cloud Run / Agent Engine use):

The robust idiom is to build an `IAMSigner` and pass it explicitly to `generate_signed_url(...)` — that way the same code works regardless of where the credentials came from (user ADC on a laptop, an SA key file, or GCE/Cloud Run metadata). The fragile shortcut you often see — reading `credentials.service_account_email` and `credentials.token` straight off `google.auth.default()` — only works on `compute_engine.Credentials` (i.e., when running on GCE/Cloud Run); on a developer laptop with user ADC it raises `AttributeError` because user creds have no SA email attached.

```python
# Robust pattern — works on Cloud Run AND on a dev laptop with user ADC.
import google.auth
from google.auth import iam
from google.auth.transport import requests as g_requests
from google.cloud import storage

# 1) Get whatever credentials ADC found (user creds locally, SA on Cloud Run).
#    We need the IAM scope to call signBlob.
source_credentials, project = google.auth.default(
    scopes=["https://www.googleapis.com/auth/iam"],
)
source_credentials.refresh(g_requests.Request())

# 2) Name the service account that will *actually* sign the URL.
#    On Cloud Run / GCE this is usually the runtime SA itself.
#    Locally, it's the SA you've granted yourself permission to impersonate.
signer_email = "my-agent-sa@my-proj.iam.gserviceaccount.com"

# 3) Build an IAM-backed Signer. It calls iamcredentials.signBlob under the hood
#    — no private key material on disk, no AttributeError on user creds.
signer = iam.Signer(
    request=g_requests.Request(),
    credentials=source_credentials,
    service_account_email=signer_email,
)

# 4) Pass `credentials=` explicitly so generate_signed_url uses our signer.
class _SignerCredentials:
    """Thin shim: storage client only needs .signer + .signer_email."""
    def __init__(self, signer, email):
        self.signer = signer
        self.signer_email = email

url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=10),
    method="PUT",
    credentials=_SignerCredentials(signer, signer_email),
)
```

When to use which pattern:

- **`google.auth.compute_engine.Credentials`** (the SA-email-and-access-token shortcut) — *runtime only*: Cloud Run, GCE, GKE, anywhere the metadata server is reachable and the SA email is auto-discovered. Concise but breaks locally.
- **`google.auth.iam.Signer`** (or `iam_credentials_v1.IAMCredentialsClient.sign_blob` directly) — *works everywhere*. On a dev laptop where ADC is your user creds, you must name the SA to impersonate explicitly. This is the recommended portable pattern.

Whichever SA is named as the signer needs **`roles/iam.serviceAccountTokenCreator` on itself** (yes, on itself) to call `signBlob`. This is the canonical "no key files" pattern and what every Cloud Run / Agent Engine deploy should use.

> **🚀 In Production**
>
> Never check service-account JSON keys into the repo, never bundle them in container images. The `signBlob` pattern requires zero key material on disk and rotates automatically. Audit `roles/iam.serviceAccountKeyAdmin` to prevent anyone from creating long-lived keys behind your back.

---

## ☁️ 6. Resumable uploads — for very large or flaky uploads

For files >100 MB or unreliable networks, signed PUT URLs aren't ideal — a network blip restarts the upload. Use a **resumable session URL** instead:

```python
# Server: create a resumable session, hand its URL to the client
blob = bucket.blob("uploads/big.zip")
session_url = blob.create_resumable_upload_session(
    content_type="application/zip",
    size=1_500_000_000,                # bytes; helps GCS allocate
    origin="https://app.example.com",  # for CORS
)
# Return session_url to the client
```

```javascript
// Client: upload in chunks, with Content-Range headers
// On failure, query the session URL for last-received byte, resume
```

The `session_url` is itself a one-time-use URL with a few-hour TTL. It supports chunked PUTs and resumption — the standard pattern for browser-based large-file upload.

---

## ☁️ 7. Wiring into an ADK agent

The typical end-to-end flow with an agent:

```python
# Work/upload_agent/agent.py
from datetime import timedelta
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.cloud import storage

_client = storage.Client()
_bucket = _client.bucket("my-agent-uploads")

def issue_upload_url(user_id: str, filename: str, content_type: str) -> dict:
    """Issue a 10-minute upload URL for a user-supplied file.

    Returns {"url": ..., "gcs_uri": ...}. The client PUTs the file to `url`
    with the given content_type, then reports the gcs_uri back to the agent.
    """
    blob = _bucket.blob(f"uploads/{user_id}/{filename}")
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=10),
        method="PUT",
        content_type=content_type,
    )
    return {"url": url, "gcs_uri": f"gs://{_bucket.name}/{blob.name}"}

root_agent = Agent(
    model="gemini-2.5-flash",
    name="uploader",
    instruction=(
        "When the user wants to upload a file, call issue_upload_url with "
        "their user_id, the filename, and the file's MIME type. Return the "
        "URL and tell them to PUT the file to it within 10 minutes."
    ),
    tools=[FunctionTool(func=issue_upload_url)],
)
```

The agent doesn't move bytes; it brokers permission. A separate "process_uploaded_file" tool (not shown) would then take the `gs://` URI and run extraction / OCR / etc.

---

## 🛠 Have the student try

End-to-end exercise (assumes a bucket `$BUCKET` exists, ADC set up):

```python
# Work/signed_url_smoke.py
import os
from datetime import timedelta
from google.cloud import storage
import requests

client = storage.Client()
blob = client.bucket(os.environ["BUCKET"]).blob("test/hello.txt")

url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=5),
    method="PUT",
    content_type="text/plain",
)
print("URL:", url[:80], "...")

# Upload via the URL — note: NO google-cloud auth, just a plain HTTP PUT
r = requests.put(url, data=b"hello", headers={"Content-Type": "text/plain"})
print("status:", r.status_code)  # 200

print("contents:", blob.download_as_bytes())  # b"hello"
```

Then deliberately break it:

1. Change `Content-Type` to `application/octet-stream` on the PUT → expect 403 `SignatureDoesNotMatch`.
2. Sleep 6 minutes, then retry → expect 403 `Request signature expired`.
3. Truncate one character off the URL → expect 403 `Invalid signature`.

Each failure reinforces what the signature actually binds.

---

[← Back to: 04A_ArtifactsHeavyData/04_SignedURLPattern](../04A_ArtifactsHeavyData/07_SignedUrlsHandoff.md)  [↑ Map](../../MAP.md)

**When you're done:** return to module 04A. The dissecting-sample page shows the same flow inside an agent that processes user-uploaded receipts.
