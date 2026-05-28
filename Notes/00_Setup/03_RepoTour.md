---
module: 00_Setup
page: 03_RepoTour
title: Three repos you will live in
estimated_minutes: 10
prereqs: [00_Setup/02]
concepts: [adk-python, adk-samples, adk-course]
icon: 🗺
in_production: false
detours_suggested: []
---

[← Prev: 00_Setup/02_HelloFunFacts](02_HelloFunFacts.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/04_DissectingSample →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 03 Repo Tour

# 🗺 The three repos

Throughout this course you'll consult three directories. Knowing which one to open for which question saves hours.

```
{{ repo_tour }}
```

(The ASCII version lives at [`_figures/repo_tour.txt`](_figures/repo_tour.txt) — pasted below.)

```
{{INCLUDE _figures/repo_tour.txt}}
```

> 🤖 **Tutor:** the `{{INCLUDE …}}` placeholder above is for the static site renderer. When you're walking the student through this page live, just open `_figures/repo_tour.txt` in another pane.

## 🧠 When to open which

| Question | Open |
|---|---|
| "What does `LlmAgent` actually do under the hood?" | `adk-python/src/google/adk/agents/llm_agent.py` |
| "How do real teams structure a multi-agent project?" | `adk-samples/python/agents/<closest sample>` |
| "I'm fuzzy on Sessions — where's the lesson?" | `adk-course/Notes/04_SessionsState/` |

## 🧠 The 90/10 rule

* **90% of the time** you read `adk-samples`. The framework was designed so that 35-line files like `fun-facts/agent.py` actually solve real problems. If you're tempted to dive into the framework source, first check whether a sample already shows the pattern.
* **10% of the time** you read `adk-python`. Module 19 is dedicated to this — until then, treat the framework as a black box that delivers on its docstrings.

> ❓ **Ask the student:** if you wanted to learn how multi-agent delegation works in practice, which directory would you grep first?
> *(Expected: `adk-samples/python/agents/` — specifically samples whose names start with `workflow` or that have `sub_agents/` subdirs.)*

> 🛠 **Have the student run:**
> ```bash
> $ ls ~/study/adk-samples/python/agents/ | wc -l
> ```
> Expect somewhere in the **70s** (the catalog grew from ~60 at ADK 1.x to ~75 at 2.0, and Google keeps adding). The exact number isn't load-bearing — the point is "this textbook is large; almost any pattern you'll need has a real example in here."

> 🤖 **Tutor:** if the count is far off (e.g., 12), the student probably cloned the wrong fork or a stale tag. Verify with `cd ~/study/adk-samples && git log -1 --oneline` and ensure they're on `main` of `github.com/google/adk-samples`.

## 🧭 Where your work lives

Your hand-written code goes in `adk-course/Work/`. It's gitignored. **`Solutions/` is read-only until you've tried the exercise** — peeking before the wheels come off defeats the point.

---

[← Prev: 00_Setup/02_HelloFunFacts](02_HelloFunFacts.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/04_DissectingSample →]
