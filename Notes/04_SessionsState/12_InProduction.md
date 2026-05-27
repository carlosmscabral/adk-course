---
module: 04_SessionsState
page: 12_InProduction
title: Sessions & State — production checklist
estimated_minutes: 15
prereqs: [04_SessionsState/11]
concepts: [secrets, prefix-bugs, state-size, eventual-consistency, caching, compaction, rewind, migrate]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/13_KnowledgeCheck →](13_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 12 In Production

# 🚀 Sessions & State — production checklist

The mistakes that cause the most production pages, plus the 2.0-specific concerns.

## 🚀 1. Never store secrets in state

State writes become events. Events are logged. Logs end up in dashboards. **API keys, passwords, PII, payment info, OAuth tokens — none belong in state.** If you need to pass a credential to a tool, fetch it inside the tool from your secret manager; don't pre-load it into state.

## 🚀 2. The state-prefix mistake is the #1 bug

By a wide margin, the most common state bug is **missing the `user:` prefix** when you mean to remember something across sessions, or **forgetting `temp:`** for scratch values that pollute the session.

Mitigations:
* Code review checklist: "is every state write the right scope?"
* A `before_tool_callback` (Module 07) can validate keys against an allowlist.
* Run a state audit periodically: log all keys present after a long-running user's 100th session — anything weird? Refactor.

## 🚀 3. State is not a database

The state dict is meant for ~kilobytes per session. If you're tempted to store conversation transcripts, full search-result pages, or generated images **in state**, stop and use:
* **Artifacts** (Module 04A) for large or binary blobs.
* **Memory** (Module 11) for semantically-queryable history.
* **External DB** for structured data you'll query independently.

Symptoms of state misuse: slow Runner cold-starts (loading huge sessions), OOMs in the Postgres pod, "the agent feels sluggish."

## 🚀 4. State is eventually consistent across deltas

If a tool writes `state["x"]`, then the same tool reads `state["x"]` later in the same call expecting the new value — that works (local Python). But if a *different* tool runs in parallel on the same session (Module 06's `ParallelAgent`), the read may see the pre-write value. **Don't expect linearizability across parallel sub-agents.**

## 🚀 5. Context caching — track hit rate, not just bills

`ContextCacheConfig` (page 05) silently no-ops if the prefix is shorter than `min_tokens` or if the provider rotates cache infra. Both regressions look like "the app got more expensive."

Mitigations:
* Log `event.usage_metadata.cached_content_token_count` per turn and dashboard the hit rate.
* Page on **0% hit rate for 1 hour** as a regression signal.
* Keep `{user:*}` and `{session:*}` templating **out of the system instruction** — templated personalization defeats cross-turn caching for that user.

## 🚀 6. Context compaction — guard the summarizer prompt

`ContextCompactionConfig` runs an LLM call to summarize old turns (page 06). Two failure modes:
* **Summarizer drops facts.** The user's stated deadline / name / decision is gone from the live context. Mitigation: write a summarizer prompt that explicitly says "preserve names, dates, IDs, file paths, user decisions verbatim."
* **Summarizer is slow.** Compaction happens on the request path; a 4-second summarizer means a 4-second user-visible pause. Use a fast model (`gemini-2.5-flash`) for the summarizer regardless of what the main agent uses.

Set `compaction_interval` ≥ 20 and `keep_recent_events` ≥ 10 as a starting floor.

## 🚀 7. Session rewind — log every rewind

`Runner.rewind(...)` (page 07) is privileged: it changes what the agent appears to remember. Treat it like `DROP DATABASE`.

* Gate behind admin auth.
* Log `(actor, session_id, to_event_id, reason)` to your audit pipeline.
* Pair side-effecting tools with **idempotency keys** — rewind does not un-charge the card.
* If you also run compaction, beware the interaction: compaction summaries reference events that may no longer be active after rewind. Re-summarize, or disable compaction on sessions earmarked for replay.

## 🚀 8. Session migrate — always `--dry-run`, always plan rollback

`adk migrate session` (page 08) moves sessions across backends. Two production rules:
* `--dry-run` first to validate the plan. Read the report before committing.
* **Dual-write during transition**: write to both source and destination for at least 24 hours; cut reads over only when destination is verified.
* Artifact references migrate; artifact **bytes** do not — migrate `GcsArtifactService` (or whatever you use) before sessions, or links break.
* `temp:` state is dropped (by definition); plan around it.
* You cannot downgrade schema (`v1 → v0` is rejected). Keep older fleets on the older schema until cutover.

## 🚀 9. Migrating session backends loses in-memory data

Going from `InMemorySessionService` to `DatabaseSessionService` at launch: no data to lose (in-memory was always going to die). Going between persistent backends mid-flight: use `adk migrate session` (rule 8). **Pick your production backend early. Don't run dev with one and prod with another without exercising the migration path.**

## ❓ Pop check

> ❓ **Ask the student:** which rule would have caught the bug *"after rolling out a new agent version, every user reports their preferences were reset"*?
> *(Expected: rules 8 + 9 — somebody changed session backends (or rotated the DB) and didn't migrate `user:`-prefixed state. The conversations themselves come back; the `user:` state vanished.)*

> ❓ **Ask the student:** which rule would have caught the bug *"agent cost-per-request quietly doubled over two weeks"*?
> *(Expected: rule 5. The cache silently stopped hitting. Could be a templated `{user:*}` getting into the system prompt; could be a provider-side TTL change; could be a `min_tokens` threshold issue. Without a dashboard on `cached_content_token_count`, you don't notice until the bill arrives.)*

> 🤖 **Tutor:** before the student starts the mini-drill, walk them through rule 2 specifically. The drill *requires* `user:` prefix; if they skip it, the test passes turn 1 but fails the bonus (where "remembering" means surviving a fresh session_id with same user_id).

---

[← Prev: 04_SessionsState/11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/13_KnowledgeCheck →](13_KnowledgeCheck.yml)
