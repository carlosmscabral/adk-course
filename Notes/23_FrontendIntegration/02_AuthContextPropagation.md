---
module: 23_FrontendIntegration
page: 02_AuthContextPropagation
title: Auth context propagation — token → backend → ToolContext
estimated_minutes: 25
prereqs: [23_FrontendIntegration/01, 16_ProductionSecurity/00]
concepts: [Firebase, OIDC, IAP, bearer_token, ToolContext, state_user_prefix]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 01_WhoOwnsTheSession](01_WhoOwnsTheSession.md)  [↑ Map](../../MAP.md)  [Next: 03_SseFromTheBrowser →](03_SseFromTheBrowser.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 02 Auth Context Propagation

# 🛠 The token's three-hop journey

A user clicks "Send". Their identity needs to travel from their browser all the way down to a tool function that might call BigQuery. That's three hops:

```
   browser ── ID token ──► backend ── verified claims ──► ToolContext ──► tool fn
```

Skip a hop and your tool either runs with the wrong identity, or with no identity at all.

## Hop 1 — browser attaches the token

For **Firebase Auth**:

```javascript
// Work/frontend/auth_fetch.js
async function callRun(prompt, sessionId, userId, firebaseAuth) {
  const token = await firebaseAuth.currentUser.getIdToken();
  const res = await fetch("/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,  // the token rides here
    },
    body: JSON.stringify({
      app_name: "demo",
      user_id: userId,
      session_id: sessionId,
      new_message: { parts: [{ text: prompt }] },
    }),
  });
  return res.json();
}
```

For **OIDC** (Auth0, Okta, Google Sign-In) it's the same shape — your library exposes `getIdToken()` or equivalent.

For **IAP**: you don't attach anything. IAP terminates at the load balancer and injects `X-Goog-Authenticated-User-Email` / `X-Goog-Authenticated-User-Id` headers. The browser is unaware.

## Hop 2 — backend verifies, then forwards

Never trust the token blindly. Verify the signature against the provider's JWKS and check `iss`, `aud`, `exp`.

```python
# Work/23_frontend/verify_firebase.py — run with: uv run python Work/23_frontend/verify_firebase.py
# A FastAPI dependency that turns a Bearer token into a verified user dict.
from fastapi import Depends, FastAPI, Header, HTTPException
from firebase_admin import auth as fb_auth, initialize_app

initialize_app()

async def current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.removeprefix("Bearer ")
    try:
        claims = fb_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(401, f"Bad token: {e}") from e
    return claims  # contains 'uid', 'email', custom claims...

app = FastAPI()

@app.post("/run")
async def run(payload: dict, user: dict = Depends(current_user)):
    # Override any client-supplied user_id with the verified one.
    verified_uid = user["uid"]
    # ... build Runner, call runner.run_async(user_id=verified_uid, ...)
    return {"ok": True, "as": verified_uid}
```

The key move: **the verified `uid` overrides whatever was in the request body.** The client can hint but the server decides.

## Hop 3 — ToolContext sees it via session state

ADK tools don't read FastAPI headers. They read `tool_context.state`. So the hand-off is: **before** calling `runner.run_async`, write the auth claims into `state["user:auth"]` (or similar). Tools then read it.

```python
# Work/23_frontend/auth_into_state.py — run with: uv run python Work/23_frontend/auth_into_state.py
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types as genai_types

def whoami(tool_context: ToolContext) -> dict:
    """Return the current user's email from session state."""
    return {"email": tool_context.state.get("user:email", "anon")}

agent = Agent(
    name="auth_demo",
    model="gemini-2.5-flash",
    instruction="If asked who I am, call whoami() and quote the email.",
    tools=[FunctionTool(whoami)],
)

async def main():
    runner = InMemoryRunner(app_name="demo", agent=agent)
    session = await runner.session_service.create_session(
        app_name="demo",
        user_id="firebase-uid-123",
        state={"user:email": "carlos@example.com"},  # set at session creation
    )
    msg = genai_types.Content(role="user", parts=[genai_types.Part(text="who am I?")])
    async for event in runner.run_async(
        user_id="firebase-uid-123", session_id=session.id, new_message=msg
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.text:
                    print(p.text)

asyncio.run(main())
```

Note `user:email` — the `user:` prefix means the value persists across **all sessions for this `user_id`**. Module [04_SessionsState/02_StateScopes](../04_SessionsState/02_StateScopes.md) covers the four prefixes; for auth claims, `user:` is almost always what you want.

## IAP behind Cloud Run

If the backend is behind IAP, the token verification is *already done* for you. Read the header:

```python
# Work/23_frontend/iap_dep.py
from fastapi import Header, HTTPException

async def iap_user(
    x_goog_authenticated_user_email: str | None = Header(None),
    x_goog_authenticated_user_id: str | None = Header(None),
) -> dict:
    if not x_goog_authenticated_user_id:
        raise HTTPException(401, "No IAP header")
    return {
        "uid": x_goog_authenticated_user_id.removeprefix("accounts.google.com:"),
        "email": (x_goog_authenticated_user_email or "").removeprefix("accounts.google.com:"),
    }
```

**Gotcha:** IAP headers are easy to spoof if anyone can reach your service *bypassing* IAP. Lock the Cloud Run ingress to "Internal and Cloud Load Balancing only" before trusting them.

> 🚀 **In Production**
>
> Every `current_user`-style dependency must reject expired tokens (`exp` claim) and check `aud` against your *exact* project. A token signed for a sibling Firebase project but with the same parent Google org will verify against Google's JWKS happily. Module [16_ProductionSecurity](../16_ProductionSecurity/) has the full checklist.

> ❓ **Ask the student:** "Why do we copy `user:email` into session state on session creation instead of having the tool re-verify the token on every call?"
>
> (Answer: tools don't see HTTP headers. The Runner runs them off the request. State is the only handle they have to upstream context.)

> 🛠 **Have the student run:** the `auth_into_state.py` snippet. Then change `user_id` mid-run and confirm `whoami()` still returns the stored email (state persists, the verified identity is what was set at session create).

[← Prev: 01_WhoOwnsTheSession](01_WhoOwnsTheSession.md)  [↑ Map](../../MAP.md)  [Next: 03_SseFromTheBrowser →](03_SseFromTheBrowser.md)
