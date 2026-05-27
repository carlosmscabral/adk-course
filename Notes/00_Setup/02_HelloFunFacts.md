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

## 🛠 Clone the samples repo

```bash
$ git clone https://github.com/google/adk-samples.git
$ cd adk-samples/python/agents/fun-facts
$ ls fun_facts/
agent.py  __init__.py
```

(If you already cloned `adk-samples` into `~/study/`, skip the clone and `cd` straight to it.)

## 🛠 Drop your `.env` next to the agent

```bash
$ cat > fun_facts/.env <<'EOF'
GOOGLE_API_KEY=AIza...
GOOGLE_GENAI_USE_VERTEXAI=FALSE
EOF
```

`fun_facts/agent.py` already calls `load_dotenv(override=True)` on import — it'll pick this file up automatically.

## 🛠 Run it

```bash
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
