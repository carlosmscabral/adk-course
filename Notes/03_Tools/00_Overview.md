---
module: 03_Tools
page: 00_Overview
title: Tools — give the agent a body
estimated_minutes: 10
prereqs: [02_FirstAgent/08]
concepts: [FunctionTool, ToolContext, built-in tools, AgentTool]
icon: 🛠
in_production: false
detours_suggested: [PY_typing]
---

[← Prev: 02_FirstAgent/08_MiniDrill](../02_FirstAgent/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 03_Tools/01_WhyTools →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 00 Overview

# 🛠 Module 03 — Tools

An agent without tools is a chatbot. **Tools are how the agent acts on the world.** This module shows that writing a tool is writing a Python function — the framework does the schema work.

## What you'll learn

* Write a `FunctionTool` from a typed Python function.
* Understand the docstring → schema translation.
* Use `ToolContext` to read/write session state from inside a tool.
* The catalog of built-in tools: `google_search`, `load_memory`, `exit_loop`, `transfer_to_agent`.
* The **Computer Use** preview toolset — let the agent drive a real browser.
* Tool **limitations** — which built-ins must be sole-tool, and how to compose around the rule.
* Preview `AgentTool` (call an agent like a tool — Module 05).
* Preview `LongRunningFunctionTool` (for slow tools).
* Dissect how `currency-agent` and `academic-research` use tools.

## Prereqs

* Module 02 complete — you can build Agent + Runner + Session.
* Type hints feel natural. If they're rusty, take [[PY_typing]] now (20 min).

## Estimated time

About **two days**, including the calculator drill. (Add ~45 min if you walk the Computer Use page end-to-end with Playwright installed.)

## Sample anchors

* [`currency-agent`](../../../adk-samples/python/agents/currency-agent/) — uses an MCP-backed tool; we focus on the *signature* of the exchange-rate function.
* [`academic-research`](../../../adk-samples/python/agents/academic-research/) — uses `google_search` (built-in) and composes `AgentTool` sub-agents.

## Pages in this module

1. [01 Why tools?](01_WhyTools.md)
2. [02 FunctionTool](02_FunctionTool.md)
3. [03 Docstring as schema](03_DocstringAsSchema.md)
4. [04 ToolContext](04_ToolContext.md)
5. [05 Built-in tools](05_BuiltInTools.md)
6. [06 Computer Use toolset (preview)](06_ComputerUse.md)
7. [07 Tool limitations & single-instance constraints](07_ToolLimitations.md)
8. [08 AgentTool preview](08_AgentToolPreview.md)
9. [09 LongRunningFunctionTool preview](09_LongRunningTool.md)
10. [10 Dissecting samples](10_DissectingSample.md)
11. [11 In production](11_InProduction.md)
12. [12 Knowledge check](12_KnowledgeCheck.yml)
13. [13 Mini-drill — calculator](13_MiniDrill.yml)

> 🤖 **Tutor:** the mini-drill solution at `Solutions/03_Tools/calc_agent.py` is a **gate-keeper** (first tool of the course). Encourage the student to write it without peeking; reveal only if stuck after ≥15 minutes.

---

[← Prev: 02_FirstAgent/08_MiniDrill](../02_FirstAgent/08_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 03_Tools/01_WhyTools →]
