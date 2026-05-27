---
module: 19_Internals
page: 00_Overview
title: Reading the ADK source — what, why, when
estimated_minutes: 30
prereqs: [02_FirstAgent/04, 03_Tools/02, 04_SessionsState/02, 05_MultiAgent/02, 06_GraphWorkflows/02, 11_Memory/02, 13_Plugins/02, 14_Evaluation/02]
concepts: [source-reading, debugging-by-stack, contribution]
icon: 🧠
in_production: true
detours_suggested: [PY_async, PY_pydantic]
---

[← Prev: 18_StreamingLive/last]  [↑ Map](../../MAP.md)  [Next: 19_Internals/01_RepoMap →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 00 Overview

# 🧠 Internals — read the framework

By module 18 you've used every public surface. Now we open the lid. **Not to memorize the source** — to give you a map you can navigate when:

- a behavior contradicts the docs (rare, but it happens)
- a stack trace lands in `adk/flows/llm_flows/base_llm_flow.py:1024` and you need to know if that's user-fixable
- you want to subclass `BaseAgent` for a custom control flow
- you're contributing back a bug fix

## What you'll learn

- The high-level repo layout (one sentence per top-level subdir).
- The `LlmAgent → _llm_flow → LLMRegistry → BaseLlm` chain.
- Where state deltas actually mutate the `Session`.
- How a tool invocation flows from LLM response → `ToolContext` → function → event.
- How `Workflow` runs nodes; where `AutoFlow` lives.

## What you will **not** do

Memorize line numbers. Treat source as docs. The source is pinned to a version — `2026-05-27` GA — and will drift. Use it as **a debugger's map**, not as a textbook.

## Time

**3 days**. One day of orientation (pages 01-08), one of tracing (09-11), one for production guidance and the mini-drill (12-14).

## Sample / source anchors

All paths live under `/home/carloscabral/study/adk-python/src/google/adk/`.

| File | Role |
|---|---|
| `agents/llm_agent.py` | The agent class |
| `agents/base_agent.py` | The base contract |
| `runners.py` | Top-level entry: `Runner.run_async` |
| `sessions/session.py` | The data model |
| `events/event.py` | The unit of transport |
| `tools/base_tool.py` | The tool contract |
| `flows/llm_flows/base_llm_flow.py` | The actual LLM loop |
| `flows/llm_flows/auto_flow.py` | Single-agent flow + transfer |
| `workflow/_workflow.py` | Graph workflow runtime |
| `models/registry.py` | LLM resolution |

> 🤖 **Tutor:** keep this module breezy. The student should leave with a **mental map**, not exhaustive recall. If they ask "should I memorize this?" — the answer is no.

> 🛠 **Have the student run:** `tree -L 2 /home/carloscabral/study/adk-python/src/google/adk/ | head -40` before continuing.

[← Prev: 18_StreamingLive/last]  [↑ Map](../../MAP.md)  [Next: 19_Internals/01_RepoMap →]
