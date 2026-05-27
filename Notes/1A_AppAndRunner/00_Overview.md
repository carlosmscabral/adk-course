---
module: 1A_AppAndRunner
page: 00_Overview
title: App & Runner Architecture — the 2.0 container that owns everything cross-cutting
estimated_minutes: 10
prereqs: [02_FirstAgent/08]
concepts: [App, Runner, app-scope, resumability, context-cache, context-compaction]
icon: 🗺
in_production: false
detours_suggested: [PY_pydantic]
---

[← Prev: 02_FirstAgent/08_MiniDrill](../02_FirstAgent/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_AppVsRunnerVsAgent →](01_AppVsRunnerVsAgent.md)

You are here: 🗺 Foundation Track ▸ 1A App & Runner ▸ 00 Overview

# 🗺 Module 1A — App & Runner Architecture

In Module 02 you built `Runner(app_name=..., agent=..., session_service=...)` by hand. That signature **still works** in 2.0, but it is the *legacy compatibility shim*. The modern construction is `Runner(app=App(...), session_service=...)`. The `App` is the new top-level container: it owns the root agent, the plugins, the resumability config, the context-cache config, the events-compaction config, and the `app:`-scoped state boundary.

This module is the contract that lets later modules be taught coherently:

- **Module 04 (Sessions & State)** can talk about `app:`-state lifetime because the App is what owns it.
- **Module 04 (caching & compaction sub-pages)** can talk about `context_cache_config` and `events_compaction_config` because they are App-level fields.
- **Module 4B (Human-in-the-Loop & Resume/Cancel)** can talk about `resumability_config` because it is set on the App.
- **Module 11 (Memory)** can talk about cross-session memory because the App is the unit of "same app".

If 1A does not land, half of the later runtime story dangles.

## 🎯 Goals

By the end of this module you can:

- Wire an `App(name=, root_agent=, plugins=, ...)` and pass it to `Runner(app=app, session_service=...)`.
- Name the four App-level config fields (plugins, events_compaction_config, context_cache_config, resumability_config) and what each one buys you.
- Decide when to put state under `app:`, `user:`, no-prefix, or `temp:`.
- Run a startup/shutdown hook around an App (MCP server boot, DB pool open, model warm-up).
- Explain — in one breath — why ADK 2.0 introduced `App` instead of leaving everything as Runner kwargs.

## 📋 Prereqs

- [02 First Agent](../02_FirstAgent/) — you have written `Runner + InMemorySessionService` by hand at least once.
- [01 Foundations § 04 State lives on the Session](../01_Foundations/04_StateLivesOnSession.md) — you know that state is a dict the Session carries.

## ⏱ Estimated time

- **Total**: ~2.5 hours over 1–2 sessions.
- Per-page estimates in each page's frontmatter `estimated_minutes:`.

## 🧪 Sample anchor

This module dissects **`memory-bank`** at `/home/carloscabral/study/adk-samples/python/agents/memory-bank/` in [08 Dissecting Sample](08_DissectingSample.md). It is small (~one agent file), uses `App(...)` explicitly, and shows how `app:`-state and `App`-level memory wiring compose.

> 🤖 **Tutor:** before the dissection page, confirm the student can `ls` the sample directory locally. The sample lives at `adk-samples/python/agents/memory-bank/app/agent.py` — if it is missing, fetch it first.

## 🛣 Plan

1. **01 App vs Runner vs Agent** — what each one owns; why 2.0 split them
2. **02 On startup / shutdown** — wrapping the App with lifecycle hooks (MCP boot, DB pool, model warm-up)
3. **03 The `app:` state boundary** — lifetime semantics, contrasted with `user:`, no-prefix, `temp:`
4. **04 Wiring resumability** — `resumability_config` (forward link to Module 4B)
5. **05 Wiring context cache** — `context_cache_config` (forward link to Module 04 caching page)
6. **06 Wiring context compaction** — `events_compaction_config`
7. **07 Runner inside the App** — Runner is now constructed *from* the App, not in parallel
8. **08 Dissecting Sample — `memory-bank`** — a real sample that uses `App(...)`
9. **09 In Production** — App startup costs, cold-start tradeoffs, when NOT to use lifecycle hooks
10. **10 Knowledge Check** — 5–7 questions
11. **11 Mini-Drill** — wrap your hello agent in an App

After this module: → [Module 03 Tools](../03_Tools/) for the per-agent tool surface, or jump ahead to [Module 4B Human-in-the-Loop](../4B_HumanInTheLoop/) if resumability is what you came for.

---

[← Prev: 02_FirstAgent/08_MiniDrill](../02_FirstAgent/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_AppVsRunnerVsAgent →](01_AppVsRunnerVsAgent.md)
