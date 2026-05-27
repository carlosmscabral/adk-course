---
module: 02_FirstAgent
page: 00_Overview
title: First Agent — instantiate the runtime by hand
estimated_minutes: 10
prereqs: [01_Foundations/08]
concepts: [LlmAgent, Runner, InMemorySessionService, run_async]
icon: 🛠
in_production: false
detours_suggested: [PY_async, GeminiPayload]
---

[← Prev: 01_Foundations/08_MiniDrill](../01_Foundations/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/01_LlmAgentByHand →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 00 Overview

# 🛠 Module 02 — First Agent (by hand)

The whole point: build everything `adk run` hid from you. Type `LlmAgent`, `InMemorySessionService`, `Runner.run_async` with your own fingers. Once you've done it once, the CLI becomes a 10-line wrapper instead of a magic command.

## What you'll learn

* Instantiate `LlmAgent` in a REPL.
* Create a Session via `InMemorySessionService`.
* Build a `Runner` and iterate its async generator.
* Construct the `types.Content` message Gemini expects.
* Pull text out of an `Event`.
* Re-read `currency-agent/agent.py` with this new understanding.

## Prereqs

* Module 01 complete — you can place every primitive on a diagram.
* You're comfortable with `async`/`await`. If not, take detour [[PY_async]] first.

## Estimated time

About **two days**, including the mini-drill. This is your first real code.

## Sample anchor

[`adk-samples/python/agents/currency-agent/`](../../../adk-samples/python/agents/currency-agent/). One agent, one MCP-backed tool. We dissect on page 05.

## Pages in this module

1. [01 LlmAgent by hand](01_LlmAgentByHand.md)
2. [02 Runner and Session](02_RunnerAndSession.md)
3. [03 `run_async` is a generator](03_RunAsyncIsAGenerator.md)
4. [04 The Gemini payload (`types.Content`)](04_TheGeminiPayload.md)
5. [05 Dissecting currency-agent](05_DissectingSample.md)
6. [06 In production](06_InProduction.md)
7. [07 Knowledge check](07_KnowledgeCheck.yml)
8. [08 Mini-drill](08_MiniDrill.yml)

> 🤖 **Tutor:** the mini-drill solution is a **gate-keeper** at `Solutions/02_FirstAgent/hello_agent.py`. Encourage the student to write it without peeking; offer the solution only if they're truly stuck.

---

[← Prev: 01_Foundations/08_MiniDrill](../01_Foundations/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/01_LlmAgentByHand →]
