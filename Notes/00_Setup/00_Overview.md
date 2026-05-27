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
