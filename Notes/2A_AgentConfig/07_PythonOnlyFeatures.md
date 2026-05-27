---
module: 2A_AgentConfig
page: 07_PythonOnlyFeatures
title: What YAML can't express
estimated_minutes: 15
prereqs: [2A_AgentConfig/06]
concepts: [callbacks, dynamic-instruction, plugins, custom-base-agent]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 06_YamlVsPythonTradeoffs](06_YamlVsPythonTradeoffs.md)  [↑ Map](../../MAP.md)  [Next: 08_DissectingSample →](08_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 07 Python-Only Features

# 🧠 What YAML can't express (and what to do about it)

YAML's expressive ceiling. The four big categories where you must drop into Python — and the recommended hybrid pattern for each.

## 🧠 Category 1 — Callbacks

The `LlmAgent` callback hooks (`before_model_callback`, `after_model_callback`, `before_tool_callback`, `after_tool_callback`, `before_agent_callback`, `after_agent_callback`) are **all Python callables**. YAML cannot inline a function.

**Workaround:** load the YAML, attach the callback after.

```python
# Work/2A_callback_after_load.py
from google.adk.agents import config_agent_utils

def trace_model_calls(callback_context, llm_request):
    print(f"[model call] agent={callback_context.agent_name}")
    return None

agent = config_agent_utils.from_config("Work/2A_anatomy.yaml")
agent.before_model_callback = trace_model_calls
```

The YAML still drives the shape (name, instruction, model, tools). The Python attaches the behavior. This is pattern 2 from page 01.

**Anti-pattern:** trying to encode "callback-like" behavior as an LLM tool. The LLM-as-router approach (have the LLM call a `log_this` tool whenever it wants logging) is unreliable, slow, and burns tokens. Use a real Python callback.

## 🧠 Category 2 — Dynamic instructions

YAML `instruction:` is a static string. The Python form accepts `instruction=callable` for state-aware prompts:

```python
# Python form — state-aware instruction
def make_instruction(ctx):
    user_name = ctx.state.get("user:name", "friend")
    return f"You are talking to {user_name}. Be warm."

agent = LlmAgent(name="warm_bot", model="gemini-2.5-flash", instruction=make_instruction)
```

There is no YAML equivalent. The closest workaround is YAML for the static prefix + Python wrapper that mutates `instruction` per turn:

```python
# Work/2A_dynamic_instruction.py — hybrid
from google.adk.agents import config_agent_utils

agent = config_agent_utils.from_config("Work/2A_anatomy.yaml")
base_instruction = agent.instruction

def make_instruction(ctx):
    user_name = ctx.state.get("user:name", "friend")
    return f"{base_instruction}\n\nCurrent user: {user_name}."

agent.instruction = make_instruction
```

Honestly: if you need a callable instruction, just use Python end-to-end. The hybrid above is uglier than the all-Python form. The YAML→callable bridge is "I have to" not "I want to."

## 🧠 Category 3 — Plugins

Plugins live on the **App**, not the agent. The YAML schema covers `LlmAgent` and its sub-agents — it does **not** cover `App(plugins=...)`. As of ADK 2.0 GA, plugin wiring is Python only:

```python
# main.py — App-level plugin wiring (cannot move to YAML today)
from google.adk.apps import App
from google.adk.agents import config_agent_utils
# GlobalInstructionPlugin is not re-exported from google.adk.plugins.__init__;
# import from its module directly.
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin

agent = config_agent_utils.from_config("root_agent.yaml")
app = App(
    name="my_app",
    root_agent=agent,
    plugins=[GlobalInstructionPlugin("You are part of AcmeCo.")],
)
```

This means **every YAML-driven ADK project still has a Python entry point** for the `App(...)` construction. That is fine — it is one short file, often named `main.py` next to `root_agent.yaml`. Don't fight this; just expect it.

## 🧠 Category 4 — Custom `BaseAgent` subclasses

The YAML schema's `agent_class:` accepts a fixed set: `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` (per `agent_config.py:_ADK_AGENT_CLASSES`). Anything else falls through to `BaseAgent`. Graph workflows (`google.adk.workflow.Workflow`) are **not** YAML-loadable — they live in Python only. If you wrote `class MyCustomRouter(BaseAgent): ...` to implement your own routing logic (Module 09 covers when this is appropriate), YAML cannot construct it either.

**Workaround:** Python entry point.

```python
# Python — custom agent subclass
from my_pkg.agents import MyCustomRouter
from google.adk.agents import config_agent_utils

# YAML sub-agents
math_tutor = config_agent_utils.from_config("math_tutor.yaml")
code_tutor = config_agent_utils.from_config("code_tutor.yaml")

# Custom root that can't be expressed in YAML
root = MyCustomRouter(
    name="root",
    sub_agents=[math_tutor, code_tutor],
    routing_strategy="weighted_random",   # custom kwarg
)
```

Mix freely — `from_config()` returns a `BaseAgent`, so `MyCustomRouter` can hold YAML-loaded sub-agents in its `sub_agents=` list.

## 🧠 Category 5 — Anything passing a complex Python object

`model=Gemini(retry_options=..., cache_config=...)` accepts an object, not a string. YAML can express the string form (`model: gemini-2.5-flash`) but not the object form. Same applies to `planner=` (only certain planner shapes have YAML schemas), advanced `generate_content_config=` settings (most basics work; some types don't serialize cleanly), and any `tools=` entry that is a custom `Toolset` instance constructed with non-trivial logic.

**Heuristic:** if the Python form requires you to *construct an object* with multiple kwargs, YAML probably can't do it cleanly. Use Python.

## 🛠 The hybrid pattern that scales

For a real production agent, the file layout converges on:

```
my_agent/
├── __init__.py
├── .env
├── root_agent.yaml           # shape: name, model, instruction, tools refs, sub_agents
├── main.py                   # App + Runner + plugins + callback attachment
├── tools.py                  # @tool-decorated functions
└── callbacks.py              # before_/after_ callbacks (attached in main.py)
```

YAML for *what the agent is*. Python for *what it does at runtime*. The seam is the `App(...)` construction call.

> ❓ **Ask the student:** "Where in this layout does dynamic instruction live — `root_agent.yaml`, `main.py`, or somewhere else?"
> *(Expected: it can't live in `root_agent.yaml` at all — YAML is static. The pragmatic answer is to put the callable in `main.py` (or `callbacks.py`) and assign it to `agent.instruction` after `from_config(...)`. Better: if you need dynamic instructions, accept the cost and write the agent in Python end-to-end — the hybrid is uglier than the all-Python form.)*

## 🚀 In Production

> **🚀 In Production**
>
> The single most common YAML production bug is "I added a callback but forgot to attach it after `from_config`." The agent loads fine, runs fine, just silently skips your logging/guardrails. Mitigation: in `main.py`, write the attachment block as a single function `attach_runtime_behaviors(agent)` and call it once. Easier to grep for, easier to unit-test, and a missing attachment becomes a code-review finding instead of a silent prod incident.

> 🛠 **Have the student do:** take one of their existing Python agents from Module 02 that has callbacks/dynamic instructions, sketch the hybrid layout (YAML + `main.py` attachment). If they find themselves writing a 50-line attachment block, that's the signal to stay all-Python.

---

[← Prev: 06_YamlVsPythonTradeoffs](06_YamlVsPythonTradeoffs.md)  [↑ Map](../../MAP.md)  [Next: 08_DissectingSample →](08_DissectingSample.md)
