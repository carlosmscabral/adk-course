---
module: 04A_ArtifactsHeavyData
page: 11_InProduction
title: Artifacts in production — checklist
estimated_minutes: 15
prereqs: [04A_ArtifactsHeavyData/10]
concepts: [lifecycle, signed-url-ttl, PII, cost, fallback-pattern]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/12_KnowledgeCheck →](12_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 04A Artifacts & Heavy Data ▸ 11 In Production

# 🚀 Artifacts & Heavy Data — production checklist

The six mistakes that turn artifact handling from "works in dev" into a Sev-1 page.

## 🚀 1. `InMemoryArtifactService` in any deployment

**Risk**: process restart = total data loss. Cloud Run scales to zero; you lose every artifact.
**Mitigation**: pick `GcsArtifactService` for prod (or `FileArtifactService` on a persistent volume for single-host). Wire the fallback ladder from page 03: try GCS, log + degrade to in-memory only if explicitly absent in dev.
**Inline source**: [02_ArtifactServiceShape § 🚀 In Production](02_ArtifactServiceShape.md)

## 🚀 2. No lifecycle policy on the bucket

**Risk**: every artifact version every user ever wrote sits in GCS forever. Storage cost grows monotonically; eventually it dwarfs your compute bill.
**Mitigation**: set a lifecycle policy at bucket creation — page 03's `gcloud storage buckets update --lifecycle-file` recipe. Pick a TTL appropriate to your domain (30 days for ephemeral; 365 days for compliance; never for legal-hold). **Day-one config, not month-six firefighting.**
**Inline source**: [03_GcsArtifactService § 🚀 In Production](03_GcsArtifactService.md)

## 🚀 3. PII in artifacts

**Risk**: artifacts are still data. The user uploads a passport photo, a medical record, a payslip — and your bucket now holds regulated PII. Lifecycle policies + access logs + IAM all become compliance scope.
**Mitigation**: (a) document what artifacts you accept and their classification; (b) run user uploads past a content-safety check before storing (Module 16); (c) honour deletion-on-request — for GDPR-scope artifacts, your lifecycle policy should support per-user purge; (d) never log signed URLs or `inline_data` bytes in observability pipelines.

## 🚀 4. Signed-URL TTL too long

**Risk**: a signed URL is a bearer token. A 24-hour URL that escapes — pasted in chat, captured in a screenshot, logged accidentally — is exploitable for 24 hours by anyone.
**Mitigation**: default to ≤ 15 minutes. Renew programmatically if the consumer needs more time. Never log signed URLs (the `?X-Goog-Signature=` query string is the smoking gun). Prefer PUT signed URLs for browser uploads so bytes never touch your backend.
**Inline source**: [07_SignedUrlsHandoff § 🚀 In Production](07_SignedUrlsHandoff.md)

## 🚀 5. Returning bytes from a tool

**Risk**: tool returns a `Part` or a long base64 string. That string goes back to the LLM in the next turn's prompt, blows up your tokens, and bloats the event log.
**Mitigation**: tools that produce artifacts return short status strings: `"saved as report.md v0"`. The filename and version are all the LLM ever needs — it can call `load_artifact` later if it needs the bytes.
**Inline source**: [04_SaveAndLoadFromTools § 🚀 In Production](04_SaveAndLoadFromTools.md)

## 🚀 6. Cost — inlining when you should reference

**Risk**: a 35 MB MP4 inlined as `inline_data` triples your request body, burns egress on retries, and may exceed Gemini's per-request size cap. A high-resolution image rendered 50 times per session inlines 50 copies into the event log.
**Mitigation**: bytes > 10 MB → upload to GCS, build a `Part(file_data=FileData(file_uri="gs://..."))`. Reused asset → store once, reference many times. Long videos → trim with `VideoMetadata(start_offset, end_offset)` before sending.
**Inline source**: [05_MultimodalParts § 🚀 In Production](05_MultimodalParts.md), [06_VideoUnderstanding § 🚀 In Production](06_VideoUnderstanding.md)

---

## Cross-references

- [16 Production & Security](../16_ProductionSecurity/) — synthesises every module's checklist, including artifact-specific safety scanning.
- [22 Deployment Models / 03 Agent Engine](../22_DeploymentModels/03_AgentEngine.md) — which GCS bucket your agent talks to depends on the deployment shape; Agent Engine provides one automatically.
- [15 Observability](../15_Observability/) — wire `artifact_delta` into structured logs from day one.
- [Detour: SignedUrls_GCS](../Detours/SignedUrls_GCS.md) — deep dive on V4 signing, browser-direct uploads, audience-restricted URLs.

> 🚀 **In Production** — composite reminder
>
> The single failure mode that bites hardest: shipping `InMemoryArtifactService` to prod because GCS was "not configured yet". The fallback pattern on page 03 is your friend — but only if your deployment env has `GCS_BUCKET_NAME` set. **Make this an env-var-presence check in your CI**, not just in the running agent.

> 🤖 **Tutor:** before the student starts the mini-drill, walk them through rule 5 specifically. Drill grading checks that the tool returns a short status string, not the bytes — students raised on REPL-print habits will instinctively return the artifact content.

---

[← Prev: 04A_ArtifactsHeavyData/10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 04A_ArtifactsHeavyData/12_KnowledgeCheck →](12_KnowledgeCheck.yml)
