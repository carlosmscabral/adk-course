---
module: 12_CodeExecution
page: 07_DissectingSample
title: Dissecting the data-science analytics sub-agent
estimated_minutes: 45
prereqs: [12_CodeExecution/04, 12_CodeExecution/06]
concepts: [sample read-through, VertexAiCodeExecutor in practice, stateful=True, prompt-executor coupling, multi-agent code-exec wiring]
icon: 🧪
in_production: false
detours_suggested: [GeminiPayload]
---

[← Prev: 12_CodeExecution/06_AgentEngineSandbox]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/08_InProduction →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 07 Dissecting data-science

# 🧪 A real `VertexAiCodeExecutor` in the wild

Sample: `adk-samples/python/agents/data-science/`

This is the deepest code-execution sample in `adk-samples`. The root agent is a multi-agent system; among its sub-agents, `analytics_agent` is the one that actually executes Python. Four files matter for this dissection:

```
data-science/
└── data_science/
    ├── agent.py                          ← root multi-agent (213 lines)
    ├── tools.py                          ← AgentTool wrappers for the sub-agents (127 lines)
    └── sub_agents/
        ├── analytics/
        │   ├── agent.py                  ← THE code-executor agent (32 lines)
        │   └── prompts.py                ← the prompt the executor depends on (127 lines)
        ├── bigquery/                     ← NL2SQL on BQ (no code exec)
        ├── alloydb/                      ← NL2SQL on AlloyDB (no code exec)
        └── bqml/                         ← ML on BQ
```

We'll read them in dependency order: the executor agent first, then the prompt that pairs with it, then the tool wrapping it, then the root that orchestrates.

## File 1: `sub_agents/analytics/agent.py` (32 lines)

```python
analytics_agent = Agent(
    model=os.getenv("ANALYTICS_AGENT_MODEL", ""),           # :25
    name="analytics_agent",                                   # :26
    instruction=return_instructions_analytics(),              # :27
    code_executor=VertexAiCodeExecutor(                       # :28-31
        optimize_data_file=True,
        stateful=True,
    ),
)
```

Five things to name before moving on:

1. **`code_executor=` is attached at the agent level**, not on a tool (`:28`). Code execution is not a tool — it's a parallel mechanism the agent has, separate from `tools=[...]`. Pages 01 and 04 established this; the sample is your first sighting in the wild.
2. **Model is env-driven** (`:25`). The sample reads `ANALYTICS_AGENT_MODEL` so you can swap Pro/Flash/local without touching code. The empty-string default is intentional: if you don't set it, you get a clear "model name required" error at first call rather than silent fallback to a stale default.
3. **`stateful=True`** — Vertex kernel persists across calls in one session. Required for the multi-turn analytics UX: `df = pd.read_csv(...)` once, `.groupby(...)` many times.
4. **`optimize_data_file=True`** — uploaded CSV data is extracted from the request once and cached (see `04_VertexAiCodeExecutor.md`'s "`optimize_data_file=True` mechanics" section). Only `text/csv` benefits; parquet uploads here would be a no-op.
5. **No `timeout_seconds=`**, no `error_retry_attempts=` overrides — the sample takes the framework defaults (`None`, `2`). For an analytics agent that may run a slow `.groupby` or a 10s SciPy fit, the `None` timeout is probably right; for a calculator it would be too generous. **The right default depends on the workload**, and this sample's workload is "long analytical operations are fine."

## File 2: `sub_agents/analytics/prompts.py` (127 lines)

This is the prompt-executor coupling lesson. The sample's `VertexAiCodeExecutor(stateful=True)` is half the story; the prompt is the other half — and **they have to agree**, in writing, or the model and the runtime drift apart.

Three blocks to read:

**Statefulness contract (`:40-42`):**

```
**Statefulness:** All code snippets are executed and the variables stay in
the environment. You NEVER need to re-initialize variables. You NEVER need to
reload files. You NEVER need to re-import libraries.
```

This sentence is what `stateful=True` *means at the model level*. Without it, the LLM has no idea its kernel is sticky and will helpfully re-import pandas on every turn — wasting tokens, wall time, and your patience. Flip `stateful=False` and you must remove this block, or the model will reference variables that no longer exist.

**Pre-imported libraries (`:44-55`):**

```
**Imported Libraries:** The following libraries are ALREADY imported and
should NEVER be imported again:
  import io, math, re, matplotlib.pyplot as plt, numpy as np, pandas as pd, scipy
```

This mirrors `vertex_ai_code_executor.py:36-85` (the `_IMPORTED_LIBRARIES` constant). The executor injects those imports at the top of every submission via `_get_code_with_imports` (`:229-242`). The prompt is just *telling the model what the executor is going to do anyway*. Drift between these two — e.g., add `seaborn` to the prompt without adding it to `_IMPORTED_LIBRARIES` — and the LLM emits `sns.barplot(...)` against a `NameError`.

**Output protocol (`:57-79`):**

The prompt tells the model exactly what the executor's return envelope will look like (` ```tool_outputs ... ``` `) and adds the crucial guardrail:

```
- You **never** generate ```tool_outputs yourself.
```

Because the runtime *does* emit those blocks (as `code_execution_result` parts — see `01_WhyCodeExecution.md`), and if the model hallucinates one, the conversation gets a fake "execution result" that no execution produced. This is a real-world prompt-injection vector turned inward: the model can fake its own tool output unless told not to.

> 🤖 **Tutor:** ask the student to compare `prompts.py:44-55` line-for-line with `_IMPORTED_LIBRARIES` at `vertex_ai_code_executor.py:36-85`. Naming the alignment makes the coupling visceral.

## File 3: `data_science/tools.py` (127 lines, focus on lines `:59-126`)

The analytics agent doesn't get called by the root LLM directly via `transfer_to_agent`. It's wrapped as an `AgentTool` so the root agent calls it like any other tool:

```python
async def call_analytics_agent(question: str, tool_context: ToolContext):
    bigquery_data = tool_context.state.get("bigquery_query_result", "")     # :99-100
    alloydb_data  = tool_context.state.get("alloydb_query_result", "")      # :101-102
    question_with_data = f"""... <BIGQUERY>{bigquery_data}</BIGQUERY> ..."""  # :104-118
    agent_tool = AgentTool(agent=analytics_agent)                            # :120
    return await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )                                                                          # :122-124
