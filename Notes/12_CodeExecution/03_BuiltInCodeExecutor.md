---
module: 12_CodeExecution
page: 03_BuiltInCodeExecutor
title: BuiltInCodeExecutor — Gemini's own sandbox
estimated_minutes: 15
prereqs: [12_CodeExecution/02]
concepts: [BuiltInCodeExecutor, model-side execution, package allowlist]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/02_UnsafeLocalCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/04_VertexAiCodeExecutor →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 03 BuiltIn

# ☁️ BuiltInCodeExecutor: the model runs it itself

Some Gemini models can execute code *inside Google's infrastructure*, with no roundtrip back to your runtime. The LLM writes code, runs it Google-side, and incorporates the result into the very same response.

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="math_helper",
    instruction="Use the code execution capability for arithmetic and small data tasks.",
    code_executor=BuiltInCodeExecutor(),
)
```

From your runtime's perspective, no `executable_code` part ever crosses the wire. You get the final text (with the computation already done) plus, optionally, a code-execution-result part for transparency.

## What's available

- A curated set of Python packages (numpy, pandas, sympy, matplotlib, statsmodels, etc.). The exact allowlist is model- and version-dependent — check the model's docs.
- A short execution timeout (seconds, not minutes).
- No outbound network. No filesystem. No long-running processes.

## When to use it

- Math, stats, symbolic algebra.
- Chart generation (the model can return the image as an inline part).
- Anything pure-computational where you don't need custom packages.

## Trade-offs vs the runtime-side executors

| Property | BuiltIn | Runtime-side (Vertex/Container/etc.) |
|----------|---------|--------------------------------------|
| Package control | Google's allowlist | yours |
| Custom files | no | yes (`ContainerCodeExecutor` mounts) |
| Latency | one round trip total | two |
| Cost | rolled into model billing | sandbox + model |
| Debuggability | partial (you see the code) | full (you own the sandbox logs) |

> ⚠️ **Gotcha.** `BuiltInCodeExecutor()` ignores `executable_code` parts in your *own* runtime — they don't get routed back. If you're seeing "model wrote code, runtime did nothing," that's expected for this executor: the execution happened inside Gemini already.

> ❓ **Ask the student:** "Your agent needs a custom pricing library that's not in the Built-In allowlist. Which executor?" *(Expected: a runtime-side one — Vertex with image customization, Container, or GKE.)*

> **🚀 In Production**
>
> `BuiltInCodeExecutor` is the right default for the "math / plot only" subset. Cheap, no extra infra, but you cannot bring custom code or data files. For anything richer, see 04-06.

---

[← Prev: 12_CodeExecution/02_UnsafeLocalCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/04_VertexAiCodeExecutor →]
