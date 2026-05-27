---
module: 01_Foundations
page: 00_Overview
title: Foundations — the mental model
estimated_minutes: 10
prereqs: [00_Setup/07]
concepts: [agent-loop, runner, session, event, tool, state]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 00_Setup/07_MiniDrill](../00_Setup/07_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/01_WhatIsAnAgent →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 00 Overview

# 🧠 Module 01 — Foundations

In Module 00 you watched an agent talk. In Module 01 you build the **mental model** of *why* it talked. No new code yet — just diagrams, vocabulary, and re-reading `fun-facts/agent.py` with fresh eyes. By the end you should be able to draw the data flow of one turn on a napkin, including a tool call.

In Module 02 you'll instantiate every box in that diagram by hand.

## What you'll learn

* The agent loop: `user msg → LLM → (tool? execute → feed result back) → reply`.
* Three runtime primitives: **Runner**, **Session**, **Event**.
* What a tool actually is (preview: a Python function).
* Where state lives (preview: on the Session, accumulated via event deltas).
* How those primitives sit invisibly around the `fun-facts/agent.py` you already ran.

## Prereqs

* Module 00 complete — `adk run fun_facts` worked at least once.
* No new dependencies. No new code to write.

## Estimated time

About **one day**. Mostly reading + drawing.

## Sample anchor

We re-read [`adk-samples/python/agents/fun-facts/`](../../../adk-samples/python/agents/fun-facts/) — same file as Module 00, very different lens.

## Pages in this module

1. [01 What is an agent?](01_WhatIsAnAgent.md)
2. [02 Runner, Session, Event](02_RunnerSessionEvent.md)
3. [03 Tools are Python functions](03_ToolsArePythonFunctions.md)
4. [04 State lives on the session](04_StateLivesOnSession.md)
5. [05 Dissecting the sample (re-read)](05_DissectingSample.md)
6. [06 In production](06_InProduction.md)
7. [07 Knowledge check](07_KnowledgeCheck.yml)
8. [08 Mini-drill](08_MiniDrill.yml)

> 🤖 **Tutor:** the goal of this module is **vocabulary and arrows**. Resist the urge to write code. The student gets to type plenty in Module 02. If they get itchy, point them at the mini-drill on page 08 — it's deliberately a *paper* exercise.

---

[← Prev: 00_Setup/07_MiniDrill](../00_Setup/07_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/01_WhatIsAnAgent →]
