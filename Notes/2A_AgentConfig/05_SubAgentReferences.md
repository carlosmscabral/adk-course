---
module: 2A_AgentConfig
page: 05_SubAgentReferences
title: Composing sub-agents in YAML
estimated_minutes: 20
prereqs: [2A_AgentConfig/04]
concepts: [sub_agents, config_path, composition, multi-agent]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_ToolReferences](04_ToolReferences.md)  [↑ Map](../../MAP.md)  [Next: 06_YamlVsPythonTradeoffs →](06_YamlVsPythonTradeoffs.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 05 Sub-Agent References

# 🛠 Composing sub-agents in YAML

A YAML root agent can have YAML sub-agents. Each one is a separate file, referenced by `config_path:` from the parent.

## 🛠 Two YAML sub-agents

```yaml
# Work/2A_multi/code_tutor.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
name: code_tutor_agent
description: Coding tutor that helps with programming concepts and questions.
instruction: |
  You are a helpful coding tutor that specializes in teaching programming.
  Explain concepts clearly, debug code, and provide examples.
```

```yaml
# Work/2A_multi/math_tutor.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
name: math_tutor_agent
description: Math tutor that helps with mathematical concepts and problems.
instruction: |
  You are a helpful math tutor. Explain mathematical concepts clearly,
  walk through problems step by step, and encourage problem-solving.
```

The root composes them:

```yaml
# Work/2A_multi/root_agent.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: Learning assistant that provides tutoring in code and math.
instruction: |
  You are a learning assistant. You delegate coding questions to the
  code_tutor_agent and math questions to the math_tutor_agent.

  Follow these steps:
  1. If the user asks about programming, delegate to code_tutor_agent.
  2. If the user asks about math, delegate to math_tutor_agent.
  3. Always provide clear explanations and encourage learning.
sub_agents:
  - config_path: code_tutor.yaml
  - config_path: math_tutor.yaml
```

Three YAML files. One conceptual agent tree.

## 🧠 How `config_path:` resolves

```
Work/2A_multi/
├── root_agent.yaml       # references "code_tutor.yaml", "math_tutor.yaml"
├── code_tutor.yaml
└── math_tutor.yaml
```

`config_path:` is **relative to the YAML file that contains it**, not to the project root. If your sub-agents live in a subdirectory:

```
Work/2A_multi/
├── root_agent.yaml       # references "sub_agents/code_tutor.yaml"
└── sub_agents/
    ├── code_tutor.yaml
    └── math_tutor.yaml
```

Then:

```yaml
sub_agents:
  - config_path: sub_agents/code_tutor.yaml
  - config_path: sub_agents/math_tutor.yaml
```

The loader resolves each path against the parent YAML's directory, calls `from_config(...)` recursively, and assigns the resulting `LlmAgent` to the parent's `sub_agents` list.

## 🛠 Load the tree and confirm

```python
# Work/2A_multi/load_tree.py — run with: uv run python Work/2A_multi/load_tree.py
from google.adk.agents import config_agent_utils

root = config_agent_utils.from_config("Work/2A_multi/root_agent.yaml")
print("root.name:", root.name)
print("root.sub_agents count:", len(root.sub_agents))
for sub in root.sub_agents:
    print(f"  - {sub.name}: {sub.description[:50]}...")
```

```
$ uv run python Work/2A_multi/load_tree.py
root.name: root_agent
root.sub_agents count: 2
  - code_tutor_agent: Coding tutor that helps with programming conc...
  - math_tutor_agent: Math tutor that helps with mathematical concept...
```

The tree is fully reconstructed in memory. From here it behaves like a hand-built multi-agent app (Module 05).

## 🧠 Sub-agent `model:` inheritance

Notice the sub-agent YAMLs above do **not** set `model:`. They inherit from the root agent in the standard ADK way (the `LlmAgent.canonical_model` resolver walks up `parent_agent` if `self.model` is empty). If you want a sub-agent on a *different* model — say, a cheaper one for routing — set `model:` on the sub-agent YAML:

```yaml
# code_tutor.yaml
agent_class: LlmAgent
name: code_tutor_agent
model: gemini-2.5-flash-lite        # override — use the cheap model for this sub-agent
description: ...
instruction: ...
```

This is the same rule as Python (`LlmAgent(model=None)` inherits from parent), expressed declaratively.

## 🧠 Mixing YAML and Python sub-agents

The architectural answer is **yes**, and the practical mechanism today is: build the tree in Python, where you can interleave YAML-loaded and hand-built agents:

```python
# Work/2A_mixed_tree.py
from google.adk.agents import LlmAgent, config_agent_utils

# YAML sub-agent
math_tutor = config_agent_utils.from_config("Work/2A_multi/math_tutor.yaml")

# Python sub-agent with a callback (YAML can't express this)
code_tutor = LlmAgent(
    name="code_tutor_agent",
    model="gemini-2.5-flash",
    instruction="You are a coding tutor.",
    before_model_callback=lambda *args, **kwargs: None,   # callback here!
)

root = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="Delegate to the right tutor.",
    sub_agents=[math_tutor, code_tutor],
)
```

This is pattern 2 from page 01: YAML for declarative shape, Python for the parts that need to run code. The two compose cleanly because `from_config()` returns the same `LlmAgent` type the Python constructor returns.

> ❓ **Ask the student:** "If `root_agent.yaml` and `code_tutor.yaml` both set `agent_class: LlmAgent` and the same `model:`, what happens? Is one wrong?"
> *(Expected: neither is wrong; the sub-agent's explicit model wins for that sub-agent. The inheritance rule only kicks in when `model:` is OMITTED. Setting it on every sub-agent is verbose but explicit — fine for production where you want each agent's model to be greppable.)*

## 🚀 In Production

> **🚀 In Production**
>
> When the YAML tree grows past ~10 sub-agents, you start playing "find which YAML defines this name." Two mitigations: (1) Put each sub-agent in its own subdirectory under `sub_agents/`, even if the YAML itself is short — the directory structure becomes a navigable index. (2) Add a CI check that loads the root YAML and asserts `len(root.sub_agents) == expected_count`. Catches accidental delete-an-entry-from-the-list bugs that schema validation alone misses.

> 🛠 **Have the student do:** physically draw the agent tree from the three YAML files above on paper (root with two children). Confirm they can do this without looking at `root_agent.yaml` after one read-through. If they need to re-scan, the YAML compose pattern hasn't landed — re-read this page.

---

[← Prev: 04_ToolReferences](04_ToolReferences.md)  [↑ Map](../../MAP.md)  [Next: 06_YamlVsPythonTradeoffs →](06_YamlVsPythonTradeoffs.md)
