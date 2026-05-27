---
module: 2A_AgentConfig
page: 01_WhyDeclarative
title: Why declarative — when YAML beats Python
estimated_minutes: 15
prereqs: [2A_AgentConfig/00]
concepts: [declarative, imperative, gitops, prompt-iteration]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_RootAgentYaml →](02_RootAgentYaml.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 01 Why Declarative

# 🧠 Why declarative — when YAML beats Python (and when it doesn't)

You have written `LlmAgent(name=, model=, instruction=, tools=)` four times now. It works. So why does ADK 2.0 ship a YAML alternative?

## 🧠 The honest answer in one paragraph

YAML wins when the agent's **definition is the deliverable** — when prompt engineers, product managers, or a CI pipeline need to diff/review/version the agent without reading Python. Python wins when the agent's **behavior is the deliverable** — callbacks, dynamic routing, custom logic, anything that has to *run*. Most real agents have both: a YAML shape (prompt, model, tools by name) and Python escape hatches (callbacks, custom tools).

## 🛠 Side-by-side — same agent, two forms

```yaml
# Work/2A_greeter.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
name: greeter
model: gemini-2.5-flash
description: Greets the user briefly.
instruction: |
  Reply in exactly one short sentence. Be friendly.
```

```python
# Work/2A_greeter.py — Python equivalent
from google.adk.agents import LlmAgent

greeter = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    description="Greets the user briefly.",
    instruction="Reply in exactly one short sentence. Be friendly.",
)
```

Same agent. Same behavior at runtime. The YAML is 6 lines; the Python is 7. Length is not the point.

## 🧠 What you gain with YAML

| Win | Why it matters |
|---|---|
| **Diffable in PR review** | A prompt engineer can review a 4-line instruction change in a YAML without scrolling past Python boilerplate. |
| **No Python execution at load time** | Loading the agent is parse + validate. No `__init__.py` side effects. Safer in untrusted CI contexts. |
| **GitOps native** | Same shape as Kubernetes manifests. CD pipelines, Argo apps, version-pinning workflows already understand "diff the YAML, apply the change." |
| **Schema-backed auto-complete** | The `# yaml-language-server: $schema=...` line gives every modern IDE field-level auto-complete and validation. You cannot misspell `instruction` and have it silently ignored. |
| **Easy for non-Python tools to generate** | A "build me an agent" wizard, a no-code admin UI, an LLM that writes agent configs — all easier with YAML than with AST manipulation. |

## 🧠 What you lose with YAML

| Loss | Why it hurts |
|---|---|
| **No callbacks** | `before_model_callback`, `after_tool_callback`, etc. require Python functions. YAML can reference a tool *function* by import path; it cannot inline a callback. |
| **No dynamic instruction** | YAML `instruction: |` is a static string. The Python form accepts `instruction=callable` for state-aware prompts. |
| **No custom `BaseAgent` subclasses** | If your agent class is something other than `LlmAgent` / `SequentialAgent` / `ParallelAgent` / `LoopAgent` / `WorkflowAgent`, YAML cannot construct it. |
| **No plugin wiring** | Plugins live on the **App**, not the agent — and `App` is still constructed in Python today. YAML reaches the agent boundary, not the App boundary. |
| **Stringly-typed errors** | If you misspell a tool's import path in YAML, the error surfaces at load time as a string error, not a Python `NameError` your IDE caught two seconds after typing. |

## 🧠 The three real-world patterns

After watching enough teams adopt 2A, three usage patterns are dominant:

1. **All-YAML, simple agent.** A single `root_agent.yaml`, no sub-agents, tools are pre-shipped (built-ins or one Python `tools.py`). Best for: prototypes, internal demos, agents owned by a non-Python team.
2. **YAML root + Python escape hatches.** `root_agent.yaml` for shape; one Python file beside it that defines callbacks, custom tools, and the `App(...)` wrapper. Best for: most production agents.
3. **All-Python.** No YAML. Best for: agents whose behavior is dominantly callbacks / dynamic routing / custom `BaseAgent` subclasses, e.g. the `llm-auditor` sample with its critic/reviser loop.

> ❓ **Ask the student:** "Your team has a prompt engineer who reviews every instruction change and a Python engineer who writes the tools. Which pattern (1, 2, or 3) fits?"
> *(Expected: pattern 2. The prompt engineer reviews the YAML; the Python engineer owns the callbacks and tools. Clean separation along the YAML/Python seam.)*

## 🧠 The third option people forget

You can mix forms **at the sub-agent boundary**:

```yaml
# root_agent.yaml — YAML root
sub_agents:
  - config_path: math_tutor.yaml         # ← YAML sub-agent
  - python_module: my_pkg.code_critic    # ← Python sub-agent (hypothetical syntax)
```

The exact YAML syntax for referencing a Python sub-agent is still evolving in 2.0; check the live schema at `https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json` before relying on it. But the architectural option is real: you do not have to pick one shape for the whole tree.

## 🚀 In Production

> **🚀 In Production**
>
> The deciding question is **who edits this file most often?** If the answer is "a prompt engineer who does not read Python", default to YAML — the cost of a Python engineer translating their edits is real. If the answer is "the Python engineer who also writes the tools", default to Python — context-switching to YAML for the agent and back to Python for the tool slows iteration. Optimize for whoever does the most diffs.

> 🛠 **Have the student do:** open one of their existing Module 02 agents and ask out loud: "if I were handing this to a prompt engineer to iterate on, would YAML help?" The answer trains their intuition for future projects.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_RootAgentYaml →](02_RootAgentYaml.md)
