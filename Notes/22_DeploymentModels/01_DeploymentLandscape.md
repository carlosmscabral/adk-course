---
module: 22_DeploymentModels
page: 01_DeploymentLandscape
title: The deployment landscape — Cloud Run vs Agent Engine vs GKE
estimated_minutes: 20
prereqs: [22_DeploymentModels/00]
concepts: [Cloud Run, Agent Engine, GKE, decision criteria]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_CloudRunPath →](02_CloudRunPath.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 01 Landscape

---

## ☁️ The three paths

Three official destinations for an ADK agent on GCP. See [_figures/deployment_comparison.txt](_figures/deployment_comparison.txt) for the side-by-side ASCII.

```
┌─────────────────┬──────────────────────┬──────────────────────┐
│   Cloud Run     │   Agent Engine       │   GKE                │
│   container     │   managed Runtime    │   Kubernetes         │
└─────────────────┴──────────────────────┴──────────────────────┘
```

All three serve the **same `/run`, `/run_sse`, `/run_live`** wire surface from module 21. The agent code does not change. What changes is **who owns** the runtime.

## ☁️ The summary table

| Dimension                  | Cloud Run                  | Agent Engine                 | GKE                         |
|----------------------------|----------------------------|------------------------------|-----------------------------|
| **Deploy unit**            | Container (OCI)            | `AgentEngineApp` Python obj  | Container in a Pod          |
| **Build**                  | Your Dockerfile            | Vertex builds for you        | Your Dockerfile             |
| **Sessions out of box**    | InMemory (you wire DB)     | **Managed (`VertexAiSessionService`)** | InMemory (you wire DB) |
| **Auth at edge**           | You add IAP / OIDC         | **IAP + Gemini Enterprise**  | You add IAP / ingress       |
| **Auto-scaling**           | Yes (0..N)                 | Yes (managed)                | HPA (you configure)         |
| **Scale to zero**          | **Yes (default)**          | Yes (cold-start managed)     | No (replicas ≥ 1 usually)   |
| **Cold start**             | 2-6s (mitigatable)         | Managed                      | None if min-replicas > 0    |
| **Max request duration**   | 60min                      | Managed                      | You configure               |
| **WebSocket (Live)**       | Yes (15min cap)            | **Yes (extended)**           | Yes (you set cap)           |
| **Observability**          | You wire OTel + Cloud Log  | **Built-in to Vertex**       | You wire OTel               |
| **Custom sidecars**        | No                         | No                           | **Yes**                     |
| **Workload Identity**      | Service account binding    | Vertex SA                    | **Workload Identity**       |
| **Per-request cost**       | Lowest (compute only)      | Higher (managed premium)     | Lowest (compute only)       |
| **Ops weight**             | Low                        | Lowest                       | Highest                     |
| **Lock-in**                | OCI standard, low          | High (Vertex SDK contract)   | Low (k8s standard)          |

The bold cells are the **distinctive wins** of each path.

## ☁️ A decision flowchart

```
START
  │
  ├─ "I need it live by tomorrow, simplest path"         → Cloud Run
  │
  ├─ "I want sessions, auth, observability all built in" → Agent Engine
  │
  ├─ "I already run GKE / need sidecars / mesh / VPC"    → GKE
  │
  ├─ "I'm doing voice/video Live"                        → Agent Engine
  │    (Cloud Run works but caps at 15min; GKE works but you own the LB tuning)
  │
  ├─ "I need to ship to Gemini Enterprise UI"            → Agent Engine
  │    (only path that natively integrates with the GE OAuth + agent registry)
  │
  └─ "Cost is the dominant constraint"                   → Cloud Run
       (token cost dominates everywhere; compute cost matters mostly at high RPS)
```

This is not a sacred order. Many production agents start on Cloud Run for speed and migrate to Agent Engine once they need managed sessions.

## ☁️ What each path is *not*

- **Cloud Run is not "ADK on Cloud Run".** It's a container. The container can run ADK; it can also run your wrapping FastAPI + custom routes (module 21 page 06). That's the whole appeal.
- **Agent Engine is not "Cloud Run for agents".** It's a Pydantic-typed Vertex resource (`AdkApp` subclass) where the runtime is Google's. The Python contract is narrower.
- **GKE is not "harder Cloud Run".** It's the only path that lets you co-locate your agent with a sidecar, run inside a service mesh, or use Workload Identity Federation across clusters.

## ☁️ Quick mental model

```
                 Trade-off axis
control ◄─────────────────────────────────────────► managed
  GKE              Cloud Run            Agent Engine
  (full)          (container)        (Vertex-typed)
```

Pick the leftmost point that gives you what you need. Going further right buys you less work; going further left buys you more flexibility.

## ⚠️ Gotcha — region availability

- **Cloud Run**: all GCP regions.
- **Agent Engine**: limited regions (currently `us-central1`, `us-east4`, `europe-west4`, `asia-northeast1` — verify before designing).
- **GKE**: all GCP regions.

If you have a data-residency requirement that lands you in a region without Agent Engine, that decision is made for you.

> ❓ **Ask the student:** "Your team owns 4 GKE clusters and your auth is already on Workload Identity Federation. Which path?" *(GKE — using Cloud Run or Agent Engine would force you to bridge two identity systems.)*

## 🚀 In Production

> **🚀 In Production**
>
> Pick the deployment path **after** you've answered three questions: (1) who handles sessions? (2) who handles auth at the edge? (3) what's your reconnect strategy for long-running requests (SSE / WS)? If you can answer those three the same on all three paths, pick the lowest ops weight (Agent Engine). If your answers differ per path, the answer with the cleanest fit wins.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_CloudRunPath →](02_CloudRunPath.md)
