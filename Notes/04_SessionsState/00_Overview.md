---
module: 04_SessionsState
page: 00_Overview
title: Sessions and State — persisting context across turns
estimated_minutes: 10
prereqs: [03_Tools/11]
concepts: [Session, State, prefixes, output_key, persistence]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/11_MiniDrill](../03_Tools/11_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/01_SessionVsState →]

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 00 Overview

# 🧠 Module 04 — Sessions and State

You've used `InMemorySessionService` mechanically since Module 02. Now we open it up. State is what lets agents remember things across turns — and the prefix system controls what survives across sessions and users.

## What you'll learn

* Session vs. State: the conversation container vs. its key-value dict.
* Four state prefixes: (none), `user:`, `app:`, `temp:` — and what each survives.
* Read state in prompts via `{var}` and `{var?}` templating.
* Write state from tools via `tool_context.state[...]`.
* **Context caching (2.0)** — `ContextCacheConfig` to reuse the prefix and slash token cost.
* **Context compaction (2.0)** — `ContextCompactionConfig` + `LlmEventSummarizer` to keep long sessions in-window.
* **Session rewind (2.0)** — `Runner.rewind(...)` to branch at a prior event, patch state, replay.
* **Session migrate (2.0)** — `adk migrate session` to move sessions across backends and schema versions.
* The `output_key=` shortcut that pipes an agent's reply directly into state.
* Persistent backends: `DatabaseSessionService` with SQLite or Postgres URLs.
* Dissect `llm-auditor` — how a SequentialAgent passes context between sub-agents.

## Prereqs

* Module 03 complete — you've written tools, including a `ToolContext`-using one.

## Estimated time

About **two days**, including the two-turn remember-name drill.

## Sample anchor

[`llm-auditor`](../../../adk-samples/python/agents/llm-auditor/) — a critic/reviser pair. We trace how the critic's output becomes the reviser's input. (Note: the as-shipped sample relies on `SequentialAgent` chaining; we'll also show the `output_key` pattern explicitly, which appears in many other samples like `workflows-sequential` and `academic-research`.)

## Pages in this module

1. [01 Session vs. State](01_SessionVsState.md)
2. [02 State scopes — the four prefixes](02_StateScopes.md)
3. [03 Reading state in prompts](03_ReadingStateInPrompts.md)
4. [04 Writing state from tools](04_WritingStateFromTools.md)
5. [05 Context caching (NEW 2.0)](05_ContextCaching.md)
6. [06 Context compaction (NEW 2.0)](06_ContextCompaction.md)
7. [07 Session rewind (NEW 2.0)](07_SessionRewind.md)
8. [08 Session migrate (NEW 2.0)](08_SessionMigrate.md)
9. [09 `output_key=` shortcut](09_OutputKeyShortcut.md)
10. [10 Persistent sessions](10_PersistentSessions.md)
11. [11 Dissecting llm-auditor](11_DissectingSample.md)
12. [12 In production](12_InProduction.md)
13. [13 Knowledge check](13_KnowledgeCheck.yml)
14. [14 Mini-drill — remember the user's name](14_MiniDrill.yml)

> 🤖 **Tutor:** state is the #1 source of confusion in early ADK code. Resist the urge to skip prefixes — the bugs they prevent (cross-user data leaks, ephemeral retry counters polluting permanent state) are catastrophic. Linger on page 02.

---

[← Prev: 03_Tools/11_MiniDrill](../03_Tools/11_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/01_SessionVsState →]
