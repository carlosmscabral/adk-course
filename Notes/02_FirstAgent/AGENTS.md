# AGENTS.md — Module 02 First Agent (teaching notes for the AI tutor)

## What the student should walk away knowing

- `LlmAgent(...)` is a **config object**. No I/O happens until a Runner calls it.
- `InMemorySessionService.create_session(app_name=, user_id=, session_id=)` returns a `Session` after `await`.
- `Runner(app_name=, agent=, session_service=)` ties them together. `app_name` must match.
- `runner.run_async(...)` is an **async generator** of `Event`. You drive it with `async for`.
- Messages are `types.Content(role="user", parts=[types.Part(text=...)])`. Replies come back the same way.
- Read text with `event.is_final_response() and event.content and event.content.parts and event.content.parts[0].text`.
- The pattern scales: every sample in `adk-samples/` exposes a `root_agent` you can plug into this same skeleton.

## Pacing

- **Easy if** the student is comfortable with `async`/`await` and has done one or two `asyncio.run()` scripts before. Should land the mini-drill in 30 minutes.
- **Hard if** they're new to `async`. Pause before page 03 and walk through [[PY_async]] — show them what `async def`, `await`, and `async for` mean separately.
- **Hard if** they're trying to memorize the API. The point is to *recognize* the seams, not memorize them. Refer them to `Reference/CheatSheets/` if/when those exist.

## Watch for these mistakes

- Calling `session_service.create_session(...)` without `await`. Gets a coroutine object instead of a session.
- Hard-coding `session_id="hello"`. Works once, then collides on rerun (`AlreadyExistsError`). Use `uuid.uuid4()`.
- Iterating `for event in runner.run_async(...)` instead of `async for`. Hard-to-diagnose error.
- Reading `event.content.parts[0].text` unconditionally → `AttributeError: 'NoneType' object has no attribute 'parts'` on a bookkeeping event.
- Calling `runner = Runner(...)` inside the request loop instead of once. Slow.

## When to suggest a detour

- "What's `async` again?" → [[PY_async]] now.
- "What's a generator?" → [[PY_generators]] (the *sync* version; async generators are a small twist on top).
- "What are all the `types.Part` variants?" → [[GeminiPayload]] (optional unless they're going multimodal).
- "What's Pydantic?" → [[PY_pydantic]] (only if they're poking at `LlmAgent`'s validation).

## Mini-drill grading

- **Pass = the script reads stdin, prints reply, exits cleanly.** Pretty-printing, color, etc. are NOT required.
- Common mistakes are listed in the YAML `tutor_notes`. Probe for each before showing the solution.
- After pass, probe: "what would you change to make this a multi-turn REPL?" (Answer: a `while True:` loop with `input()`, reusing the same `session_id` — that's M1.)

## After this module

- The student now has the **plumbing reflex**. Module 03 adds tools — meaning the agent loop now has a real branch (LLM picks tool vs. reply). The same Runner + Session pattern carries over unchanged.
- If the student wants to make their `hello_agent.py` persistent, point them at `DatabaseSessionService(db_url="sqlite:///sessions.db")` (one-line change). It's a great way to make Module 04 land before they get there.
