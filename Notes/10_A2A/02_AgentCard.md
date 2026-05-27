---
module: 10_A2A
page: 02_AgentCard
title: AgentCard — the manifest your agent publishes
estimated_minutes: 20
prereqs: [10_A2A/01]
concepts: [AgentCard, AgentSkill, AgentCapabilities, AgentProvider, SecurityScheme]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 10_A2A/01_WhatIsA2A](01_WhatIsA2A.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/03_ServeWithToA2a →](03_ServeWithToA2a.md)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 02 Agent Card

# 🧠 The AgentCard

```python
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
```

The `AgentCard` is the manifest. It's what `/.well-known/agent-card.json` returns. Field tour:

> 🪧 **Path note** — the canonical well-known path is `/.well-known/agent-card.json`. The a2a-sdk also keeps the legacy `/.well-known/agent.json` route alive as a fallback for older callers (see `a2a/utils/constants.py:4` — `PREV_AGENT_CARD_WELL_KNOWN_PATH`). New code (and ADK's `to_a2a()`) should publish at and resolve from the new path.

| Field                             | What it carries                                         |
| --------------------------------- | ------------------------------------------------------- |
| `name`                            | Identifier (alphanumeric, used in URLs).                |
| `description`                     | One-liner for humans and for caller LLMs.               |
| `url`                             | The RPC endpoint (where to POST messages).              |
| `version`                         | Semver string. **This is your API version.**            |
| `capabilities`                    | `AgentCapabilities()` — streaming, push-notify, etc.    |
| `skills`                          | `list[AgentSkill]` — what the agent can do, in detail.  |
| `default_input_modes`             | e.g. `["text/plain"]`.                                  |
| `default_output_modes`            | e.g. `["text/plain"]`.                                  |
| `provider`                        | `AgentProvider(...)` — your org, contact, license URL.  |
| `security_schemes`                | OpenAPI-style auth declarations.                        |

## A minimal hand-built card

```python
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

card = AgentCard(
    name="currency_agent",
    description="An agent that helps with currency conversions.",
    url="http://localhost:10000/",
    version="0.1.0",
    capabilities=AgentCapabilities(),
    skills=[
        AgentSkill(
            id="get_exchange_rate",
            name="get_exchange_rate",
            description="Convert between currencies using current FX rates.",
            tags=["finance", "fx"],
        ),
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
)
```

You don't usually write this by hand. ADK auto-builds one from your agent's `name`, `description`, and tools/skills/sub-agents (via `AgentCardBuilder` in `google/adk/a2a/utils/agent_card_builder.py`). Hand-built is only when you need precise control (e.g. custom auth, custom skill metadata).

## Skills inside the card

The `AgentSkill` entries are the *callable surface* the caller's LLM sees. ADK fills them in by reflecting:

- Every `LlmAgent` tool becomes a skill.
- Every sub-agent becomes a (named) skill bundle.
- Planner / code-executor capabilities show up as skills too.

So your *card* is shaped by what your agent *can do*. If you add a new tool, the card grows.

## Capabilities

```python
AgentCapabilities(
    streaming=True,        # the agent supports SSE streaming responses
    push_notifications=True,  # the agent can push task updates via webhook
)
```

`to_a2a()` enables sensible defaults; override only if you want something specific.

## Auth (security_schemes)

A2A inherits OpenAPI-style security schemes:

```python
from a2a.types import HTTPAuthSecurityScheme

scheme = HTTPAuthSecurityScheme(scheme="bearer", bearer_format="JWT")
```

`SecurityScheme` in `a2a.types` is a **union** wrapper (`APIKeySecurityScheme | HTTPAuthSecurityScheme | OAuth2SecurityScheme | OpenIdConnectSecurityScheme | MutualTLSSecurityScheme`), not a constructor — you instantiate one of the concrete classes (see `a2a/types.py:447` for `HTTPAuthSecurityScheme`, `:1524` for the union). Fields are snake_case (`bearer_format`, not `bearerFormat`). The `type` field defaults to `'http'` on the HTTP scheme so you don't pass it. That's how callers learn *how* to authenticate. The actual enforcement is in your server-side middleware.

## The well-known URL

Spec: the AgentCard lives at `{url}/.well-known/agent-card.json`. ADK's `to_a2a()` wires this route for free.

```
$ curl http://localhost:10000/.well-known/agent-card.json
{
  "name": "currency_agent",
  "description": "An agent that helps with currency conversions.",
  "url": "http://localhost:10000/",
  "version": "0.1.0",
  "capabilities": {...},
  "skills": [...],
  ...
}
```

> 🛠 **Have the student run:** once their currency agent is serving (page 03), `curl /.well-known/agent-card.json` and read the auto-built card aloud.

> 🚀 **In Production**
>
> Bump `version` whenever you change skills, capabilities, or the meaning of the description. Callers cache the card; old versions will mis-route if you change semantics without version bumps. Treat the AgentCard like an OpenAPI spec for an HTTP service.

[← Prev: 10_A2A/01_WhatIsA2A](01_WhatIsA2A.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/03_ServeWithToA2a →](03_ServeWithToA2a.md)
