# 🤖 AGENTS.md — Module 23 Frontend Integration (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening 00_Overview. This module is the most "JS-flavored" in the course — the student will spend more time in HTML/JS than in Python.

## What the student should walk away knowing

- `user_id` is server-derived from verified auth, never client-invented.
- `session_id` ownership is a per-app policy decision (pattern A = frontend mints, B = backend mints). Pick one and document it.
- The browser's `EventSource` has a one-line API for SSE *but* cannot set headers — use a fetch polyfill for `Authorization`.
- WebSocket is required for Live (bidi audio); SSE suffices for text response streaming.
- Tool calls and tool responses are discrete events in the stream; render them as visual affordances (chips), not as text.
- Auth claims reach tools via session state (`user:` prefix), not via HTTP headers.
- `adk web` is a dev tool; production needs a custom SPA against `get_fast_api_app(web=False)` with auth + CORS + rate limits.

## Pacing

- **Easy if**: student has shipped any web frontend before. The patterns will feel familiar — they're just normal web app patterns with ADK events on the wire.
- **Hard if**: student is back-end-only and has never written an SPA. Bias time to pages 05 and 11 (the dissection) and skip 06/07 lightly.
- **Hard if**: student is fuzzy on async generators / SSE wire format — backfill with [[PY_generators]] or detour to 18/03 first.
- Expected total time for an on-pace student: ~4 hours (sum of page estimates).

## Watch for these mistakes

- **Trusting client-supplied `user_id`.** This is the IDOR. Push back hard — the rule is non-negotiable.
- **Hard-coded `user_id` in their sample SPA.** Fine for a drill, NEVER ship. If they say "I'll wire auth later" — verify they actually do.
- **Double-rendering text** by appending to both partial events and the final consolidated event. The student's chat bubble will show "hellohello world world".
- **Calling `EventSource` and trying to attach Bearer token.** Will look like it should work; doesn't. Reach for the polyfill workaround immediately.
- **Skipping `\n\n` delimiter handling** in a custom SSE parser. They'll see "no events received" until the connection closes.
- **Deploying `adk api_server` directly to prod.** Major: it has no auth, no rate limit. Push them to `get_fast_api_app(web=False)` immediately.
- **Cloud Run 60-minute timeout surprise.** A long-running deep-search-style agent will silently drop. Mention this when they ship.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "WebSockets are confusing" | [[WebSockets]] — protocol primitives in 25 min |
| "How do I run the SPA *with* the API?" | [[FastAPI_for_ADK]] — wrapping pattern |
| "Where should the static SPA live?" | [[Cloud_Run]] — serving Vite build alongside ADK |
| "Can I just use adk web?" | [[a2UI]] — yes for dev, no for prod |
| "How do callbacks fit in here?" | back to module 07; we don't re-teach |

If the same detour is declined twice, stop offering.

## Mini-drill grading

- **Clean pass** = `Work/23_frontend/todo_backend.py` runs, `Work/frontend/todo_spa.html` renders streaming tokens, three messages round-trip cleanly, partials don't double, input disables/re-enables.
- **Pass with hint** = student missed the partial-vs-final pattern; tutor pointed it out; student fixed and re-ran.
- **Fail** = backend uses `adk api_server` raw (no auth, no CORS), or frontend trusts a client-supplied user_id without comment.

### Edge case to probe (after the basic drill passes)

- Kill the backend mid-stream. What does the SPA show? (Should: surface a clean error, allow retry; should NOT: silently spin forever.) If they hadn't thought about it, point at page 03's reconnect storm callout.

## Cross-module hooks

- **Prereqs**: module 21 (the HTTP surface this consumes), 18 (the SSE/streaming pattern on the server), 04 (sessions/state).
- **Consumed by**: module 24 (channel integrations) — the "frontend" there is Slack/Discord, but the user→session mapping rules from 23/01 still apply.
- **Cross-links to**: 16 (security), 22 (deployment), 4B (HITL approval — frontend half lives here).
- If the student forgets a prerequisite (e.g., what `/run_sse` returns), back up to 21 briefly — don't re-teach inline.

## Sample anchor notes

- `deep-search` is the canonical sample. Real Vite/React, real SSE parser, real activity timeline.
- `realtime-conversational-agent` is the canonical WebSocket sample (bidi audio). Reference for page 04, dissect more deeply in module 18.
- `ambient-expense-agent` has a frontend that queries `GET /apps/.../sessions` for pending approvals — relevant for page 10 / 4B cross-link.
