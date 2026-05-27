---
module: 04_SessionsState
page: 07_SessionRewind
title: Session rewind — reverse to before a prior invocation
estimated_minutes: 20
prereqs: [04_SessionsState/06]
concepts: [Runner.rewind_async, branching, debugging, eval-replay]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/06_ContextCompaction](06_ContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/08_SessionMigrate →](08_SessionMigrate.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 07 Session Rewind

# 🛠 Session rewind (NEW in 2.0)

A 50-turn conversation went sideways at turn 32. Pre-2.0 your options were: start fresh, or accept the bad state. ADK 2.0 added `Runner.rewind_async(...)`: name an invocation to rewind to, the runner appends a special rewind event that reverses the state and artifact deltas, and the next turn behaves as if the bad branch never happened. The earlier events stay on `session.events`; the rewind event signals the boundary.

## 🧠 The shape

```python
# Work/07_rewind.py — run with: uv run python Work/07_rewind.py
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio


agent = LlmAgent(
    name="counter",
    model="gemini-2.5-flash",
    instruction="Reply with the current counter value: {counter?}",
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="rewind_demo")
    sess = await runner.session_service.create_session(
        app_name="rewind_demo", user_id="u1", state={"counter": 0},
    )

    async def turn(text: str):
        async for ev in runner.run_async(
            user_id="u1", session_id=sess.id,
            new_message=types.Content(role="user", parts=[types.Part(text=text)]),
        ):
            if ev.is_final_response():
                print(f"  reply: {ev.content.parts[0].text[:80]}")

    print("turn 1:")
    await turn("hi")
    print("turn 2:")
    await turn("again?")

    print("turn 3 (will be rewound):")
    await turn("badly worded prompt that derails things")
    # Grab the invocation_id of that last (bad) turn — rewind targets an
    # invocation, not a single event.
    bad_invocation_id = (await runner.session_service.get_session(
        app_name="rewind_demo", user_id="u1", session_id=sess.id,
    )).events[-1].invocation_id

    print(f"rewinding to before invocation {bad_invocation_id!r}…")
    await runner.rewind_async(
        user_id="u1",
        session_id=sess.id,
        rewind_before_invocation_id=bad_invocation_id,
    )

    print("turn 3' (replayed from the rewind boundary):")
    await turn("now ask cleanly please")


asyncio.run(main())
```

```
$ uv run python Work/07_rewind.py
turn 1:
  reply: The counter is currently 0.
turn 2:
  reply: Counter is still 0.
turn 3 (will be rewound):
  reply: I'm not sure what you'd like me to do.
rewinding to before invocation 'inv_…'…
turn 3' (replayed from the rewind boundary):
  reply: The counter is currently 0.
```

The bad turn 3's state and artifact effects are reversed by the appended rewind event; the agent's next turn behaves as if the bad branch never happened.

## 🧠 What rewind actually does

Reading `runners.py` (`rewind_async`):

1. Walks `session.events` to find the first event whose `invocation_id == rewind_before_invocation_id`.
2. **Computes a state delta** that reverses every session-scoped state mutation made by events at or after that index. (Keys prefixed `app:` or `user:` are deliberately left alone — those are not session-scoped.)
3. Computes an **artifact delta** that restores each artifact to the version it had at the rewind point (or marks it inaccessible if it didn't exist yet).
4. Appends a single synthetic `rewind_event` whose `actions.rewind_before_invocation_id` carries the boundary, plus the computed `state_delta` and `artifact_delta`. Subsequent `run_async` builds context against the resulting state.

The original events are NOT deleted — they remain in `session.events`. You can scan them yourself and look for any event whose `actions.rewind_before_invocation_id` is set to find boundaries. This makes rewind safe for production: it is non-destructive and the audit trail is intact.

Note: `rewind_async` itself does not accept `state_overrides`. If you want to patch state in addition to the reversal, append a second event with your own `actions.state_delta` after the rewind call.

## 🧠 Three canonical use cases

* **Eval replay.** Re-run a known-good conversation up to event N, then test how a new agent version handles the next turn. Module 14 (`AgentEvaluator`) hooks into this.
* **Hot-fix a bad action.** Customer-facing agent emitted something offensive. Rewind to before the bad event, patch state to suppress that branch, resume.
* **A/B branching.** Fork a conversation by creating a new session, replaying events from the original up to invocation N via the public session API, then rewinding the original to that same boundary. Run path A on session A, path B on session B.

## ⚠️ Gotchas

* Tool side effects already happened. Rewinding does not "un-send" the email or "un-charge" the card. Pair with **idempotency keys** on side-effecting tools.
* Compaction (page 06) interacts: if the compactor already summarized the rewound range, the summary still references events that are no longer active. Production setups usually disable compaction on sessions earmarked for rewind, or re-summarize after rewind.

## ❓ Quiz

> ❓ **Ask the student:** you rewind a session over an invocation whose tool sent an email. Will the recipient un-receive it?
> *(Expected: no. Rewind only reverses session state and artifact deltas inside ADK; it cannot undo real-world side effects. Pair side-effecting tools with idempotency keys, and design the rewind UX assuming the side effect already happened.)*

> ❓ **Ask the student bonus:** the bad invocation wrote `state["user:flag"] = True`. After rewind, what is the value of `state["user:flag"]`?
> *(Expected: still `True`. The rewind state delta deliberately skips keys prefixed `app:` or `user:` — those scopes outlive the session. Only session-scoped keys are reversed.)*

> 🛠 **Have the student run:** the script above, then reload the session and walk `session.events` printing `(ev.invocation_id, ev.actions.rewind_before_invocation_id, bool(ev.actions.state_delta))`. Confirm the bad invocation's events are still present, and that a synthetic rewind event with `rewind_before_invocation_id` set sits at the tail.

> **🚀 In Production**
>
> Rewind is a privileged operation — it changes what the agent appears to "remember." Gate it behind admin auth and always log the `(actor, rewind_before_invocation_id, reason)` triple. Treat rewind in production like `DROP DATABASE`: useful, dangerous, audit-required.

---

[← Prev: 04_SessionsState/06_ContextCompaction](06_ContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/08_SessionMigrate →](08_SessionMigrate.md)
