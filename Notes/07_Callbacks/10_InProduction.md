---
module: 07_Callbacks
page: 10_InProduction
title: Callbacks in production — guardrail checklist
estimated_minutes: 15
prereqs: [07_Callbacks/09]
concepts: [callbacks, policy, guardrails, observability, async, idempotency]
icon: 🚀
in_production: true
detours_suggested: [PY_async, PY_testing]
---

[← Prev: 07_Callbacks/09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/11_KnowledgeCheck →](11_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 10 In Production

# 🚀 Production checklist for callbacks

## Latency budget

A slow callback blocks the whole agent. The agent can't respond while you're waiting on your callback. Two rules:

1. **Sync I/O in a sync callback is a bug.** Use `async def` and `await` for anything network.
2. **Anything > 50 ms** should either be cached or be on a `temp:`-state-gated path so it only runs when needed.

```python
async def fast_policy_lookup(tool, args, tool_context):
    # cache the policy bundle in user state, only refresh hourly
    state = tool_context.state
    if "user:policy" not in state or stale(state):
        state["user:policy"] = await fetch_policy_async(state["user:id"])
    return None
```

## Don't make error callbacks loop

```python
# Anti-pattern
def on_tool_error_callback(tool, args, ctx, err):
    return tool.run(...)  # what if THIS fails too?
```

Guard with a `temp:`-state counter. We showed the pattern in 05.

## Callbacks are the policy surface — treat them like security code

Use cases that belong in callbacks:

- **Input filter** — `before_model_callback` strips PII, refuses banned topics.
- **Output filter** — `after_model_callback` redacts emails / phone numbers / API keys.
- **Tool guard** — `before_tool_callback` enforces "no `rm -rf`", path whitelists, money caps.
- **Tool result trimmer** — `after_tool_callback` truncates fat search results to top-N.
- **Audit** — `after_tool_callback` logs `{tool, args_hash, duration, success}` to [[15_Observability/00_Overview]].

What does *not* belong:

- Anything an LLM should decide ("is this question political?") — that needs a judge agent, not a callback.
- Anything user-visible-but-stylistic — those are prompt rules.

## Test them like any other code

```python
def test_block_dangerous_shell():
    fake_tool = FakeTool(name="run_shell")
    out = block_dangerous_shell(fake_tool, {"command": "rm -rf /"}, FakeCtx())
    assert out == {"error": "Blocked: dangerous pattern in command"}
```

You don't need the agent runner to unit-test callbacks. They are pure functions of their inputs. See [[PY_testing]].

## Callback vs plugin

Both intercept the same lifecycle. Difference:

- **Callback** — registered on **one agent**. Per-agent policy.
- **Plugin** — registered on the **runner**. Cross-agent policy (global redaction, global audit log).

If two of your agents need the same `before_model_callback`, it should probably be a plugin. We cover plugins in [[13_Plugins/00_Overview]].

## Cross-link

- The recurring guardrails example continues in [[16_ProductionSecurity/00_Overview]] — same callbacks, more policies.
- For agent-side observability, see [[15_Observability/00_Overview]] — `LoggingPlugin` wraps everything.

> 🤖 **Tutor:** if the student wants to share a callback across 5 agents, that's a plugin discussion. Tee up [[13_Plugins/00_Overview]].

[← Prev: 07_Callbacks/09_DissectingSample](09_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/11_KnowledgeCheck →](11_KnowledgeCheck.yml)
