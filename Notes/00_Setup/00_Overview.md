---
module: 00_Setup
page: 00_Overview
title: Setup — install ADK, run your first agent
estimated_minutes: 10
prereqs: []
concepts: [install, env, adk-cli, fun-facts]
icon: 📦
in_production: false
detours_suggested: []
---

[← Prev: —]  [↑ Map](../../MAP.md)  [Next: 00_Setup/01_InstallingADK →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 00 Overview

# 📦 Module 00 — Setup

The smallest possible loop from a fresh machine to a talking agent. We install ADK 2.0, point it at a Gemini API key, and run the canonical `fun-facts` sample. The runtime is hidden inside `adk run` — that's fine for today. In Module 02 we tear that runtime open and build it by hand.

## What you'll learn

* Install `google-adk` (CLI + library).
* Wire a `GOOGLE_API_KEY` via `.env`.
* Run an agent with the `adk run` CLI.
* Read the 35 lines of `fun-facts/agent.py` and recognize every name.
* The three repos on disk you'll consult forever: `adk-python`, `adk-samples`, `adk-course`.

## Prereqs

* Python 3.11+ (`python3 --version`).
* Comfortable in a terminal: `cd`, `pip`/`uv`, `git`, `export`.
* A Gemini API key (free tier is fine for this module). Get one from https://aistudio.google.com/apikey.
* **A workspace directory decided.** The course assumes three sibling repos — `adk-course/`, `adk-samples/`, `adk-python/` — under one parent (canonical: `~/study/`, but anywhere works). Page 01 walks you through cloning the two companion repos; just pick the parent dir before you start.

## 🗺 Workspace layout — the authoritative answer

**Every "where does this go?" question in this course resolves to this diagram.** Read it once now; refer back whenever a page asks you to create a file.

```
<workspace>/                                  ← e.g., ~/study/  (or ~/_demos/, ~/code/ — any parent)
│
├── .venv/                                    ← Python virtualenv. ONE per workspace. Activated from
│                                                workspace root: `source .venv/bin/activate`.
│                                                Contains the `adk` CLI after `pip install google-adk`.
│
├── adk-course/                               ← THIS REPO (read-only EXCEPT Work/)
│   ├── Notes/                                ← Lessons. You read these; you do not edit them.
│   ├── Solutions/                            ← Gate-keeper solutions. Read-only until you've tried.
│   ├── Reference/                            ← Cheat sheets.
│   ├── Drills/                               ← Milestone integration exercises (M1–M5).
│   └── Work/                                 ← 🟢 YOUR scratch dir. Gitignored. EVERYTHING you write
│       │                                        from Module 02 onward goes here. For an exercise
│       │                                        called "calc_agent", that's `Work/calc_agent/`.
│       └── _template_run.py                  ← starter scaffolding (copy when starting a drill)
│
├── adk-samples/                              ← Canonical agents (read-only). You DISSECT these.
│   └── python/agents/
│       └── fun-facts/                        ← Module 00's sample lives here.
│           └── fun_facts/                    ← the agent package (note: hyphen → underscore)
│               ├── agent.py
│               ├── __init__.py
│               └── .env                      ← 🟢 Module 00's .env goes HERE. Nowhere else.
│                                                Created on page 02. NOT on page 01. NOT in
│                                                workspace root. NOT in adk-course/.
│
└── adk-python/                               ← Framework source (read-only). Opened from Module 19.
```

### The three rules that cover every page in this course

1. **Course pages are read-only.** You never edit anything under `adk-course/Notes/`, `adk-course/Solutions/`, `adk-course/Reference/`, or `adk-course/Drills/`. If a lesson asks you to write code, it goes in `Work/`.
2. **Samples are read-only.** You never edit `adk-samples/python/agents/<whatever>/` source. You can drop a `.env` next to a sample's agent module (as you'll do for `fun-facts` on page 02) — that's not "editing," that's local config the sample's `load_dotenv()` call expects.
3. **`.env` files live next to the agent module that needs them.** Not in the workspace root. Not in the course root. Next to the `agent.py` (or wherever `load_dotenv()` is called). For `fun-facts`, that's `adk-samples/python/agents/fun-facts/fun_facts/.env`. For your own agents in `Work/my_agent/`, it'd be `Work/my_agent/.env`.

### Quick reference — "where do I create X?"

| Thing | Where it goes |
|---|---|
| Virtualenv | `<workspace>/.venv/` |
| Cloned `adk-samples`, `adk-python` | siblings of `adk-course/` under `<workspace>/` |
| `.env` for **`fun-facts`** (this module) | `<workspace>/adk-samples/python/agents/fun-facts/fun_facts/.env` |
| `.env` for **your own** agents (Module 02+) | next to your agent file, e.g. `<workspace>/adk-course/Work/my_agent/.env` |
| Your hand-written exercise code | `<workspace>/adk-course/Work/<exercise_name>/` |
| Notes you take while learning | anywhere you want — they aren't part of the course |

> 🤖 **Tutor — MANDATORY before page 01:** walk the student through this layout diagram and the three rules. Confirm they understand which directories are read-only and where their own work will live. **Do not improvise alternate locations.** If the student's actual workspace doesn't match `~/study/` (e.g., they're at `~/_demos/`), substitute the parent path in commands — the *layout* (three siblings + shared `.venv/`) is load-bearing; the *parent path* is not. If a later page seems to contradict this layout, the page is wrong — flag it, do not paper over it.

## Estimated time

About **one day**, including the dissection page and the mini-drill. Most of that is reading.

## Sample anchor

[`adk-samples/python/agents/fun-facts/`](../../../adk-samples/python/agents/fun-facts/). 35 lines. One agent, one built-in tool (`google_search`). We will return to it in Module 01 with fresh eyes.

## Pages in this module

1. [01 Installing ADK](01_InstallingADK.md)
2. [02 Hello, fun-facts](02_HelloFunFacts.md)
3. [03 Repo tour](03_RepoTour.md)
4. [04 Dissecting the sample](04_DissectingSample.md)
5. [05 In production](05_InProduction.md)
6. [06 Knowledge check](06_KnowledgeCheck.yml)
7. [07 Mini-drill](07_MiniDrill.yml)

> 🤖 **Tutor:** confirm Python ≥ 3.11 and a working `pip` before opening page 01. If the student is on Python 3.10 or older, hold here and walk them through `pyenv` or `uv python install 3.11`.

---

[← Prev: —]  [↑ Map](../../MAP.md)  [Next: 00_Setup/01_InstallingADK →]
