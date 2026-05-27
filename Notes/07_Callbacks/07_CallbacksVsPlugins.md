---
module: 07_Callbacks
page: 07_CallbacksVsPlugins
title: Callbacks vs Plugins — when to reach for which
estimated_minutes: 20
prereqs: [07_Callbacks/06]
concepts: [callbacks, plugins, scope, runner, per-agent, cross-cutting]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 07_Callbacks/06_CallbackRecipeCookbook](06_CallbackRecipeCookbook.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/08_ErrorCallbacks →](08_ErrorCallbacks.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 07 Callbacks vs Plugins

# 🧠 Same hooks, different scope

Callbacks and plugins (Module 13) hook the **same lifecycle**. They are not competing — they are stacked layers. The right question is "where does this policy belong?" Use this page as the decision rubric before you write either.

## 🧠 The 30-second mental model

```
┌─────────────────────────── Runner ──────────────────────────┐
│                                                              │
│   ┌──── plugin: LoggingPlugin ───────────────────────────┐  │  ← runner-wide
│   ┌──── plugin: ContextFilterPlugin ─────────────────────┐  │
│                                                              │
│   ┌───────── Agent A ──────────┐  ┌──── Agent B ────────┐   │
│   │  callback: pii_redact      │  │  callback: cite     │   │  ← per-agent
│   │  callback: rate_limit      │  │                     │   │
│   └────────────────────────────┘  └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

A plugin fires for **every agent under that runner**. A callback fires for **the one agent it's registered on**.

## 🧠 The decision rubric

| Question | Answer → reach for |
|---|---|
| Does this policy depend on the specific agent's prompt or tools? | **Callback** |
| Should this apply to ALL agents in the app uniformly? | **Plugin** |
| Are you adding it to ≥ 3 agents already? | **Plugin** (refactor) |
| Is the policy tied to a feature flag per agent? | **Callback** |
| Are you observing for telemetry / metrics / audit? | **Plugin** |
| Is the policy security-critical (PII, prompt injection, money caps)? | **Plugin** (with a callback fallback) |
| Will the team write more than one of these? | **Plugin** (registry pattern) |

## 🧠 Concrete worked examples

* **PII redaction across the whole product** → plugin. Every agent benefits; one source of truth.
* **PII redaction in the customer-facing agent only** → callback. The internal admin agent is allowed to see emails.
* **Audit log** → plugin. Always. (`LoggingPlugin` is the canonical example.)
* **Per-agent rate limit** → callback. Each agent has its own budget.
* **Global rate limit by user** → plugin.
* **Tool guard ("no `rm -rf`")** → callback on the agent that has the shell tool. The other agents don't have a shell tool, the guard is meaningless there.

## 🧠 Mutation semantics differ

```python
# Callback — registered ON the agent
agent = Agent(
    ...,
    before_model_callback=[guardrail, cache_check],   # list also accepted
)

# Plugin — registered ON the runner
runner = Runner(
    agent=agent,
    app_name="x",
    session_service=ses,
    plugins=[LoggingPlugin(), MyPolicyPlugin()],      # plugins STACK
)
```

* **Callbacks stack per agent.** Every `*_callback` field on `LlmAgent` is typed `Union[Callable, list[Callable]]` (see `llm_agent.py:75-87`). Pass a list and ADK runs them in declared order; the first to return a non-`None` value short-circuits the rest (and, for `before_model_callback`, replaces the LLM call). You can still compose by hand when you need conditional plumbing between steps (page 06).
* **Plugins stack runner-wide.** Order matters: they fire in list order on the "before" side, reverse order on the "after" side (LIFO).

## 🧠 The promotion path

A callback graduates to a plugin in three steps:

1. You wrote the callback on Agent A.
2. You copy-pasted it onto Agent B.
3. The third request to add it to Agent C — **promote**.

```python
# from per-agent callback (07/06):
def per_user_limit(ctx, llm_request): ...

# to a plugin (13/04):
class PerUserLimitPlugin(BasePlugin):
    async def before_model_callback(self, callback_context, llm_request):
        return per_user_limit(callback_context, llm_request)
```

The function body doesn't change. The shell does.

## ⚠️ Two anti-patterns

1. **Cross-agent state shared via a plugin global.** Don't. Plugins are stateless across requests; use `state["app:..."]` for shared state.
2. **Callback that does cross-cutting observability.** Audit logs that only fire for one of your eight agents will eventually leave you blind. Promote to a plugin.

## 🧠 The full surface map

| Surface | Scope | Stacks? | Where it lives | Module |
|---|---|---|---|---|
| Callback | One agent | Yes — pass a list (per-agent) | `Agent(before_model_callback=[...])` | 07 (this) |
| Plugin | One runner (all agents under it) | Yes — module-wide | `Runner(plugins=[...])` | 13 |
| Tool guard | All uses of one tool | One per tool | tool definition | 03 |
| `output_schema=` | One agent's reply shape | n/a | `Agent(output_schema=Model)` | 17 |

## ❓ Quiz

> ❓ **Ask the student:** you've written `pii_redact` as a callback on three different agents. A fourth agent is being added next sprint. Should it be a callback again?
> *(Expected: no — promote to a plugin. The "rule of three" applies: by the third copy you have a refactor, by the fourth you have a fire. Plugin gives one place to update the regex, one place to test, one place to disable for the admin agent (you can scope plugins per runner).)*

> 🛠 **Have the student do this:** take the `redact_pii` recipe from page 06 and rewrite it as a `BasePlugin` subclass. Wire it to a runner with two agents. Confirm it fires on both without either agent declaring it.

> **🚀 In Production**
>
> Security-critical policies (PII, auth, money caps) belong as **plugins** so they are uniform and auditable. A per-agent callback that someone forgets to wire on the next agent IS the vulnerability. The standard pattern in production: plugins for guardrails, callbacks for agent-specific behavior tweaks.

[← Prev: 07_Callbacks/06_CallbackRecipeCookbook](06_CallbackRecipeCookbook.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/08_ErrorCallbacks →](08_ErrorCallbacks.md)
