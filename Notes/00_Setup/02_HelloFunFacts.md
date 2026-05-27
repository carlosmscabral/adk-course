---
module: 00_Setup
page: 02_HelloFunFacts
title: Hello, fun-facts — your first agent conversation
estimated_minutes: 15
prereqs: [00_Setup/01]
concepts: [adk-run, fun-facts, agent-loop]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 00_Setup/01_InstallingADK](01_InstallingADK.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/03_RepoTour →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 02 Hello, fun-facts

# 🛠 Hello, fun-facts

The point of this page is **a working conversation, end-to-end, before we open a single source file**. Engine-first, but you don't get to the engine without first hearing it run.

## 🛠 Navigate to the sample

You cloned `adk-samples` on the previous page. Go to the `fun-facts` agent:

```bash
$ cd "$ADK_WORKSPACE/adk-samples/python/agents/fun-facts"
$ ls fun_facts/
agent.py  __init__.py
```

(If you started a fresh terminal, re-`export ADK_WORKSPACE="$HOME/study"` first — or just use the absolute path.)

## 🛠 Drop your `.env` next to the agent

This is the `.env` creation step deferred from page 01. The file goes **inside `fun_facts/`**, next to `agent.py` — that's where `load_dotenv(override=True)` (called on import) looks for it. Full path, no ambiguity:

```
<workspace>/adk-samples/python/agents/fun-facts/fun_facts/.env
```

Create it:

```bash
$ cat > fun_facts/.env <<'EOF'
GOOGLE_API_KEY=AIza...your-key-here...
GOOGLE_GENAI_USE_VERTEXAI=FALSE
EOF
```

Verify:

```bash
$ ls -la fun_facts/.env
$ cat fun_facts/.env
```

> 🤖 **Tutor — `.env` location rules (repeat verbatim if asked):**
> 1. The `.env` goes in `fun_facts/`, the agent's package directory. Not in the parent `fun-facts/` dir. Not in `adk-samples/`. Not in `adk-course/`. Not in the workspace root. Not in the venv.
> 2. Why: `load_dotenv()` is called from inside `fun_facts/agent.py`, and dotenv's default search begins at the calling module's directory.
> 3. If the student created the `.env` somewhere else, have them `mv` (not re-create) it into `fun_facts/`.
> 4. The course's workspace-layout diagram on `00_Overview` shows this path explicitly — if there's any doubt, re-read that diagram with the student.

## 🛠 Run it

You're now in `…/adk-samples/python/agents/fun-facts/`. Make sure your venv (created on page 01 in your workspace root) is activated — `adk` must be on PATH:

```bash
$ source "$ADK_WORKSPACE/.venv/bin/activate"     # if not already active
$ which adk                                       # sanity check
$ adk run fun_facts
[user]: octopuses
[Facts]: Octopuses have three hearts, blue copper-based blood,
         and can taste with their suckers...
[user]: exit
```

`adk run <package>` does three things you'll do by hand in Module 02:

1. Imports the module, finds the symbol named `root_agent` (or the `App`'s root).
2. Spins up an in-memory session.
3. Loops: read stdin → wrap as `types.Content` → `runner.run_async(...)` → print events.

> 🛠 **Have the student run:** `adk run fun_facts` and have one back-and-forth. They should see the agent search (the model invokes `google_search`) and stream a reply.

## ❓ What just happened?

* You typed text. The CLI wrapped it as a Gemini message.
* The agent's instruction told Gemini to be wacky and use search.
* Gemini decided to call `google_search`, got results, summarized them, and replied.
* The CLI printed the reply and looped.

That whole loop is **the agent loop**. We'll draw it on page 04 of Module 01.

> 🤖 **Tutor:** if `adk run` errors with `google.auth.exceptions.DefaultCredentialsError`, the student likely forgot `GOOGLE_GENAI_USE_VERTEXAI=FALSE` — the SDK is trying to authenticate to Vertex instead of AI Studio. Fix and retry.

---

[← Prev: 00_Setup/01_InstallingADK](01_InstallingADK.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/03_RepoTour →]
