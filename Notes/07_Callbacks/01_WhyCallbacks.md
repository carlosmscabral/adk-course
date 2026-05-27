---
module: 07_Callbacks
page: 01_WhyCallbacks
title: Why callbacks (the prompt is not your guardrail)
estimated_minutes: 15
prereqs: [07_Callbacks/00]
concepts: [callbacks, guardrails, policy, lifecycle, interception]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 07_Callbacks/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/02_BeforeAfterModel →](02_BeforeAfterModel.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 01 Why Callbacks

# 🧠 Why callbacks exist

## The failure mode that motivates them

You have an agent with a `delete_file` tool. You write in the instruction:

> "Never delete files outside `/tmp`."

Run it 200 times. The model obeys 198 times. The 199th request happens during a long tool-loop where the original instruction is far up the context, and the LLM, having drifted, calls `delete_file("/etc/passwd")`. The instruction was a wish; **the wish is not the policy**.

A callback is the policy:

```python
def block_dangerous_paths(tool, args, tool_context):
    if tool.name == "delete_file" and not args["path"].startswith("/tmp"):
        return {"error": "Blocked: deletes restricted to /tmp"}
    return None  # passthrough
```

Now the model can ask 1,000 times. The bytes never leave the agent.

## The 6 hook points

ADK exposes 6 lifecycle hooks plus 2 error hooks. Every hook follows the same shape: **return `None` to passthrough, return a value to override or short-circuit.**

```
┌──────────────────┐
│ before_agent     │  setup, load context, refuse the whole invocation
│ before_model     │  inspect/modify the LlmRequest, or short-circuit with an LlmResponse
│ after_model      │  inspect/rewrite the LlmResponse (citations, redaction, formatting)
│ before_tool      │  guard tool calls (block / rewrite args / mock for tests)
│ after_tool       │  rewrite tool results (truncate, redact, transform)
│ after_agent      │  teardown, persist artifact, finalize state
└──────────────────┘
plus:
│ on_model_error   │  recover from LLM exceptions (return an LlmResponse to heal)
│ on_tool_error    │  recover from tool exceptions (return a dict to heal)
```

See the figure for the full lifecycle:

```
{{_figures/callback_lifecycle.txt}}
```

(Open `_figures/callback_lifecycle.txt` in your editor for the ASCII flow.)

## Three idioms

Every callback you'll write reduces to one of three:

| Idiom        | Hook examples                       | Pattern                                              |
| ------------ | ----------------------------------- | ---------------------------------------------------- |
| **Filter**   | `before_model`, `before_tool`       | Inspect, mutate, optionally short-circuit.           |
| **Guard**    | `before_tool`, `before_agent`       | Return a canned response to block the operation.    |
| **Decorate** | `after_model`, `after_tool`         | Pass-through the value but enrich/trim/format it.    |

You'll meet all three in the next four pages.

> ❓ **Ask the student:** name one thing in your current agent (real or imagined) that should be a callback instead of a prompt rule.

> 🚀 **In Production**
>
> Callbacks-as-policy is the standard ADK guardrail pattern. Anything that must hold under adversarial input (PII, prompt injection, dangerous tool args) goes here. Anything that's a style preference can stay in the prompt. See [`safety-plugins/safety_plugins/plugins/model_armor.py`](/home/carloscabral/study/adk-samples/python/agents/safety-plugins/safety_plugins/plugins/model_armor.py) for the Google reference implementation.

[← Prev: 07_Callbacks/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/02_BeforeAfterModel →](02_BeforeAfterModel.md)
