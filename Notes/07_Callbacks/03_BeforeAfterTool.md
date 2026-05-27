---
module: 07_Callbacks
page: 03_BeforeAfterTool
title: before/after_tool_callback — guard and reshape tool calls
estimated_minutes: 25
prereqs: [07_Callbacks/02]
concepts: [before_tool_callback, after_tool_callback, BaseTool, ToolContext, guardrail]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 07_Callbacks/02_BeforeAfterModel](02_BeforeAfterModel.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/04_BeforeAfterAgent →](04_BeforeAfterAgent.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 03 Before/After Tool

# 🛠 Wrapping the tool call

Tool callbacks bracket every tool invocation. They are where most production guardrails live, because tools are where the agent reaches out and touches the world (filesystem, DB, payment API).

```python
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

def before_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None: ...

def after_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None: ...
```

Return `None` to passthrough. Return a `dict` to **replace the tool result** — meaning, from the agent's perspective, that dict is what the tool returned.

## Idiom 1 — block the call (guard)

```python
DANGEROUS = ("rm -rf", "DROP TABLE", "sudo")

def block_dangerous_shell(tool, args, tool_context):
    if tool.name == "run_shell":
        cmd = args.get("command", "")
        if any(s in cmd for s in DANGEROUS):
            return {"error": f"Blocked: dangerous pattern in command"}
    return None
```

The shell never runs. The LLM sees `{"error": "..."}` as the tool result and can react.

## Idiom 2 — rewrite the args (filter)

You can mutate `args` in place before passthrough — useful for normalizing inputs:

```python
def normalize_email_args(tool, args, tool_context):
    if tool.name == "send_email" and "to" in args:
        args["to"] = args["to"].strip().lower()
    return None  # let it through with mutated args
```

## Idiom 3 — truncate / redact the result (decorate)

After-tool callbacks are the right place to shrink fat tool outputs before they pollute the context:

```python
def truncate_search_results(tool, args, tool_context, tool_response):
    if tool.name == "google_search" and isinstance(tool_response, dict):
        results = tool_response.get("results", [])
        if len(results) > 5:
            tool_response["results"] = results[:5]
            tool_response["truncated"] = True
    return tool_response  # return the modified dict
```

(Note: when you `return` a non-`None` value from `after_tool_callback`, that replaces the result.)

## Wiring it up

```python
agent = Agent(
    model="gemini-2.5-flash",
    name="ops_agent",
    tools=[run_shell, send_email, google_search],
    before_tool_callback=block_dangerous_shell,
    after_tool_callback=truncate_search_results,
)
```

> 🛠 **Have the student run:** wire `block_dangerous_shell` to a fake `run_shell` tool (just `def run_shell(command: str) -> str: return f"ran: {command}"`). Ask the agent to "delete everything in /". Confirm the tool is never called and the LLM is forced to acknowledge the block.

> ⚠️ **Gotcha** — the `tool` argument is a `BaseTool`, not your bare Python function. Use `tool.name` (string) for dispatch, not `tool is my_fn`.

> 🚀 **In Production**
>
> Two patterns stack here: (1) a **policy** `before_tool_callback` that enforces what's allowed, (2) an **observability** `after_tool_callback` that records `tool.name`, args hash, duration, success — feeding [[15_Observability/00_Overview]]. Stack them by writing one composite callback that calls both, or use plugins (covered in 13).

[← Prev: 07_Callbacks/02_BeforeAfterModel](02_BeforeAfterModel.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/04_BeforeAfterAgent →](04_BeforeAfterAgent.md)
