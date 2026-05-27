---
module: 13_Plugins
page: 07_WritingACustomPlugin
title: Writing a custom plugin
estimated_minutes: 30
prereqs: [13_Plugins/06]
concepts: [BasePlugin subclass, hook implementation, state on the plugin instance]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 13_Plugins/06_BigQueryAgentAnalyticsPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/08_DissectingSample →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 07 Writing a Custom Plugin

# 🛠 The minimal custom plugin

Subclass `BasePlugin` from `google.adk.plugins.base_plugin`. Override only the hooks you need. The rest are no-ops.

```python
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

class ToolCallCounterPlugin(BasePlugin):
    """Counts every tool call by name. Prints summary at session end."""

    def __init__(self) -> None:
        super().__init__(name="tool_call_counter")
        self._counts: dict[str, int] = {}

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict,
        tool_context: ToolContext,
    ) -> None:
        self._counts[tool.name] = self._counts.get(tool.name, 0) + 1
        return None    # don't short-circuit

    async def on_session_end_callback(self, *, session) -> None:
        print(f"[counter] {self._counts}")
        self._counts.clear()
        return None
```

Wire it:

```python
runner = Runner(
    app_name="dev",
    agent=root_agent,
    plugins=[ToolCallCounterPlugin()],
)
```

## The contract

- Every hook is `async def` (even if you don't await anything).
- Returning `None` means "I observed, didn't change anything." Returning a value can *short-circuit* — e.g. a `before_model_callback` returning an `LlmResponse` skips the actual model call. (See `safety-plugins`' `LlmAsAJudge` for a real example.)
- Keep state on the instance (`self._counts`). The Runner uses one plugin instance for its lifetime.

## What the safety-plugins sample does

Look at `safety-plugins/safety_plugins/plugins/agent_as_a_judge.py`. `LlmAsAJudge` overrides:

- `on_user_message_callback` — judges the incoming message; if unsafe, replaces it.
- `before_tool_callback` — judges tool inputs; if unsafe, refuses the tool call.
- `after_tool_callback` — judges tool outputs.
- `after_model_callback` — judges model outputs.

It composes itself across the whole runner. That's the canonical "plugin as policy" pattern.

## Designing plugin state

- For request-scoped state (e.g. "did this turn trigger a safety review?"), prefer `ToolContext.state` (a session-state shortcut available in many hooks) over `self`.
- For aggregate state across runs (counters, rate-limit windows), `self` is fine — but remember it dies with the runner.
- For state that must survive a process restart, write to external storage (Redis, BQ, the SessionService).

> ⚠️ **Gotcha.** A plugin that silently swallows errors (`try/except: pass` inside a hook) creates ghost failures — the runner reports success, but the side effect didn't happen. Re-raise or surface to a metric.

> 🛠 **Have the student run:** Build `ToolCallCounterPlugin` above, wire it to any tool-using agent (e.g. M1 calculator), run five turns. Confirm the counts at session end.

> **🧭 See also**: `safety-plugins` — `/home/carloscabral/study/adk-samples/python/agents/safety-plugins/safety_plugins/plugins/` ships two production-grade custom plugins (`LlmAsAJudge`, `ModelArmorSafetyFilter`). Both are good prior art for "plugin holds an inner LlmAgent / external service + overrides five hooks." Dissected on the next page ([[13_Plugins/08_DissectingSample]]) and re-dissected from the security angle in [[16_ProductionSecurity/08_DissectingSafetyPlugins]].

> 🤖 **Tutor:** When the student goes to write their own plugin in the mini-drill, this is the page to come back to.

---

[← Prev: 13_Plugins/06_BigQueryAgentAnalyticsPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/08_DissectingSample →]
