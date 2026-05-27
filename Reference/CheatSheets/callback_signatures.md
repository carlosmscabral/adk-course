# 📋 Cheat Sheet — Callback signatures

ADK exposes nine callback slots on `LlmAgent`. Each has a specific signature, a specific return-value contract (`None` = pass through, non-`None` = override), and specific context types. Get the signature wrong → the runtime swallows it silently and your guardrail does nothing.

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext, BaseTool
from google.adk.models import LlmRequest, LlmResponse
```

## The nine slots

| Slot | Signature (param types) | Return-value semantics |
|---|---|---|
| `before_model_callback` | `(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse \| None` | Return `LlmResponse` → **short-circuit**: skip the LLM call entirely, use this response. Return `None` → pass through (let the LLM run). Mutating `llm_request` in place is also valid. |
| `after_model_callback` | `(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse \| None` | Return `LlmResponse` → **override** the LLM's response. Return `None` → pass through the original. |
| `before_tool_callback` | `(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext) -> dict \| None` | Return `dict` → **short-circuit**: skip the tool call, use this as the tool's result. Return `None` → pass through (let the tool run). Mutating `args` is also valid. |
| `after_tool_callback` | `(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict) -> dict \| None` | Return `dict` → **override** the tool's result. Return `None` → pass through the original. |
| `before_agent_callback` | `(callback_context: CallbackContext) -> types.Content \| None` | Return `Content` → **short-circuit**: skip the agent's turn entirely, use this as the agent's response. Return `None` → pass through. |
| `after_agent_callback` | `(callback_context: CallbackContext) -> types.Content \| None` | Return `Content` → **override** the agent's final response. Return `None` → pass through. |
| `on_model_error_callback` | `(callback_context: CallbackContext, llm_request: LlmRequest, error: Exception) -> LlmResponse \| None` | Return `LlmResponse` → recover (retry / fallback). Return `None` → re-raise the error. |
| `on_tool_error_callback` | `(tool: BaseTool, args: dict, tool_context: ToolContext, error: Exception) -> dict \| None` | Return `dict` → recover. Return `None` → re-raise. |

## Wiring them on the agent

```python
def block_bad_args(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None:
    """Block any tool call whose args contain 'rm -rf'."""
    flat = " ".join(str(v) for v in args.values())
    if "rm -rf" in flat:
        return {"error": "blocked: dangerous arg pattern"}
    return None  # passthrough

agent = LlmAgent(
    name="guarded",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[shell_tool],
    before_tool_callback=block_bad_args,
)
```

## Context object cheatsheet

- **`CallbackContext`** — read/write `.state`, read `.user_content`, mutate `.actions` (state_delta etc.). Used by model + agent callbacks.
- **`ToolContext`** — superset of `CallbackContext` plus artifact I/O. Used by tool callbacks.
- **`LlmRequest`** — what the LLM is about to be called with: `.contents`, `.config`, `.tools`. Mutate to inject system messages, redact, etc.
- **`LlmResponse`** — what the LLM returned: `.content` (with `.parts`), `.usage_metadata`, `.error`. Mutate to redact, append, etc.
- **`BaseTool`** — `.name`, `.description`. Useful for routing on tool identity in a generic callback.

## Order of execution per turn

```
before_agent_callback
  └→ before_model_callback
       └→ LLM call
       └→ after_model_callback
       └→ (if tool call requested:)
            before_tool_callback
              └→ tool runs
              └→ after_tool_callback
            (back to LLM with tool result)
            before_model_callback (again)
              └→ LLM call
              └→ after_model_callback
  └→ after_agent_callback
```

Errors:
- LLM API exception → `on_model_error_callback`.
- Tool function raises → `on_tool_error_callback`.

## Common confusions

- **Returning `None` vs `{}`**: `None` = passthrough. `{}` = override with empty dict (and the tool result is now empty!). They are not interchangeable.
- **Mutating in place AND returning a value** = the return value wins. Pick one style and stick to it.
- **`tool_response` in `after_tool_callback` is the *processed* result**, after the runtime has converted the tool's return value to a dict. If your tool returns a Pydantic model, you see the dict here.
- **`before_*` short-circuit Events still appear in the session history** — the tool/LLM was "called" from the conversation's perspective even though no external call happened.
- **`on_*_error_callback` fires per-call, not per-turn** — if a tool fails three times, the callback fires three times.

## Where it's covered in the course

- Engine-first walks per slot:
  - [Notes/07_Callbacks/01_BeforeAfterModel](../../Notes/07_Callbacks/01_BeforeAfterModel.md)
  - [Notes/07_Callbacks/02_BeforeAfterTool](../../Notes/07_Callbacks/02_BeforeAfterTool.md)
  - [Notes/07_Callbacks/03_BeforeAfterAgent](../../Notes/07_Callbacks/03_BeforeAfterAgent.md)
  - [Notes/07_Callbacks/04_OnErrorCallbacks](../../Notes/07_Callbacks/04_OnErrorCallbacks.md)
- Callbacks-as-policy (production): [Notes/16_ProductionSecurity/03_CallbacksAsPolicy](../../Notes/16_ProductionSecurity/03_CallbacksAsPolicy.md)
- Guardrails cookbook: [Notes/16_ProductionSecurity/04_GuardrailsCookbook](../../Notes/16_ProductionSecurity/04_GuardrailsCookbook.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
