---
module: 13_Plugins
page: 03_ReflectAndRetryToolPlugin
title: ReflectAndRetryToolPlugin
estimated_minutes: 20
prereqs: [13_Plugins/02]
concepts: [ReflectAndRetryToolPlugin, tool error recovery, LLM self-correction]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 13_Plugins/02_LoggingPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/04_ContextFilterPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 03 ReflectAndRetryToolPlugin

# 🛠 Letting the LLM correct its own tool calls

When a tool call fails (bad args, exception inside the tool body), you have two choices:

1. Bubble the error up. The agent's reply will probably be apologetic and useless.
2. Show the error back to the LLM, let it think, let it retry.

`ReflectAndRetryToolPlugin` automates option 2.

```python
from google.adk.runners import Runner
from google.adk.plugins import ReflectAndRetryToolPlugin

runner = Runner(
    app_name="dev",
    agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(
            max_retries=2,
            # the plugin builds a reflection prompt for the LLM
        ),
    ],
)
```

## What it does, mechanically

1. Tool call fires; tool raises (or returns an error structure the plugin recognizes).
2. The plugin intercepts in `on_tool_error` / `after_tool`.
3. It synthesizes a "the previous tool call failed because <error>; reconsider your arguments and try again" message and feeds it back to the LLM.
4. The LLM re-emits a tool call with revised args.
5. If still failing after `max_retries`, the plugin gives up and lets the error surface.

## When this is the right tool

- The LLM frequently passes slightly-wrong args (typoed field names, wrong units, missing required param). Reflection catches these.
- Transient flakiness in upstream APIs (rate limits, brief 5xx). Pair with backoff.

## When it's the wrong tool

- The tool failure is *not* the LLM's fault (auth expired, downstream service down). Retrying is wasted budget; surface the error.
- The tool is non-idempotent and the failure happens mid-side-effect. Retrying might double-charge a credit card. Have the tool itself be idempotent or wrap with a deduplication key.

> ⚠️ **Gotcha.** Reflection adds an extra LLM round trip per failed call. Cost adds up if tools fail often. If your tool fails > 20% of calls, the bug is the tool, not the plugin.

## Composing with other plugins

If you also have a `LoggingPlugin`, place it *after* `ReflectAndRetryToolPlugin` so the logs show the eventual successful call, not the intermediate failures (unless you specifically want to log the retries — both choices are valid).

> ❓ **Ask the student:** "Your `sql_query(query: str)` tool sometimes fails with 'syntax error near token X'. Is `ReflectAndRetryToolPlugin` the right fix?" *(Expected: yes — the LLM-generated SQL has a fixable error, reflection lets it correct. But longer-term, a SQL-validator pre-check is even better.)*

> **🚀 In Production**
>
> Cap `max_retries` at 1 or 2. Higher values turn one bad call into a runaway cost burn. Also log every retry to your analytics plugin so you can spot tools that fail systematically.

---

[← Prev: 13_Plugins/02_LoggingPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/04_ContextFilterPlugin →]
