---
module: 22_DeploymentModels
page: 06_AuthAndIAM
title: Auth and IAM across platforms
estimated_minutes: 25
prereqs: [22_DeploymentModels/05, 21_AdkApiSurface/08]
concepts: [service accounts, IAP, Workload Identity, principal of least privilege, end-user vs service identity]
icon: 🔐
in_production: true
detours_suggested: []
---

[← Prev: 05_ScalingAndColdStart](05_ScalingAndColdStart.md)  [↑ Map](../../MAP.md)  [Next: 07_ObservabilityWiring →](07_ObservabilityWiring.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 06 Auth & IAM

---

## 🔐 Two identities — keep them separate

Every prod agent has **two** identities that should not be confused:

1. **Service identity** — what the *agent process* uses to call GCP APIs (Vertex AI, BigQuery, Cloud Storage).
2. **End-user identity** — who is making this conversation request, derived from the inbound auth token.

If you mix them — e.g., the agent calls BigQuery as the end user via OAuth — you've added complexity and constraints (per-user quotas, per-user audit trail). If you separate them, the agent uses a service account for Google APIs and tracks end-user identity in `user_id` for application-level authorization.

The exception: **OAuth-on-behalf-of-user** flows. The `adk-ae-oauth` sample (page 10) is the canonical pattern: agent uses service identity for itself, but holds a *separate* user token to read the user's Drive.

## 🔐 Service identity per platform

| Platform      | Default service identity                                  | How to bind a custom one                           |
|---------------|-----------------------------------------------------------|----------------------------------------------------|
| Cloud Run     | `PROJECT-compute@developer.gserviceaccount.com` (broad)   | `gcloud run deploy --service-account=...`          |
| Agent Engine  | A Vertex-managed SA, you grant the SA roles               | Set on the Engine resource at deploy time          |
| GKE           | `default` KSA → node SA (everything in the cluster)       | **Workload Identity** binds KSA ↔ GSA per-pod      |

**Default Cloud Run SA is overprivileged.** Always specify `--service-account=` with a custom SA that has only the roles the agent needs.

## 🔐 Principle of least privilege — the actual roles

For an agent that:

- Calls Gemini via Vertex AI → `roles/aiplatform.user`
- Reads/writes its session DB (Cloud SQL Postgres) → `roles/cloudsql.client`
- Reads BigQuery (e.g., for `BigQueryToolset`) → `roles/bigquery.dataViewer` + `roles/bigquery.jobUser`
- Writes artifacts to GCS → `roles/storage.objectAdmin` on the specific bucket
- Sends OTel traces → `roles/cloudtrace.agent`
- Writes Cloud Logging → `roles/logging.logWriter`

That's it. Anything else is suspect. **Specifically don't** add `roles/owner` or `roles/editor` because "it's easier" — those are the audit findings you'll fix later under pressure.

## 🔐 IAP — Identity-Aware Proxy

IAP sits in front of Cloud Run / GKE and authenticates end users **before** the request reaches your agent. Two benefits:

1. You don't write auth code in the agent.
2. The end-user identity arrives as a signed JWT header (`x-goog-iap-jwt-assertion`).

Enable per platform:

- **Cloud Run**: `gcloud run services update --update-env-vars=...` to enable IAP via the service config; verify the JWT in your middleware.
- **GKE**: enable on the BackendConfig CRD; the JWT lands on every request.
- **Agent Engine**: integrate via Gemini Enterprise (managed); IAP-equivalent flow handled for you.

Page 21 page 08 has the JWT-verification middleware. Re-use it across platforms.

## 🔐 Workload Identity — GKE's killer feature

Recapping from page 03A: Workload Identity binds a Kubernetes ServiceAccount to a Google ServiceAccount.

```
KSA (research-assistant)  ↔  GSA (research-assistant-gsa@project.iam.gserviceaccount.com)
                                          ↓
                              Roles: aiplatform.user, cloudsql.client
                                          ↓
                              Pod calls google.auth.default() → gets GSA creds
                                          ↓
                              No JSON key files. No secrets. Auto-rotated.
```

This is the **single most important security control** for GKE deployments. Without it, you're either (a) mounting JSON key files (rotatable but error-prone) or (b) using the node SA (every workload on the node shares creds). Both lose you any meaningful audit trail.

## 🔐 Agent Engine + Gemini Enterprise OAuth

When you ship to Gemini Enterprise (Agent Engine's UI surface), end-user OAuth is **the platform's job**:

1. Register the OAuth resource (`make register-oauth` in the sample).
2. Register the agent against Gemini Enterprise with the OAuth resource ID.
3. End user signs in to Gemini Enterprise.
4. On the first tool call needing OAuth, Gemini Enterprise presents the consent screen.
5. The granted token is **injected** into `tool_context.state["temp:<AUTH_ID>"]` — your tool reads it from there.

The `negotiate_creds()` three-stage pattern in `adk-ae-oauth/app/tools.py` handles both this flow and the local-dev `request_credential()` flow with the same code. Cross-link: [10_DissectingSample](10_DissectingSample.md).

## 🔐 The end-to-end picture

```
Browser
   │  user logs in (Firebase / IAP / Gemini Enterprise)
   ▼
Ingress (IAP / LB / Gemini Enterprise UI)
   │  forwards request + signed JWT
   ▼
ADK API surface (`/run`, `/run_sse`)
   │  middleware verifies JWT → request.state.user_id
   ▼
Runner.run_async(...)  ← uses SERVICE identity (SA) for Vertex AI
   │
   ├─ Tool call (BigQuery)         ← uses SERVICE identity
   ├─ Tool call (Google Drive)     ← uses USER OAuth token (from tool_context.state)
   └─ Session write (Cloud SQL)    ← uses SERVICE identity
```

End-user identity flows through `user_id` (and optionally end-user OAuth tokens for specific tools). Service identity flows through the SA. They don't mix unless you explicitly bridge them.

## ⚠️ Gotcha — IAP behind a custom domain needs OAuth client config

Putting IAP on `agent.mycompany.com` requires the OAuth consent screen to be configured in the project, with `mycompany.com` as a verified domain. Symptom: IAP says "authorized but redirect failed." Fix: `gcloud iap web add-iam-policy-binding` for users, and ensure the OAuth client lists the right callback URL.

## ⚠️ Gotcha — service account key files in CI

If your CI pipeline uses a long-lived JSON key to deploy, that key is a permanent secret in CI's vault. Modern alternative: **Workload Identity Federation** between GitHub Actions / GitLab / etc. and GCP — short-lived tokens, no JSON keys.

```yaml
# GitHub Actions snippet
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123/locations/global/workloadIdentityPools/gh/providers/gh'
    service_account: 'deployer@project.iam.gserviceaccount.com'
```

If you're still using JSON keys for CI in 2026, rotate them today and migrate to Federation next.

## 🚀 In Production

> **🚀 In Production**
>
> Mixing service identity and end-user identity is the **#1 source of agent security incidents**. Two patterns that go wrong: (a) using the agent's SA to access end-user data (no audit trail per user; broad blast radius if SA leaks); (b) using end-user OAuth to call Google APIs the agent should own (rate-limited per user; users see "permission denied" for things the platform should provide). Decide which identity owns which call, write it down, code-review against it.

> ❓ **Ask the student:** "If the agent's SA gets compromised, what data is at risk?" *(Everything the SA can read. Now go list its IAM roles and explain why each one is needed. That's the threat model.)*

---

[← Prev: 05_ScalingAndColdStart](05_ScalingAndColdStart.md)  [↑ Map](../../MAP.md)  [Next: 07_ObservabilityWiring →](07_ObservabilityWiring.md)
