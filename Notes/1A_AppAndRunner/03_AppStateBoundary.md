---
module: 1A_AppAndRunner
page: 03_AppStateBoundary
title: The `app:` state boundary — lifetime semantics
estimated_minutes: 25
prereqs: [1A_AppAndRunner/02, 01_Foundations/04]
concepts: [state-prefixes, app-state, user-state, temp-state, BaseSessionService]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 02_OnStartupShutdown](02_OnStartupShutdown.md)  [↑ Map](../../MAP.md)  [Next: 04_WiringResumability →](04_WiringResumability.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 03 App State Boundary

# 🧠 The `app:` state boundary

State in ADK is just a dict that lives on the `Session`. But **the key prefix changes where the dict actually lives** — and how long it lives. The `app:` prefix is the one that requires the `App` to make sense, which is why this page is here.

## 🧠 The four prefixes

```
key                  scope                   lives until                  belongs to
─────────────────────────────────────────────────────────────────────────────────────
"theme"              session-scoped          session is deleted           one (user, session)
"user:tier"          user-scoped             user is forgotten            one user across all sessions
"app:feature_flags"  app-scoped              app is rebuilt fresh         everyone using this app
"temp:tool_buffer"   invocation-scoped       end of this one invocation   nobody, ever; not persisted
```

The session service inspects the key prefix on every write and routes the entry to a different storage bucket. From the agent's perspective it is all the same `state` dict.

## 🛠 Watch the prefix decide where state goes

```python
# Work/1A_state_prefixes.py — run with: uv run python Work/1A_state_prefixes.py
import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


agent = LlmAgent(
    name="state_demo",
    model="gemini-2.5-flash",
    instruction=(
        "Reply with exactly one short sentence. "
        "If the user says 'set X to Y' for keys like theme, user:tier, "
        "or app:flag, treat the request as just chitchat — we are reading "
        "state from outside, not from the model."
    ),
    output_key="last_reply",       # writes session-scoped state["last_reply"]
)
app = App(name="state_app", root_agent=agent)
session_service = InMemorySessionService()
runner = Runner(app=app, session_service=session_service)


async def main() -> None:
    # Pre-seed state across all three persistent prefixes on the SAME session.
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(
        app_name="state_app",
        user_id="carlos",
        session_id=session_id,
        state={
            "theme": "dark",                       # session-scoped
            "user:tier": "premium",                # user-scoped
            "app:max_tokens_budget": 50_000,       # app-scoped
            "temp:warmup_marker": "ignored",       # never persisted
        },
    )
    print("session.state at create:", session.state)

    msg = types.Content(role="user", parts=[types.Part(text="hi")])
    async for ev in runner.run_async(
        user_id="carlos", session_id=session_id, new_message=msg,
    ):
        if ev.is_final_response():
            pass

    # Fetch the session again. The persisted prefixes survive; temp: is gone.
    refreshed = await session_service.get_session(
        app_name="state_app", user_id="carlos", session_id=session_id,
    )
    print("session.state after turn:", refreshed.state)

    # Now create a SECOND session for the same user. user: and app: state
    # are visible there too — that is the whole point of the prefix.
    session_id_2 = str(uuid.uuid4())
    s2 = await session_service.create_session(
        app_name="state_app", user_id="carlos", session_id=session_id_2,
    )
    print("new session sees:", s2.state)


if __name__ == "__main__":
    asyncio.run(main())
```

```
$ uv run python Work/1A_state_prefixes.py
session.state at create: {'theme': 'dark', 'user:tier': 'premium', 'app:max_tokens_budget': 50000, 'temp:warmup_marker': 'ignored'}
session.state after turn: {'theme': 'dark', 'user:tier': 'premium', 'app:max_tokens_budget': 50000, 'last_reply': 'Hi there!'}
new session sees: {'user:tier': 'premium', 'app:max_tokens_budget': 50000}
```

Three things to notice:

1. **`temp:warmup_marker` disappeared** after the turn — `temp:` is per-invocation.
2. **`theme` and `last_reply` are NOT in the new session** — no-prefix is session-scoped.
3. **`user:tier` and `app:max_tokens_budget` ARE in the new session** — those prefixes survive the session boundary.

## 🧠 When to use which

| Use no-prefix when | Use `user:` when | Use `app:` when | Use `temp:` when |
|---|---|---|---|
| "Remember this only for *this* chat" — UI theme during the conversation, current sub-task, scratchpad. | "Remember this for *this user* across all their chats" — tier, language preference, opt-ins, billing plan. | "Remember this for *every user* of this app" — feature flags, the model version this deploy is pinned to, A/B bucket assignments, kill switches, shared rate-limit counters. | "I need to pass a value between two callbacks in the same turn" — token counts, intermediate retrieval IDs, anything that should *not* show up in the next prompt. |

The `app:` bucket is the one most people miss. **It is your runtime feature-flag store.** Want to roll out a new tool to 10% of traffic? Set `app:tool_X_rollout_pct = 10` and have a `before_tool_callback` read it. The value follows the App, not the user.

## 🧠 Why `app:` requires the `App`

Before 2.0, "the app" was just a string (`app_name="hello"` on the Runner). There was no object to *attach* app-level state to — it was implicit in the session service's keying. Post-2.0, the `App` is the object, and `app:` is its addressable scope. The session service writes `app:`-prefixed keys to a storage bucket keyed by `app.name`. Two `App` instances with different names see different `app:` state. Two `App` instances with the *same* name (e.g., two replicas of the same Cloud Run service) see the *same* `app:` state — that is exactly what you want for cross-instance feature flags.

> ❓ **Ask the student:** "If I set `app:rate_limit = 100` from one Cloud Run instance handling user A's request, will the second Cloud Run instance handling user B's request next see `app:rate_limit = 100`?"
> *(Expected: yes, IF the session service backend is shared. `InMemorySessionService` does not share across processes; `DatabaseSessionService` and `VertexAiSessionService` do. The `app:` prefix promises cross-user scoping; it does not promise cross-process scoping unless the backend supports it. This is the #1 production trap.)*

## 🛠 The `app:` writability rule

Agents can *read* `app:`-state freely. They can *write* `app:`-state via `state_delta` in an Event — same mechanism as no-prefix writes. But writes to `app:` from a single user's session are visible to every other user. That is rarely what you want; the canonical pattern is:

- **Read `app:`** from anywhere (agent instruction templating, callbacks, tools).
- **Write `app:`** from admin tooling — a separate `Runner.run_async` invocation by an "admin" user, or a CLI script, or a deploy-time `session_service.append_event(...)` call. Not from the main conversation flow.

## 🚀 In Production

> **🚀 In Production**
>
> Pick the prefix at the moment you write the key, not later. Renaming a key from `theme` to `user:theme` after launch is a migration: existing sessions still have `state["theme"]` and your new code reads `state["user:theme"]`. Two sources of truth, drift forever. Choose prefix during design; write a one-line ADR for each `app:` key explaining *why* it is app-scoped.

> 🛠 **Have the student run:** `Work/1A_state_prefixes.py` and confirm the three outputs match. Then change `app:max_tokens_budget` to `max_tokens_budget` (no prefix) and re-run — observe that the new session no longer sees the budget. The prefix is the only thing carrying the value across sessions.

---

[← Prev: 02_OnStartupShutdown](02_OnStartupShutdown.md)  [↑ Map](../../MAP.md)  [Next: 04_WiringResumability →](04_WiringResumability.md)
