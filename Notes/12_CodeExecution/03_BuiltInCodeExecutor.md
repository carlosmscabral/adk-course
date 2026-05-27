---
module: 12_CodeExecution
page: 03_BuiltInCodeExecutor
title: BuiltInCodeExecutor — Gemini's own sandbox
estimated_minutes: 20
prereqs: [12_CodeExecution/02]
concepts: [BuiltInCodeExecutor, model-side execution, package allowlist, request-side mutation]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/02A_SandboxBypassClasses]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/04_VertexAiCodeExecutor →]

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

## Mechanics: a request-side mutation, not a response-side handler

This is the executor where reading the source pays off most — it's only 57 lines.

- `execute_code()` is a no-op `pass` (`built_in_code_executor.py:36-42`). The runtime never calls it for actual work.
- The real work happens in `process_llm_request()` (`:44-57`), which the request pre-processor calls. It mutates `llm_request.config.tools` to append `types.Tool(code_execution=types.ToolCodeExecution())`.
- That's the entire integration: tell Gemini "you have a code-execution tool" via the API request, and let Gemini handle the rest server-side.

This is the wire-level difference from `VertexAiCodeExecutor`: BuiltIn is a **request-side** mutation (you tell the model it has the capability); Vertex is a **response-side** handler (you intercept code parts and ship them to a sandbox). The two are not just different sandboxes — they live in different halves of the request/response cycle.

## Model compatibility

`process_llm_request` checks `is_gemini_eap_or_2_or_above(llm_request.model)` (`:47`) and raises `ValueError("Gemini code execution tool is not supported for model {...}")` (`:54-57`) otherwise. `BuiltInCodeExecutor` + `gpt-4` (via LiteLLM) = startup error. `BuiltInCodeExecutor` + `gemini-1.0-pro` = startup error. The escape hatch is `is_gemini_model_id_check_disabled()` (env-driven, used for tests/private models) — don't disable in prod just to silence the check.

## What this means for tracing

When you iterate over events from `runner.run_async(...)` with a BuiltIn executor, you will **not** see `executable_code` parts in your local event stream. The model executed everything Google-side. Some Gemini responses do include the executed code and its output as `code_execution_result` parts for transparency, but the execution itself is opaque — you have no sandbox to log, no stdout to capture, no per-call timing. This matters for the dissecting page (07) where the contrast with `VertexAiCodeExecutor` becomes visible: with Vertex you get both parts and own the sandbox boundary; with BuiltIn you get neither.

## What's available inside the sandbox

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
| Where on the wire | request-side mutation | response-side handler |

## Sandbox-bypass posture

Per the matrix in `02A_SandboxBypassClasses`: BuiltIn scores **YES** on all four threat classes — it's Google-managed and the sandbox has no network at all. The residual risks are not yours-the-operator's:

- The model can leak conversation history INTO the code it submits (you wrote that history into the prompt; the model can quote it).
- The code-execution result coming back is unconstrained text → downstream prompt-injection vector (anything the model emits is now in the next turn's input).

Neither risk is fixed by switching sandboxes. Both are addressed at the callback / guardrail layer — see `[[16_ProductionSecurity/05_GuardrailsCookbook]]`.

> ⚠️ **Gotcha.** `BuiltInCodeExecutor()` ignores `executable_code` parts in your *own* runtime — they don't get routed back. If you're seeing "model wrote code, runtime did nothing," that's expected for this executor: the execution happened inside Gemini already.

> ❓ **Ask the student:** "Your agent needs a custom pricing library that's not in the Built-In allowlist. Which executor?" *(Expected: a runtime-side one — Vertex with image customization, Container, or GKE.)*

> ❓ **Ask the student:** "I want to log every snippet the model executed. Can I do that with `BuiltInCodeExecutor`?" *(Expected: partially — some responses include the code as a returned part, but you don't own the sandbox, so you can't log stdout/stderr the way you can with a runtime-side executor. If full audit logging is a requirement, use `VertexAiCodeExecutor` or higher.)*

> 🚀 **In Production**
>
> `BuiltInCodeExecutor` is the right default for the "math / plot only" subset.
> Cheap, no extra infra, but you cannot bring custom code or data files. For
> anything richer, see 04-06. Don't reach for the model-id check-disable env
> var to silence Gemini-2-required errors — those errors are saving you from
> wiring this executor against a model that won't honor the tool.

---

[← Prev: 12_CodeExecution/02A_SandboxBypassClasses]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/04_VertexAiCodeExecutor →]
