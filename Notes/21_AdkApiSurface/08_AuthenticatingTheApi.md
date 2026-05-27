---
module: 21_AdkApiSurface
page: 08_AuthenticatingTheApi
title: Authenticating the API — IAP, OIDC, custom middleware
estimated_minutes: 25
prereqs: [21_AdkApiSurface/06]
concepts: [auth middleware, IAP headers, OIDC token verify, user_id derivation]
icon: 🔐
in_production: true
detours_suggested: []
---

[← Prev: 07_SessionAndEventResources](07_SessionAndEventResources.md)  [↑ Map](../../MAP.md)  [Next: 09_DissectingSample →](09_DissectingSample.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 08 Auth at the boundary

---

## 🔐 The default: nothing

`adk api_server` (and `get_fast_api_app`) ship **no auth**. Anyone who can reach the port can POST `/run`. That's intentional — the framework doesn't pick your identity provider for you.

Three real production patterns:

1. **Cloud IAP** (Google) — your platform handles auth, ADK trusts headers.
2. **OIDC token verify** — your client sends a JWT, you verify in middleware.
3. **Custom token** — your existing auth service issues an opaque token, you exchange it for `user_id`.

All three boil down to: **middleware sets `request.state.user_id` before the route runs.**

## 🔐 Pattern 1 — Cloud IAP

Identity-Aware Proxy sits in front of your Cloud Run / GKE service. After auth, it forwards two headers:

- `x-goog-authenticated-user-email`: `alice@example.com`
- `x-goog-iap-jwt-assertion`: a signed JWT proving IAP authed the request

Middleware that trusts IAP:

```python
# Work/21_AdkApiSurface/08_iap_middleware.py
from fastapi import Request, HTTPException
from google.adk.cli.fast_api import get_fast_api_app

adk_app = get_fast_api_app(agents_dir="./agents", web=False)

@adk_app.middleware("http")
async def iap_auth(request: Request, call_next):
    email = request.headers.get("x-goog-authenticated-user-email")
    if not email:
        raise HTTPException(401, "IAP header missing")
    # Strip the "accounts.google.com:" prefix IAP adds
    user_id = email.split(":")[-1]
    request.state.user_id = user_id
    return await call_next(request)
```

**Critical**: IAP signing must be verified in *prod* (not just on dev). The `x-goog-authenticated-user-email` header can be spoofed if anyone can reach the service bypassing IAP. Verify the `x-goog-iap-jwt-assertion` against IAP's public keys for the deployed audience — `google.auth.jwt.decode` does this with the right `audience` arg.

## 🔐 Pattern 2 — OIDC token verify

Your client gets an OIDC ID token (Firebase, Auth0, Okta) and sends it as `Authorization: Bearer <jwt>`. You verify the signature, audience, and expiry in middleware.

```python
# Work/21_AdkApiSurface/08_oidc_middleware.py
from fastapi import Request, HTTPException
from google.adk.cli.fast_api import get_fast_api_app
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token

adk_app = get_fast_api_app(agents_dir="./agents", web=False)

_request = g_requests.Request()
EXPECTED_AUDIENCE = "my-frontend-client-id.apps.googleusercontent.com"

@adk_app.middleware("http")
async def oidc_auth(request: Request, call_next):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    token = auth.removeprefix("Bearer ").strip()
    try:
        claims = id_token.verify_oauth2_token(token, _request, EXPECTED_AUDIENCE)
    except Exception as e:
        raise HTTPException(401, f"invalid token: {e}")
    request.state.user_id = claims["sub"]
    request.state.email = claims.get("email")
    return await call_next(request)
```

Cache the OIDC discovery keys (the library does some of this); avoid hitting Google's JWKS endpoint per request — that adds 50-200ms.

## 🔐 The matching authz step — user_id must agree with the URL

Middleware sets `request.state.user_id` from the token. The URL has `/users/{user_id}/sessions/...`. **You must check they match** — otherwise an authenticated user can read any session by typing a different `user_id` into the URL.

```python
# Work/21_AdkApiSurface/08_authz_check.py
from fastapi import Request, HTTPException

@adk_app.middleware("http")
async def user_id_matches_url(request: Request, call_next):
    if not request.url.path.startswith("/apps/"):
        return await call_next(request)
    # paths look like /apps/{app}/users/{user}/sessions/...
    parts = request.url.path.split("/")
    try:
        url_user = parts[4]
    except IndexError:
        return await call_next(request)
    if request.state.user_id != url_user:
        raise HTTPException(403, "user_id mismatch")
    return await call_next(request)
```

Apply this **after** the auth middleware so `request.state.user_id` is populated.

> ❓ **Ask the student:** "If I skip this check, which OWASP top-10 category am I violating?" *(Broken Access Control — A01:2021. The single most common API security bug.)*

## 🔐 Pattern 3 — custom token

You have a legacy auth service. Two real options:

- **Exchange the token at the edge**: your gateway converts the opaque token to a signed JWT or known headers; ADK trusts those (pattern 1 mechanics).
- **Verify in-process**: your middleware calls your auth service per request to validate. Adds latency; consider caching the verification result for the token's lifetime.

For high-RPS services, push auth to the edge (load balancer, API gateway). For low-RPS internal services, in-process is fine.

## ⚠️ Gotcha — bypassed by `/health` and `/version`

You probably want `/health` and `/version` to be **unauthenticated** (probes don't have tokens). Either:

- Check the path in your middleware and skip auth for those routes.
- Mount unauthenticated routes on a separate FastAPI app that doesn't have the middleware.

Forgetting this means k8s readiness probes fail with 401.

## 🚀 In Production

> **🚀 In Production**
>
> The auth middleware runs on **every** request — including SSE `/run_sse` connections that may stay open for minutes. Verify tokens **once at handshake**, then keep the connection alive without re-verifying. Re-verifying mid-stream is wasted work; expiring mid-stream is a UX disaster (you'd kill the user's open conversation). Standard practice: tokens valid at SSE-open are valid for that stream's lifetime, capped at e.g. 15min by your reconnect policy.

> 🛠 **Have the student run:** start `06_wrap_fastapi.py`, add the IAP middleware from this page, and `curl /run` with and without the `x-goog-authenticated-user-email` header. The without-header case should be `401`, the with-header case `200`.

---

[← Prev: 07_SessionAndEventResources](07_SessionAndEventResources.md)  [↑ Map](../../MAP.md)  [Next: 09_DissectingSample →](09_DissectingSample.md)
