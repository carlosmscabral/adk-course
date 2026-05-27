---
module: 22_DeploymentModels
page: 00_Overview
title: Overview — where ADK agents actually run in production
estimated_minutes: 10
prereqs: [21_AdkApiSurface/12]
concepts: [Cloud Run, Agent Engine, GKE, deployment trade-offs]
icon: ☁️
in_production: true
detours_suggested: [Cloud_Run, AgentEngine]
---

[← Prev: 21_AdkApiSurface/12_MiniDrill](../21_AdkApiSurface/12_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_DeploymentLandscape →](01_DeploymentLandscape.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 00 Overview

---

## ☁️ What you'll learn

By the end of this module you will:

- Compare the three production paths — **Cloud Run, Agent Engine (Vertex), GKE** — across cost, ops weight, feature surface.
- Pick a path with a decision flowchart you can defend in a design review.
- Know the Dockerfile shape for `adk deploy cloud_run` and what `--with_ui` actually toggles.
- Read an `agent_engine_app.py` line by line (`AdkApp` subclass, telemetry, register_operations).
- Configure persistent sessions for each platform — when to use Postgres vs Vertex-managed vs in-memory.
- Wire auth + IAM + secrets consistently across all three platforms.
- Wire observability so traces are uniform regardless of where the agent runs.
- Compare costs realistically (token cost dominates compute; ops weight dominates engineering cost).
- Dissect `adk-ae-oauth` — a real sample that ships both Agent Engine and Cloud Run configs.

## 🧭 Prereqs

- **21 ADK API Surface** — you must know the routes that get deployed. This module is *where* that surface runs.
- **15 Observability** — we wire trace/log exporters per platform; you've seen the OTel basics.
- **16 Production & Security** — secrets + auth basics. We extend them to platform specifics here.

## ⏱ Time budget

**2 days.** One day on the three-path landscape + Cloud Run (pages 01-02). One day on Agent Engine + GKE + the cross-cutting concerns (03-09). The dissection + drill is the second day's closing exercise.

## 📦 Sample anchor

`/home/carloscabral/study/adk-samples/python/agents/adk-ae-oauth/` — an OAuth-aware ADK agent that ships **two** deployment configs: a Cloud Run path and an Agent Engine path. We read both in [10_DissectingSample](10_DissectingSample.md).

## 🗺 Page map

| #   | Page                              | Why                                                          |
|-----|-----------------------------------|--------------------------------------------------------------|
| 01  | DeploymentLandscape               | The three paths in one table.                                |
| 02  | CloudRunPath                      | Dockerfile, `adk deploy cloud_run`, env vars.                |
| 03  | AgentEnginePath                   | `AgentEngineApp`, `agent_engine_app.py`, managed Runtime.    |
| 03A | GKE                               | Helm chart shape, Workload Identity, when GKE wins.          |
| 04  | SessionPersistenceComparison      | In-memory, Postgres, Vertex-managed — what each path defaults to. |
| 05  | ScalingAndColdStart               | Concurrency, cold-start mitigations, Live API constraints.   |
| 06  | AuthAndIAM                        | Service accounts, IAP, OIDC across the three paths.          |
| 07  | ObservabilityWiring               | OTel exporters, Cloud Logging, BigQuery sink per platform.   |
| 08  | SecretsAcrossPlatforms            | Secret Manager, env vars, sealed secrets.                    |
| 09  | CostModelComparison               | Tokens > compute > ops. The actual math.                     |
| 10  | DissectingSample                  | Read `adk-ae-oauth` — both deployment configs.               |
| 11  | InProduction                      | The consolidated hardening checklist.                        |
| 12  | KnowledgeCheck                    | 7 questions.                                                 |
| 13  | MiniDrill                         | Deploy the M4 auditor to Cloud Run, then to Agent Engine.    |

> 🤖 **Tutor:** before page 01, ask the student which of the three paths they *think* they want. Their first instinct is usually wrong (Agent Engine for "I want simple", but it has feature lag; Cloud Run for "I want control", but it gives less than they think). Use the decision flowchart on page 01 to challenge that intuition.

> 🚀 **In Production**
>
> The right answer is rarely "one path forever." Many teams ship to Cloud Run first (fastest path to URL), then migrate to Agent Engine once they need managed sessions + observability, OR to GKE once they need sidecars / mesh. Build the deployment so the agent code does not change across moves — that's what module **21** was setting up.

---

[← Prev: 21_AdkApiSurface/12_MiniDrill](../21_AdkApiSurface/12_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_DeploymentLandscape →](01_DeploymentLandscape.md)
