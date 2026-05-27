---
module: 2A_AgentConfig
page: 02_RootAgentYaml
title: Anatomy of `root_agent.yaml`
estimated_minutes: 20
prereqs: [2A_AgentConfig/01]
concepts: [root_agent.yaml, agent_class, instruction, model, schema]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 01_WhyDeclarative](01_WhyDeclarative.md)  [↑ Map](../../MAP.md)  [Next: 03_AdkCreateCli →](03_AdkCreateCli.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 02 Anatomy of `root_agent.yaml`

# 🧠 Anatomy of `root_agent.yaml`

A canonical `root_agent.yaml`, every field annotated. The YAML on the left maps 1:1 to a Python kwarg you have already seen.

```yaml
# Work/2A_anatomy.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json

agent_class: LlmAgent              # ←┬─ which BaseAgent subclass to instantiate.
                                   #  │  Default is LlmAgent if omitted. The full set
                                   #  │  recognised by the discriminator (see
                                   #  │  agent_config.py:_ADK_AGENT_CLASSES) is:
                                   #  │  LlmAgent, SequentialAgent, ParallelAgent,
                                   #  │  LoopAgent. Anything else falls through to
                                   #  │  BaseAgent. Graph workflows (`Workflow`)
                                   #  │  are NOT YAML-loadable — they live in Python.

name: root_agent                   # ── agent name (Event.author label).

model: gemini-2.5-flash            # ── model string. Same shape as Python's `model=`.

description: |                     # ── used by OTHER agents to decide whether to
  Coordinates routing of student      delegate. Optional for a leaf agent; required
  questions to specialist sub-agents. for sub-agents (otherwise the parent can't pick).

instruction: |                     # ── the system prompt. Multi-line via YAML `|`.
  You are a learning assistant.       Static string only. For dynamic instructions
  Route programming questions to       (state interpolation, callables), use Python.
  code_tutor_agent and math
  questions to math_tutor_agent.

sub_agents:                        # ── list of sub-agents, each by config path.
  - config_path: code_tutor.yaml   #    Paths are relative to THIS yaml's directory.
  - config_path: math_tutor.yaml   #    Sub-agent YAML omits agent_class default to LlmAgent.

tools:                             # ── list of tool references by dotted import path.
  - name: my_pkg.my_tool           #    ADK loads the symbol via importlib. The tool
                                   #    function itself MUST be in Python — YAML only
                                   #    *references* it.

generate_content_config:           # ── per-agent Gemini config (safety, response schema).
  safety_settings:                 #    Maps to `genai.types.GenerateContentConfig`.
    - category: HARM_CATEGORY_DANGEROUS_CONTENT
      threshold: 'OFF'

# global_instruction:              # ── NOT a YAML field. LlmAgentConfig is
#                                   #    extra='forbid', so writing this key raises
#                                   #    a validation error at load time. The
#                                   #    behavior exists only as Python's
#                                   #    LlmAgent(global_instruction=...) kwarg
#                                   #    (deprecated). For new code, use the App-
#                                   #    level GlobalInstructionPlugin instead.

output_key: last_reply             # ── if set, the agent's reply is also written to
                                   #    state[output_key] via an Event delta.
                                   #    Maps 1:1 to Python's `output_key=`.

# planner: ...                    # ── (optional) planner config for thinking-mode
                                   #    agents. See Module 17 Advanced Models.
```

That is the **entire shape of an LlmAgent in YAML today**. Every field above has a 1:1 Python equivalent.

> ⚠️ **Workflow graphs are not YAML-loadable.** `WorkflowAgent` is not a valid `agent_class:`. The 2.0 discriminator (`agent_config.py:_ADK_AGENT_CLASSES`) only accepts `LlmAgent`, `LoopAgent`, `ParallelAgent`, `SequentialAgent`. Graph workflows live in Python via `from google.adk.workflow import Workflow` — see [Module 06 Graph Workflows](../06_GraphWorkflows/).

## 🧠 Quick crib — YAML → Python kwarg map

| YAML field | Python `LlmAgent(...)` kwarg | Notes |
|---|---|---|
| `agent_class:` | (the class itself) | Picks which `BaseAgent` subclass to construct. |
| `name:` | `name=` | |
| `model:` | `model=` | String only. For `Gemini(retry_options=...)` or `LiteLlm(...)`, use Python. |
| `description:` | `description=` | |
| `instruction:` | `instruction=` | Static string only. |
| `sub_agents:` | `sub_agents=` | Each entry is `{config_path: ...}`. Loaded recursively. |
| `tools:` | `tools=` | Each entry is `{name: dotted.path}` — see page 04. |
| `generate_content_config:` | `generate_content_config=` | Maps to `genai.types.GenerateContentConfig`. |
| `output_key:` | `output_key=` | |
| `planner:` | `planner=` | See Module 17. |

If a field exists in Python but not in this table, **YAML does not support it today** — that is page 07's whole story.

## 🧠 The schema line is load-bearing

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
```

This comment is read by:

- **VS Code with the YAML extension** — gives you auto-complete on every field, validates types, surfaces hover docs.
- **`yamllint` with the schema plugin** — catches misspellings in CI.
- **`adk` itself when loading** — validates the YAML against the same schema at load time (raises with a clear error pointing at the offending field).

**Always include the schema line.** It is one line of comment that turns a stringly-typed YAML file into a typed, autocompleted contract. Every official ADK YAML sample has it.

## 🛠 Load the YAML into Python and confirm

```python
# Work/2A_load_yaml.py — run with: uv run python Work/2A_load_yaml.py
from google.adk.agents import config_agent_utils

# ADK's config loader resolves the YAML into a live BaseAgent.
agent = config_agent_utils.from_config("Work/2A_anatomy.yaml")

print("type:", type(agent).__name__)
print("name:", agent.name)
print("model:", agent.model)
print("description:", agent.description[:60], "...")
print("sub_agents:", [s.name for s in agent.sub_agents])
print("tools:", [t.__class__.__name__ for t in agent.tools])
```

```
$ uv run python Work/2A_load_yaml.py
type: LlmAgent
name: root_agent
model: gemini-2.5-flash
description: Coordinates routing of student questions to specialist...
sub_agents: ['code_tutor_agent', 'math_tutor_agent']
tools: ['FunctionTool']
```

The YAML produced a real, fully-equivalent `LlmAgent` instance. After `from_config`, the object is indistinguishable from one you typed by hand.

> ❓ **Ask the student:** "If I load `root_agent.yaml` and then mutate `agent.instruction = '...new prompt...'` in Python, does the YAML file get rewritten?"
> *(Expected: no. `from_config` is a one-way load. The Python object is a fresh `LlmAgent` instance; subsequent mutations live in-memory only. YAML is the **source**, Python is the **runtime form** — they do not round-trip back automatically.)*

## 🚀 In Production

> **🚀 In Production**
>
> Pin the schema URL to a specific tag, not `refs/heads/main`. The `main` branch can update the schema mid-quarter; pinning to a tag (`refs/tags/v2.0.0`) means your CI validation doesn't suddenly fail because someone added a required field. Same rule as pinning a model version: `gemini-2.5-flash-001` over `gemini-2.5-flash`. Boring infrastructure choices pay off.

> 🛠 **Have the student do:** open the file `Work/2A_anatomy.yaml` in VS Code and confirm they see auto-complete when they type a new field at the top level. If they do not, the YAML extension is not installed or the schema line is missing.

---

[← Prev: 01_WhyDeclarative](01_WhyDeclarative.md)  [↑ Map](../../MAP.md)  [Next: 03_AdkCreateCli →](03_AdkCreateCli.md)
