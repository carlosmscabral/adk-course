---
module: 13_Plugins
page: 08_DissectingSample
title: Dissecting the safety-plugins sample
estimated_minutes: 30
prereqs: [13_Plugins/07]
concepts: [sample read-through, custom plugin composition, LlmAsAJudge, ModelArmor]
icon: 🧪
in_production: false
detours_suggested: []
---

[← Prev: 13_Plugins/07_WritingACustomPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/09_InProduction →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 08 Dissecting safety-plugins

# 🧪 Real custom plugins in action

Sample: `/home/carloscabral/study/adk-samples/python/agents/safety-plugins/`

```
safety-plugins/
└── safety_plugins/
    ├── agent.py         ← a simple two-agent system (root + sub_agent)
    ├── main.py          ← runner wiring; --plugin CLI flag selects which safety policy
    ├── plugins/
    │   ├── agent_as_a_judge.py    ← LlmAsAJudge: an LLM rates safety on each hook
    │   └── model_armor.py         ← ModelArmorSafetyFilterPlugin: external safety API
    ├── prompts.py
    └── tools.py
```

## Read along: `main.py`

```python
from google.adk import runners
from .agent import root_agent
from .plugins import agent_as_a_judge, model_armor

LlmAsAJudge = agent_as_a_judge.LlmAsAJudge
ModelArmorSafetyFilter = model_armor.ModelArmorSafetyFilterPlugin

async def main():
    plugin_name = FLAGS.plugin
    plugins = []
    if plugin_name == "llm_judge":
        plugins.append(LlmAsAJudge())
    elif plugin_name == "model_armor":
        plugins.append(ModelArmorSafetyFilter())

    runner = runners.InMemoryRunner(
        agent=root_agent,
        app_name="test_app_with_plugin",
        plugins=plugins,
    )
```

Three things to highlight to the student:

1. **No built-in plugins are composed here** — both choices are custom. This is the canonical "plugin as policy" sample.
2. **Plugins are passed as a list to the Runner**, exactly as the spec says.
3. **The agent file (`agent.py`) is unchanged regardless of which safety plugin is attached.** The same agent runs under different policies — that's the value of runner-scope.

## Read along: `plugins/agent_as_a_judge.py`

`LlmAsAJudge` (excerpt):

```python
class JudgeOn(enum.StrEnum):
    USER_MESSAGE = "user_message"
    BEFORE_TOOL_CALL = "before_tool_call"
    TOOL_OUTPUT = "tool_output"
    MODEL_OUTPUT = "model_output"

class LlmAsAJudge(BasePlugin):
    def __init__(
        self,
        judge_agent: LlmAgent = default_jailbreak_safety_agent,
        analysis_parser: Callable[[str], bool] = default_safety_analysis_parser,
        judge_on: set[str] | None = None,
    ) -> None:
        super().__init__(name="judge_agent")
        self._judge_agent = judge_agent
        ...
```

Patterns to name:

- The plugin holds an **inner LlmAgent** as the judge. A plugin can host its own agent / runner — that's how `LlmAsAJudge` runs the safety classifier separately.
- The `judge_on` set is a config knob: the user picks *which* hooks the judge runs on. Defaults are `user_message` and `tool_output`. The judge can be wired into any subset.
- The `analysis_parser` is a callable: "given the judge's text, return True if unsafe." That's a swap point — plug in any classifier without touching the plugin core.

## Identify in your head

> ❓ **Ask the student:** "Without looking at the file, what hooks does `LlmAsAJudge` override on `BasePlugin`?" *(Expected: roughly `on_user_message_callback`, `before_tool_callback`, `after_tool_callback`, `after_model_callback` — one per JudgeOn variant.)*

> ❓ **Ask the student:** "If you ran this with BOTH `LlmAsAJudge` and `ModelArmorSafetyFilter`, would they conflict? Which would you put first?" *(Expected: not necessarily conflict — ModelArmor is a fast deterministic filter, judge is slower LLM analysis. Put ModelArmor first to short-circuit obvious cases; judge runs only on what survives.)*

> 🤖 **Tutor:** This sample is the best argument for "plugins, not callbacks" in the whole course. The same agent, different policies, attached at the runner. Make sure the student feels that.

---

[← Prev: 13_Plugins/07_WritingACustomPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/09_InProduction →]
