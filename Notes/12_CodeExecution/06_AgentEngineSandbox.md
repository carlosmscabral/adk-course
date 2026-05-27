---
module: 12_CodeExecution
page: 06_AgentEngineSandbox
title: AgentEngineSandboxCodeExecutor — the Agent-Engine-native sandbox
estimated_minutes: 20
prereqs: [12_CodeExecution/05A]
concepts: [AgentEngineSandboxCodeExecutor, Agent Engine, sandbox lifecycle, per-session sandbox, TTL semantics]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/05A_GkeCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/07_DissectingSample →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 06 Agent Engine Sandbox

# ☁️ The Agent-Engine-native executor

When you deploy via **Agent Engine** (the managed Vertex runtime for ADK agents), Google provides a code-execution sandbox that's already wired into the deployment. `AgentEngineSandboxCodeExecutor` is the way to opt into it.

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="analyst",
    code_executor=AgentEngineSandboxCodeExecutor(),
)
```

Almost no configuration in code. The sandbox lifecycle (start, run, persist between calls in a session, tear down) is managed for you. Resource limits, networking, and observability flow from your Agent Engine config, not from kwargs here.

## Mechanics: three init modes + per-session sandboxes

`agent_engine_sandbox_code_executor.py` is 258 lines, and the constructor + first call do more than the kwargs suggest.

**Three init modes** (`:79-103`):

| You pass | What happens |
|---|---|
| `sandbox_resource_name="projects/.../sandboxEnvironments/789"` | Load an existing sandbox. No creation. Project/location parsed out of the resource name (`:81-86`). |
| `agent_engine_resource_name="projects/.../reasoningEngines/456"` | Use an existing reasoning engine; a sandbox will be created under it on first call (`:97-103`). |
| Neither | Read `GOOGLE_CLOUD_PROJECT` from env, `GOOGLE_CLOUD_LOCATION` (defaults to `"us-central1"`), then **lazy-create the agent engine itself** on first call (`:91-93, :115-129`). |

The no-arg form is the convenient one but it has a hidden cost: the first `execute_code()` call creates a brand-new agent engine via `self._get_api_client().agent_engines.create()` (`:122`). That's a one-time control-plane operation, but it's not free — and it happens lazily, so it's the first execution that pays the latency, not import time. Production: pin a resource name (sandbox or engine) and skip the auto-create entirely.

**Per-session sandbox** (`:131-173`):

Once the engine exists, the executor doesn't make one sandbox per executor — it makes **one sandbox per session**. The sandbox name lives in `invocation_context.session.state['sandbox_name']` (`:138, :173`). Each `execute_code()` call:

1. Reads `sandbox_name` from session state (`:138`).
2. If not present, or if `agent_engines.sandboxes.get(name=sandbox_name)` returns a sandbox whose `state != 'STATE_RUNNING'`, or a 404 — flag `create_new_sandbox = True` (`:140-156`).
3. If flagged, create a fresh sandbox with `display_name='default_sandbox'`, `ttl='31536000s'` (one year), and store the new name back into session state (`:158-173`).

This gives you stateful kernel execution per session (same shape as `VertexAiCodeExecutor(stateful=True)`) plus automatic recovery if a sandbox is gone — without you having to handle it.

**TTL: the 14-day gotcha** (`:163-170`):

The sandbox *resource* has a 1-year TTL (matching `VertexAiSessionService`'s default), but the in-line comment names a separate, sharper constraint: **if the sandbox hasn't been used for 14 days, the kernel state is lost.** A returning user-after-three-weeks gets a `STATE_RUNNING` sandbox with a fresh kernel, not their old `df`. The framework recovers (it just executes against the empty kernel), but the user's mental model of "my agent remembers" silently breaks. Surface this in product copy or rebuild context before the first call.

## Output handling: stdout, stderr, files

Per `:196-227`: the response splits each output by mime type. `application/json` outputs without a `file_name` attribute are parsed as the stdout/stderr envelope (`msg_out`, `msg_err` at `:206-207`); anything else lands in `saved_files` (`:220-226`). So a snippet that emits `print(...)` and `plt.savefig('chart.png')` returns both `stdout` text and a `chart.png` file part — the latter flows back through the runtime as an inline file attachment.

## When to use it

- You deploy with Agent Engine (`AdkApp`, `agent_engine_app.py` pattern — see the `memory-bank` sample).
- You want the lowest-ops option that still gives you a real sandbox (vs the BuiltIn model-side one).
- You want stateful kernels per session managed for you (no Container/GKE-side wiring).

## How it differs from `VertexAiCodeExecutor`

Both are Google-managed sandboxes. The differences are operational:

| | `VertexAi` | `AgentEngineSandbox` |
|--|--|--|
| Deployment context | any | Agent Engine specifically |
| Backing extension | code-interpreter extension (Vertex Extensions) | Agent Engine reasoning engine + sandbox resource |
| Sandbox-per-what | shared kernel keyed by `session_id` | one sandbox resource per session, stored in `state['sandbox_name']` |
| Auto-create posture | extension auto-created and cached via `CODE_INTERPRETER_EXTENSION_NAME` env var | agent engine + sandbox auto-created on first call if neither resource name is pinned |
| State-loss boundary | session_id reuse | 14-day idle window |
| Setup | standalone | comes with your Agent Engine deploy |

Rule of thumb: if your deploy target is Agent Engine, prefer `AgentEngineSandboxCodeExecutor`. If your deploy target is a Vertex agent that isn't Agent Engine, prefer `VertexAiCodeExecutor`. Don't mix and match across the same product without a reason — your eval set and your observability tooling will diverge.

## Sandbox-bypass posture

Per the `02A` matrix: filesystem, env, and privilege-escalation all **YES** (Google-managed). Network egress is **◐ PARTIAL** — same caveat as Vertex: Google's allowlist applies, you can't extend it, and you can't shrink it to "no egress" either. Same answer as Vertex: confirm the current allowlist with your security team before shipping a workflow that depends on no exfil.

> ⚠️ **Gotcha #1.** The no-arg form raises only when the first `execute_code()` runs — not at construction. If you import the executor at module load and `GOOGLE_CLOUD_PROJECT` is unset, you won't find out until the agent gets its first user turn. Set it explicitly in your deploy env or pin a `sandbox_resource_name`.

> ⚠️ **Gotcha #2.** The 14-day state-loss window is a product surface, not just an infra detail. If your agent advertises "I remember our last analysis," a user returning 3 weeks later silently gets a fresh kernel — but a populated session transcript. The model's narrative will mismatch its actual state. Pre-load the kernel at session resume, or down-scope your product claims.

> ❓ **Ask the student:** "You construct `AgentEngineSandboxCodeExecutor()` with no args inside a unit test. It doesn't blow up at construction time but does at first call. Why?" *(Expected: the lazy auto-create lives inside `execute_code()`, not `__init__`. The constructor just records `agent_engine_resource_name = None`; the call site is where the API hit happens.)*

> ❓ **Ask the student:** "Two sessions hit the same `AgentEngineSandboxCodeExecutor` instance — same `df = pd.read_csv(...)` defined in session A's first turn. Will session B see `df`?" *(Expected: no. Sandbox is per-session via `state['sandbox_name']`; session B gets a different sandbox name, hence a different kernel.)*

> 🚀 **In Production**
>
> Pin either `sandbox_resource_name` or `agent_engine_resource_name` in your deploy
> config. The no-arg auto-create is great for local exploration and terrible for
> production: it adds an opaque control-plane call to the first user turn and
> creates an Agent Engine your IaC doesn't know about. If you also use
> `VertexAiSessionService`, align its TTL with the sandbox's 14-day kernel-loss
> window — either document the cliff to the user, or pre-warm kernel state on
> session resume. Confirm the managed egress allowlist matches your security
> policy; if it doesn't, you want `GkeCodeExecutor` with your own `NetworkPolicy`,
> not this.

---

[← Prev: 12_CodeExecution/05A_GkeCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/07_DissectingSample →]
