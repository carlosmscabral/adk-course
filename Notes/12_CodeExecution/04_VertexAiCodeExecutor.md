---
module: 12_CodeExecution
page: 04_VertexAiCodeExecutor
title: VertexAiCodeExecutor — the managed default
estimated_minutes: 30
prereqs: [12_CodeExecution/03]
concepts: [VertexAiCodeExecutor, stateful execution, optimize_data_file, Vertex code interpreter extension]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/03_BuiltInCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05_ContainerCodeExecutor →]

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
        optimize_data_file=True,  # extracts CSV data files from the request and attaches them to the executor
        stateful=True,            # variables persist across calls in one session
    ),
)
```

(Adapted from `adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py`.)

## Under the hood

`vertex_ai_code_executor.py` is 242 lines and worth a glance — three pieces matter for prod operation.

- **Extension load-or-create** (`:88-104`, `_get_code_interpreter_extension`): on first instantiation, the executor either loads the extension named in the `CODE_INTERPRETER_EXTENSION_NAME` env var or creates a fresh one via `Extension.from_hub('code_interpreter')`. **Side effect** (`:101-103`): if it creates one, it writes the new resource name back into the env var. Subsequent constructions in the same Python process reuse the extension; subsequent processes do not (unless you persist the env var). This is a one-line cost optimization: pin `CODE_INTERPRETER_EXTENSION_NAME` to a stable resource name in your deploy and you skip the creation hop forever.
- **Pre-imported library list** (`:36-85`, `_IMPORTED_LIBRARIES`): every submission has `io, math, re, matplotlib.pyplot as plt, numpy as np, pandas as pd, scipy` plus two helpers (`crop()` for string truncation, `explore_df()` for DataFrame previews) injected at the top via `_get_code_with_imports` (`:229-242`). The model never has to write the imports. **This is why analytics-agent prompts say "the following libraries are ALREADY imported" — the executor enforces it, the prompt mirrors it.** Drift between the two and the model wastes tokens re-importing.
- **Operation params** (`:200-227`, `_execute_code_interpreter`): the actual call ships `{'code': ..., 'files': [...], 'session_id': ...}` to the extension's `execute` operation. `session_id` is the entire mechanism behind `stateful=True` — passing it tells the extension "reuse the kernel for this session"; omitting it asks for a fresh kernel.

## The two knobs

- **`stateful=True`** — across multiple code-exec calls in the same session, the Python kernel persists. The model can define `df = pd.read_csv(...)` in one turn and reference `df.describe()` in the next. Off, each call starts a fresh interpreter. Stateful is what makes the "data analyst" UX feel natural.
- **`optimize_data_file=True`** — uploaded data artifacts (CSVs, parquet) are made available to the sandbox without re-uploading on every call.

## Stateful execution: what it actually costs

This is the most-misunderstood knob in the executor lineup. The cost isn't on the Vertex side (kernel state is cheap to keep alive); the cost is in your model's context window.

The mechanism is asymmetric:
- **Vertex side**: the extension keeps the Python kernel alive between calls for one `session_id`. `df = pd.read_csv(...)` once, `df.describe()` later — same `df`. Cheap and fast.
- **Model side**: the LLM never sees kernel state directly. It only sees the conversation transcript — which means every turn's prior `tool_outputs` (the `code_execution_result` parts the executor emitted) accumulate in the model's input on the next turn.

A worked example (illustrative, order-of-magnitude — verify against your own logs):
- Turn 1: model emits 80 tokens of code; sandbox returns 400 tokens of result. Cost: 480 tokens output + ~400 tokens of context going forward.
- Turn 2: model emits 80 more tokens; result is 400. Context now carries the previous result. Cumulative context: ~800 tokens of tool_outputs.
- Turn 5: ~4 prior `tool_outputs` × ~500 tokens preview ≈ **2000 extra input tokens** on top of the system prompt + user history.
- Turn 20: ~10000 extra input tokens. On Pro pricing this matters; on Flash pricing it's noise. Verify against your model's price card.

**When stateful wins**: iterative data-analyst conversations ("now sort by date", "now plot it") where the kernel state IS the value. Recomputing `pd.read_csv` from scratch every turn is 10× the latency. The `data-science` analytics agent uses `stateful=True` for exactly this reason (`analytics/agent.py:28-31`).

**When stateful loses**: one-shot calculators where the kernel state isn't reused. You pay the context-bloat tax for nothing. Default `stateful=False` unless the agent's UX is multi-turn data analysis.

**In production**: monitor average turns-per-session per agent. If the average is < 3, you're paying stateful context cost without the UX benefit; flip the knob.

## `optimize_data_file=True` mechanics

The flag changes the request preprocessor's behavior (`_code_execution.py:190-205, 172-264`). Without it, data attached to a user turn is re-uploaded on every code execution. With it: the preprocessor extracts CSV blobs once, runs `explore_df()` to cache the schema, stores `processed_input_files` in session state, and skips re-processing thereafter (`code_executor_context.py:78-96` is where the `_processed_file_names` cache lives).

Only `text/csv` is supported — the data-file utility map (`_code_execution.py:70-75`) hardcodes it. Parquet, JSON, XLSX: not auto-optimized. If your agent works on Parquet, the optimization flag has no effect.

## What the model sees

Same `executable_code` / `code_execution_result` part dance from page 01. The runtime ships the code to the Vertex code interpreter, awaits the result, returns it as a `code_execution_result` part on the next model turn. See `_figures/code_exec_event_flow.txt`.

## When to choose it

- You're deploying on Vertex AI (Agent Engine or not).
- You want Google to operate the sandbox.
- You don't need OS-level customization (custom binaries, specific Linux libs) beyond what the sandbox ships.

## What you lose vs Container/GKE

- You don't control the image. If you need a niche compiled library, you can't apt-get it in.
- Outbound network from the sandbox is restricted by Vertex policy, not yours — a `◐ PARTIAL` cell in the `02A` bypass matrix.
- Sandbox lifetime is managed; you can't pin it to a node.

## Sandbox-bypass posture

Per the `02A` matrix: filesystem/env/priv-esc all **YES** (Google-managed); network egress **◐ PARTIAL** (vendor-managed allowlist — your team can't extend it for "we need to call our internal API," and the model can still hit whatever Google allows). If you have a strict "no egress" policy, confirm what the current Vertex allowlist looks like before you ship — the policy is theirs, not yours.

> ❓ **Ask the student:** "Why is `stateful=True` better for an analytics workflow but worse for a one-shot calculator?" *(Expected: stateful adds context cost between calls and creates coupling; for a stateless one-shot you want the kernel reset and the smaller transcript.)*

> ❓ **Ask the student:** "Your analytics agent has been in service for a week. How would you decide whether `stateful=True` is paying for itself?" *(Expected: measure avg turns-per-session; if < 3, flip it off and re-measure latency/cost.)*

> 🛠 **Have the student run:** Take the agent above, point it at a small CSV via Vertex artifact upload, ask "what's the mean of column 'price'?" Then ask "and the median?" Watch the second turn's trace — with `stateful=True`, the model writes `df.price.median()` without re-loading the CSV.

> 🚀 **In Production**
>
> `VertexAiCodeExecutor` is the right default when you're already on Vertex.
> Pin `CODE_INTERPRETER_EXTENSION_NAME` in your deploy env so you don't pay
> the extension-creation cost on every cold start. Set explicit per-execution
> timeouts (`timeout_seconds=`, default `None` per `base_code_executor.py:79-80`)
> and a memory ceiling. Audit-log the executed code via the
> `_code_execution_results` session-state key (`code_executor_context.py:167-191`)
> — see `[[15_Observability]]`. Default `stateful=False` unless the UX is
> multi-turn data analysis; revisit quarterly.

---

[← Prev: 12_CodeExecution/03_BuiltInCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05_ContainerCodeExecutor →]
