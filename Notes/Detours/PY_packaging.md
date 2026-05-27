---
module: Detours
page: PY_packaging
title: Packaging — pyproject.toml, uv, and shipping an agent
estimated_minutes: 30
icon: 🐍
prereqs: []
concepts: [pyproject, uv, poetry, entry_points, version_pinning]
---

[← Back to Map](../../MAP.md)

Triggered from: `99_Capstone` (ship your agent).

> Take this detour when "my agent works on my laptop" needs to become "anyone can `pip install` it and run it". ~30 min.

---

## 🐍 1. `pyproject.toml` — one file to rule them all

PEP 621 made `pyproject.toml` the single source of truth: metadata, deps, build config. The minimum viable:

```toml
[project]
name = "my-agent"
version = "0.1.0"
description = "A research-assistant ADK agent"
requires-python = ">=3.10"
dependencies = [
  "google-adk>=2.0,<3.0",
  "google-genai>=1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

`pip install .` in that directory builds and installs it. That's the floor; everything below is quality-of-life.

---

## 🐍 2. `uv` — the recommended tool in 2026

`uv` (by Astral) is a Rust-implemented pip/venv/lockfile manager, ~10-100x faster than pip. Workflow:

```bash
$ uv init my-agent              # scaffold pyproject.toml + .venv
$ cd my-agent
$ uv add google-adk             # adds to [project.dependencies], updates uv.lock
$ uv add --dev pytest           # dev-only dep
$ uv sync                       # install everything from lockfile
$ uv run python -m my_agent     # run inside the venv without activating
```

`uv.lock` is the lockfile — commit it. `uv sync` is reproducible across machines.

> ⚠️ **Recent syntax shift**: pre-2025 `uv` used `uv pip install` for everything. Modern `uv` prefers `uv add` / `uv sync` (project-aware). The `uv pip` subcommand still works for ad-hoc installs into a venv — but for project deps, use `uv add`.

---

## 🐍 3. `poetry` and `pip-tools` — the alternatives

**Poetry** (mature, opinionated):

```bash
$ poetry new my-agent
$ poetry add google-adk
$ poetry install
$ poetry run python -m my_agent
```

Poetry writes its own `[tool.poetry]` section instead of (older versions) or alongside (newer) `[project]`. Lockfile is `poetry.lock`.

**pip-tools** (minimal, just compile-and-sync):

```bash
$ pip-compile pyproject.toml -o requirements.txt   # produce pinned set
$ pip-sync requirements.txt                         # install exactly that
```

Use pip-tools if your team already has a pip-centric workflow and just wants reproducibility. Otherwise `uv` is the path of least friction.

---

## 🐍 4. Layout — package your agent so imports work

```
my-agent/
├── pyproject.toml
├── uv.lock
├── README.md
└── src/
    └── my_agent/
        ├── __init__.py
        ├── agent.py            # root_agent = LlmAgent(...)
        ├── tools.py
        └── cli.py              # main() entry point
```

`src/` layout (recommended) means imports only work after install — catches "works because of cwd" bugs early.

In `pyproject.toml`:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_agent"]
```

In `src/my_agent/__init__.py`, re-export the agent so `from my_agent import root_agent` works:

```python
from .agent import root_agent
__all__ = ["root_agent"]
```

That re-export is what ADK CLI (`adk run my_agent`) looks for.

---

## 🐍 5. Console-script entry points

Turn your CLI into a real shell command:

```toml
[project.scripts]
my-agent = "my_agent.cli:main"
```

After `uv sync` (or `pip install -e .`), the shell has a `my-agent` binary that calls `my_agent.cli.main()`. No `python -m my_agent` needed.

```python
# src/my_agent/cli.py
def main():
    import asyncio
    from .agent import root_agent
    # ... wire up runner, REPL, etc.
    asyncio.run(...)
```

---

## 🐍 6. Pin ADK and the Gemini SDK

Both ship breaking changes between minor versions. Pin to a compatible range:

```toml
dependencies = [
  "google-adk>=2.0,<3.0",        # 2.x compatible
  "google-genai>=1.0,<2.0",      # 1.x compatible
  "pydantic>=2.0,<3.0",
]
```

Then let `uv.lock` (or `poetry.lock`) pin the exact patch versions. The compatibility range is for humans reading `pyproject.toml`; the lockfile is for machines reproducing the env.

> ⚠️ **In Production**: never deploy from an unlocked env. "It worked last week" + a new minor release of a transitive dep = your incident. `uv sync --frozen` in CI enforces "use the lockfile, no surprises".

---

## 🛠 Have the student try

Write a `pyproject.toml` for the M1 todo agent so it installs cleanly. Minimal target:

```toml
[project]
name = "todo-agent"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "google-adk>=2.0,<3.0",
  "google-genai>=1.0,<2.0",
]

[project.scripts]
todo-agent = "todo_agent.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/todo_agent"]
```

Then:

```bash
$ uv sync
$ uv run todo-agent          # confirms the entry point fires
$ uv pip show todo-agent     # confirms metadata
```

If `uv run todo-agent` launches your REPL, you've shipped a real package.

---

Back to: `99_Capstone` (or whichever ship-it page triggered this).

[← Back to Map](../../MAP.md)
