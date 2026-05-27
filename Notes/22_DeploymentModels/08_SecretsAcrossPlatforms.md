---
module: 22_DeploymentModels
page: 08_SecretsAcrossPlatforms
title: Secrets across platforms
estimated_minutes: 20
prereqs: [22_DeploymentModels/07]
concepts: [Secret Manager, env vars, mounted files, rotation]
icon: 🔐
in_production: true
detours_suggested: []
---

[← Prev: 07_ObservabilityWiring](07_ObservabilityWiring.md)  [↑ Map](../../MAP.md)  [Next: 09_CostModelComparison →](09_CostModelComparison.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 08 Secrets

---

## 🔐 The four secrets every agent has

1. **LLM API key** (only if not using Vertex AI ADC) — `GOOGLE_API_KEY` etc.
2. **Database credentials** — Postgres password if not using IAM auth.
3. **Tool credentials** — third-party API keys for tools the agent calls (Frankfurter, Brave, Stripe).
4. **OAuth client secret** — if the agent participates in user OAuth flows (`adk-ae-oauth`).

Each one must be **stored encrypted**, **rotated**, and **scoped** so a leak of one doesn't compromise everything.

## 🔐 Secret Manager — the GCP-native answer

`Google Cloud Secret Manager` is the right home for all four. Versioned, encrypted at rest, IAM-controlled, audit-logged.

```bash
# Create a secret
echo -n "sk_live_..." | \
  gcloud secrets create stripe-api-key --data-file=-

# Grant the agent's SA read access
gcloud secrets add-iam-policy-binding stripe-api-key \
    --member="serviceAccount:research-assistant@$PROJECT.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Rotate — new version, old still readable until you disable it
echo -n "sk_live_new_..." | \
  gcloud secrets versions add stripe-api-key --data-file=-
```

## 🔐 Cloud Run — mount as env var

The Cloud Run-native way: bind a Secret Manager version to an env var at deploy time.

```bash
gcloud run deploy research-assistant \
    --set-secrets="STRIPE_API_KEY=stripe-api-key:latest,DB_PASSWORD=db-password:latest"
```

In Python:

```python
import os
stripe_api_key = os.environ["STRIPE_API_KEY"]
```

**`:latest` is convenient but risky** — a rotation will swap the value mid-run without an explicit redeploy. For mission-critical secrets, pin a version:

```bash
--set-secrets="STRIPE_API_KEY=stripe-api-key:7"
```

Then bump the version explicitly during a controlled rollout.

## 🔐 Cloud Run — mount as file (alternative)

Some libraries expect a file path (TLS certs, GCP JSON keys for non-default identities):

```bash
gcloud run deploy research-assistant \
    --set-secrets="/etc/secrets/tls.pem=tls-cert:latest"
```

Read with:

```python
with open("/etc/secrets/tls.pem") as f:
    cert = f.read()
```

File-mounted secrets are not in `os.environ`, which is harder to accidentally log.

## 🔐 GKE — `Secret` + Workload Identity + External Secrets Operator

Two GKE patterns:

### Pattern A: Kubernetes `Secret` (built-in, weak crypto)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
data:
  stripe-api-key: c2tfbGl2ZV8u...   # base64
```

Kubernetes secrets are only **base64-encoded**, not encrypted at rest by default. Enable **etcd encryption** for the cluster, or use Pattern B.

### Pattern B: External Secrets Operator pulling from Secret Manager

ESO is a controller that syncs from external secret stores (Secret Manager, Vault, AWS Secrets Manager) into Kubernetes secrets. The agent reads the K8s secret; ESO keeps it fresh.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: agent-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: gcp-secrets
    kind: ClusterSecretStore
  target:
    name: agent-secrets
  data:
    - secretKey: stripe-api-key
      remoteRef:
        key: stripe-api-key
```

Combined with Workload Identity, the secret never lives in a JSON file in the image and rotates within an hour of Secret Manager updates.

## 🔐 Agent Engine — env vars at deploy

Agent Engine accepts env vars at engine-create time. The `adk deploy agent_engine` flow injects them via `--set-env-vars`. There's no built-in Secret Manager binding analogous to Cloud Run; the canonical pattern is to read Secret Manager **at startup** in `set_up()`:

```python
# in AgentEngineApp.set_up()
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{PROJECT_ID}/secrets/stripe-api-key/versions/latest"
response = client.access_secret_version(name=name)
os.environ["STRIPE_API_KEY"] = response.payload.data.decode()
```

The Vertex SA running the Engine must have `secretmanager.secretAccessor` on the secret. Rotate by killing the engine instance (Vertex restarts it; new `set_up()` reads new secret).

## 🔐 What to do with `GOOGLE_API_KEY`

If you're using **Vertex AI** (recommended in GCP), you don't need it — ADC handles auth.

If you're using **Gemini API** (e.g., dev / non-GCP environments), the API key is a secret. Put it in Secret Manager. Never:

- Commit it to git.
- Pass it on the command line (`gcloud run deploy --set-env-vars="GOOGLE_API_KEY=..."` — visible in shell history, logs).
- Print it in logs (set up a log scrubber if your error handlers might dump env).

## ⚠️ Gotcha — secrets in process memory

Secrets read into Python strings are in process memory until GC. Crash dumps, OOM cores, debug printouts can leak them. Mitigations:

- Use `secretstr` (Pydantic's SecretStr) — masks in `repr()` and logs.
- Clear after use where feasible: `del key`.
- Disable core dumps in production: `ulimit -c 0` in the entrypoint.

This is not paranoia; the OWASP API top-10 has a category for it.

## ⚠️ Gotcha — secrets in events

Tool calls may include secrets in **arguments**. ADK's `LoggingPlugin` and `BigQueryAgentAnalyticsPlugin` log the args verbatim. **Sanitize** in a `before_tool_callback`:

```python
def redact_secret_args(callback_context, tool, args, **_):
    redacted = {k: ("<redacted>" if "key" in k.lower() or "token" in k.lower() else v)
                for k, v in args.items()}
    return {"args": redacted}
```

Cross-link: module 16 page 04 § secrets handling.

## 🚀 In Production

> **🚀 In Production**
>
> **Rotate before you have to.** Quarterly rotation for all secrets, monthly for high-blast-radius ones (database root, OAuth client secret). Automate it. The "we don't rotate because nothing has happened" team is the one in the postmortem next year. Set a Cloud Scheduler job that calls a Cloud Function that bumps Secret Manager versions and re-deploys; budget half a day to wire it once, then never think about it again.

> ❓ **Ask the student:** "What's the difference between `--set-env-vars` and `--set-secrets` on Cloud Run, and why does it matter for `Cloud Logging`?" *(`--set-env-vars` puts the value in plaintext in the service config — visible in `gcloud run services describe`. `--set-secrets` puts a *reference*; Cloud Run resolves it at startup. Logs of the deploy command include the env var value but not the secret value.)*

---

[← Prev: 07_ObservabilityWiring](07_ObservabilityWiring.md)  [↑ Map](../../MAP.md)  [Next: 09_CostModelComparison →](09_CostModelComparison.md)
