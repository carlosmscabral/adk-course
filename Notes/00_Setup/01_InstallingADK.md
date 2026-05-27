---
module: 00_Setup
page: 01_InstallingADK
title: Installing google-adk and configuring your API key
estimated_minutes: 15
prereqs: [00_Setup/00]
concepts: [pip, uv, dotenv, GOOGLE_API_KEY]
icon: 📦
in_production: true
detours_suggested: []
---

[← Prev: 00_Setup/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/02_HelloFunFacts →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 01 Installing ADK

# 📦 Installing ADK

One package, one env var. That's the whole setup — once your workspace is laid out.

## 🛠 Pick a workspace, clone the two companion repos

Everything in this course assumes three sibling directories on disk:

```
<workspace>/
├── adk-course/      ← this repo (you're already in it)
├── adk-samples/     ← 60+ canonical agents you'll dissect every module
└── adk-python/      ← framework source — opened from Module 19 onward
```

`<workspace>` can be anywhere; the course assumes `~/study/` and the figures and cross-references will show that path, but `~/code/`, `~/Developer/`, `~/_demos/` all work identically. Pick one and stick to it.

> 🛠 **Have the student run** (in their terminal — not yours):
>
> ```bash
> $ export ADK_WORKSPACE="$HOME/study"     # or wherever you prefer
> $ mkdir -p "$ADK_WORKSPACE" && cd "$ADK_WORKSPACE"
> $ git clone https://github.com/google/adk-samples.git
> $ git clone https://github.com/google/adk-python.git
> $ ls
> adk-course  adk-python  adk-samples
> ```
>
> Ask them to paste the `ls` output back so you can confirm the three siblings exist. **Do not run `git clone` yourself** — that's a contract violation (see `AGENTS.md` ▸ "Hands on keys means hands on the STUDENT's keys"). The cloning IS the lesson; the wait is part of the muscle memory.

`adk-python` is optional for Modules 00–18; the course only opens it in Module 19. Cloning it now means you won't have to break flow later.

> 🤖 **Tutor:** if the student's machine layout doesn't match `~/study/` — for example they're at `~/_demos/adk-course/` — that's fine. Adapt the paths in subsequent commands to their actual workspace. The *layout* (three siblings) is load-bearing; the *parent path* is not.

## 🛠 Install the package

From your workspace root, pick a fresh virtualenv (don't pollute system Python).

> 🛠 **Have the student run** (in their terminal):
>
> ```bash
> $ python3 -m venv .venv && source .venv/bin/activate
> (.venv) $ pip install google-adk
> (.venv) $ adk --version
> adk 2.0.x
> ```
>
> Prefer `uv`? Same idea — same student-types-it rule:
>
> ```bash
> $ uv venv && source .venv/bin/activate
> $ uv pip install google-adk
> ```
>
> Wait for the `pip install` to finish in the student's terminal. **Do not run any of these yourself.** Ask the student to share the `adk --version` output. If the command isn't found, the venv isn't activated — have THEM re-source it before moving on.

## 🛠 Get a Gemini API key

Open https://aistudio.google.com/apikey, click **Create API key**, copy the value. The free tier covers all of Foundation Track.

## 🧠 Where your API key will live (preview — do nothing yet)

ADK reads `GOOGLE_API_KEY` from the process environment. The `python-dotenv` package (already pulled in by `google-adk`) loads it from a `.env` file **next to the agent module being run** — see the workspace layout diagram on `00_Overview`, rule #3.

For Module 00, that means the `.env` will live at:

```
<workspace>/adk-samples/python/agents/fun-facts/fun_facts/.env
```

You will create that file on **page 02** (`02_HelloFunFacts`), once you've `cd`'d into the sample. Not here. Not in your workspace root. Not in `adk-course/`.

You will also need a second env var alongside the key — `GOOGLE_GENAI_USE_VERTEXAI=FALSE` — to tell the SDK to use the AI Studio endpoint (free key) instead of Vertex AI. We'll revisit Vertex in `10A_EmbeddingsVectorSearch`.

> 🤖 **Tutor — DO NOT** have the student create a `.env` on this page under any circumstances. The `.env` is created on page 02, inside the `fun_facts/` package directory. Any instruction phrased as "create a `.env` in your workspace root," "create a `.env` in adk-course/," or "create a `.env` here" is **wrong** — `load_dotenv()` would not find it, the agent would fail to authenticate, and the student would have a broken setup blamed on the course. If you find yourself wanting to give an immediate `.env` instruction, that's a signal to advance to page 02 instead of improvising on page 01.

## ❓ Why two ways to authenticate?

ADK supports both **AI Studio** (an API key, the easy path) and **Vertex AI** (Google Cloud ADC, the production path). The same `LlmAgent` code runs against either; only the env vars differ. For Foundation Track we stay on AI Studio.

> **🚀 In Production**
>
> Never bake an API key into your source, and never commit a `.env` to git. In Cloud Run / Agent Engine you read keys from **Secret Manager** or use Vertex AI's ADC (no key at all). The `.env` pattern is dev-only — production agents read from the environment that the platform injects. We'll formalize this in page 05.

---

[← Prev: 00_Setup/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/02_HelloFunFacts →]
