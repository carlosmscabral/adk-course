---
module: 16_ProductionSecurity
page: 03_Authentication
title: Auth context for tools — AuthHandler and CredentialManager
estimated_minutes: 25
prereqs: [16_ProductionSecurity/02, 03_Tools/05]
concepts: [AuthConfig, BaseAuthenticatedTool, request_credential, get_auth_response, ToolContext, per-user auth]
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

- **`AuthConfig`** (`google.adk.auth.auth_tool.AuthConfig`) — bundles the `auth_scheme` (OAuth2, API key, …) with the `raw_auth_credential` your tool was configured with. The shape that ADK passes around the framework.
- **`AuthHandler`** — internal — turns the `AuthConfig` into a request the client must satisfy, and reads the response back out of session state.
- **`CredentialManager`** — internal — caches the resolved credential per session so you do not re-auth every turn.
- **`BaseAuthenticatedTool`** (`google.adk.tools.base_authenticated_tool.BaseAuthenticatedTool`) — the base class to subclass when you want the framework to do the auth dance for you and hand you a ready `credential`. Source: `src/google/adk/tools/base_authenticated_tool.py`.
- **`ToolContext.request_credential(auth_config)` and `ToolContext.get_auth_response(auth_config)`** — the two methods you actually call from a tool body. See `src/google/adk/agents/context.py` lines 679 (get_auth_response) and 696 (request_credential).

The shape — two turns, not one:

```
turn 1  tool body
        ──────────────────────────────────────────────
        cred = tool_context.get_auth_response(auth_config)
        if cred is None:
            tool_context.request_credential(auth_config)
            return "auth required"      # client sees this and starts OAuth

turn 2  (client has now completed OAuth and replayed the function call)
        ──────────────────────────────────────────────
        cred = tool_context.get_auth_response(auth_config)   # now non-None
        use cred.oauth2.access_token to call the API
        return real result
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

## 🔐 `BaseAuthenticatedTool` — the framework recipe

> ⚠️ There is **no** `@requires_auth(...)` decorator in `google.adk` and **no** `tool_context.auth_state` attribute. If you see those in a snippet — yours, an LLM's, or an older write-up of this page — it is fabricated. The real API is `BaseAuthenticatedTool` + `tool_context.request_credential` / `get_auth_response`.

For a tool that needs per-user OAuth (or an API key the client must supply), subclass `BaseAuthenticatedTool`. The framework will:

1. Look up a cached credential for this `auth_config` via the `CredentialManager`.
2. If none exists, call `request_credential(auth_config)` on your behalf, return your `response_for_auth_required` placeholder, and pause.
3. On the next turn — after the client has driven the OAuth flow and replayed the function call — call your `_run_async_impl(...)` with a ready `credential: AuthCredential` argument.

Minimal example (verify shapes against `src/google/adk/tools/base_authenticated_tool.py` and `src/google/adk/auth/auth_tool.py`):

```python
from typing import Any
from google.adk.tools.base_authenticated_tool import BaseAuthenticatedTool
from google.adk.tools.tool_context import ToolContext
from google.adk.auth.auth_tool import AuthConfig
from google.adk.auth.auth_credential import AuthCredential
from fastapi.openapi.models import OAuth2  # the real OAuth2 class
# Note: `google.adk.auth.auth_schemes` re-exports FastAPI's `OAuth2`
# (auth_schemes.py:22) — importing it from ADK gives you the FastAPI class,
# not an ADK-defined one. Import directly from FastAPI to avoid confusion.
# ADK's own auth-scheme types are `OpenIdConnectWithConfig` (auth_schemes.py:33)
# for OIDC and `ExtendedOAuth2` (auth_schemes.py:89) for OAuth2 with issuer-URL
# auto-discovery — reach for those when you need ADK-specific behavior.

class AccessCartTool(BaseAuthenticatedTool):
    def __init__(self, auth_config: AuthConfig):
        super().__init__(
            name="access_cart",
            description="Read the current user's shopping cart.",
            auth_config=auth_config,
            response_for_auth_required="Pending user authorization.",
        )

    async def _run_async_impl(
        self,
        *,
        args: dict[str, Any],
        tool_context: ToolContext,
        credential: AuthCredential,
    ) -> Any:
        token = credential.oauth2.access_token       # ready to use
        cart_id = args["cart_id"]
        return await fetch_cart(cart_id, bearer=token)
```

If you cannot subclass (e.g. you are wrapping a `FunctionTool`), do the dance by hand:

```python
async def access_cart(cart_id: str, tool_context: ToolContext):
    cred = tool_context.get_auth_response(auth_config)
    if cred is None:
        tool_context.request_credential(auth_config)   # function_call_id required
        return {"status": "auth_required"}
    return await fetch_cart(cart_id, bearer=cred.oauth2.access_token)
```

That is the same flow the base class implements for you — see `BaseAuthenticatedTool.run_async` in the source.

## 🧠 Per-user vs per-app credentials

| Credential | Stored where | Used for |
|---|---|---|
| **Per-user** (OAuth refresh token, user JWT) | `CredentialManager` keyed by session | Tools that act *as the user* (their Gmail, their Drive). |
| **Per-app** (service-account key, GCP ADC) | Process env / Secret Manager | Tools that act *as the app* (your DB, your billing). |

Mixing them is the second-most-common security bug. The agent should never use the service account to read a per-user resource without an additional authorization check.

> 🛠 **Have the student run:** in the M4 auditor, seed `tool_context.state["user_id"] = "alice"` and add a tool that reads `user_id` from its args. Then craft a prompt that tries to make the model pass a *different* user_id. The `before_tool_callback` should compare `args["user_id"]` to `tool_context.state["user_id"]` and block the mismatch.

> 🚀 **In Production**
>
> Every auth refusal should be logged with `tool_name`, `requested_principal`, `actual_principal`, `decision`, `trace_id`. This is the **audit trail** your security team will demand. See [[16_ProductionSecurity/10_InProduction]] § audit.

---

[← Prev: 16_ProductionSecurity/02_PromptInjectionDefense](02_PromptInjectionDefense.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/04_SecretsHandling →](04_SecretsHandling.md)
