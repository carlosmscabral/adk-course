---
module: 2A_AgentConfig
page: 03_AdkCreateCli
title: Generating an agent with `adk create`
estimated_minutes: 15
prereqs: [2A_AgentConfig/02]
concepts: [adk-create, scaffold, template, .env]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 02_RootAgentYaml](02_RootAgentYaml.md)  [↑ Map](../../MAP.md)  [Next: 04_ToolReferences →](04_ToolReferences.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 03 `adk create` CLI

# 🛠 Generating an agent with `adk create`

The CLI ships a scaffold command that creates either a Python agent or a YAML agent from a template. You will use this **once per project**, then live in the files it generated.

## 🛠 The command

```bash
$ adk create my_yaml_agent --type config --model gemini-2.5-flash
```

Flags:

| Flag | What it sets |
|---|---|
| `--type config` | Scaffold a YAML agent (`root_agent.yaml`). The alternative is `--type code` for the Python form. |
| `--model gemini-2.5-flash` | The model string to write into the template. Defaults to `gemini-2.5-flash` if omitted. |
| `--api_key KEY` | Writes `GOOGLE_API_KEY=KEY` into `.env` and sets `GOOGLE_GENAI_USE_VERTEXAI=0`. |
| `--project PROJECT --region us-central1` | The Vertex AI alternative — writes `GOOGLE_GENAI_USE_VERTEXAI=1` and the project/region. |

If you omit `--type`, `--model`, or the auth flags, the CLI prompts you interactively. The prompts are friendly; pass flags only when you want the command to be non-interactive (CI scripts).

## 🛠 What gets created

```
$ adk create my_yaml_agent --type config --model gemini-2.5-flash
Agent created in my_yaml_agent:
- .env
- __init__.py
- root_agent.yaml

⚠️  WARNING: Secrets (like GOOGLE_API_KEY) are stored in .env.
Please ensure .env is added to your .gitignore to avoid committing secrets to version control.

$ tree my_yaml_agent/
my_yaml_agent/
├── __init__.py          # empty
├── .env                 # GOOGLE_API_KEY, backend flags
└── root_agent.yaml      # the scaffold YAML
```

And the scaffolded `root_agent.yaml`:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: root_agent
description: A helpful assistant for user questions.
instruction: Answer user questions to the best of your knowledge
model: gemini-2.5-flash
```

Bare minimum: the four required fields and the schema line. No `agent_class:` (defaults to `LlmAgent`), no tools, no sub-agents. **Ready to run immediately.**

## 🛠 Run it

```bash
$ adk run my_yaml_agent
```

`adk run` looks for either `root_agent` (in `agent.py` for the code form) or `root_agent.yaml` (for the config form) in the named directory, loads it, builds the Runner, and gives you a REPL. Same UX as the Python form from Module 00.

## 🧠 What `adk create --type code` looks like, for comparison

```
$ adk create my_python_agent --type code --model gemini-2.5-flash
Agent created in my_python_agent:
- .env
- __init__.py
- agent.py

$ cat my_python_agent/agent.py
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
```

Same content, same defaults. The only difference is `root_agent.yaml` vs `agent.py`. Project structure (`__init__.py`, `.env`, the agent folder) is identical — Module 3A covers how `adk run` / `adk web` discover both shapes from this same layout.

> ❓ **Ask the student:** "If I rename `root_agent.yaml` to `my_agent.yaml`, does `adk run my_yaml_agent` still work?"
> *(Expected: no. The `adk` CLI discovers by exact name — `root_agent.yaml` for config, `agent.py` exposing `root_agent` for code. The discovery contract is in [Module 3A § 05 CLI Expectations](../3A_ProjectStructure/05_AdkCliExpectations.md).)*

## 🛠 Adding tools to a scaffolded YAML agent

The scaffold has no tools. To add one, you typically:

1. Create a Python file beside `root_agent.yaml`:

   ```python
   # my_yaml_agent/tools.py
   def get_weather(city: str) -> str:
       """Return current weather for a city."""
       return f"It is sunny in {city}."
   ```

2. Reference it from the YAML:

   ```yaml
   # my_yaml_agent/root_agent.yaml
   # ... existing fields ...
   tools:
     - name: my_yaml_agent.tools.get_weather
   ```

The dotted path is a **Python import path** — ADK uses `importlib` to resolve it. Page 04 covers all the supported reference forms.

## 🚀 In Production

> **🚀 In Production**
>
> `adk create` writes secrets into `.env`. The CLI warns about adding `.env` to `.gitignore`, but that warning is easy to miss in CI. Standard mitigation: add `.env` to your repo's root `.gitignore` **before** the first `adk create` call, and use a secret-manager (GCP Secret Manager, Vault) for production deploys — never ship the dev `.env` to prod. See [16 Production & Security § 02 Secrets Handling](../16_ProductionSecurity/02_SecretsHandling.md).

> 🛠 **Have the student run:** `adk create scratch_yaml --type config --model gemini-2.5-flash --api_key $GOOGLE_API_KEY`. Then `adk run scratch_yaml` and confirm the agent replies. The whole loop should take under two minutes — that is the point of the scaffold. (Flag names verified against `cli_tools_click.py:436-498`.)

---

[← Prev: 02_RootAgentYaml](02_RootAgentYaml.md)  [↑ Map](../../MAP.md)  [Next: 04_ToolReferences →](04_ToolReferences.md)
