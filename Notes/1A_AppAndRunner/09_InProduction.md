---
module: 1A_AppAndRunner
page: 09_InProduction
title: In Production — App & Runner hardening checklist
estimated_minutes: 15
prereqs: [1A_AppAndRunner/08]
concepts: [cold-start, app-scope, lifecycle, deprecation]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 08_DissectingSample](08_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_KnowledgeCheck →](10_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 09 In Production

# 🚀 In Production — App & Runner Architecture

> 🤖 **Tutor:** this page **consolidates** the inline `> 🚀 In Production` callouts from pages 01–07 into a single checklist. Walk it against the student's mini-drill solution (page 11) or against the `memory-bank` sample from page 08.

The course teaches production-readiness inline (rule #14 in the [authoring brief](../../_AUTHORING_AGENT_BRIEF.md)), not in a single deferred module. This page is the checklist the student walks before shipping anything built on `App` + `Runner`.

---

## Checklist

> ❓ **Ask the student:** "Open your most recent `Work/1A_*.py`. We are going to walk this checklist against it."

### 1. App constructed once at module scope

- **Risk**: Building a fresh `App(...)` per request defeats every cross-cutting feature it owns (plugins, cache, compaction, resumability). Plugin instances would be rebuilt, MCP subprocesses re-spawned, cache state lost.
- **Mitigation**: Module-scope construction, or `functools.lru_cache` factory. One App per process.
- **Inline source**: [01 App vs Runner vs Agent § 🚀 In Production](01_AppVsRunnerVsAgent.md#-in-production)

### 2. Lifecycle hooks always include shutdown

- **Risk**: Forgetting `await runner.plugin_manager.close()` on SIGTERM leaks MCP subprocesses, file descriptors, and gRPC channels across redeploys.
- **Mitigation**: Use FastAPI `lifespan` (or `adk api_server`'s built-in) so the framework guarantees shutdown runs. Treat shutdown as load-bearing even with an empty plugin list — future-you will add plugins.
- **Inline source**: [02 On Startup / Shutdown § 🚀 In Production](02_OnStartupShutdown.md#-in-production)

### 3. State prefix chosen at design time, not after launch

- **Risk**: Renaming `theme` → `user:theme` after launch is a migration: existing sessions still have `state["theme"]`, new code reads `state["user:theme"]`, two sources of truth drift forever.
- **Mitigation**: For every state key, write a one-line ADR naming the prefix and *why*. For `app:` keys especially — they are cross-user feature flags, never default to `app:`.
- **Inline source**: [03 App State Boundary § 🚀 In Production](03_AppStateBoundary.md#-in-production)

### 4. Resumability requires persistent session service AND idempotent tools

- **Risk**: `ResumabilityConfig(is_resumable=True)` with `InMemorySessionService` looks like it works in tests, then loses every paused state on process restart in prod.
- **Mitigation**: Switch to `DatabaseSessionService` or `VertexAiSessionService` *before* turning on resumability. Audit every `LongRunningFunctionTool` for idempotency — at-least-once means a retry will re-run. Consider Temporal/Dapr if you need stronger guarantees.
- **Inline source**: [04 Wiring Resumability § 🚀 In Production](04_WiringResumability.md#-in-production)

### 5. Context cache hit rate is observed before celebrated

- **Risk**: Caching has per-cache overhead. Low hit rate (< 30%) means you are paying for writes with no read benefit. Caching is silently expensive when it does not work.
- **Mitigation**: Wire the cache-hit-rate metric ([Module 15 § Metrics](../15_Observability/04_MetricsAndDashboards.md)) before flipping on `context_cache_config` in prod. Tune `min_tokens` and `ttl_seconds` based on real hit data, not guesses.
- **Inline source**: [05 Wiring Context Cache § 🚀 In Production](05_WiringContextCache.md#-in-production)

### 6. Compaction uses a cheap summarizer model

- **Risk**: Each compaction is an extra LLM call. A 1000-turn day with `compaction_interval=20` is 50 extra LLM calls just for summarization. Using your main expensive model for compaction doubles your bill.
- **Mitigation**: Set `summarizer=LlmEventSummarizer(model="gemini-2.5-flash-lite")` (or similar cheap model) even if the main agent uses `gemini-2.5-pro`. Tune `compaction_interval` upward for low-stakes chat; downward only when you see context-window hits.
- **Inline source**: [06 Wiring Context Compaction § 🚀 In Production](06_WiringContextCompaction.md#-in-production)

### 7. Modern Runner form over legacy

- **Risk**: New code written in the `Runner(app_name=..., agent=..., plugins=...)` form is acquiring debt — every 2.0+ feature lands on `App`, not on Runner kwargs. The legacy form will keep working but stop gaining capabilities.
- **Mitigation**: One-line migration: replace `Runner(app_name="x", agent=a, plugins=p)` with `Runner(app=App(name="x", root_agent=a, plugins=p))`. Do it before adding any new feature.
- **Inline source**: [07 Runner Inside the App § 🚀 In Production](07_RunnerInsideTheApp.md#-in-production)

### 8. Lifecycle hooks are NOT for everything

- **Risk**: Stuffing every heavy init into `on_startup` makes cold start unbearable — 20s startup means 20s before Cloud Run reports the instance ready, 20s of latency on a scale-from-zero event.
- **Mitigation**: Profile your startup. Anything > 1s should be **lazy-loaded on first use**, not in startup. The rule of thumb: only the *minimum required to serve the first request* belongs in `on_startup`. Heavy models, optional integrations, warm-up calls — let them happen on first request, behind a `functools.lru_cache`.

---

## Cross-references

- The cross-cutting production module: [16 Production & Security](../16_ProductionSecurity/) — synthesizes every module's checklist.
- The observability module: [15 Observability](../15_Observability/) — instrument your hardened App before you ship.
- The deployment module: [22 Deployment Models](../22_DeploymentModels/) — Cloud Run vs Agent Engine vs GKE shape what lifecycle/cold-start look like.
- The HITL module: [4B Human-in-the-Loop](../4B_HumanInTheLoop/) — the deep-dive on resumability after you have wired it here.

> 🚀 **In Production** — composite reminder
>
> The `App` is your one chance to express "this is the agentic application as a whole". If you cannot answer "what is the App's name, what plugins it carries, what cross-cutting config it has, and what happens on startup/shutdown?" off the top of your head for your service, you do not yet own the production deploy. Go back to the page for each gap, re-read the callout, then come here.

---

[← Prev: 08_DissectingSample](08_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_KnowledgeCheck →](10_KnowledgeCheck.yml)
