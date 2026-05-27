# AGENTS.md — Module 00 Setup (teaching notes for the AI tutor)

## What the student should walk away knowing

- ADK is one `pip install google-adk` and one env var (`GOOGLE_API_KEY`) away from a running conversation.
- `adk run <package>` imports the package and looks for `root_agent` (or an `App`).
- The 35-line `fun-facts/agent.py` already exposes every concept we'll spend Foundation Track unpacking: `Agent`, `model`, `instruction`, `tools`, `name`.
- The three repos (`adk-python` framework, `adk-samples` textbook, `adk-course` you-are-here).
- Five production hygiene rules: gitignore `.env`, pin model, pin `google-adk`, choose tier with intent, never commit secrets.

## Pacing

- **Easy if** the student already has Python 3.11 + a Gemini API key. Should finish in ~3 hours including reading.
- **Hard if** the student is wrestling with Python install / venv basics. Hold here and walk them through `pyenv` or `uv python install`. Do NOT advance into Module 01 until `adk run fun_facts` works.
- **Hard if** the student is on Vertex AI by default (corporate GCP project). Make sure they set `GOOGLE_GENAI_USE_VERTEXAI=FALSE` for Foundation Track — we'll switch to Vertex deliberately in Module 10A.

## Watch for these mistakes

- Forgetting to activate the venv → `adk: command not found`.
- Putting `.env` in the wrong directory (must be next to `agent.py`, or in CWD when you run `adk`).
- Trying to authenticate to Vertex with just an API key (results in `DefaultCredentialsError`).
- Editing the `instruction=` string in the mini-drill but forgetting to save before re-running.

## When to suggest a detour

- Student asks "what is `load_dotenv` doing?" → 30-second explanation, no detour needed.
- Student asks "why use `uv` over `pip`?" → 30-second pitch (faster, lockfile-by-default), no detour.
- Student asks "what's `App` vs `root_agent`?" → defer to Module 02; for now "App is the deployable wrapper" is enough.

## Mini-drill grading

- Pass = visibly different style in the reply, same model and tools.
- Probe question: "what's the difference between editing `instruction=` and editing `model=` in terms of behavior change?" (Instruction = personality; model = capability/cost. Different axes.)

## After this module

The student is ready for Module 01 (Foundations), which re-reads `fun-facts/agent.py` but draws the runtime around it. Don't open Module 02 until both 00 and 01 are done — Module 02 has the student type a Runner by hand and that's frustrating without the mental model from 01.
