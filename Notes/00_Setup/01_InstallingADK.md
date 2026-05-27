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

One package, one env var. That's the whole setup.

## 🛠 Install the package

Pick a fresh virtualenv (don't pollute system Python):

```bash
$ python3 -m venv .venv && source .venv/bin/activate
(.venv) $ pip install google-adk
(.venv) $ adk --version
adk 2.0.x
```

Prefer `uv`? Same idea:

```bash
$ uv venv && source .venv/bin/activate
$ uv pip install google-adk
```

> 🛠 **Have the student run:** `adk --version`. If the command isn't found, the venv isn't activated — make them re-source it before moving on.

## 🛠 Get a Gemini API key

Open https://aistudio.google.com/apikey, click **Create API key**, copy the value. The free tier covers all of Foundation Track.

## 🧠 Configure with a `.env`

ADK looks for `GOOGLE_API_KEY` in the process environment. The `python-dotenv` package (already pulled in by `google-adk`) loads it from a file next to your agent. Create one:

```bash
$ cat > .env <<'EOF'
GOOGLE_API_KEY=AIza...your-key...
GOOGLE_GENAI_USE_VERTEXAI=FALSE
EOF
```

The second line tells the SDK to use the AI Studio endpoint (free key) instead of Vertex AI. We'll revisit Vertex in `10A_EmbeddingsVectorSearch`.

## ❓ Why two ways to authenticate?

ADK supports both **AI Studio** (an API key, the easy path) and **Vertex AI** (Google Cloud ADC, the production path). The same `LlmAgent` code runs against either; only the env vars differ. For Foundation Track we stay on AI Studio.

> ❓ **Ask the student:** open the `.env` file — should this ever be committed to git?
> *(Expected: no, add it to `.gitignore`. We'll formalize this on page 05.)*

> **🚀 In Production**
>
> Never bake an API key into your source. In Cloud Run / Agent Engine you read keys from **Secret Manager** or use Vertex AI's ADC (no key at all). The `.env` pattern is dev-only — production agents read from the environment that the platform injects.

---

[← Prev: 00_Setup/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 00_Setup/02_HelloFunFacts →]
