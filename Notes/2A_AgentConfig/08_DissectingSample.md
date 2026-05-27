---
module: 2A_AgentConfig
page: 08_DissectingSample
title: Dissecting `multi_agent_basic_config`
estimated_minutes: 25
prereqs: [2A_AgentConfig/07]
concepts: [sample-walkthrough, three-yaml-tree, delegation]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 07_PythonOnlyFeatures](07_PythonOnlyFeatures.md)  [↑ Map](../../MAP.md)  [Next: 09_InProduction →](09_InProduction.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 08 Dissecting `multi_agent_basic_config`

# 🛠 Dissecting `multi_agent_basic_config`

The canonical "YAML multi-agent" sample from `adk-python/contributing/samples/multi_agent/multi_agent_basic_config/`. Three YAML files, no Python at all, full delegation tree. Every concept from pages 02–05 in one runnable artifact.

## 🛠 The directory at a glance

```
multi_agent_basic_config/
├── README.md
├── root_agent.yaml         # learning assistant — routes to one of the two tutors
├── code_tutor_agent.yaml   # leaf — programming help
└── math_tutor_agent.yaml   # leaf — math help
```

Nothing else. No `tools.py`, no `main.py`, no `__init__.py`. `adk run multi_agent_basic_config` discovers `root_agent.yaml` and constructs the tree.

## 🛠 `root_agent.yaml` — the router

```yaml
# multi_agent_basic_config/root_agent.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: Learning assistant that provides tutoring in code and math.
instruction: |
  You are a learning assistant that helps students with coding and math questions.

  You delegate coding questions to the code_tutor_agent and math questions to the math_tutor_agent.

  Follow these steps:
  1. If the user asks about programming or coding, delegate to the code_tutor_agent.
  2. If the user asks about math concepts or problems, delegate to the math_tutor_agent.
  3. Always provide clear explanations and encourage learning.
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

Notes line by line:

- **Schema comment** (line 1) — gives the IDE auto-complete and validates the file at save time. Always include.
- **`agent_class: LlmAgent`** (line 2) — explicit even though it is the default. Greppable, reviewer-friendly.
- **`model: gemini-2.5-flash`** (line 3) — set only on the root. The two tutors *inherit this* via `canonical_model` (see page 05). One place to upgrade the whole tree.
- **`description:`** (line 5) — short, action-oriented. **Will be used by no one** for the root (nothing routes to it) but kept for documentation. Sub-agents need a description to be routable, the root doesn't, but consistency is cheap.
- **`instruction:`** (lines 6–14) — the system prompt. Note three things:
  1. Names the sub-agents by their YAML `name:` (`code_tutor_agent`, `math_tutor_agent`) — these must match exactly.
  2. Gives the LLM a numbered procedure. The LLM is the router; the instruction is the routing logic.
  3. No Python `if/else` involved. The model picks the sub-agent. This is *LLM-driven delegation*, and it is the default ADK pattern.
- **`sub_agents:`** (lines 15–17) — two `config_path:` entries, resolved relative to `root_agent.yaml`'s directory.

## 🛠 `code_tutor_agent.yaml` — leaf 1

```yaml
# multi_agent_basic_config/code_tutor_agent.yaml
agent_class: LlmAgent
name: code_tutor_agent
description: Coding tutor that helps with programming concepts and questions.
instruction: |
  You are a helpful coding tutor that specializes in teaching programming concepts.

  Your role is to:
  1. Explain programming concepts clearly and simply
  2. Help debug code issues
  3. Provide code examples and best practices
  4. Guide students through problem-solving approaches
  5. Encourage good coding habits

  Always be patient, encouraging, and provide step-by-step explanations.
```

Three things to notice:

- **No `model:`** — inherits `gemini-2.5-flash` from the root via `canonical_model`. If you wanted a cheaper model for the leaf, you'd add `model: gemini-2.5-flash-lite` here.
- **`description:` is load-bearing.** The root agent's LLM reads each sub-agent's description to decide whether to delegate. If you change this to `description: foo`, delegation breaks — the root LLM no longer knows what this agent is for.
- **`instruction:` is the leaf's persona.** When the root delegates, this is the system prompt the leaf runs under.

`math_tutor_agent.yaml` is the same shape (description tailored to math, instruction tailored to math tutoring). Symmetric leaves are common — copy + tweak.

## 🛠 Loading and inspecting the tree

```python
# Work/2A_dissect.py — run with: uv run python Work/2A_dissect.py
from google.adk.agents import config_agent_utils

root = config_agent_utils.from_config(
    "adk-python/contributing/samples/multi_agent/multi_agent_basic_config/root_agent.yaml"
)

print("ROOT")
print(f"  name:        {root.name}")
print(f"  model:       {root.model}")
print(f"  description: {root.description}")
print(f"  sub_agents:  {len(root.sub_agents)}")
print()
for sub in root.sub_agents:
    print(f"SUB: {sub.name}")
    print(f"  model (inherited via canonical_model): {sub.canonical_model.model}")
    print(f"  parent: {sub.parent_agent.name}")
    print(f"  description: {sub.description[:60]}...")
    print()
```

```
$ uv run python Work/2A_dissect.py
ROOT
  name:        root_agent
  model:       gemini-2.5-flash
  description: Learning assistant that provides tutoring in code and math.
  sub_agents:  2

SUB: code_tutor_agent
  model (inherited via canonical_model): gemini-2.5-flash
  parent: root_agent
  description: Coding tutor that helps with programming concepts and qu...

SUB: math_tutor_agent
  model (inherited via canonical_model): gemini-2.5-flash
  parent: root_agent
  description: Math tutor that helps with mathematical concepts and pro...
```

Two confirmations from this output:

1. **`parent_agent` is set automatically.** `from_config()` wires the parent pointer when assembling the tree. This is what enables `canonical_model` to walk upward when a sub-agent omits `model:`.
2. **`canonical_model` returns the resolved model**, not the raw `model:` field. `sub.model` is `""` on the leaves (because their YAML omits `model:`); `sub.canonical_model.model` is `gemini-2.5-flash` (inherited from the parent).

## 🛠 Running it end-to-end

```bash
$ adk run adk-python/contributing/samples/multi_agent/multi_agent_basic_config
[user]: How do I write a for loop in Python?
[code_tutor_agent]: A for loop in Python iterates over items in a sequence...

[user]: What is the quadratic formula?
[math_tutor_agent]: The quadratic formula solves ax² + bx + c = 0...

[user]: ^D
```

The root receives the user message, decides which sub-agent to delegate to (based on the routing instruction), and the chosen sub-agent's reply comes back labelled with its own `name:`. The `[code_tutor_agent]` / `[math_tutor_agent]` prefix is `Event.author` — same machinery as the Python multi-agent form (Module 05 covers the delegation mechanism in depth).

## 🧠 What this sample doesn't show (and where to look)

| Missing | Covered in |
|---|---|
| Tools | [Module 2A § 04 Tool References](04_ToolReferences.md) |
| Callbacks | [Module 2A § 07 Python-Only Features](07_PythonOnlyFeatures.md) |
| `App(...)` wrapper / plugins | [Module 1A § 01 App vs Runner vs Agent](../1A_AppAndRunner/01_AppVsRunnerVsAgent.md) |
| `SequentialAgent` / `ParallelAgent` / `LoopAgent` (template workflows) | [Module 06 Graph Workflows](../06_GraphWorkflows/) |
| `adk web` UI for this sample | [Module 3A § 05 CLI Expectations](../3A_ProjectStructure/05_AdkCliExpectations.md) |

This sample is intentionally minimal — three files, no tools, no callbacks, no App. It is the *cleanest expression of the YAML multi-agent pattern*. Add complexity from here.

> ❓ **Ask the student:** "If you wanted to add a `get_weather` tool to `code_tutor_agent`, would you edit `code_tutor_agent.yaml` directly, or would you need to add a Python file too?"
> *(Expected: both. Add a `tools.py` next to the YAMLs defining `get_weather`, then add `tools: [{name: multi_agent_basic_config.tools.get_weather}]` to the YAML. The YAML can REFERENCE a tool; it cannot define one. Page 04 covers this in detail.)*

## 🚀 In Production

> **🚀 In Production**
>
> This sample's directory shape (sibling YAMLs in one folder) scales to about 5–7 sub-agents before becoming hard to navigate. Beyond that, group sub-agents into subdirectories (`code_tutors/`, `math_tutors/`) and reference them with `config_path: code_tutors/python_tutor.yaml`. The CI mitigation from page 05 (assert `len(root.sub_agents) == expected_count`) becomes essential at this scale — visual scanning of a 10-entry `sub_agents:` list misses single-line deletions.

> 🛠 **Have the student do:** clone the sample to `Work/2A_dissect/`, run `adk run Work/2A_dissect`, ask it one coding and one math question, then add a third sub-agent (`history_tutor_agent.yaml`) and re-run. The whole loop should take under five minutes — that is the YAML productivity story.

---

[← Prev: 07_PythonOnlyFeatures](07_PythonOnlyFeatures.md)  [↑ Map](../../MAP.md)  [Next: 09_InProduction →](09_InProduction.md)
