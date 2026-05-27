---
module: 22_DeploymentModels
page: 03A_GKE
title: GKE — the third path
estimated_minutes: 25
prereqs: [22_DeploymentModels/03]
concepts: [GKE, Helm chart, Workload Identity, sidecars, when GKE wins]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 03_AgentEnginePath](03_AgentEnginePath.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionPersistenceComparison →](04_SessionPersistenceComparison.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 03A GKE

---

## ☁️ When GKE is the right answer

GKE is the answer when **none** of these are true:

- "I want the simplest thing." → Cloud Run.
- "I want sessions + observability + safety classifier built in." → Agent Engine.

GKE is the answer when **at least one** of these is true:

- You already run GKE. Adding the agent to existing infra is cheaper than starting a parallel deployment story.
- You need a **sidecar** — a TLS terminator, a protocol bridge (gRPC ↔ HTTP), an Envoy proxy for mTLS, a Vault agent.
- You need a **service mesh** — Anthos Service Mesh / Istio for mTLS, circuit breakers, traffic shifting.
- You need **strict network policies** — Kubernetes NetworkPolicy is finer-grained than VPC SC.
- You need **Workload Identity Federation** across clusters / clouds.
- You need a **specific kernel / GPU configuration** — Cloud Run gives you neither.

If none of those resonate, you do not need GKE. The ops weight is real.

## ☁️ `adk deploy gke` — the official path

```bash
adk deploy gke \
    --project=$PROJECT \
    --cluster_name=my-cluster \
    --region=us-central1 \
    --service_name=research-assistant \
    --app_name=research_assistant \
    ./research_assistant
```

What it does:

1. Builds a Docker image (same Dockerfile as Cloud Run path; page 02).
2. Pushes to Artifact Registry.
3. Renders Kubernetes manifests:
   - `Deployment` (1+ replicas, with the image)
   - `Service` (ClusterIP by default; can override to LoadBalancer)
   - Optional `HorizontalPodAutoscaler`
   - Optional `ServiceAccount` with Workload Identity binding
4. Applies via `kubectl apply -f -` against your current kubeconfig context.

Suitable for a getting-started deploy. For real prod, you write your own manifests / Helm chart.

## ☁️ The Helm chart shape

Real teams put the agent in a Helm chart that they version + roll forward. Sketch:

```
charts/research-assistant/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── serviceaccount.yaml
    ├── hpa.yaml
    └── networkpolicy.yaml
```

Key `deployment.yaml` fragments:

```yaml
spec:
  replicas: {{ .Values.replicas }}
  template:
    spec:
      serviceAccountName: {{ .Release.Name }}        # Workload Identity SA
      containers:
        - name: agent
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
          ports:
            - containerPort: 8080
          env:
            - name: GOOGLE_CLOUD_PROJECT
              value: {{ .Values.gcp.project }}
            - name: SESSION_SERVICE_URI
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: session-uri
          resources:
            requests: { cpu: "500m", memory: "1Gi" }
            limits:   { cpu: "2",    memory: "2Gi" }
          readinessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 10
          livenessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 30
```

`requests` is for the scheduler; `limits` is the hard cap. Agent processes are usually request-bound (not throughput-bound) — set CPU `requests` to your **per-request CPU** so HPA scales when the queue grows, not when CPU saturates.

## ☁️ Workload Identity — the security win

Workload Identity binds a Kubernetes ServiceAccount to a Google ServiceAccount. The pod gets GCP credentials **without** mounting a JSON key file.

```bash
# 1. Create the GSA
gcloud iam service-accounts create research-assistant-gsa \
    --project=$PROJECT

# 2. Grant the GSA Vertex AI access
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:research-assistant-gsa@$PROJECT.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# 3. Bind KSA → GSA
gcloud iam service-accounts add-iam-policy-binding \
    research-assistant-gsa@$PROJECT.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:$PROJECT.svc.id.goog[default/research-assistant]"

# 4. Annotate the KSA so it knows which GSA to impersonate
kubectl annotate serviceaccount research-assistant \
    iam.gke.io/gcp-service-account=research-assistant-gsa@$PROJECT.iam.gserviceaccount.com
```

Now the agent's Python code calls `google.auth.default()` and gets the GSA's credentials transparently — no key files, no env vars with secrets. This is the **single biggest reason GKE wins for security-conscious teams**.

## ☁️ When you need a sidecar

A real example: you need to ground agent responses against an on-prem document store reachable only via a corporate proxy. The proxy needs mTLS with your fleet's CA.

- **Cloud Run / Agent Engine**: cannot run a sidecar. You'd need a separate reverse proxy in front, adding hops + latency.
- **GKE**: deploy `envoy` as a sidecar container in the same pod. Agent talks to `localhost:9000`; envoy handles mTLS to the corporate proxy. Same pod, same network namespace, no extra latency.

```yaml
spec:
  containers:
    - name: agent
      image: my-agent:latest
      env:
        - name: GROUNDING_BACKEND_URL
          value: "http://localhost:9000"
    - name: envoy
      image: envoyproxy/envoy:v1.28-latest
      volumeMounts:
        - name: envoy-config
          mountPath: /etc/envoy
      ports:
        - containerPort: 9000
```

## ⚠️ Gotcha — health checks must be cheap

GKE liveness probes hit `/health` every few seconds. If your `/health` accidentally invokes the LLM (e.g., "check the model is reachable"), you'll spend **dollars per pod per day** on health checks. Make `/health` purely local — return `{"status": "ok"}` without touching downstream deps. Use `/readiness` (called less often) for deeper checks if needed.

## ⚠️ Gotcha — log volume

GKE pods can log GB per day per pod. Cloud Logging charges per GB ingested. Mitigations:

- Use **structured logging** (JSON) and let Cloud Logging route based on severity.
- Sample debug logs in prod (page 7 of module 15).
- Set log-based metric rules instead of grep-based queries.

## 🚀 In Production

> **🚀 In Production**
>
> GKE gives you all the control and all the responsibility. The cluster needs upgrades, the network policies need maintenance, the HPA needs tuning, and the cost of a misconfigured pod (OOM loop, runaway autoscale) is real. Budget at least **0.5 engineer-week per month** for ongoing ops, more if you don't already run GKE. If that's more than you can afford, Cloud Run or Agent Engine wins on TCO even if their per-request cost looks higher.

> ❓ **Ask the student:** "Your agent needs to call an internal API reachable only inside your VPC. Which path?" *(All three work if configured. GKE is simplest because the pod is already in the VPC. Cloud Run needs Serverless VPC Connector. Agent Engine needs Private Service Connect + custom networking — non-trivial.)*

---

[← Prev: 03_AgentEnginePath](03_AgentEnginePath.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionPersistenceComparison →](04_SessionPersistenceComparison.md)
