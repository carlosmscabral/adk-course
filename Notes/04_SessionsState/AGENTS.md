# AGENTS.md — Module 04 Sessions & State (teaching notes for the AI tutor)

## What the student should walk away knowing

- **Session** = conversation container (id, app_name, user_id, events, state).
- **State** = a dict on the Session; mutated via `state_delta`s attached to events, never directly from outside.
- **Four prefixes**: (none) → session; `user:` → cross-session per user; `app:` → all users; `temp:` → one invocation.
- **Templating** in `instruction=`: `{var}` requires the key, `{var?}` makes it optional.
- **Writing state from tools** via `tool_context.state["key"] = value`. The write becomes a delta on the tool-result event.
- **`output_key=`** on `LlmAgent` writes the agent's final reply text into `state[key]` automatically.
- **Persistence**: swap `InMemorySessionService` for `DatabaseSessionService(db_url=...)` with a SQLite or Postgres URL. `VertexAiSessionService` for Agent Engine.
- **`llm-auditor`** chains sub-agents via `SequentialAgent`; data flows implicitly through shared conversation history. `output_key` makes it explicit when needed.

## 2.0-specific concepts (4 pages added in the expansion)

- **Page 05 — Context caching** (`ContextCacheConfig`): cache the stable prefix (instruction + tool schemas + early turns) for cheap prefix reuse. `min_tokens`, `ttl_seconds`, `cache_intervals`. Templated `{user:*}` in the instruction *breaks cross-turn reuse for that user* and *destroys cross-user reuse entirely*.
- **Page 06 — Context compaction** (`ContextCompactionConfig` + `LlmEventSummarizer`): summarize old turns into one synthetic event when `compaction_interval` is hit; keep the last `keep_recent_events` verbatim. The summarizer prompt is production-critical text — instruct it to preserve dates, names, IDs, decisions verbatim. Costs another LLM call per compaction.
- **Page 07 — Session rewind** (`Runner.rewind(...)`): non-destructive branch at a prior event with optional `state_overrides`. Events after the cut are marked inactive (still on disk). Does NOT undo side effects (use idempotency keys). Interacts with compaction — re-summarize after rewind.
- **Page 08 — Session migrate** (`adk migrate session` CLI + `migrate_sessions(...)`): moves sessions across backends and schema versions. `--dry-run` first. Artifact bytes do NOT move (migrate artifact backend separately). `temp:` state is dropped. `v1 → v0` downgrades are rejected.

## Pacing

- **Easy if** the student is comfortable with the state-as-dict model and `tool_context` (from Module 03 page 04).
- **Hard if** the student confuses the four prefixes. Don't move past page 02 until they can place each correctly in the quiz scenarios.
- **Hard if** they treat state as a transactional database. State is eventually-consistent across deltas; reads are "as-of-last-applied-delta."

## Watch for these mistakes

- Forgetting `user:` prefix on cross-session data (#1 bug in real code).
- Forgetting `temp:` on scratch data → state grows monotonically.
- Mutating containers in place (`state["cart"].append(x)`) — works but delta tracking can miss it. Reassign the whole value.
- Using `{var}` required form for genuinely optional context → first turn errors.
- Storing secrets in state.
- Picking `InMemorySessionService` for production.

## When to suggest a detour

- "What's Pydantic?" → [[PY_pydantic]] (only if poking at `output_schema=`, which is Module 17).
- "What's eventual consistency?" → 60-second explainer; no full detour needed. Point at Module 06 (ParallelAgent) for the case that matters.
- "How do I migrate sessions between backends?" → defer to Module 16.

## Mini-drill grading

- **Pass = Turn 2 reply correctly names the user**, AND the bonus re-run with fresh session_id still remembers (proves `user:` prefix worked).
- If Turn 2 works but bonus fails → bare `name` key (no prefix). Push refactor.
- If Turn 1 errors before LLM → missing `?` in `{user:name?}`. Push refactor.

## After this module

- The student has Agent, Runner, Session, Tools, State. **That's the entire Foundation Track surface.**
- Next is **Milestone M1** at `Drills/M1_ConversationServer.md` — a CLI loop with two tools and persistent state. M1 is the integration test for everything you taught so far.
- Module 05 (Multi-Agent) is the next big concept. The recurring `research-assistant` mini-app makes its first multi-agent appearance there.
