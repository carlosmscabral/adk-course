---
module: 22_DeploymentModels
page: 04_SessionPersistenceComparison
title: Session persistence — what each platform gives you
estimated_minutes: 20
prereqs: [22_DeploymentModels/03A, 04_SessionsState/05]
concepts: [InMemorySessionService, DatabaseSessionService, VertexAiSessionService, defaults per platform]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 03A_GKE](03A_GKE.md)  [↑ Map](../../MAP.md)  [Next: 05_ScalingAndColdStart →](05_ScalingAndColdStart.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 04 Session persistence

---

## ☁️ The defaults — and why they're dangerous

| Platform       | Default session backend         | Survives pod restart?       | What you need to do                  |
|----------------|---------------------------------|------------------------------|--------------------------------------|
| Cloud Run      | `InMemorySessionService`        | **NO**                       | Set `SESSION_SERVICE_URI`.           |
| GKE            | `InMemorySessionService`        | **NO**                       | Set `SESSION_SERVICE_URI`.           |
| Agent Engine   | `VertexAiSessionService`        | YES (managed)                | Nothing — it's already on.           |

The Cloud Run / GKE defaults are **the same as dev**. Without an explicit `SESSION_SERVICE_URI`, sessions vanish whenever:

- A container is replaced by autoscaling (every few minutes during traffic shifts).
- You deploy a new version.
- The pod OOMs.
- The user comes back next week.

The user-visible symptom: "the agent forgot what we were talking about." If you ship to Cloud Run / GKE without wiring persistence, this is your week-one bug.

## ☁️ Cloud Run + Cloud SQL (Postgres)

The canonical Cloud Run recipe:

```bash
# 1. Provision Cloud SQL Postgres (one-time)
gcloud sql instances create agent-sessions \
    --project=$PROJECT \
    --region=us-central1 \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro

gcloud sql databases create sessions --instance=agent-sessions

# 2. Grant the agent's service account
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:research-assistant@$PROJECT.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# 3. Deploy with the URI
gcloud run deploy research-assistant \
    --add-cloudsql-instances=$PROJECT:us-central1:agent-sessions \
    --set-env-vars="SESSION_SERVICE_URI=postgresql+psycopg://app:PASSWORD@/sessions?host=/cloudsql/$PROJECT:us-central1:agent-sessions"
```

ADK's `DatabaseSessionService` builds on SQLAlchemy. The schema is auto-created on first connect. Use **Cloud SQL Auth Proxy** (the `--add-cloudsql-instances` flag in Cloud Run does this implicitly) so you never put DB credentials in env vars beyond the local user/password.

## ☁️ Cloud Run + Vertex sessions (the unusual case)

You can use `VertexAiSessionService` from Cloud Run *if* you have an Agent Engine resource ID to bind to:

```bash
SESSION_SERVICE_URI="agentengine://projects/123/locations/us-central1/reasoningEngines/456"
```

Use case: you want managed sessions but custom compute (Cloud Run for the agent process). Rare but legit.

## ☁️ GKE + Postgres

Same backend, different ingress:

- Use Cloud SQL via private IP (recommended) or Cloud SQL Auth Proxy as a sidecar.
- Or run Postgres inside the cluster on a StatefulSet (only if you already operate stateful workloads on GKE).

Workload Identity (page 03A) lets the pod authenticate to Cloud SQL without password env vars — issue an `iam:` username.

## ☁️ Agent Engine sessions — what you cannot do

- **No SQL access.** You go through the Vertex API. `list_sessions(user_id=...)`, `get_session(session_id=...)`, `delete_session(...)`.
- **No bulk export built in.** If support needs to grep across sessions, write a daily Cloud Function that walks the Vertex API and writes JSON to BigQuery.
- **No custom schema columns.** You cannot add `tenant_id` as a first-class queryable column. Push it into `state` and accept the API-only query path.

The trade-off is real: zero ops, lower flexibility.

## ☁️ Choosing per platform — the table

| You need…                                  | Cloud Run               | Agent Engine          | GKE                   |
|--------------------------------------------|-------------------------|-----------------------|-----------------------|
| Fast SQL queries across sessions           | Postgres ✓              | ✗ (export to BQ)      | Postgres ✓            |
| Multi-tenant with tenant-scoped backups    | Postgres ✓              | Limited               | Postgres ✓            |
| Zero ops on the session DB                 | Cloud SQL (semi-managed)| **VertexAiSession ✓** | (you own it)          |
| Session history available offline          | Postgres dump ✓         | API export only       | Postgres dump ✓       |
| Cross-region failover                      | Cloud SQL HA ✓          | Managed by Vertex     | Cloud SQL HA ✓        |

If "multi-tenant + SQL queries + ops budget" describe you → Cloud Run + Postgres. If "ship fast + accept lock-in" describe you → Agent Engine.

## ⚠️ Gotcha — schema migrations

`DatabaseSessionService` creates tables on first connect via `CREATE TABLE IF NOT EXISTS`. ADK upgrades that add columns will **not** auto-migrate existing tables. Symptom: `column "new_field" does not exist`. Mitigations:

- Pin the ADK version in your prod requirements and migrate intentionally.
- If you upgrade ADK and the schema changed: drop tables (dev) or write an Alembic migration (prod).

Cross-link: module **04 SessionsState page 06** covers the schema in detail.

## ⚠️ Gotcha — session sharding

A single Postgres instance saturates around **5-10k active sessions** with frequent event writes. Beyond that:

- Shard by `user_id` hash across multiple instances.
- Or move to `VertexAiSessionService` (Vertex shards for you).
- Or use a NoSQL backend (Firestore via a custom session service — not provided out of the box, but the `SessionService` ABC is short).

## 🚀 In Production

> **🚀 In Production**
>
> The session DB is **the single most important durable dependency**. If it's down, your agent looks broken — new sessions fail to create, existing ones can't read history. Treat it like the primary DB of any web service: backups, monitoring, HA, runbook. Cloud SQL HA + automated backups + a tested restore procedure is the bar. "We'll restore from yesterday's snapshot" is not a recovery plan; it's a postmortem footnote.

> ❓ **Ask the student:** "If you deploy v2 of your agent and it crashes on boot, what happens to active conversations?" *(Cloud Run: the previous revision keeps serving until the new one is healthy — sessions intact. Agent Engine: Vertex manages this transparently. GKE: depends on your rollout strategy — RollingUpdate keeps old pods until new are ready.)*

---

[← Prev: 03A_GKE](03A_GKE.md)  [↑ Map](../../MAP.md)  [Next: 05_ScalingAndColdStart →](05_ScalingAndColdStart.md)