```

Two design choices worth naming:

- **Data is passed through session state, not through the LLM's context.** The BQ sub-agent stores its result table in `state["bigquery_query_result"]`; the analytics wrapper reads it from state and injects it into the analytics agent's request. The root LLM never has to carry a multi-thousand-row table in its prompt window. (You can see why: at 5 turns of round-tripping, that would dominate the context.)
- **The wrapper writes its own output back to state too** (`:125`, `analytics_agent_output`), so downstream tools or a re-summarization pass can read it without re-running.

## File 4: `data_science/agent.py` (root, 213 lines)

The root agent is built dynamically in `get_root_agent()` (`:177-204`), and three calls in the constructor matter:

```python
agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),  # :188
    name="data_science_root_agent",
    instruction=return_instructions_root()
              + get_dataset_definitions_for_instructions(),    # :190-191
    global_instruction=f"""... Todays date: {date.today()}""", # :192-197
    sub_agents=sub_agents,   # bqml_agent only                 # :198
    tools=tools,             # call_analytics + call_bigquery  # :199
    before_agent_callback=load_database_settings_in_context,   # :200
    generate_content_config=types.GenerateContentConfig(
        temperature=0.01),                                      # :201
)
```

- **`sub_agents=[bqml_agent]` only, not analytics.** Read carefully: `analytics_agent` is *not* in `sub_agents`. It's reached via the `call_analytics_agent` tool (`:199`). Compare against `bqml_agent`, which IS in `sub_agents` — meaning the root can `transfer_to_agent` to BQML but only *calls* analytics. The choice of `AgentTool` vs `sub_agents` per agent is what controls invocation style ([[05_MultiAgent/03_AgentAsTool]]). Code-executor sub-agents are usually wrapped as tools so the root keeps control after the analytics turn finishes.
- **`before_agent_callback=load_database_settings_in_context`** (`:200, :171-174`) — runs once per session, loads BQ schema into state under `state["database_settings"]`. The schema lives in state from then on; sub-agents read it without re-querying BQ for `INFORMATION_SCHEMA` every turn. This is the cost-control pattern of section "BigQuery as analytical store" in [[10C_BigQueryAgents]].
- **`temperature=0.01`** (`:201`) — near-zero. Generated SQL and Python should be deterministic; you do not want creative variance on a `GROUP BY`.

## The wire trace: one execution end-to-end

User asks: *"What's the average flight delay by airline?"* and we want the chart back. Here's what crosses the wire, in order.

```
user_msg ──→ root LLM call
              outputs FunctionCall(name='call_bigquery_agent',
                                   args={'question':'avg delay by airline'})
        │
        ▼
    runtime invokes call_bigquery_agent tool (tools.py:27-40)
        AgentTool(agent=bigquery_agent).run_async(...)
        bigquery_agent emits NL2SQL → executes → writes result to
        state['bigquery_query_result']
        returns table summary to root
        │
        ▼
    root LLM call #2
        sees the BQ tool's return value
        outputs FunctionCall(name='call_analytics_agent',
                             args={'question':'plot it as a bar chart'})
        │
        ▼
    runtime invokes call_analytics_agent tool (tools.py:59-126)
        reads state['bigquery_query_result']
        builds question_with_data, calls AgentTool(analytics_agent)
        │
        ▼
    analytics_agent LLM call
        outputs Part(executable_code=ExecutableCode(
            language='PYTHON',
            code='import pandas as pd\\n... plt.bar(...)\\nplt.savefig("chart.png")'))
        │
        ▼
    _CodeExecutionResponseProcessor catches the executable_code Part
    (flows/llm_flows/_code_execution.py:151-169)
    VertexAiCodeExecutor.execute_code → POST to extension's `execute` op
    with {code, files, session_id}
    extension runs in stateful kernel (because stateful=True)
    returns {stdout: "...", stderr: "", output_files: [chart.png]}
        │
        ▼
    _post_process_code_execution_result (_code_execution.py:435-470)
    wraps into Content(role='model',
                       parts=[Part(code_execution_result=CodeExecutionResult(
                           outcome='OUTCOME_OK',
                           output='Code execution result:\\n...'))])
    + an inline file part for chart.png
        │
        ▼
    analytics_agent LLM call #2 (sees its own execution result)
        outputs text summary "The plot shows..." + the chart
        │
        ▼
    analytics_agent_output written to state['analytics_agent_output']
    return value flows back through AgentTool → root LLM
        │
        ▼
    root LLM call #3
        synthesizes final user-facing reply
