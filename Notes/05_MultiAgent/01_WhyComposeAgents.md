---
module: 05_MultiAgent
page: 01_WhyComposeAgents
title: Why compose agents at all?
estimated_minutes: 15
prereqs: [05_MultiAgent/00]
concepts: [prompt-bloat, role-conflict, separation-of-concerns]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 05_MultiAgent/00_Overview]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/02_SubAgents →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 01 Why Compose

## 🧠 The mono-agent trap

Beginners stuff every responsibility into a single `LlmAgent`. The instruction grows to a 600-line mega-prompt with sections like "When the user asks X, do Y; when they ask Z, do W; never forget K; also follow style guide S". This breaks in three predictable ways:

### 1. Prompt bloat ⚠️

The instruction crosses ~4-6 KB and the model starts *forgetting the middle*. Classic "lost in the middle" symptom: rules at the top and bottom are honored; rules in section 7 of 14 are not.

### 2. Role conflict ⚠️

You ask one agent to be **both** a creative writer (high temperature, wild ideas) **and** a fact-checker (low temperature, conservative). The temperature is a single dial — pick one, lose the other. Same for tool sets, output formats, style.

### 3. Untestable spaghetti 🧪

When the agent flubs, you can't tell *which role* flubbed. Was it the planner? the writer? the editor? They all live in the same prompt.

## 🛠 The split

Three agents, three short prompts, three temperatures, three tool kits:

```
            single mega-agent                  composed team
            ─────────────────                  ─────────────
                                              ┌──────────┐
            ┌──────────────┐                  │  planner │  T=0.2
            │              │                  └─────┬────┘
            │  600-line    │                        ↓
            │  instruction │       →           ┌──────────┐
            │              │                   │  writer  │  T=0.9
            │              │                   └─────┬────┘
            └──────────────┘                         ↓
                                                ┌──────────┐
                                                │  critic  │  T=0.0
                                                └──────────┘
```

Each specialist gets ~80 lines of instruction. Each is independently testable. You can swap one without touching the others.

## ❓ The cost

Latency: 3x model calls instead of 1. Cost: 3x tokens. Use composition when the *quality lift* justifies it — for one-shot Q&A, a single agent is fine.

> 🚀 **In Production**
>
> The break-even is usually around the third "section" in your mega-prompt. If you're typing `## When the user asks about X...` for the third time, stop and split.

> 🧭 If you're about to add a 4th agent or a 2nd sub-agent, this is the point where a single `agent.py` starts to strain. See [[3A_ProjectStructure/04_GrowingLayout]] for when to escalate to the directory-per-concept layout (one folder per sub_agent, shared `prompts.py`/`tools.py`).

> ❓ **Ask the student:** what's a task they're working on right now that has at least 3 distinct sub-responsibilities? (Use that as the running example for this module.)

> 🤖 **Tutor:** if the student's example genuinely has only 1 responsibility, don't force composition. Note it and continue — they'll feel the bloat naturally when they hit it.

---

[← Prev: 05_MultiAgent/00_Overview]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/02_SubAgents →]
