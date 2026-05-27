---
module: 2A_AgentConfig
page: 00_Overview
title: Agent Config (YAML) — declarative agent definitions
estimated_minutes: 10
prereqs: [1A_AppAndRunner/11]
concepts: [AgentConfig, root_agent.yaml, adk-create, declarative]
icon: 🗺
in_production: false
detours_suggested: []
---

[← Prev: 1A_AppAndRunner/11_MiniDrill](../1A_AppAndRunner/11_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyDeclarative →](01_WhyDeclarative.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 00 Overview

# 🗺 Module 2A — Agent Config (YAML)

ADK 2.0 introduced a **declarative YAML** format for defining agents — `root_agent.yaml`, sub-agent YAML files, and a JSON Schema (`AgentConfig.json`) that backs IDE auto-complete. You can build an entire agent app without writing a Python file for the agents themselves; only tools stay in Python.

This is **not** a replacement for the Python form. It is an alternative. The two compose: a YAML root agent can have a Python sub-agent, and vice-versa.

> 🤖 **Tutor:** the student has just written Python `LlmAgent(...)` for two modules in a row. This module is where they meet the YAML alternative — and learn when each shape is the right shape. The mental model is *not* "YAML is the new way"; the model is "YAML is the declarative shape for the parts of an agent that are declarative, Python stays where dynamism is needed."

## 🎯 Goals

By the end of this module you can:

- Read a `root_agent.yaml` end-to-end and predict the equivalent Python.
- Use `adk create my_agent` and choose the YAML template.
- Reference tools and sub-agents from YAML (`tools:`, `sub_agents:` blocks).
- Name three things YAML cannot today express (callbacks, dynamic routing, plugins).
- Decide *for one of your own projects* whether to start in YAML or in Python.

## 📋 Prereqs

- [Module 02 First Agent](../02_FirstAgent/) — you have written `LlmAgent(...)` in Python.
- [Module 1A App & Runner](../1A_AppAndRunner/) — you know that the App owns plugins / cross-cutting config, not the agent.

## ⏱ Estimated time

- **Total**: ~2 hours over 1 session.
- Per-page estimates in each page's frontmatter.

## 🧪 Sample anchor

This module dissects **`multi_agent_basic_config`** at `/home/carloscabral/study/adk-python/contributing/samples/multi_agent/multi_agent_basic_config/` in [08 Dissecting Sample](08_DissectingSample.md). Three YAML files (a root and two sub-agents) — the cleanest demo in the ADK source tree of a pure-YAML multi-agent app.

> 🤖 **Tutor:** the sample lives in `adk-python` (the framework repo), not `adk-samples`. That is deliberate — the contributing/samples tree is where ADK keeps its config-driven canon. Confirm the student has the framework repo cloned at `/home/carloscabral/study/adk-python/`.

## 🛣 Plan

1. **01 Why declarative** — when YAML beats Python, when it doesn't
2. **02 The `root_agent.yaml` anatomy** — every field, what it maps to
3. **03 `adk create`** — generating an agent from the template, with the `--type` flag
4. **04 Tool references** — `tools: [- name: dotted.path]` and other forms
5. **05 Sub-agent references** — `sub_agents: [- config_path: other.yaml]`
6. **06 YAML vs Python tradeoffs** — the honest comparison
7. **07 Python-only features** — what YAML cannot express today (callbacks, plugins, dynamic logic)
8. **08 Dissecting Sample — `multi_agent_basic_config`** — the three-YAML demo
9. **09 In Production** — versioning agents declaratively, the GitOps story
10. **10 Knowledge Check** — 5–7 questions
11. **11 Mini-Drill** — convert your Module 02 agent to YAML

After this module: → [Module 3A Project Structure](../3A_ProjectStructure/) (where does `root_agent.yaml` live in a real project layout?), or jump to [Module 03 Tools](../03_Tools/) if you want to add tools to your YAML agent.

---

[← Prev: 1A_AppAndRunner/11_MiniDrill](../1A_AppAndRunner/11_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyDeclarative →](01_WhyDeclarative.md)
