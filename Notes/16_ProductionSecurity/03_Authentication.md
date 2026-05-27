---
module: 16_ProductionSecurity
page: 03_Authentication
title: Auth context for tools — AuthHandler and CredentialManager
estimated_minutes: 25
prereqs: [16_ProductionSecurity/02, 03_Tools/05]
concepts: [AuthHandler, CredentialManager, base_authenticated_tool, ToolContext, per-user auth]
icon: 🔐
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/02_PromptInjectionDefense](02_PromptInjectionDefense.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/04_SecretsHandling →](04_SecretsHandling.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 03 Authentication

---

## 🔐 The problem

Your agent is multi-tenant. Alice's session must not be able to fetch Bob's data — even if Alice asks nicely and the model is willing.

The wrong place to enforce this is *the prompt* ("the user is Alice, do not access Bob's data"). The model will be talked out of it.

The right place is *the tool*. The tool's first action is to consult `ToolContext` for the authenticated user and refuse any request that doesn't match.

## 🔐 The pieces

- **`AuthHandler`** — defines the auth flow (OAuth, API key, JWT verification). Knows how to validate a token and produce a principal.
- **`CredentialManager`** — stores per-session credentials (refresh tokens, etc.) so the user does not re-auth on every turn.
- **`ToolContext.auth_state`** — what the tool reads to know "who is this for?"
- **`base_authenticated_tool`** — a base class / decorator that *requires* a successful auth before the tool body runs.

The shape:

```
runner.run_async(user_id="alice", ...)
            │
            ▼
   ┌───────────────────────┐
   │ AuthHandler.resolve() │  ── token validated, principal = "alice"
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────────────────────┐
   │ tool_context.auth_state = {           │
   │   "user_id": "alice",                 │
   │   "scopes": ["read:cart"],            │
   │   "principal": ...                    │
   │ }                                     │
   └───────────────────┬───────────────────┘
                       │
                       ▼
   def access_cart(cart_id: str, tool_context: ToolContext):
       if tool_context.auth_state["user_id"] != cart_owner(cart_id):
           return {"error": "forbidden"}
       ...
```

## 🛠 Pattern in practice — `customer-service` sample

See `/home/carloscabral/study/adk-samples/python/agents/customer-service/customer_service/shared_libraries/callbacks.py` lines 88-126: `validate_customer_id` checks the model-provided `customer_id` against the session's authenticated `customer_profile`. The check runs in a `before_tool_callback` so *every* tool with a `customer_id` arg is gated.

```python
def before_tool(tool, args, tool_context):
    if "customer_id" in args:
        valid, err = validate_customer_id(args["customer_id"], tool_context.state)
        if not valid:
            return err  # short-circuits the tool, returns err to the LLM
```

The lesson: **don't trust the model to pick the right user_id**. The model can be tricked. The tool gate cannot.

> **🧭 See also**: `adk-ae-oauth` — `/home/carloscabral/study/adk-samples/python/agents/adk-ae-oauth/` shows the full OAuth 2.0 dance for Agent Runtime / Gemini Enterprise: the `negotiate_creds()` three-stage credential resolution, the `auths.py` configuration, and reading Google Drive *as the user*. Read `adk_ae_oauth/auths.py` and the Drive tools — that is the production reference for per-user OAuth in ADK. Dissected end-to-end at [[22_DeploymentModels/10_DissectingSample]].

## 🔐 base_authenticated_tool — the decorator approach

For new code, prefer wrapping the tool with the framework's `base_authenticated_tool` (or `@requires_auth(scope=...)`-style decorator). The pattern:

```python
@requires_auth(scopes=["read:cart"])
def access_cart(cart_id: str, tool_context: ToolContext):
    # body only runs if auth_state has the scope
    ...
```

The decorator does three things you would otherwise re-do: presence check, scope check, audit log of the decision (see L6 in `_figures/defense_in_depth.txt`).

## 🧠 Per-user vs per-app credentials

| Credential | Stored where | Used for |
|---|---|---|
| **Per-user** (OAuth refresh token, user JWT) | `CredentialManager` keyed by session | Tools that act *as the user* (their Gmail, their Drive). |
| **Per-app** (service-account key, GCP ADC) | Process env / Secret Manager | Tools that act *as the app* (your DB, your billing). |

Mixing them is the second-most-common security bug. The agent should never use the service account to read a per-user resource without an additional authorization check.

> 🛠 **Have the student run:** in the M4 auditor, add a fake `tool_context.state["user_id"]` and a tool that reads `user_id`. Then craft a prompt that tries to make the model pass a *different* user_id. The before_tool_callback should block it.

> 🚀 **In Production**
>
> Every auth refusal should be logged with `tool_name`, `requested_principal`, `actual_principal`, `decision`, `trace_id`. This is the **audit trail** your security team will demand. See [[16_ProductionSecurity/10_InProduction]] § audit.

---

[← Prev: 16_ProductionSecurity/02_PromptInjectionDefense](02_PromptInjectionDefense.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/04_SecretsHandling →](04_SecretsHandling.md)
