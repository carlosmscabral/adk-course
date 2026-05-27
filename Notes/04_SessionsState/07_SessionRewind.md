---
module: 04_SessionsState
page: 07_SessionRewind
title: Session rewind — replay from a prior event with modified state
estimated_minutes: 20
prereqs: [04_SessionsState/06]
concepts: [Runner.rewind, branching, debugging, eval-replay]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/06_ContextCompaction](06_ContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/08_SessionMigrate →](08_SessionMigrate.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 07 Session Rewind

# 🛠 Session rewind (NEW in 2.0)

A 50-turn conversation went sideways at turn 32. Pre-2.0 your options were: start fresh, or accept the bad state. ADK 2.0 added `Runner.rewind(...)`: snip the event log at event N, optionally patch state, then continue from there. The earlier events stay on disk; what you get back is a session whose "live" view ends at event N.

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
    checkpoint = (await runner.session_service.get_session(
        app_name="rewind_demo", user_id="u1", session_id=sess.id,
    )).events[-1].id

    print("turn 3 (will be rewound):")
    await turn("badly worded prompt that derails things")

    print(f"rewinding to event {checkpoint!r}, patching counter=999…")
    await runner.rewind(
        session_id=sess.id, user_id="u1",
        to_event_id=checkpoint,
        state_overrides={"counter": 999},
    )

    print("turn 3' (replayed from checkpoint):")
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
rewinding to event 'evt_…', patching counter=999…
turn 3' (replayed from checkpoint):
  reply: The counter is currently 999.
```

The bad turn 3 is gone from the live view; counter is now 999; the agent's next turn behaves as if the bad branch never happened.

## 🧠 What rewind actually does

1. Marks events after `to_event_id` as **inactive** (still on disk, queryable for audit).
2. Recomputes state by replaying the active prefix.
3. Applies `state_overrides` on top of the replayed state.
4. Subsequent `run_async` builds the LLM context only from the active events.

The original events are NOT deleted — you can `session_service.list_events(include_inactive=True)` to inspect what was branched away. This makes rewind safe for production: it is non-destructive.

## 🧠 Three canonical use cases

* **Eval replay.** Re-run a known-good conversation up to event N, then test how a new agent version handles the next turn. Module 14 (`AgentEvaluator`) hooks into this.
* **Hot-fix a bad action.** Customer-facing agent emitted something offensive. Rewind to before the bad event, patch state to suppress that branch, resume.
* **A/B branching.** Fork a conversation at turn N, run path A on session A, path B on session B (`migrate` then `rewind`; see page 08).

## ⚠️ Gotchas

* Tool side effects already happened. Rewinding does not "un-send" the email or "un-charge" the card. Pair with **idempotency keys** on side-effecting tools.
* Compaction (page 06) interacts: if the compactor already summarized the rewound range, the summary still references events that are no longer active. Production setups usually disable compaction on sessions earmarked for rewind, or re-summarize after rewind.

## ❓ Quiz

> ❓ **Ask the student:** you rewind a session and patch `state["user:auth_token"] = "expired"`. The user's next turn invokes a tool that needs auth. What should happen?
> *(Expected: the tool should observe the expired token and either refuse or refresh. Rewind only controls what state the next LLM build sees — it does not invalidate live external resources. The tool's job is to validate auth every time.)*

> 🛠 **Have the student run:** the script above, then call `runner.session_service.list_events(session_id=sess.id, include_inactive=True)` to confirm the rewound event is still on disk, just not in the live view.

> **🚀 In Production**
>
> Rewind is a privileged operation — it changes what the agent appears to "remember." Gate it behind admin auth and always log the `(actor, to_event_id, reason)` triple. Treat rewind in production like `DROP DATABASE`: useful, dangerous, audit-required.

---

[← Prev: 04_SessionsState/06_ContextCompaction](06_ContextCompaction.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/08_SessionMigrate →](08_SessionMigrate.md)
