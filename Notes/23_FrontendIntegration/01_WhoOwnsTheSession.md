---
module: 23_FrontendIntegration
page: 01_WhoOwnsTheSession
title: Who owns user_id and session_id?
estimated_minutes: 20
prereqs: [23_FrontendIntegration/00, 04_SessionsState/02]
concepts: [user_id, session_id, session_ownership, mint_policy]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_AuthContextPropagation →](02_AuthContextPropagation.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 01 Who Owns The Session

# 🧠 Two IDs, two owners

Every ADK call you make from the browser carries two strings:

- **`user_id`** — *the person*. Stable across sessions, devices, and time.
- **`session_id`** — *one conversation*. New every time the user clicks "New chat".

Get the ownership wrong and the symptoms are weird: conversations bleed across tabs, "new chat" reuses old history, two devices think they're the same session. The rule is **boring once stated**, and stating it is half this page.

## Rule 1 — `user_id` is supplied by the frontend, but it is **not invented** there

The frontend reads `user_id` from the authenticated identity. **It does not mint it.** Concretely:

| Auth | `user_id` source |
|------|------------------|
| Firebase Auth | `firebaseUser.uid` |
| OIDC (Google/Auth0/Okta) | `id_token.sub` |
| IAP (Cloud Run / GKE) | `x-goog-authenticated-user-id` from the IAP-signed header |
| Dev / unauth | a UUID stored in `localStorage` — fine for dev, **never** prod |

```javascript
// Work/frontend/identity.js — run with: node Work/frontend/identity.js (smoke)
// In a real browser app this runs on page load.
async function getUserId(firebaseAuth) {
  const user = firebaseAuth.currentUser;
  if (!user) throw new Error("Not signed in");
  return user.uid;  // Firebase: stable, opaque, e.g. "Xy3kZ..."
}
```

The backend will *re-verify* the token (page 02) and refuse the call if the `user_id` the frontend asserts doesn't match. **Never trust a client-supplied `user_id` without verification.**

> 🚀 **In Production**
>
> If the backend ever takes `user_id` from a request body without verifying the token, you have an IDOR. The fix is: ignore the body field, derive `user_id` from the verified token, server-side. Treat the body `user_id` as a *hint for logging only*.

## Rule 2 — `session_id` is minted by **whoever needs to address the session first**

Two valid patterns. Pick one per app and stick with it.

### Pattern A — Frontend mints (the common case)

The browser generates a `session_id` when the user clicks "New chat". It's a UUID. The frontend sends it on every request. The backend calls `session_service.create_session(session_id=...)` *lazily* on first use — `get_session` then `create_session` if missing.

```python
# Work/23_frontend/session_lazy_create.py — run with: uv run python Work/23_frontend/session_lazy_create.py
import asyncio
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent

agent = Agent(name="demo", model="gemini-2.5-flash", instruction="be terse")

async def get_or_create(runner, app_name, user_id, session_id):
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
    return session

async def main():
    runner = InMemoryRunner(app_name="demo", agent=agent)
    s = await get_or_create(runner, "demo", "user-abc", "session-from-frontend-123")
    print("session:", s.id, "events:", len(s.events))

asyncio.run(main())
```

**Pros:** the frontend has the ID *before* the network call, so it can render an optimistic "new chat" UI immediately. No round-trip to learn your own session ID.

**Cons:** the frontend has to generate UUIDs (`crypto.randomUUID()` — boring, fine).

### Pattern B — Backend mints, returns it

The browser calls `POST /sessions` with no body, the backend calls `session_service.create_session()` (which generates an ID), and the response is `{"session_id": "..."}`. The browser stores it.

**Pros:** the frontend never touches UUID generation; the backend has total control.

**Cons:** a round-trip before any UI can render. For chat UIs this is usually fine — the user hits "New chat", you POST, you get an ID, you're ready.

## The rule (after the two patterns)

**The session is whoever's name is on it first.** Pick A or B at the start of the project. Document it in your README. Never mix.

> ❓ **Ask the student:** "Your team picked pattern A (frontend mints). A user opens a new tab — should that tab share the existing `session_id` or mint a new one?"
>
> (Answer: depends on UX. If "open in new tab" means "continue this conversation in a new window", reuse. If it means "start fresh", mint. Most chat UIs use a per-tab `sessionStorage` UUID — fresh per tab.)

## Where this lives in ADK

The Runner takes both: `runner.run_async(user_id=..., session_id=..., new_message=...)`. The `SessionService` is the only thing that mutates the session — never write to `session.events` from your handler code. Cross-reference: [04_SessionsState/02_StateScopes](../04_SessionsState/02_StateScopes.md) names the four scopes (`user:`, `app:`, `temp:`, no-prefix) that determine *where* the data lives once IDs are pinned.

> 🚀 **In Production**
>
> A subtle one: when you scale beyond `InMemorySessionService`, *every* replica needs to be able to look up *any* `session_id`. `DatabaseSessionService` or `VertexAiSessionService` handles this. In-memory + multi-replica = sessions vanish on load-balancer round-robin. Module [22 Deployment](../22_DeploymentModels/) covers the swap.

> 🛠 **Have the student run:** `Work/23_frontend/session_lazy_create.py` twice in a row with the same `session_id`. Confirm the second run finds the session. Now change the `session_id` and confirm it creates fresh.

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_AuthContextPropagation →](02_AuthContextPropagation.md)
