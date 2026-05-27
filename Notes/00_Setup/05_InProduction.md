---
module: 00_Setup
page: 05_InProduction
title: Setup hygiene for real projects
estimated_minutes: 10
prereqs: [00_Setup/04]
concepts: [secrets, model-pinning, pyproject, gitignore]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 00_Setup/04_DissectingSample](04_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/06_KnowledgeCheck →]

You are here: 🗺 Foundation Track ▸ 00 Setup ▸ 05 In Production

# 🚀 Setup hygiene for real projects

Five things you'll regret skipping. Internalize them now while the project is small.

## 🚀 1. Never commit `.env`

Add it to `.gitignore` the moment you create it:

```bash
$ echo ".env" >> .gitignore
$ echo "*/.env"  >> .gitignore   # also catches fun_facts/.env
```

Leaked API keys are revoked by the provider and rotated by the on-call. The standard production pattern is to read keys from **Secret Manager** (GCP) / **AWS Secrets Manager** / your platform's equivalent, and let the runtime inject them as environment variables. The `os.environ['GOOGLE_API_KEY']` lookup looks the same in both worlds — only the source of the value changes.

## 🚀 2. Pin your model

`fun-facts` uses `"gemini-flash-latest"` for the demo. **Don't ship that.** "Latest" can change underneath you and silently regress your prompts. Pin a concrete version like `"gemini-2.5-flash"` (we use this throughout the course). Upgrade deliberately and re-run your evals (Module 14) before promoting.

## 🚀 3. Pin `google-adk` too

In `pyproject.toml`:

```toml
[project]
dependencies = [
    "google-adk==2.0.3",   # pin the minor at least
    "python-dotenv>=1.0",
]
```

ADK 2.0 is GA but still moving fast. Floating dependencies are how Friday deploys become Monday outages.

## 🚀 4. Choose your model tier with intent

| Model | Use for | Don't use for |
|---|---|---|
| `gemini-2.5-flash` | Tool-routing, short replies, high-volume loops | Long-chain reasoning, code review |
| `gemini-2.5-pro` | Complex reasoning, code, research synthesis | Per-request hot path with strict latency budgets |

Cost difference is roughly an order of magnitude. Default to Flash; promote to Pro per-agent where you measurably need it.

## 🚀 5. Treat `.env` files as **per-environment**, not per-developer

A common bug: developer A puts their personal Gemini key in `fun_facts/.env`, commits it (ignoring the warning), it ends up in CI. Standard fix: `.env.example` is committed with placeholder values; the real `.env` is loaded by the platform.

```bash
$ cat .env.example
GOOGLE_API_KEY=your-key-here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

> ❓ **Ask the student:** which of the five rules above does the `fun-facts` sample violate out of the box?
> *(Expected: it uses `"gemini-flash-latest"` — rule 2. Everything else is fine for a demo.)*

> 🤖 **Tutor:** if the student is impatient ("can we skip this and get to multi-agent?"), agree to skim it now and **revisit before any deploy step** (Module 16). These five rules are the difference between a working agent and a working *deployed* agent.

---

[← Prev: 00_Setup/04_DissectingSample](04_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/06_KnowledgeCheck →]