```

Two facts worth holding:

- **The user→answer path includes 4 LLM calls** (root x2, analytics x2) and 2 tool invocations (BQ, analytics). The `stateful=True` flag is what makes the second analytics call cheap — the kernel still has `df` loaded from the first.
- **The `chart.png` file part crosses three boundaries**: sandbox → executor → response processor → analytics agent's next turn → AgentTool return → root → user. Each boundary is a place a tracing span can hang off ([[15_Observability]]).

## Per-executor configuration knob table

If you cloned this sample and wanted to retarget it to a different executor, here's the migration map:

| Knob in this sample | `VertexAi` (current) | `BuiltIn` | `Container` | `Gke` | `AgentEngineSandbox` |
|---|---|---|---|---|---|
| stateful kernel | `stateful=True` | n/a — model-side, opaque | per-container (state leaks) | `executor_type="sandbox"` only; `"job"` is fresh-per-call | per-session via `state['sandbox_name']` (always on) |
| data-file optimization | `optimize_data_file=True` | n/a | bake into image / mount volume | mount via ConfigMap or PVC | upload via `code_execution_input.input_files` per call |
| timeout | `timeout_seconds=` (default `None`) | model-side, short | container runtime config | `timeout_seconds=` constructor arg, default 300 | Agent Engine sandbox default |
| package set | `_IMPORTED_LIBRARIES` constant; prompt must mirror | Google's allowlist | your image's installed pkgs | your image's installed pkgs | Google's allowlist for the sandbox |
| egress | vendor allowlist (`◐ PART.`) | none (`✅ NONE`) | your daemon (`◐ DEP.`) | your `NetworkPolicy` (`◐ DEP.`) | vendor allowlist (`◐ PART.`) |

The point of the table: the analytics agent's *prompt* depends on `stateful=True` and the `_IMPORTED_LIBRARIES` set. Retargeting to a different executor means rewriting both the constructor and the prompt — they're coupled.

> ❓ **Ask the student:** "Why is code execution wired to a *sub-agent* (`analytics_agent`) instead of being a tool on the root?" *(Expected: separation of concerns. Root orchestrates; analytics_agent specializes in 'execute Python on tabular data'. The sandbox's blast radius is narrower; the prompt is specialized to the task; the eval surface is decoupled.)*

> ❓ **Ask the student:** "If you flipped `stateful=True` to `False` in `analytics/agent.py:30` but changed nothing in `prompts.py`, what breaks and when?" *(Expected: the prompt tells the model 'variables stay in the environment' — but the kernel is now reset per call. Turn 2 references `df`, gets a `NameError`. Symptom: silently bad answers on every multi-turn analysis. The fix is to edit BOTH the constructor AND the prompt — they're coupled.)*

> ❓ **Ask the student:** "The prompt at `prompts.py:78` says 'You **never** generate `tool_outputs` yourself.' Why is this defensive line there?" *(Expected: the runtime emits real `tool_outputs` blocks as `code_execution_result` parts; if the model hallucinates one in its own response, the conversation has a fake 'execution result' nobody executed — a self-induced prompt-injection vector. The prompt explicitly blocks the foot-gun.)*

> 🛠 **Have the student run:** Clone the sample, set `ANALYTICS_AGENT_MODEL=gemini-2.5-flash` and the BQ env vars, ask "what's the average of column X" against a small BQ table. In the trace, find the `executable_code` part on the analytics agent's first call and the `code_execution_result` part on its second. Confirm the kernel state by asking a follow-up ("now sort it") and watching for absence of re-import / re-load.

---

[← Prev: 12_CodeExecution/06_AgentEngineSandbox]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/08_InProduction →]
