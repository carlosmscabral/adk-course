---
module: 3A_ProjectStructure
page: 07A_ConfigAndEnvVars
title: Config & env vars — one settings class, env-driven defaults
estimated_minutes: 20
prereqs: [3A_ProjectStructure/07]
concepts: [pydantic-settings, dotenv, env-var-validation, multi-env]
icon: ⚙️
in_production: true
detours_suggested: [PY_pydantic]
---

[← Prev: 07_SharedUtilities](07_SharedUtilities.md)  [↑ Map](../../MAP.md)  [Next: 08_EvalAndTestsLayout →](08_EvalAndTestsLayout.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 07A Config & env vars

# ⚙️ Config & env vars — the project-structure view

> 🤖 **Tutor:** env-var coverage is scattered (`00_Setup/01`, `Detours/Cloud_Run`, `22/08`, per-provider pages in 17). This page is the **structural** home: *where* config lives in the repo, *how* it flows, what NOT to do. We do not re-explain Secret Manager here — link out.

## The env vars ADK actually respects

| Var | Used for |
|---|---|
| `GOOGLE_API_KEY` | AI Studio path. Read by `google.genai` at model call. |
| `GOOGLE_GENAI_USE_VERTEXAI` | `TRUE` flips to Vertex (ADC); `FALSE` uses AI Studio. |
| `GOOGLE_CLOUD_PROJECT` | Vertex / BigQuery / GCS project. Required when Vertex=TRUE. |
| `GOOGLE_CLOUD_LOCATION` | Vertex region (e.g. `us-central1`). |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to a service-account JSON (dev only — prod uses ADC). |
| `ADK_LOG_LEVEL` | `DEBUG`/`INFO`/`WARNING` for ADK's own logger. |
| `ADK_DISABLE_TELEMETRY` | Opt out of anonymized usage telemetry. |

That's the full list ADK 2.0 reads directly. Everything else (`DB_URL`, `REDIS_HOST`, your tool config) is yours.

## The one settings class — `pydantic-settings`

One class, env-driven, used everywhere. Pre-empts the "ten files each call `os.environ[...]`" anti-pattern.

```python
# my_agent/config.py — run with: uv run python -c "from my_agent.config import settings; print(settings)"
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    model_name: str = "gemini-2.5-flash"
    project_id: str | None = None                        # required when use_vertex=True
    location: str = "us-central1"
    api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    use_vertex: bool = Field(default=False, alias="GOOGLE_GENAI_USE_VERTEXAI")

settings = Settings()                                    # module-level singleton
```

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from .config import settings

root_agent = LlmAgent(
    name="researcher",
    model=settings.model_name,                           # ← no hardcoded string
    instruction="You are a careful research assistant.",
)
```

Two wins: (1) every value has a default + a type, so a typo'd env var fails loud; (2) tests pass `Settings(model_name="gemini-2.5-pro")` directly — no env-var monkey-patching.

## Multi-env separation — `.env.dev` / `.env.prod` / `.env.local`

```
my_agent/
├── .env                ← ignored by git; what dev actually runs against
├── .env.example        ← committed; placeholders only
├── .env.dev            ← committed; non-secret dev defaults (model, location)
├── .env.prod           ← committed; non-secret prod defaults
└── config.py
```

`pydantic-settings` reads **one** `env_file` at a time. Pick which to load with an envvar of envvars:

```python
import os
env = os.environ.get("APP_ENV", "dev")
settings = Settings(_env_file=f".env.{env}")
```

Secrets are never in any of these files in prod — the platform injects them: **Cloud Run** binds Secret Manager → env var at deploy ([[22_DeploymentModels/08_SecretsAcrossPlatforms]]); **Agent Engine** reads Secret Manager in `set_up()` ([[Detours/Cloud_Run]] for the dev parity story).

## Config flows

```
   .env / platform env
          │
          ▼
   ┌─────────────────┐
   │ Settings(pyd.)  │   ← single source of truth, validated at import
   └────────┬────────┘
            │ settings.model_name, settings.project_id, ...
            ▼
   ┌─────────────────┐
   │ LlmAgent / App  │   ← no os.environ[...] reads past this line
   └─────────────────┘
```

Validation at `App.on_startup` ([[1A_AppAndRunner/02_OnStartupShutdown]]) is the catch — fail loud before the first request, not on request #47.

## Anti-patterns

- **Hardcoded model strings** — `model="gemini-2.5-flash"` scattered across 6 files. One promotion to Pro now takes 6 PRs.
- **`os.environ["GOOGLE_API_KEY"]` reads in agents, tools, callbacks** — three of them mis-spell it, two have no fallback, one logs the value on error.
- **Secrets in `.env` checked into git** — and then "rewriting history" on Friday afternoon. Use `.env.example` (placeholders, committed) + `.env` (real, gitignored). See `[00_Setup/05_InProduction](../00_Setup/05_InProduction.md)`.
- **Reading env vars at module top-level inside a sub-agent file** — import-time side effect, breaks `pytest` collection (page 08).
- **One giant `Settings` class for a 6-agent monorepo** — split by package; each agent's `config.py` extends a `BaseConfig` from `shared/`.

> **🚀 In Production**
>
> Three rules. (1) **Bind, don't bake**: Cloud Run `--set-secrets` resolves Secret Manager → env at boot; values never sit in your image. (2) **Validate in `on_startup`**: instantiate `Settings()` there and assert the combinations you need (`if settings.use_vertex: assert settings.project_id`). Crashes the App, not request #1. (3) **Fail loud on missing config** — never silently default a production setting to a dev value. The pattern is `Field(...)` (required, no default) for prod-critical fields and a startup assertion that catches them. Model-routing nuance lives in [[17_AdvancedModels/10A_ModelSelectionPatterns]].

> 🛠 **Have the student run** the import-time validation:
>
> ```bash
> uv run python -c "from my_agent.config import Settings; Settings(use_vertex=True, project_id=None)"
> ```
>
> Expected: pydantic complains, exits non-zero. That's the point — same crash in CI catches it before deploy.

> ❓ **Ask the student:** "You have a `GOOGLE_API_KEY` in `.env`, but `GOOGLE_GENAI_USE_VERTEXAI=TRUE`. What wins, and is that what you want?"
>
> *(Expected: Vertex wins — ADK ignores the API key when Vertex is on. Almost never what you want in dev. The settings class should warn or hard-fail on the combination.)*

---

[← Prev: 07_SharedUtilities](07_SharedUtilities.md)  [↑ Map](../../MAP.md)  [Next: 08_EvalAndTestsLayout →](08_EvalAndTestsLayout.md)
