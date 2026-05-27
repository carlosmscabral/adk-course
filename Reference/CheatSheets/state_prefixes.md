# 📋 Cheat Sheet — State prefixes

ADK session state has **four scopes**, distinguished by the key's prefix. Pick wrong and you'll either leak data across users or lose data you wanted to keep.

## The table

| Prefix | Scope | Persistence | Survives across | Example key | Example value |
|---|---|---|---|---|---|
| _(none)_ | **Session** | Persisted with the session | This conversation only | `current_step` | `"reviewing"` |
| `user:` | **User** | Persisted across all sessions for that `user_id` | Any session for `user_id="alice"` | `user:name` | `"Alice"` |
| `app:` | **App** | Persisted across all users of the `app_name` | Every session of every user | `app:default_currency` | `"USD"` |
| `temp:` | **Turn-local** | **Not persisted** — wiped at end of turn | Within a single `run_async` call only | `temp:tool_call_count` | `3` |

## When to pick which

- **no-prefix (session)**: anything that pertains to *this conversation* — current step in a workflow, accumulated tool outputs, draft document being revised. Lost when the session is destroyed.
- **`user:`**: anything that pertains to *who this user is* — name, preferences, language, role. Survives session deletion as long as the same `user_id` returns.
- **`app:`**: anything that is *configuration for the whole app* — feature flags, default models, base URLs, tenant settings. Read-mostly; rarely written by agents.
- **`temp:`**: anything *intermediate within one turn* — a tool's interim output that the next callback inspects, a flag a `before_tool_callback` sets that the `after_tool_callback` reads. Deliberately ephemeral — do not rely on it surviving the turn.

## Reading state

In an agent's instruction:

```python
LlmAgent(
    instruction="Hello {user:name?}. The current step is {current_step}.",
    # {var}  → KeyError if missing
    # {var?} → silently empty if missing
)
```

In a tool / callback via `ToolContext` / `CallbackContext`:

```python
def my_tool(arg: str, tool_context: ToolContext) -> str:
    # The context parameter is detected by the `ToolContext` annotation
    # (preferred); a param literally named `tool_context` is the fallback
    # if the annotation is missing.
    name = tool_context.state.get("user:name", "stranger")  # dict-like read
    tool_context.state["current_step"] = "thinking"          # dict-like write — staged
    return f"Hello {name}"
```

## Writing state

You **do not** mutate `session.state` directly. You either:

1. **`output_key=` on the agent** — the agent's final text is written to `state[output_key]` automatically.
2. **From inside a tool/callback** — write to `ctx.state[key] = value`. The runner stages it as a `state_delta` on the resulting Event, then applies + persists.
3. **Construct-time seed** — pass `state={"user:name": "Alice"}` to `session_service.create_session(...)`.

## Common confusions

- **`user:` is not enforced by some session services**. `InMemorySessionService` and `DatabaseSessionService` honor it; verify with `VertexAiSessionService` for your project.
- **`temp:` is genuinely wiped each turn**. If you need cross-turn ephemeral data, use no-prefix; if you need cross-session, use `user:`.
- **Don't put PII in `user:` without redaction**. The whole point of `user:` is durability — that includes the PII. Use a callback to scrub on write.
- **Reading `{user:name}` in `instruction` requires the agent to have already seen `user:` populated**. If the seed only lands on turn 1's tool, turn 1's instruction interpolation will fail. Either seed at session creation or use `{user:name?}`.

## Where it's covered in the course

- Engine-first walk: [Notes/04_SessionsState/02_StateScopes](../../Notes/04_SessionsState/02_StateScopes.md)
- Instruction interpolation: [Notes/04_SessionsState/03_ReadingStateInPrompts](../../Notes/04_SessionsState/03_ReadingStateInPrompts.md)
- `output_key=`: [Notes/04_SessionsState/03_ReadingStateInPrompts](../../Notes/04_SessionsState/03_ReadingStateInPrompts.md)
- Event deltas: [Notes/04_SessionsState/04_WritingStateFromTools](../../Notes/04_SessionsState/04_WritingStateFromTools.md)
- PII redaction (production): [Notes/16_ProductionSecurity/05_GuardrailsCookbook](../../Notes/16_ProductionSecurity/05_GuardrailsCookbook.md)

---

[← Cheat sheets](../CheatSheets/) · [📍 Progress](../../PROGRESS.md)
