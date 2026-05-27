---
module: 3A_ProjectStructure
page: 07_SharedUtilities
title: Shared utilities — when one agent isn't enough
estimated_minutes: 15
prereqs: [3A_ProjectStructure/06]
concepts: [shared-package, monorepo-of-agents, auth-helpers, common-tools]
icon: 🧰
in_production: true
detours_suggested: [PY_packaging]
---

[← Prev: 06_DeploymentExpectations](06_DeploymentExpectations.md)  [↑ Map](../../MAP.md)  [Next: 07A_ConfigAndEnvVars →](07A_ConfigAndEnvVars.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 07 Shared utilities

# 🧰 Shared utilities — `shared/` across agents

> 🤖 **Tutor:** this page applies **only** when the student has (a) two sub-agents that genuinely use the same helper, or (b) two top-level agents in a monorepo that need a common library. Premature `shared/` directories are the most common over-structuring mistake in ADK projects.

## Within a single agent — `shared/` (or `shared_libraries/`)

When two sub-agents both need the same auth wrapper or the same retry policy:

```
my_agent/
├── agent.py
├── sub_agents/
│   ├── critic/
│   │   └── agent.py             ← imports from ..shared.auth
│   └── reviser/
│       └── agent.py             ← imports from ..shared.auth
└── shared/
    ├── __init__.py
    ├── auth.py                  ← BigQuery client factory, token refresher
    ├── retry.py                 ← @retry decorator with backoff
    └── types.py                 ← Pydantic models used by >1 sub-agent
```

```python
# my_agent/shared/auth.py
import functools
from google.cloud import bigquery

@functools.cache
def bigquery_client(project: str) -> bigquery.Client:
    """Return a process-wide BigQuery client for `project`."""
    return bigquery.Client(project=project)
```

```python
# my_agent/sub_agents/critic/agent.py
from ...shared.auth import bigquery_client    # ← three dots = up to my_agent

def lookup_fact(query: str) -> dict:
    client = bigquery_client("my-project")
    ...
```

Real samples that use this exact pattern:

- `customer-service/customer_service/shared_libraries/callbacks.py` — shared `before_*` callbacks.
- `travel-concierge/travel_concierge/shared_libraries/constants.py` — Pydantic types reused across sub-agents.

The plural `shared_libraries/` is Google's convention; `shared/` is shorter and equally fine. Pick one and be consistent across your codebase.

## Across agents — the monorepo of agents

When you have **multiple agent packages** that share code:

```
my_org/
├── pyproject.toml             ← root project; depends on all agents
├── shared/                    ← installable package, shared across agents
│   ├── pyproject.toml         ← packages = ["shared"]
│   └── shared/
│       ├── __init__.py
│       ├── auth.py
│       └── retry.py
├── agents/
│   ├── auditor/
│   │   ├── pyproject.toml     ← depends on shared/
│   │   └── auditor/
│   │       └── agent.py       ← from shared.auth import ...
│   └── researcher/
│       ├── pyproject.toml     ← depends on shared/
│       └── researcher/
│           └── agent.py
└── README.md
```

Each agent has its own `pyproject.toml` listing `shared` as a dependency. The `shared/` package becomes a first-class wheel — testable in isolation, versionable, optionally publishable to a private index.

> ⚠️ **The monorepo is a serious commitment.** Once you split agents into separate packages with cross-deps, you need a strategy for: shared CI, version bumps, locking inner deps so updating `shared` doesn't break `auditor`. Don't do this for fun. Do it when you have at least two agents in production and at least one piece of code they both genuinely need to call.

## What does *not* belong in `shared/`

- **Tools that only one agent uses.** Those live in that agent's `tools/`.
- **Prompts.** Prompts are agent-specific; sharing them is almost always a "we'll regret this" decision.
- **Config that's environment-dependent.** Use `.env` and `os.environ`, not a `shared/config.py` that hard-codes per-env values.

## What *does* belong in `shared/`

- Auth helpers (token refresh, credential factories).
- Retry / backoff wrappers (`@retry` decorators).
- Pydantic types that appear in >1 agent's tool signatures.
- Telemetry / tracing setup (one OpenTelemetry init shared by N agents).
- DB / cache clients (one BigQuery client, one Redis pool).

## When to *not* put it in `shared/`

If only one agent calls it today and there's no concrete plan for a second caller, **leave it in that agent's `tools/` or `shared/`**. You can promote it later in 5 minutes. The reverse (extracting a shared module back into one agent because no one else ever used it) takes hours and bruises egos.

> **🚀 In Production**
>
> The monorepo-of-agents pattern shows up at teams running >3 agents in prod. **Below that threshold, every agent is its own repo with its own `pyproject.toml`** and there is no monorepo. Don't pre-monorepo — you can always merge later. We connect this to deployment in [10_InProduction](10_InProduction.md).

> 🛠 **Have the student** grep `adk-samples/python/agents/` for `shared_libraries`:
>
> ```bash
> find /home/carloscabral/study/adk-samples/python/agents -name "shared_libraries" -type d
> ```
>
> Count: how many of the 75 samples use it? *(Answer: a small minority. Most are single-agent and don't need it. Don't over-rotate on a pattern that the majority of working code doesn't use.)*

> ❓ **Ask the student:** "Two sub-agents both need a function `redact_pii(text: str) -> str`. They use it identically. Where does it go?"
>
> *(Expected: `my_agent/shared/redact.py`, with `from ...shared.redact import redact_pii` in each sub-agent. Not in either sub-agent's `tools/` — that creates duplication.)*

---

[← Prev: 06_DeploymentExpectations](06_DeploymentExpectations.md)  [↑ Map](../../MAP.md)  [Next: 07A_ConfigAndEnvVars →](07A_ConfigAndEnvVars.md)
