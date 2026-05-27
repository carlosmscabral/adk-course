# 🤖 AGENTS.md — Module 21 ADK API Surface (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this after the global [AGENTS.md](../../AGENTS.md) and before opening the first concept page. Module 21 is the **bridge** between writing agents and shipping them. Frame it that way explicitly when introducing it.

## What the student should walk away knowing

- Every entry point `adk` ships and what each one is for.
- The real call graph behind `adk run` and `adk web` (`AgentLoader → _to_app → _setup_runner_context → Runner`).
- How to hit `/run`, `/run_sse`, `/run_live` by hand with `curl` and a tiny client.
- The Event JSON shape (content, parts, actions) and why `actions` matters.
- How to wrap ADK in their own FastAPI app for custom routes / middleware / auth.
- The session and event REST resources and why `user_id` authorization is critical.
- The 10-item production checklist on page 10.

## Pacing

- **Easy if:** the student has shipped a FastAPI service before. Cruise pages 02-07; spend most of the time on 01A-01C (the under-the-hood pages — likely new to them) and 08 (auth — easy to get wrong).
- **Hard if:** the student has only ever run `adk run` and has no HTTP server experience. Drill the [[FastAPI_for_ADK]] detour before page 06. Page 05 (WebSockets) may benefit from [[WebSockets]] detour too.
- Expected total time for an on-pace student: ~6 hours (sum of `estimated_minutes`).

## Watch for these mistakes

- **`app_name` confusion.** They use the agent's `name=` kwarg in the URL. Symptom: 404 on `/run`. Fix: use the **package directory name**.
- **`adk web` and code edits.** They edit `agent.py`, refresh the browser, see no change. Symptom: "ADK doesn't reload." Fix: it doesn't auto-reload by design — restart `adk web`.
- **SSE looks like JSON.** They try `httpx.post(...).json()` on `/run_sse`. Symptom: JSON decode error. Fix: use `httpx.stream(...)` and iterate `iter_lines`.
- **`user_id` from token vs URL.** They authenticate but don't authorize — anyone with a valid token reads anyone's sessions. Symptom: works perfectly in dev, broken access control in prod. Push them hard on this; it is the single most common ADK API security bug.
- **CORS twice.** They add CORS middleware on top of `get_fast_api_app(allow_origins=...)`. Symptom: duplicate `Access-Control-Allow-Origin` headers. Fix: pick one place.

## When to suggest a detour

| Student says / shows                                  | Suggest                                            |
|-------------------------------------------------------|----------------------------------------------------|
| "What does `@click.option` even do?"                  | Built-in Python ecosystem — point at click docs.   |
| "FastAPI middleware? lifespan?"                       | [[FastAPI_for_ADK]] — 30 min on the primitives ADK uses. |
| "Why a WebSocket and not just an HTTP stream?"        | [[WebSockets]] — protocol primitives + LB caveats. |
| "What's in an audio frame?"                           | [[AudioEncoding]] — only if they're touching `/run_live` for voice. |
| "What does the Gemini Content/Part JSON look like?"   | [[GeminiPayload]] — schema reference.              |
| "I want to deploy this."                              | Don't detour — that's all of module **22**, next.  |

If the same detour is suggested and declined twice, stop offering it.

## Mini-drill grading

- **Clean pass** = SSE stream visible via curl AND httpx; partial vs final distinguished; one hardening item (keepalive OR user_id authz) works.
- **Pass with hint** = student needed help with `httpx.stream` vs `httpx.post`, OR forgot `streaming: true` and we prompted them.
- **Fail** = they tried to use `/run` and call it "streaming" because chunks come out fast. Have them re-read page 04, specifically the partial/final split.

### Edge case to probe (after the basic drill passes)

- Open two SSE streams to the same `session_id` from two clients simultaneously. What happens? *(ADK serializes per session — the second waits for the first to finish. Discuss whether this is acceptable for the student's app; for chat UIs it usually is, for bulk-processing pipelines it usually isn't.)*

## Cross-module hooks

- **This module is referenced from**: 22 Deployment Models (every deployment serves *this* API surface), 23 Frontend Integration (the SPA consumes *this* API), 24 Channel Integrations (the webhook adapter wraps *this* API).
- **This module references**: 04 SessionsState (the `user_id`/`session_id` triple), 15 Observability (trace the API), 16 Production & Security (PII redaction, secrets), 18 Streaming/Live (the protocol underneath `/run_live`).
- If the student forgets the `state_delta` / `transfer_to_agent` semantics, back up to **04 page 06** briefly — don't re-teach inline.
