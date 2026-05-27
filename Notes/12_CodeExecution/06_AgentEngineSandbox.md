---
module: 12_CodeExecution
page: 06_AgentEngineSandbox
title: AgentEngineSandboxCodeExecutor
estimated_minutes: 15
prereqs: [12_CodeExecution/05]
concepts: [AgentEngineSandboxCodeExecutor, Agent Engine, managed deployment]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/05_ContainerAndGke]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/07_DissectingSample →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 06 Agent Engine Sandbox

# ☁️ The Agent-Engine-native executor

When you deploy via **Agent Engine** (the managed Vertex runtime for ADK agents), Google provides a sandbox that's already wired into the deployment. `AgentEngineSandboxCodeExecutor` is the way to opt into it.

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="analyst",
    code_executor=AgentEngineSandboxCodeExecutor(),
)
```

No-arg form auto-creates an agent engine — requires `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` env vars per `agent_engine_sandbox_code_executor.py:53-103`.

Almost no configuration in code: the sandbox lifecycle (start, isolate, tear down) is managed by Agent Engine. Resource limits, networking, and observability flow from your Agent Engine config, not from kwargs here.

## When to use it

- You deploy with Agent Engine (`AdkApp`, `agent_engine_app.py` pattern — see the `memory-bank` sample for the deployment shape).
- You want the lowest-ops option that still gives you a real sandbox (vs the BuiltIn model-side one).

## How it differs from `VertexAiCodeExecutor`

Both are Google-managed sandboxes. The difference is operational:

| | `VertexAi` | `AgentEngineSandbox` |
|--|--|--|
| Deployment context | any | Agent Engine specifically |
| Lifecycle | per-execution | tied to Agent Engine reasoning engine |
| Observability | Vertex logs | Agent Engine traces + Vertex logs |
| Setup | standalone | comes with your Agent Engine deploy |

Rule of thumb: if your deploy target is Agent Engine, prefer `AgentEngineSandboxCodeExecutor`. If your deploy target is a Vertex agent that isn't Agent Engine, prefer `VertexAiCodeExecutor`.

> ❓ **Ask the student:** "Why might a team prefer `VertexAiCodeExecutor` even when deploying on Agent Engine?" *(Expected: parity with their local Vertex-based dev environment; richer per-call kwargs; explicit control over sandbox config.)*

> **🚀 In Production**
>
> If your agent is on Agent Engine, this executor is the path of least resistance. Confirm with your platform team that the Agent Engine sandbox's egress, mem, and timeout defaults match your security policy — they're managed, not invisible.

---

[← Prev: 12_CodeExecution/05_ContainerAndGke]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/07_DissectingSample →]
