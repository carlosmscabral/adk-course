---
module: 22_DeploymentModels
page: 11_InProduction
title: In Production — deployment hardening checklist
estimated_minutes: 25
prereqs: [22_DeploymentModels/10]
concepts: [least-privilege SA, session durability, secrets, budgets, cold start, observability gates]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 12_KnowledgeCheck →](12_KnowledgeCheck.yml)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 11 In Production

---

## 🚀 The checklist

Consolidates the `🚀 In Production` callouts from this module's concept pages, plus the cross-cutting hardening items you only see after the first incident.

### 1. Pick the deployment model on **operational maturity**, not feature lists

- **Risk**: teams default to "GKE because we're using K8s elsewhere" or "Agent Engine because it's the newest." Both are wrong defaults for many cases.
- **Mitigation**: use the flowchart on [01 Landscape](01_DeploymentLandscape.md#a-decision-flowchart). Cloud Run is the right answer ~70% of the time. Agent Engine when sessions/long-running/Gemini-Enterprise are dealbreakers. GKE only if a cluster already exists with on-call.
- **Inline source**: [01_DeploymentLandscape § In Production](01_DeploymentLandscape.md).

### 2. Never deploy with the default compute service account

- **Risk**: Cloud Run's default SA is `PROJECT-compute@developer.gserviceaccount.com` and has `roles/editor` project-wide. A compromised agent has near-owner powers.
- **Mitigation**: `--service-account=` with a custom SA that holds **only** the roles from [06 Auth & IAM § least-privilege list](06_AuthAndIAM.md#principle-of-least-privilege-the-actual-roles).
- **Inline source**: [06_AuthAndIAM § In Production](06_AuthAndIAM.md#in-production).

### 3. Move session state off the pod before launch

- **Risk**: `InMemorySessionService` (Cloud Run / GKE default) loses every conversation on pod restart. Users get "what were we talking about?"
- **Mitigation**: `DatabaseSessionService` (Cloud SQL Postgres) or `VertexAiSessionService`. Pick before launch. Agent Engine handles this for free.
- **Inline source**: [04_SessionPersistenceComparison § In Production](04_SessionPersistenceComparison.md).

### 4. Budget alerts and token-rate alerts together

- **Risk**: a loop bug burns through tokens at $1.20/sec. By the time the monthly bill alert fires, you're at $4000.
- **Mitigation**: GCP Billing budget alerts at 50/80/100% **plus** a token-rate metric alerting at 2x baseline. Both. Catches slow leaks AND fast incidents.
- **Inline source**: [09_CostModelComparison § In Production](09_CostModelComparison.md#in-production).

### 5. Cold start needs an answer, even if the answer is "we accept it"

- **Risk**: Cloud Run cold start is 3-8s. First user of the day waits. Voice agents lose connection.
- **Mitigation**: either set `--min-instances=1` (~$10/mo, eliminates cold for first-after-idle), use `--cpu-boost`, lazy-import heavy deps, or move to Agent Engine. Pick consciously.
- **Inline source**: [05_ScalingAndColdStart § In Production](05_ScalingAndColdStart.md).

### 6. Concurrency knob is **not** the Cloud Run default

- **Risk**: Cloud Run's `--concurrency=80` default is for fast HTTP responses. Agent turns are 3-8s. 80 concurrent turns on one CPU = thrashing, 30s p99.
- **Mitigation**: start at `--concurrency=10`, load-test, raise until p95 starts to climb, use half of that.
- **Inline source**: [05_ScalingAndColdStart § concurrency tuning](05_ScalingAndColdStart.md#concurrency-tuning).

### 7. Secrets via Secret Manager, never via `--set-env-vars` or git

- **Risk**: API keys in env vars are visible in `gcloud run services describe` and in deploy command history. Keys in git stay forever (rotate everything if you push one).
- **Mitigation**: `--set-secrets` (Cloud Run), External Secrets Operator (GKE), `set_up()` Secret Manager read (Agent Engine). Pin versions for mission-critical secrets.
- **Inline source**: [08_SecretsAcrossPlatforms § In Production](08_SecretsAcrossPlatforms.md).

### 8. Rotate secrets quarterly minimum, monthly for high-blast-radius

- **Risk**: a never-rotated secret in a leaked log is a credential to your prod indefinitely.
- **Mitigation**: Cloud Scheduler → Cloud Function → `gcloud secrets versions add` → re-deploy. Half a day to wire, then automatic.
- **Inline source**: [08_SecretsAcrossPlatforms § In Production](08_SecretsAcrossPlatforms.md).

### 9. Trace sampling — full tracing at scale costs more than your compute

- **Risk**: 100% trace sampling at 100 RPS = $500+/month on Cloud Trace alone. Forgotten knob.
- **Mitigation**: 1-5% trace sampling, 100% BigQuery analytics logging (cheap). Cross-link 15 page 08.
- **Inline source**: [07_ObservabilityWiring § In Production](07_ObservabilityWiring.md).

### 10. Service identity ≠ end-user identity — write the boundary down

- **Risk**: agent's SA used for end-user data = no per-user audit, broad blast radius. End-user OAuth used for agent's own GCP calls = per-user rate limits hitting platform features.
- **Mitigation**: in the design doc, list every external call the agent makes and which identity owns it. Code-review against the doc.
- **Inline source**: [06_AuthAndIAM § In Production](06_AuthAndIAM.md).

### 11. Deploys are gated on a smoke test, not on `gcloud run deploy` exit code

- **Risk**: `gcloud run deploy` returns 0 if the container *started*. It doesn't mean the agent works. First user catches the bug.
- **Mitigation**: post-deploy smoke test: `curl /health` then a real `/run` against a known prompt with a known expected substring in the response. Roll back if it fails.
- **Inline source**: new in this checklist (not on a concept page).

### 12. Region pinning — agent region = LLM region = DB region

- **Risk**: agent in `us-central1`, Vertex in `us-east4`, Postgres in `europe-west1`. Every turn pays cross-region latency twice.
- **Mitigation**: pin all three to the same region. If you must go multi-region, use Agent Engine (handles it) or per-region Cloud Run with regional DBs and ingress-based routing.
- **Inline source**: cross-link [05_ScalingAndColdStart](05_ScalingAndColdStart.md).

---

> 🤖 **Tutor:** before the mini-drill, walk this checklist against the student's M4 auditor. Most builds violate items 2, 3, 5, 7, 11 in their first deploy. Don't fix all 12 in one sitting — the mini-drill will catch the worst offenders by forcing the student to deploy twice and notice what differs.

> 🚀 **In Production** — composite reminder
>
> The deployment model determines the **shape** of your incidents. Cloud Run gives you cold start incidents and session-loss incidents. Agent Engine gives you cost-spike and vendor-lock incidents. GKE gives you upgrade incidents and IAM misconfiguration incidents. There is no incident-free option; pick the incidents you have an answer for.

---

[← Prev: 10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 12_KnowledgeCheck →](12_KnowledgeCheck.yml)
