---
module: 16_ProductionSecurity
page: 04_SecretsHandling
title: Secrets — Secret Manager, ADC, .env is dev-only
estimated_minutes: 15
prereqs: [16_ProductionSecurity/03]
concepts: [Secret Manager, ADC, .env, CI secrets, prompt leakage]
icon: 🔑
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/03_Authentication](03_Authentication.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/05_GuardrailsCookbook →](05_GuardrailsCookbook.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 04 Secrets

---

## 🔑 The rules (short)

1. **Never hard-code.** A secret in the repo, even private, is compromised on day one.
2. **`.env` is dev-only.** Never deployed to prod. Add `.env` to `.gitignore` on the first commit.
3. **ADC for Google Cloud.** `gcloud auth application-default login` locally; service-account identity on Cloud Run / GKE / Agent Engine.
4. **Secret Manager for everything else.** Mounts as a file or env var at runtime.
5. **CI secrets via a vault.** GitHub Actions secrets, GitLab CI variables, etc. Never echo them.
6. **Secrets never enter prompts.** Not even as "context." If the model sees it, it can be exfiltrated.

## 🛠 The right pattern

```python
import os
from google.cloud import secretmanager

def _get_secret(name: str) -> str:
    # In Cloud Run: identity is the service account; ADC just works.
    client = secretmanager.SecretManagerServiceClient()
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    resp = client.access_secret_version(
        name=f"projects/{project}/secrets/{name}/versions/latest"
    )
    return resp.payload.data.decode("utf-8")

STRIPE_KEY = _get_secret("stripe-api-key")
```

Three properties:
- The code is identical in dev, staging, prod. Only the identity differs.
- Rotating the key is a Secret Manager UI click; no code change.
- The key is never written to the image, the repo, or the container env file.

## ⚠️ Common leak paths

| Leak path | Mitigation |
|---|---|
| Secret in tool args (`call_api(api_key="...")`) | Tool reads secret from env / Secret Manager. Args have no secret. |
| Secret in system instruction (`"Use API key abc123 to call X."`) | Same — tool fetches its own key. |
| Secret in stack trace shown to user | Catch and log; reply with opaque error id. |
| Secret in OTel span attribute | Sanitize in `before_tool_callback` (page 05 cookbook). |
| Secret in BigQuery analytics row | Same sanitization; cross-link [[15_Observability/08_InProduction]] § 7. |
| Secret in CI logs (printed by mistake) | Mask in CI config + secret scanner on the PR. |

> ❓ **Ask the student:** which of the six leak paths above does *placing the secret in a prompt* defend against? *(None — and it actively creates the first two.)*

## 🛠 The `.env.example` discipline

```
# .env.example  (committed)
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=us-central1
MODEL_ARMOR_TEMPLATE_ID=
```

```
# .env  (NOT committed)
GOOGLE_CLOUD_PROJECT=my-real-project
...
```

The example file documents *which* env vars are required; the real file is gitignored. Every sample in `adk-samples` does this — see `/home/carloscabral/study/adk-samples/python/agents/safety-plugins/.env.example` as a model.

> 🚀 **In Production**
>
> Add a pre-commit hook that runs a secret scanner (e.g., `gitleaks`, `trufflehog`). Catching a leaked key before push is one workflow; rotating a leaked key after push is six. See also [[16_ProductionSecurity/10_InProduction]] § secrets.

---

[← Prev: 16_ProductionSecurity/03_Authentication](03_Authentication.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/05_GuardrailsCookbook →](05_GuardrailsCookbook.md)
