---
module: 3A_ProjectStructure
page: 10_InProduction
title: In Production — Project Structure hardening checklist
estimated_minutes: 18
prereqs: [3A_ProjectStructure/09]
concepts: [version-pinning, dep-boundaries, monorepo, blast-radius]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 11_KnowledgeCheck →](11_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 10 In Production

# 🚀 In Production — Project Structure

> 🤖 **Tutor:** consolidates the inline `🚀 In Production` callouts from pages 02–09 into a single pre-ship checklist. Walk the student through it against their *own* project, not against a hypothetical one. If they don't have a project yet, walk it against the mini-drill output.

This page is the **checklist** you walk before shipping anything built on this module's primitives. Each item names a risk, a mitigation, and a backlink to the page where it was first introduced.

---

## Checklist

> ❓ **Ask the student:** "Open your most recent `Work/` project (or the mini-drill output). We are going to walk this checklist against it, item by item."

### 1. Picked the smallest layout that still works

- **Risk**: over-structured early; every change touches 4 files; new contributors lost in the tree.
- **Mitigation**: name a concrete pressure ([01](01_WhyStructureMatters.md)) for each directory in your project. If you can't, that directory is premature.
- **Inline source**: [01_WhyStructureMatters § Three pressures](01_WhyStructureMatters.md#the-three-pressures), [02_MinimalLayout](02_MinimalLayout.md).

### 2. `root_agent` (or `app`) is at module top, named exactly

- **Risk**: `adk web` shows your agent but it never responds; the CLI loaded the package but found no agent.
- **Mitigation**: `root_agent = LlmAgent(...)` or `app = App(...)` is the **only** way ADK finds your agent. Use one or both — never neither.
- **Inline source**: [05_AdkCliExpectations § Rule 3](05_AdkCliExpectations.md).

### 3. `__init__.py` imports `agent`

- **Risk**: agent appears in `adk web`'s dropdown but loading errors silently or `root_agent` is `None`.
- **Mitigation**: `from . import agent` (or `from .agent import app`) in every agent package's `__init__.py`. Never empty.
- **Inline source**: [02_MinimalLayout § the import line](02_MinimalLayout.md#my_agent__init__py-the-import-line-that-matters), [05_AdkCliExpectations § Rule 2](05_AdkCliExpectations.md).

### 4. Use `App` (not bare `root_agent`) once you're past prototype

- **Risk**: when you need lifecycle hooks, `app:` state, resumability, or context caching, you have to rewrite the wiring.
- **Mitigation**: `app = App(name=..., root_agent=root_agent)` is one line and future-proofs you.
- **Inline source**: [05_AdkCliExpectations § App vs root_agent](05_AdkCliExpectations.md#the-app-vs-root_agent-choice). Full coverage in [Module 1A](../1A_AppAndRunner/).

### 5. `pyproject.toml` declares the package explicitly

- **Risk**: wheel builds successfully but ships empty; Agent Engine deploys a no-op.
- **Mitigation**: `[tool.hatch.build.targets.wheel] packages = ["my_agent"]`. Test once locally with `uv build` and inspect the wheel.
- **Inline source**: [06_DeploymentExpectations § what both paths require](06_DeploymentExpectations.md#what-both-paths-require).

### 6. Pin a lower bound on `google-adk`, not an upper bound

- **Risk** (lower-pin): you accidentally run on a version that doesn't support the feature you're using.
- **Risk** (upper-pin): you miss security fixes; you have to ship a release every time ADK ships a minor.
- **Mitigation**: `"google-adk>=1.31.0"` — no upper bound unless you have a specific incompatibility. Pin Python (`requires-python = ">=3.11"`) for reproducibility instead.
- **Inline source**: [06_DeploymentExpectations § pyproject](06_DeploymentExpectations.md#pyprojecttoml-at-the-project-root-one-level-above-the-agent-package).

### 7. `extra_packages=["./my_agent"]` for Agent Engine

- **Risk**: classic Agent Engine deploy failure — `extra_packages=["./"]` ships the whole repo (huge), `extra_packages=["./agent.py"]` ships nothing useful.
- **Mitigation**: point at the **package directory** (the one with `__init__.py`), not a file, not the project root.
- **Inline source**: [06_DeploymentExpectations § Agent Engine shape](06_DeploymentExpectations.md#agent-engine-shape).

### 8. `eval/` and `tests/` are separate top-level dirs

- **Risk**: CI runs unit tests but never runs the evals; quality regressions ship.
- **Mitigation**: `testpaths = ["tests", "eval"]` in `pyproject.toml`; `eval/data/` for `.evalset.json`. Don't merge them under `tests/data/`.
- **Inline source**: [08_EvalAndTestsLayout](08_EvalAndTestsLayout.md). Full coverage in [Module 14](../14_Evaluation/).

### 9. `shared/` exists only when ≥2 callers exist

- **Risk**: premature shared module: half your tools live one level too deep, refactors are constant.
- **Mitigation**: extract to `shared/` **only** when a second caller appears. Until then, the helper lives next to its single caller.
- **Inline source**: [07_SharedUtilities § what does not belong](07_SharedUtilities.md#what-does-not-belong-in-shared).

### 10. Monorepo of agents only when 3+ agents in prod

- **Risk**: monorepo overhead — shared CI, version locking, cross-deps — before the cross-deps even exist.
- **Mitigation**: every agent is its own repo with its own `pyproject.toml` until you have at least three deployed and at least one piece of code two of them share. Then promote `shared/` to its own installable package.
- **Inline source**: [07_SharedUtilities § monorepo of agents](07_SharedUtilities.md#across-agents-the-monorepo-of-agents).

### 11. Don't commit `.env`; do commit `uv.lock`

- **Risk** (.env): credentials in git history.
- **Risk** (no lockfile): "works on my laptop" in container.
- **Mitigation**: `.gitignore` includes `.env`; `uv.lock` is checked in; the Dockerfile uses `uv sync --frozen`.
- **Inline source**: [06_DeploymentExpectations § The shape that works for both](06_DeploymentExpectations.md#the-shape-that-works-for-both).

### 12. Diff hygiene: prompts in their own file, wiring in another

- **Risk**: every prompt tweak risks breaking tool registration; PR review is opaque.
- **Mitigation**: `prompts.py` (or `prompts/`) separates prose from code. A diff that touches only `prompts.py` is a safer rollout than one that touches `agent.py`.
- **Inline source**: [01_WhyStructureMatters § Blast radius](01_WhyStructureMatters.md#blast-radius), [03_SmallLayout](03_SmallLayout.md).

---

## Cross-references

- The cross-cutting production module: [16 Production & Security](../16_ProductionSecurity/) — synthesizes every module's checklist.
- The deployment models: [22 Deployment Models](../22_DeploymentModels/) — picks Cloud Run vs Agent Engine vs GKE.
- The `App` / runtime: [1A App & Runner Architecture](../1A_AppAndRunner/) — when `root_agent` upgrades to `app`.
- The eval discipline: [14 Evaluation](../14_Evaluation/) — what goes in `eval/data/`.

> 🚀 **In Production** — composite reminder
>
> If you cannot point at a concrete pressure for every directory in your project, the layout is over-engineered. Delete unused directories before they accumulate `__init__.py` files. The shape of a working agent is **as small as it can be**, not as elaborate as the framework allows.

---

[← Prev: 09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 11_KnowledgeCheck →](11_KnowledgeCheck.yml)
