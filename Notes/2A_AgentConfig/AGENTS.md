# 🤖 AGENTS.md — Module 2A Agent Config (YAML) (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening the first concept page in this module. It captures module-specific pacing notes that do not fit in page frontmatter.

## What the student should walk away knowing

- Read, write, and load a `root_agent.yaml` — every field, what it maps to in Python, what the schema comment buys them.
- Decide between YAML-driven, Python-driven, and hybrid forms based on team composition and required behaviors (callbacks / dynamic instructions / custom subclasses).
- Compose multi-agent trees from YAML using `sub_agents: [{config_path: ...}]` and understand that `from_config()` resolves paths relative to the parent YAML's directory.
- Reference tools from YAML via dotted import path and know that the tool function (with docstring and type hints) is still Python.
- Recognize the four categories YAML cannot express (callbacks, dynamic instructions, plugins on `App`, custom `BaseAgent` subclasses) and the hybrid pattern that handles each.

## Pacing

- **Easy if**: the student has done Modules 02, 05, and 1A already, AND has written YAML for k8s/Argo/Helm before. → cruise; compress pages 01, 02, 03 (they will see the shape immediately) and spend the time on the dissection and the python-only-features page.
- **Hard if**: the student is fuzzy on Python's `importlib` / `PYTHONPATH` / packaging. → suggest detour [[PY_packaging]] before page 04; otherwise the tool reference page will land on sand and the mini-drill will fail with `ModuleNotFoundError`.
- Expected total time for an on-pace student: ~3 hours (sum of `estimated_minutes` in the page frontmatters).

## Watch for these mistakes

- **Trying to inline a callback into the YAML.** The student writes `before_model_callback: my_pkg.my_callback` and expects it to resolve. Symptom: schema validation error or silent ignore. Fix: callbacks attach in Python after `from_config(...)` — see page 07.
- **Forgetting the dotted import path for `tools:`.** Student writes `name: get_weather` (bare name) instead of `name: my_pkg.tools.get_weather`. Symptom: `ModuleNotFoundError`. Fix: full Python import path from the project root.
- **Naming the file something other than `root_agent.yaml`.** Symptom: `adk run my_agent` fails to discover the YAML. Fix: the discovery is hard-coded to `root_agent.yaml`. See Module 3A.
- **Pinning the schema URL to `refs/heads/main`** (or omitting the schema comment entirely). Symptom: CI suddenly fails when ADK upstream changes the schema. Fix: pin to a tag.
- **Mutating the loaded agent extensively** (5+ fields) and treating the YAML as the source of truth. The YAML is no longer authoritative; this is the "YAML drift" smell. Fix: rewrite in Python (page 06 decision tree).

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "I don't get why `my_pkg.tools.get_weather` works but `tools.get_weather` doesn't." | [[PY_packaging]] — covers Python's module-resolution rules in 20 min. |
| "Why does adding `# yaml-language-server:` make my IDE magically know the fields?" | (No formal detour — point at the JSON Schema spec briefly; this is YAML-tooling literacy, not ADK-specific.) |
| "I want to express conditional sub-agent loading in YAML." | (No detour — push back. Page 06 covers why this is the YAML-as-DSL trap. Move to Python.) |

If the same detour is suggested and declined twice (check `student_profile.md`), stop offering it.

## Mini-drill grading

- **Clean pass** = all three files (`root_agent.yaml`, `tools.py`, `main.py`) present, script runs without exception, output mentions Tokyo, `main.py` uses `from_config()` (not `LlmAgent(...)`), `App(...)` wraps the loaded agent.
- **Pass with hint** = works but used legacy Runner construction (`Runner(app_name=..., agent=...)`) or skipped the `App` wrapper. Point at page 02 of 1A; have student rewrite the wiring.
- **Fail** = `ModuleNotFoundError` on the tool reference (dotted path wrong) OR the agent loads but never calls the tool (missing docstring/type hint). Re-drill: fix the import path, add docstrings, re-run.

### Edge case to probe (after the basic drill passes)

- Ask the student to change `model:` in `root_agent.yaml` from `gemini-2.5-flash` to `gemini-2.5-flash-lite` without touching any Python and re-run. The change should take effect immediately. Then ask: "What if you wanted *different* models for the root and a sub-agent?" — they should know to set `model:` on the sub-agent YAML (page 05).

## Cross-module hooks

- This module is referenced from: Module 3A (project structure handles YAML discovery in `adk run`/`adk web`), Module 08 (MCP toolsets — the toolset YAML form), Module 13 (plugins are still Python-only as of 2.0 GA, mentioned on page 07), Module 16 (secrets/`.env` handling for `adk create` output).
- This module references: Module 02 (the Python `LlmAgent` form the student already knows), Module 03 (tool definitions in Python — YAML only references them), Module 05 (multi-agent delegation mechanism), Module 1A (`App(...)` wraps the loaded agent), Module 17 (planner config is partially YAML-expressible).
- If the student forgets a prerequisite concept, the tutor should NOT re-teach it inline — back up to the prereq page briefly, then return.

## Known divergences from the upstream sources (as of 2.0 GA, 2026-05-27)

- The course taught `EventsCompactionConfig` field name as `events_compaction_config` (correct per `adk-python/src/google/adk/apps/app.py`). The original brief used `context_compaction_config`; the page title still says "Context Compaction" for student clarity, but the YAML/Python field is `events_compaction_config`.
- `ResumabilityConfig` is publicly re-exported at `google.adk.apps` (lazy-loaded via `apps/__init__.py:21,26`); use `from google.adk.apps import ResumabilityConfig`. `EventsCompactionConfig` is NOT in `__all__` — must still come from `google.adk.apps._configs`. If a future release lifts `EventsCompactionConfig` into the public surface, update the compaction-related pages.
- `App` does not expose `on_startup` / `on_shutdown` kwargs. The brief assumed it did. Module 1A page 02 teaches the three real lifecycle patterns (bare asyncio, FastAPI lifespan, `adk api_server`) instead.
