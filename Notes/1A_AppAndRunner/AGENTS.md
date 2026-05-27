# 🤖 AGENTS.md — Module 1A App & Runner Architecture (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening `00_Overview.md`. This module is the *contract* that lets the later runtime modules be taught coherently — landing 1A means Modules 04 (cache, compaction), 4B (resumability), and 11 (memory) all have a place to bolt onto. If 1A doesn't land, those later modules feel like loose features instead of expressions of a single architecture.

## What the student should walk away knowing

- `App` (the 2.0 container) is **config truth**; `Runner` is **runtime executor**; `LlmAgent` is **per-turn brain**. They are a stack, not peers.
- The modern construction is `Runner(app=App(...), session_service=...)`; the legacy `Runner(app_name=..., agent=...)` still works but every new feature lands on App.
- App owns five cross-cutting fields: `name`, `root_agent`, `plugins`, `events_compaction_config`, `context_cache_config`, `resumability_config`.
- `on_startup` / `on_shutdown` are **not on the App** — they belong to whatever runtime hosts the App (FastAPI lifespan, `adk api_server`, your own asyncio main). The App is config; lifecycle is the host's job.
- The `app:` state prefix is the cross-user feature-flag bucket. It only makes sense because the App is what names "this app."
- Cache, compaction, and resumability are all opt-in App fields; their *wiring* lives in 1A, their *deep mechanism* lives in 04 (cache/compaction) and 4B (resumability).

## Pacing

- **Easy if**: student is comfortable with Pydantic models and FastAPI lifespan. Cruise; compress the wiring pages (04, 05, 06) into one read.
- **Hard if**: student is fuzzy on Pydantic. Drill detour [[PY_pydantic]] before page 01 — the App is a `BaseModel` with `extra="forbid"` and a `model_validator`, and pages 04–06 each show a sub-config that is also a Pydantic model. Without the Pydantic mental model, the wiring pages will feel arbitrary.
- **Hard if**: student is fuzzy on async context managers. Drill detour [[PY_async]] § "async context managers" before page 02 — the FastAPI lifespan example uses `@asynccontextmanager`.
- Expected total time for an on-pace student: ~2.5 hours (sum of page `estimated_minutes`).

## Watch for these mistakes

- Importing `App` from `google.adk` instead of `google.adk.apps`. The correct path is `from google.adk.apps import App`.
- Importing `ResumabilityConfig` / `EventsCompactionConfig` from `google.adk.apps` directly. They live in `google.adk.apps._configs` (note the underscore — that's a divergence to call out; the import path may stabilize in a future release).
- Building a fresh `App(...)` per request. The App holds plugin instances and shared state — must be module-scope.
- Setting `state["app:foo"]` from inside a user's session. Writes to `app:` from a user session **leak to every other user**. The pattern is read from agents, write from admin tooling.
- Turning on `ResumabilityConfig(is_resumable=True)` while still on `InMemorySessionService`. Looks like it works in dev, silently breaks across process restarts in prod.
- Stuffing every heavy init into `on_startup`. Cold start balloons; serverless platforms time out the readiness probe.
- Passing both `app=` and `plugins=` to Runner. The framework raises `ValueError` — plugins must go on the App when `app=` is used.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "Why does App validate at construction?" | [[PY_pydantic]] — covers `BaseModel`, `model_validator`, `ConfigDict(extra="forbid")` in 20 min |
| "What's `@asynccontextmanager` doing in the FastAPI example?" | [[PY_async]] § async context managers — 10 min |
| "How does Cloud Run know when shutdown happened?" | [[Cloud_Run]] — SIGTERM handling, drain timeout, lifecycle integration |
| "I want to wrap the App in a real web server, not just a script" | [[FastAPI_for_ADK]] — full lifespan + route patterns |

If the same detour is declined twice (check `student_profile.md`), stop offering it.

## Mini-drill grading

- **Clean pass** = student wrote `App(name="hello_app", root_agent=agent)` explicitly, used `Runner(app=app, ...)`, pre-seeded state with both prefixes, fetched session afterward and printed state, wrapped runtime in try/finally with plugin_manager.close(). Script runs cleanly and prints both reply and state.
- **Pass with hint** = student tried legacy `Runner(app_name=..., agent=...)` form first; tutor pointed out that the brief said "modern form"; student switched. Common path.
- **Fail** = student didn't construct `App` at all (just used Module 02 code as-is) OR forgot the state prefixes entirely. Re-drill: walk them back through page 01 (App is the wrapper) and page 03 (state prefixes change where state lives).

### Edge case to probe (after the basic drill passes)

Ask: "What single change to your script makes the agent capable of surviving a process restart mid-turn?" Expected answer combines two: (a) `resumability_config=ResumabilityConfig(is_resumable=True)` on the App, AND (b) replace `InMemorySessionService` with `DatabaseSessionService(db_url="sqlite:///sessions.db")`. If they name only one, ask "and?" — the pair is the load-bearing insight.

## Cross-module hooks

- This module is referenced from:
  - [04 Sessions & State](../04_SessionsState/) — for `app:`-state and the cache/compaction deep-dives
  - [4B Human-in-the-Loop](../4B_HumanInTheLoop/) — for resumability mechanism
  - [11 Memory](../11_Memory/) — `MemoryService` is keyed by `app.name`
  - [13 Plugins](../13_Plugins/) — plugins are passed to `App(plugins=[...])`
  - [16 Production & Security](../16_ProductionSecurity/) — pulls in the In Production callouts
  - [21 ADK API Surface](../21_AdkApiSurface/) — `adk api_server` is what auto-wires lifespan
  - [22 Deployment Models](../22_DeploymentModels/) — cold-start tradeoffs are Cloud Run / Agent Engine specific
- This module references:
  - [01 Foundations](../01_Foundations/) — for the Runner/Session/Event vocabulary
  - [02 First Agent](../02_FirstAgent/) — for the by-hand Runner+Session pattern this builds on

If the student forgets a prerequisite concept, the tutor should NOT re-teach it inline — back up to the prereq page briefly, then return.

## Divergences from the source

- The authoring brief asked for `on_startup` / `on_shutdown` as App fields. The real `App` class (verified at `/home/carloscabral/study/adk-python/src/google/adk/apps/app.py` on 2026-05-27) does NOT expose those kwargs directly — lifecycle is host-managed (FastAPI `lifespan`, `adk api_server`, etc.). Page 02 teaches the wrapping pattern instead of pretending kwargs exist. If a future release adds them, patch page 02 first.
- `EventsCompactionConfig` and `ResumabilityConfig` are imported from `google.adk.apps._configs` (underscore module) as of the 2.0 GA snapshot. The pages use that path. If they get re-exported from `google.adk.apps` directly in a later release, update imports.
- The brief named the page `06_WiringContextCompaction` and said `context_compaction_config`. The actual field on `App` is `events_compaction_config` (with the `EventsCompactionConfig` class). The page title keeps "Context Compaction" for student-facing clarity but the code uses the correct `events_compaction_config` field name.
