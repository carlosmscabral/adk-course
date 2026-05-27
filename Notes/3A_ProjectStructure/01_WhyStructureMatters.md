---
module: 3A_ProjectStructure
page: 01_WhyStructureMatters
title: What breaks first when you don't split
estimated_minutes: 12
prereqs: [3A_ProjectStructure/00]
concepts: [prompt-sprawl, tool-reuse, testability, blast-radius]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_MinimalLayout →](02_MinimalLayout.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 01 Why structure matters

# 🧠 Why structure matters (and why most people get it wrong)

> 🤖 **Tutor:** the failure mode this page guards against is **over-structuring early**. Frameworks-as-fashion students will copy a 6-folder layout for a 20-line agent and complain ADK is "too heavy." Lead with: *layout is a response to pressure, not a prerequisite for working code*.

A single-file agent **runs fine**. `adk web` will find it. Cloud Run will deploy it. The reason to split is not aesthetics — it's that one of three pressures has crossed a threshold:

## The three pressures

### 1. Prompt sprawl

Your `instruction="..."` started as one line and is now 40 lines of triple-quoted Markdown — with `{user_name}` interpolation, three variants, and a `description=` that's also drifting.

**Symptom**: you scroll past the prompt to find the `tools=[...]` line. Diffs in PR review are dominated by prose changes that hide the code changes.

**Fix**: move prompts to their own module. A `prompts.py` is enough until you have >1 LlmAgent; then it's `prompts/`.

### 2. Tool reuse

You wrote a `lookup_customer(id)` tool. Now the new sub-agent you're adding also needs to look up customers. You're staring at a copy-paste.

**Symptom**: two functions named the same thing in two `agent.py` files. Or worse — they diverge silently and the bug appears in only one path.

**Fix**: pull tools into a `tools.py` (or `tools/` once you have categories). Both agents import the same callable.

### 3. Testability

You want to write `pytest tests/test_lookup_customer.py`. But `lookup_customer` is defined inside `agent.py` next to a `load_dotenv()` call and a `genai` client init that reads from env at import time. Running the test crashes before it begins.

**Symptom**: `pytest` errors at *collection*, not at run.

**Fix**: tools live in a module that imports cleanly without side effects. The agent file is the only place where "wire everything together" happens.

## What the three pressures *aren't*

- They are not "what looks professional."
- They are not "how Google's samples are organized" (Google's samples are mostly **large** — they're showcasing patterns, not minimum viable shape).
- They are not "I'll need it later." You won't. Refactoring three files is a 15-minute job; refactoring a premature 12-folder tree fights you for a day.

> ❓ **Ask the student:** look at their most recent `Work/03_*.py`. Which of the three pressures (if any) is hitting *that* file right now?
>
> If the answer is **none**, the right layout for that project is `02_MinimalLayout` and we're done after page 02 + 05. Skip 03–04 and come back when a pressure hits.

## Blast radius

The hidden fourth reason — once an agent ships, *changes have consequences*.

- One file = changing the prompt risks breaking tool registration (same diff).
- Split = prompt changes touch `prompts.py` only; PR reviewers can read the diff in 10 seconds.

This is the **only** structural argument that matters in production. Everything before "you have users" is a guess.

> **🚀 In Production**
>
> The minute the agent is behind a `/run` endpoint that real callers depend on, *split for blast radius first, then for ergonomics*. A diff that touches only `prompts.py` is a safer rollout than one that touches `agent.py`. We pick this up in [10_InProduction](10_InProduction.md) and [06 In Production for Multi-Agent](../05_MultiAgent/06_InProduction.md).

> 🧭 **If the student looks stuck:** suggest detour [[PY_packaging]] — covers how Python actually resolves `from .tools import X`, which makes the rest of this module feel obvious.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_MinimalLayout →](02_MinimalLayout.md)
