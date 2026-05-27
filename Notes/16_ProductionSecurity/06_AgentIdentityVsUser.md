---
module: 16_ProductionSecurity
page: 06_AgentIdentityVsUser
title: Agent identity vs controlling-user identity
estimated_minutes: 30
prereqs: [16_ProductionSecurity/03, 16_ProductionSecurity/05]
concepts: [service account, end-user identity, impersonation, ADC, token exchange, OIDC, IAM]
icon: ⚠️
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/05_GuardrailsCookbook](05_GuardrailsCookbook.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/07_GeminiAsJudgePlugin →](07_GeminiAsJudgePlugin.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 06 Agent vs User Identity

---

## ⚠️ Two identities, one tool call

When `agent.run_async(user_id="alice", ...)` calls a BigQuery tool, **whose IAM applies?**

There are two answers and they are *both right* — for different things:

| Identity | What it is | Used for |
|---|---|---|
| **Agent identity** | The process's service account (SA). On Cloud Run that's the SA you attached at deploy. On Agent Engine, the managed runtime SA. | Calls the agent *itself* makes — Vertex AI inference, BigQuery for system tables, GCS for artifacts. |
| **Controlling-user identity** | The end-user the agent is acting for — Firebase user, OIDC `sub` claim, IAP identity, OAuth principal. | Anything the user must be authorized for — *their* Drive, *their* Calendar, *their* row in your DB. |

The bug everyone ships first: **the agent uses its service account to read a per-user resource without an extra check.** Now Alice can ask the agent for Bob's data and the SA happily fetches it — because the SA *is* allowed to read all rows.

## 🧠 Why this dichotomy is under-taught

Most ADK tutorials run on a developer laptop with `gcloud auth application-default login` — ADC is *your* user identity, and there is no second identity. Deploy to Cloud Run, ADC becomes the runtime SA, and now "the agent" is doing things on behalf of "nobody in particular." That is the moment to learn this page.

## 🛠 Pattern A — SA + tool-level authz check

The agent process holds a service account with broad read access. Every tool that touches per-user data **re-checks** that `tool_context.state["user:auth_sub"]` matches the row's owner.

```python
# Work/16_ProductionSecurity/01_sa_with_authz.py
# run with: uv run python Work/16_ProductionSecurity/01_sa_with_authz.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import ToolContext
from google.genai import types

CARTS = {"cart_42": {"owner": "alice", "items": ["book"]},
         "cart_77": {"owner": "bob",   "items": ["mug"]}}

def get_cart(cart_id: str, tool_context: ToolContext) -> dict:
    """Return the cart, only if the calling user owns it."""
    cart = CARTS.get(cart_id)
    if not cart:
        return {"error": "not found"}
    caller = tool_context.state.get("user:auth_sub")
    if cart["owner"] != caller:
        return {"error": "forbidden",
                "caller": caller, "owner": cart["owner"]}
    return cart

agent = LlmAgent(model="gemini-2.5-flash", name="shop",
                 instruction="Use get_cart for any cart query.",
                 tools=[get_cart])

async def main():
    runner = InMemoryRunner(agent=agent, app_name="shop")
    s = await runner.session_service.create_session(
        app_name="shop", user_id="alice",
        state={"user:auth_sub": "alice"})
    msg = types.Content(role="user",
        parts=[types.Part.from_text(text="show me cart_77")])
    async for ev in runner.run_async(user_id="alice",
            session_id=s.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text: print(p.text)

asyncio.run(main())
```

The SA fetched the row. The *tool body* refused. That's the only correct shape when the SA has more authority than any single user.

## 🛠 Pattern B — User-asserted token (Firebase / OIDC / IAP)

The frontend sends a signed user JWT with each request. Your API gateway (or `before_agent_callback`) verifies it and writes the `sub` into `state["user:auth_sub"]`. The SA is now only used for *infrastructure* calls. Per-user resources go through per-user clients.

```python
# Work/16_ProductionSecurity/02_user_token.py
# run with: uv run python Work/16_ProductionSecurity/02_user_token.py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Imagine: middleware decoded the Firebase JWT.
verified_claims = {"sub": "alice", "email": "alice@example.com"}

async def before_agent_callback(callback_context):
    callback_context.state["user:auth_sub"]   = verified_claims["sub"]
    callback_context.state["user:auth_email"] = verified_claims["email"]

agent = LlmAgent(model="gemini-2.5-flash", name="profile",
                 instruction="If you know the user's email, greet them by it.",
                 before_agent_callback=before_agent_callback)

async def main():
    runner = InMemoryRunner(agent=agent, app_name="p")
    s = await runner.session_service.create_session(app_name="p", user_id="alice")
    msg = types.Content(role="user", parts=[types.Part.from_text(text="hi")])
    async for ev in runner.run_async(user_id="alice", session_id=s.id, new_message=msg):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text: print(p.text)

asyncio.run(main())
```

Token verification itself belongs in the framework (FastAPI dependency, IAP header parser), not in the agent. The agent's job is to *trust the verified claim* state put in front of it. See [[22_DeploymentModels/06_AuthAndIAM]] for the platform side.

## 🛠 Pattern C — Impersonation / token exchange (act *as* the user)

When the tool must call an API that *only knows the user's identity* (their Google Drive, their Calendar), the SA cannot just fetch — it must obtain a downstream token *for that user*. Three flavors:

- **GCP service-account impersonation** (`iam.serviceAccounts.getAccessToken`): the agent SA mints a short-lived token for a per-customer SA. Useful for B2B "act as the customer's tenant."
- **OAuth refresh-token flow**: store the user's OAuth refresh token in `CredentialManager` (see page 03), exchange for a fresh access token per call. Used by Gmail / Calendar tools.
- **STS token exchange** (RFC 8693): swap an incoming OIDC token for a Google-signed token via Workload Identity Federation. The clean answer for "user came via Auth0, tool needs to call BigQuery as that user."

Sketch — the OAuth refresh case wired into a tool:

```python
# Work/16_ProductionSecurity/03_impersonate.py — sketch (no real OAuth)
from google.adk.tools import ToolContext

def list_user_drive_files(tool_context: ToolContext) -> dict:
    """Return file names from the calling user's Drive."""
    creds = tool_context.state.get("user:gdrive_creds")  # OAuth token bundle
    if not creds:
        return {"error": "no Drive credentials — prompt the user to connect"}
    # In real life: refresh token via google.oauth2.credentials, then
    #   service = build("drive", "v3", credentials=creds_obj)
    return {"files": ["readme.md", "report.pdf"]}  # mock
```

In all three flavors the principle is the same: **the agent's SA is *not* the principal that ends up at the resource.** A second identity flows in via state and is used to mint a downstream credential.

## 🧠 The decision table

| Resource type | Pattern |
|---|---|
| Vertex AI inference, your own GCS bucket for artifacts | Agent SA (Pattern A's "infrastructure" half). |
| Per-row in your multi-tenant DB | SA + tool-level authz check (Pattern A full). |
| User's Google Drive, Calendar, Gmail | OAuth refresh / impersonation (Pattern C). |
| BigQuery dataset owned by the calling user | STS / Workload Identity Federation (Pattern C). |
| Anything where a regulator will ask "who exactly did this?" | Pattern B or C — the SA is not a person. |

## ⚠️ The four common bugs

1. **No second identity at all.** Single-tenant assumption baked in. Every user "is" the SA.
2. **Trusting `tool_context.state["user_id"]` blindly.** The runner accepts whatever string you pass to `user_id`. *Verification* happens *before* the runner, in your gateway. The agent's job is to trust *verified* state.
3. **Mixing SA permissions with per-user authz.** SA can read everything; tool body forgot the owner check. Same bug as IDOR (Insecure Direct Object Reference) in classic web apps.
4. **Logging the user token.** The bearer token is a secret. Redact it from spans (see [[15_Observability/08_InProduction]]) and from any callback that touches `llm_request`.

> 🛠 **Have the student run:** `01_sa_with_authz.py`. Then change the message to `show me cart_42` — same script, no auth changes — and watch the tool succeed. The SA fetched both rows; the authz check decided.

> 🚀 **In Production**
>
> Run a quarterly "who-can-act-as-whom" audit. List every tool, every IAM role on the SA, every per-user credential the agent can mint. For each row write the principal the *resource* actually sees. If that column is "the SA" for anything per-user, you have an open IDOR. The Cloud Run-side setup of the SA itself is in [[Detours/Cloud_Run]]; the Agent Engine equivalent in [[Detours/AgentEngine]].

---

[← Prev: 16_ProductionSecurity/05_GuardrailsCookbook](05_GuardrailsCookbook.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/07_GeminiAsJudgePlugin →](07_GeminiAsJudgePlugin.md)
