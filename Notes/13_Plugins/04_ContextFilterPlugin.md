---
module: 13_Plugins
page: 04_ContextFilterPlugin
title: ContextFilterPlugin
estimated_minutes: 15
prereqs: [13_Plugins/03]
concepts: [ContextFilterPlugin, context window, cost, privacy filter]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 13_Plugins/03_ReflectAndRetryToolPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/05_GlobalInstructionPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 04 ContextFilterPlugin

# 🛠 Strip parts of session history before the LLM sees them

By default, the LLM gets the full session history each turn. That's fine for short chats. For long ones, you want to:

- **Cap cost.** Long history → big context → bigger bill per turn.
- **Cap length.** Hit the context window ceiling for high-traffic agents.
- **Hide PII.** Even if memory redacts on persist, the live history may still carry raw values.
- **Hide irrelevant detail.** A tool's giant JSON response from 12 turns ago is mostly noise.

`ContextFilterPlugin` lets you express a filter that runs **before** the model call, mutating the request's contents.

```python
from google.adk.runners import Runner
from google.adk.plugins import ContextFilterPlugin

runner = Runner(
    app_name="dev",
    agent=root_agent,
    plugins=[
        ContextFilterPlugin(
            # the exact API surface (function vs config) follows the framework;
            # the idea is "given the in-flight contents, return a filtered list"
        ),
    ],
)
```

## Three filter strategies

1. **Trim by count.** "Keep only the last N turns." Brutally simple, often enough for chatty UX.
2. **Trim by token budget.** "Keep history until it exceeds K tokens, then drop oldest." Tighter cost control.
3. **Filter by content.** "Drop any event whose tool name is `huge_dump_query` and replace with a placeholder summary."

Most teams start with (1), graduate to (2), only do (3) when an outsized tool result is repeatedly torpedoing context.

## When it interacts with memory

ContextFilter drops history *in transit to the model*. The events are still in `session.state` and still get persisted to memory if your callback runs. So:

- Memory remains complete; the model just doesn't see all of it on every turn.
- For long retention with selective display, this is the cleanest combo.

> ⚠️ **Gotcha.** If you drop history aggressively, the LLM loses context the user assumes it has. ("You said X 50 turns ago." "I have no record of that.") Pair with a `RollingSummaryPlugin` (custom — see page 07) or rely on memory recall via `load_memory`.

> ❓ **Ask the student:** "A user uploads a 200KB CSV inline. The tool result gets baked into history. Trim or summarize?" *(Expected: summarize — preserve the fact-of-upload + a digest, drop the raw bytes. Pure trim loses too much.)*

> **🚀 In Production**
>
> Set token-budget filtering before any agent goes wide. Catalogue which tools produce big payloads and have a per-tool replacement policy ("after the third turn, replace the body of `query_logs` with a summary").

---

[← Prev: 13_Plugins/03_ReflectAndRetryToolPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/05_GlobalInstructionPlugin →]
