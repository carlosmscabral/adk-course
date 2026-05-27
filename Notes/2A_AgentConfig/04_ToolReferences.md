---
module: 2A_AgentConfig
page: 04_ToolReferences
title: Referencing tools from YAML
estimated_minutes: 20
prereqs: [2A_AgentConfig/03]
concepts: [tools-yaml, dotted-path, FunctionTool, built-in-tools, importlib]
icon: 🛠
in_production: true
detours_suggested: [PY_packaging]
---

[← Prev: 03_AdkCreateCli](03_AdkCreateCli.md)  [↑ Map](../../MAP.md)  [Next: 05_SubAgentReferences →](05_SubAgentReferences.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 04 Tool References

# 🛠 Referencing tools from YAML

YAML cannot define a tool — it can only **reference** one. The tool itself is a Python function (Module 03). The YAML names the function by its **import path**.

## 🧠 The three reference forms

### Form 1 — dotted import path (most common)

```yaml
tools:
  - name: my_yaml_agent.tools.get_weather
  - name: my_yaml_agent.tools.get_current_time
```

ADK resolves each `name` via `importlib`:

```python
# Approximate internal behavior
import importlib
module_path, attr = "my_yaml_agent.tools.get_weather".rsplit(".", 1)
module = importlib.import_module(module_path)
fn = getattr(module, attr)
# fn is then wrapped: FunctionTool(func=fn)
```

The function must be importable from the running Python environment. That is the *only* constraint.

### Form 2 — built-in tools by name (no module prefix)

For tools that ADK ships, the canonical YAML form is the bare name — as shown by `contributing/samples/multi_agent/multi_agent_basic_config/`:

```yaml
tools:
  - name: google_search                           # built-in google search
  - name: load_memory                             # built-in memory loader
  - name: exit_loop                               # built-in loop exit
```

The full dotted path (`google.adk.tools.google_search`) also resolves — both forms work through the same `ToolConfig.name` field. The bare form is the sample-blessed style.

### Form 3 — toolset reference with constructor args

For tools that come from a toolset (MCP, Skills, AgentTool), the YAML form is **the same `ToolConfig` shape** — `name:` (dotted path to the toolset class) plus optional `args:`. There is **no special `toolset:` / `class:` discriminator key**.

```yaml
tools:
  - name: google.adk.tools.mcp_tool.McpToolset
    args:
      connection_params:
        url: http://localhost:8080/mcp
```

`ToolConfig` is intentionally minimal (two fields: `name`, `args`). YAML has to express *constructor kwargs* under `args:`. Use Python if this gets hairy — the line between "declarative" and "manually serializing Python" is exactly here. See [Module 08 MCP](../08_MCP/) for the in-depth coverage.

## 🛠 End-to-end — YAML agent + Python tools

Project layout:

```
my_yaml_agent/
├── __init__.py            # empty
├── .env
├── root_agent.yaml        # references the tools
└── tools.py               # defines the tools
```

```python
# my_yaml_agent/tools.py
def get_weather(city: str) -> str:
    """Return the current weather for a given city.

    Args:
        city: The city name to query weather for.

    Returns:
        A short human-readable weather description.
    """
    return f"It is 72°F and sunny in {city}."


def get_current_time(city: str) -> str:
    """Return the current local time in the given city."""
    return f"It is 14:30 in {city}."
```

```yaml
# my_yaml_agent/root_agent.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: weather_bot
model: gemini-2.5-flash
description: A small bot that answers weather and time questions.
instruction: |
  Answer the user's question. Use get_weather for weather questions,
  get_current_time for time-of-day questions, or both if relevant.
tools:
  - name: my_yaml_agent.tools.get_weather
  - name: my_yaml_agent.tools.get_current_time
```

Run it:

```bash
$ adk run my_yaml_agent
[user]: What's the weather in Seattle right now?
[weather_bot]: It is 72°F and sunny in Seattle.
```

The YAML declared *which* tools the agent has. The Python defined *what* the tools do. Clean seam.

## 🧠 Docstrings are still load-bearing

Even though the YAML references the function by name, **the LLM still relies on the function's docstring and type hints** as its schema for the tool. The YAML does not let you override the description. The single source of truth for "what does this tool do?" is still the Python docstring.

If you find yourself wanting to override a tool's description per-agent, that is a Python concern — Module 03 covers wrapping the function in a custom `FunctionTool(name=..., description=...)`.

> ❓ **Ask the student:** "In the YAML above, where does the LLM learn what `get_weather` is for? Where does it learn the parameter name `city`?"
> *(Expected: from the Python function's docstring (description) and type hints (parameter schema). The YAML's `name:` is just a reference to the function; it does not contribute schema info. This is why a YAML-driven project still has to write good Python docstrings — Module 03's pattern doesn't go away.)*

## 🛠 Common errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'my_yaml_agent'` | The agent folder is not on `PYTHONPATH`. | Run from the parent dir, or add the project to `pyproject.toml` and install with `uv pip install -e .`. |
| `AttributeError: module 'my_yaml_agent.tools' has no attribute 'get_weather'` | Typo in the dotted path. | Match the function name exactly. |
| Tool loads but LLM never calls it | Function lacks a docstring or type hints. | Add both. The LLM only sees the function via its inferred schema. |
| Tool reference works locally, fails in Docker | The agent folder is not in the container's Python path. | Either `pip install -e .` your package or ensure the working directory is correct. See [Module 22 Deployment Models](../22_DeploymentModels/). |

## 🚀 In Production

> **🚀 In Production**
>
> When you ship a YAML-driven agent, you ship *two* contracts: the YAML schema (your IDE catches breaks) AND the Python module surface (the YAML's `name:` strings are imports). Add a CI check that *parses every `tools:` reference in every YAML and confirms the symbol is importable*. A 20-line pytest covers it. The first time someone renames a tool function and forgets to update the YAML, you'll be glad you have it.

> 🧭 **If the student looks stuck on dotted paths and `PYTHONPATH`:** detour [[PY_packaging]] — 20 min covers how Python finds modules, what `pyproject.toml` does, and why `uv pip install -e .` matters.

---

[← Prev: 03_AdkCreateCli](03_AdkCreateCli.md)  [↑ Map](../../MAP.md)  [Next: 05_SubAgentReferences →](05_SubAgentReferences.md)
