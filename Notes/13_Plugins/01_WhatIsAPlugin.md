---
module: 13_Plugins
page: 01_WhatIsAPlugin
title: What is a Plugin (vs a Callback)
estimated_minutes: 20
prereqs: [07_Callbacks/01]
concepts: [BasePlugin, runner-scoped, callback vs plugin, hook surface]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 13_Plugins/00_Overview]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/02_LoggingPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 01 What is a Plugin

# 🧠 Same hooks, bigger blast radius

A **Plugin** is a bundle of cross-cutting concern logic — logging, retry, telemetry, redaction, global instructions — attached to the **Runner**, not to a single agent.

It shares almost the entire hook vocabulary with callbacks (`before_model_callback`, `after_tool_callback`, etc.). The difference is *where* it lives and *what it sees*.

| | Callback | Plugin |
|--|--|--|
| Wired on | one `LlmAgent` | the `Runner` |
| Scope | only that agent | every agent, every model call, every tool call |
| Composition | one per hook per agent | a list, fire in order |
| Use for | per-agent specialization | cross-cutting policy |

🗺 Look at the figure:

```
$ cat _figures/plugin_hooks.txt
```

## Wiring a plugin

```python
from google.adk.runners import Runner
from google.adk.plugins import LoggingPlugin

runner = Runner(
    app_name="dev",
    agent=root_agent,
    plugins=[
        LoggingPlugin(),
        # other plugins...
    ],
)
```

That's it. The Runner now invokes every configured plugin at every hook point for every agent in the tree.

## The mental model

> A **callback** is "this specific agent should do X at this point in its turn."
>
> A **plugin** is "for the whole runner, no matter which agent is currently active, do X."

If you find yourself adding the same callback to five sub-agents, that's a plugin.

## Hook surface

Plugins implement (any subset of) these — same names as callbacks plus a few runner-level ones:

- `on_user_message` — runner received a user message
- `before_agent` / `after_agent` — any agent's turn boundaries
- `before_model` / `after_model` / `on_model_error` — any LLM call
- `before_tool` / `after_tool` / `on_tool_error` — any tool call
- `on_event` — every event the runner yields

The exact methods come from `google.adk.plugins.base_plugin.BasePlugin`. We'll see custom plugin authoring in page 07.

## Order matters

Multiple plugins fire in the order you pass them. A `LoggingPlugin` placed *after* a `ContextFilterPlugin` will log the *filtered* messages; placed before, it'll log the originals. Decide on purpose.

> ⚠️ **Gotcha.** Plugins can mutate things in the pipeline (e.g. modify the message before the LLM sees it). If two plugins both mutate the same field, ordering is a correctness question, not just a logging question.

> ❓ **Ask the student:** "You want to redact PII from user messages, AND log every message for audit. Which plugin goes first?" *(Expected: depends on whether the audit log should contain raw or redacted data. Most likely audit-first if you have separate access controls; redact-first if the audit store has the same audience as the LLM.)*

> 🤖 **Tutor:** Plugin ordering is the single design question that elevates someone from "uses plugins" to "designs with plugins." Probe it whenever it comes up.

---

[← Prev: 13_Plugins/00_Overview]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/02_LoggingPlugin →]
