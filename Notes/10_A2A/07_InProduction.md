---
module: 10_A2A
page: 07_InProduction
title: A2A in production — versioning, auth, rate-limit, observability, sticky sessions
estimated_minutes: 20
prereqs: [10_A2A/06]
concepts: [versioning, auth, rate_limit, sticky_session, observability, load_balancer]
icon: 🚀
in_production: true
detours_suggested: [a2UI]
---

[← Prev: 10_A2A/06_DissectingSample](06_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/08_KnowledgeCheck →](08_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 10 A2A ▸ 07 In Production

# 🚀 Production checklist for A2A

## AgentCard is your public contract — version it

- Bump `version` on every change to skills, capabilities, or description semantics.
- Serve old versions at versioned URLs (`/v1/.well-known/agent.json`) until callers migrate.
- Treat the AgentCard like an OpenAPI spec: changelog, deprecation notices, sunset dates.

## Real auth (not just network ACLs)

The defaults are open. Production needs:

- **Bearer / OAuth** on the RPC endpoint. Enforce in Starlette middleware before requests reach the agent.
- **Declare it in the AgentCard's `security_schemes`** so callers know how to authenticate.

```python
from a2a.types import SecurityScheme

scheme = SecurityScheme(type="http", scheme="bearer", bearerFormat="JWT")
```

Network ACLs are defense in depth, never the only line.

## Rate-limit per caller

A single misbehaving caller can hammer your agent into the ground. Put a rate limiter in front:

- Per-token / per-IP (Cloud Armor, Kong, Envoy).
- Cap concurrent in-flight tasks per caller via your `TaskStore`.

## Observe latency end-to-end

A single A2A request can fan out to:

- caller → A2A endpoint (HTTP) → agent loop (LLM) → tools (MCP) → external API.

Trace propagation: pass a request id from caller through `before_agent_callback`, log at each hop. The minimum metrics:

- A2A request latency (your endpoint's RT).
- Per-turn LLM latency.
- Per-tool MCP latency (Module 08 page 07).
- End-to-end success rate.

See [[15_Observability/00_Overview]] for the wiring.

## Sticky sessions IF the agent maintains state in-process

`to_a2a()` uses **in-memory** task / session stores by default. If you scale to >1 replica and your LB does round-robin, a multi-turn conversation will hit a fresh replica halfway through and lose context.

Two cures:

1. **Persistent stores** (preferred). Swap in `DatabaseSessionService` and `DatabaseTaskStore` so any replica can resume.
2. **Sticky sessions** on the LB (consistent hashing by `context_id`). Lower scale ceiling but simpler.

```python
to_a2a(
    agent,
    port=10000,
    task_store=DatabaseTaskStore(engine=db_engine),
    runner=Runner(
        app_name="my_agent",
        agent=agent,
        session_service=DatabaseSessionService(db_url),
    ),
    lifespan=cleanup_lifespan,
)
```

## RemoteA2aAgent: client-side hardening

When you consume a remote:

- Use a shared `httpx.AsyncClient` so connections pool.
- Set a `timeout` (default is generous; tighten for your SLO).
- Wrap with `on_tool_error_callback` for graceful fallback.
- Pin the URL to a version path.

## Cross-link

- For the recurring guardrails example, see [[16_ProductionSecurity/00_Overview]].
- For session state persistence, recap [[04_SessionsState/00_Overview]].
- For multi-agent composition with A2A children, see [[05_MultiAgent/00_Overview]].
- Milestone M3 (Federated Travel Planner) puts every piece together.
- For visually composing agent-to-agent flows, see [[a2UI]].

> 🤖 **Tutor:** if the student plans to run A2A on a single VM, that's fine for dev. As soon as they think about replicas, drag in the sticky-session / persistent-store discussion.

[← Prev: 10_A2A/06_DissectingSample](06_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 10_A2A/08_KnowledgeCheck →](08_KnowledgeCheck.yml)
