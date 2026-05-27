---
module: 12_CodeExecution
page: 04_VertexAiCodeExecutor
title: VertexAiCodeExecutor — the managed default
estimated_minutes: 20
prereqs: [12_CodeExecution/03]
concepts: [VertexAiCodeExecutor, stateful execution, optimize_data_file]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/03_BuiltInCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05_ContainerAndGke →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 04 VertexAi

# ☁️ VertexAiCodeExecutor: Google-managed runtime-side sandbox

This is the prod default for Vertex-hosted agents. Code runs in a Google-managed sandbox (the Vertex code interpreter), with stronger isolation than UnsafeLocal and more flexibility than BuiltIn.

```python
from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor

analytics_agent = Agent(
    model="gemini-2.5-flash",
    name="analytics_agent",
    instruction="Generate Python (pandas/numpy/matplotlib) to answer the user's data question.",
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,  # uploaded data files persist between executions
        stateful=True,            # variables persist across calls in one session
    ),
)
```

(Adapted from `adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py`.)

## The two knobs

- **`stateful=True`** — across multiple code-exec calls in the same session, the Python kernel persists. The model can define `df = pd.read_csv(...)` in one turn and reference `df.describe()` in the next. **Off**, each call starts a fresh interpreter. Stateful is what makes the "data analyst" UX feel natural.
- **`optimize_data_file=True`** — uploaded data artifacts (CSVs, parquet) are made available to the sandbox without re-uploading on every call.

## What the model sees

Same `executable_code` / `code_execution_result` part dance from page 01. The runtime ships the code to the Vertex code interpreter, awaits the result, returns it as a `code_execution_result` part on the next model turn.

## When to choose it

- You're deploying on Vertex AI (Agent Engine or not).
- You want Google to operate the sandbox.
- You don't need OS-level customization (custom binaries, specific Linux libs) beyond what the sandbox ships.

## What you lose vs Container/GKE

- You don't control the image. If you need a niche compiled library, you can't apt-get it in.
- Outbound network from the sandbox is restricted by Vertex policy, not yours.
- Sandbox lifetime is managed; you can't pin it to a node.

> ❓ **Ask the student:** "Why is `stateful=True` better for an analytics workflow but worse for a one-shot calculator?" *(Expected: stateful adds context cost between calls and creates coupling; for a stateless one-shot you want the kernel reset.)*

> 🛠 **Have the student run:** Take the agent above, point it at a small CSV via Vertex artifact upload, ask "what's the mean of column 'price'?" Watch the executable_code part in the trace.

> **🚀 In Production**
>
> `VertexAiCodeExecutor` is the right default when you're already on Vertex. Set explicit per-execution timeouts and a memory ceiling at deploy time; don't accept defaults silently. Audit-log the executed code (see `15_Observability`).

---

[← Prev: 12_CodeExecution/03_BuiltInCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05_ContainerAndGke →]
