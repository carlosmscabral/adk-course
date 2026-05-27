---
module: 2A_AgentConfig
page: 09_InProduction
title: In Production — YAML agent checklist
estimated_minutes: 15
prereqs: [2A_AgentConfig/08]
concepts: [production, checklist, ci, schema-pinning]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 08_DissectingSample](08_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_KnowledgeCheck →](10_KnowledgeCheck.yml)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 09 In Production

# 🚀 In Production — YAML agent checklist

A consolidated checklist for shipping a YAML-driven ADK agent. Each item links back to the page where the rationale lives.

## ✅ Schema & validation

- [ ] **Every YAML has the schema comment** (`# yaml-language-server: $schema=...`). Page 02. No schema comment = no auto-complete = silent typos in prod.
- [ ] **Schema URL pinned to a tag, not `refs/heads/main`.** Page 02. Pin to `refs/tags/v2.0.0` (or whatever your ADK version uses) so a schema change upstream doesn't break your CI.
- [ ] **CI step: load every YAML with `config_agent_utils.from_config()` and assert it succeeds.** Catches typos in `agent_class:`, `tools[].name:`, `sub_agents[].config_path:`.

## ✅ Tool references

- [ ] **Every `tools: [{name: ...}]` reference resolves with `importlib`.** Page 04. Add a 20-line pytest that walks every YAML, parses tool refs, and `importlib.import_module` each one.
- [ ] **Tool functions have docstrings AND type hints.** Page 04. The LLM only sees the function via its inferred schema — YAML cannot override this.
- [ ] **The agent's Python package is installed in the deployment environment** (`uv pip install -e .` or built into the Docker image). Page 04. Local works ≠ container works.

## ✅ Sub-agent tree

- [ ] **`config_path:` is relative to the parent YAML's directory.** Page 05. If you refactor folders, run `from_config` to verify.
- [ ] **CI assertion: `len(root.sub_agents) == EXPECTED_COUNT`.** Page 05. Catches "I deleted a `- config_path:` line by accident in a merge."
- [ ] **Each sub-agent has a `description:`.** Page 05/08. The root LLM uses descriptions to decide delegation — empty or vague descriptions = broken routing.

## ✅ Model strategy

- [ ] **Decide explicit-per-agent vs inherited.** Page 05. Both are valid; pick one and be consistent. Greppable explicit models are easier for cost reviews; inherited is fewer characters.
- [ ] **Pin model versions** (`gemini-2.5-flash-001` over `gemini-2.5-flash`). Same boring-infrastructure rule as schema pinning.

## ✅ Secrets & env

- [ ] **`.env` is in `.gitignore` BEFORE the first `adk create`.** Page 03. The CLI warns; the warning is easy to miss.
- [ ] **Production secrets come from a secret manager, not `.env`.** Page 03. See [Module 16 Production & Security](../16_ProductionSecurity/).

## ✅ The Python seam

- [ ] **`App(...)` construction lives in a single file (typically `main.py`).** Page 07. Plugins, App-level config, and runtime behaviors attach here.
- [ ] **Callback attachment is wrapped in a named function** (`attach_runtime_behaviors(agent)`). Page 07. Greppable, testable, hard to silently skip.
- [ ] **Dynamic instructions either live in Python or are explicitly absent.** Page 07. No jinja templating in YAML strings — that path leads to YAML-as-DSL pain.

## ✅ Discoverability

- [ ] **The root YAML is named `root_agent.yaml`** (exactly, not `main_agent.yaml` etc.). Page 03/08. `adk run <dir>` discovery is hard-coded to this name.
- [ ] **The agent folder contains `__init__.py`** (even empty). Module 3A. Makes it importable when other code references it.

## ✅ When to escape to Python

- [ ] **If the YAML is growing custom DSL conventions** (jinja, `{{ }}` placeholders, conditional includes), stop and rewrite as Python. Page 06.
- [ ] **If you're loading the YAML in Python and then mutating ≥5 fields**, the YAML is no longer the source of truth. Move to Python. Page 07.
- [ ] **If non-Python collaborators have stopped reviewing the YAML changes**, the diffability win is gone. Reconsider. Page 06.

## 🚀 The one-paragraph summary

YAML-driven ADK works when you respect the seam: **YAML for shape, Python for behavior**. The production failure modes all come from blurring the seam — encoding logic in YAML, forgetting to attach callbacks after load, drifting away from the schema. Keep the YAML small. Keep the Python wrapper short and named. Run CI on the YAML load. Pin schema and model versions. That is the whole production story for YAML agents.

> 🛠 **Have the student do:** take any YAML agent they have on disk and run through this checklist top to bottom. The first time, expect 3–4 misses. That is the value of the checklist — making the misses visible before prod does.

---

[← Prev: 08_DissectingSample](08_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_KnowledgeCheck →](10_KnowledgeCheck.yml)
