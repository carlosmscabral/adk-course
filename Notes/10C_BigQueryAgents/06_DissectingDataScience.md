---
module: 10C_BigQueryAgents
page: 06_DissectingDataScience
title: 🔎 Dissecting the data-science sample
estimated_minutes: 40
prereqs: [10C_BigQueryAgents/05]
concepts: [data-science-sample, multi-agent, schema-injection, NL2SQL, ChaseSQL]
icon: 🔎
in_production: false
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/05_BigQueryAgentAnalyticsPlugin] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/07_InProduction →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 06 Dissecting the data-science sample

---

## 🔎 Sample anatomy

```
/home/carloscabral/study/adk-samples/python/agents/data-science/
├── data_science/
│   ├── agent.py                        # root multi-agent
│   ├── prompts.py                      # root instructions (route to subagents)
│   ├── tools.py                        # call_bigquery_agent, call_analytics_agent
│   ├── sub_agents/
│   │   ├── bigquery/
│   │   │   ├── agent.py                # the BQ subagent
│   │   │   ├── tools.py                # nl2sql + schema fetch
│   │   │   ├── prompts.py
│   │   │   └── chase_sql/              # advanced NL2SQL ("ChaseSQL")
│   │   ├── alloydb/                    # parallel structure for AlloyDB
│   │   ├── analytics/                  # Python analysis subagent
│   │   └── bqml/                       # BigQuery ML subagent
│   └── utils/
├── flights_dataset_config.json         # tells the agent which BQ tables to look at
├── cross_dataset_relations.json        # foreign-key map between BQ and AlloyDB
└── eval/, deployment/, tests/
```

This is a much heavier sample than the RAG one. It's a **multi-agent** architecture: a root planner that routes to BQ, AlloyDB, Python analytics, or BQML subagents.

For our purposes, focus on the BQ slice.

## 🔎 1. How is the schema injected into the prompt?

Two-layer pattern.

**Layer A** — `data_science/agent.py:136-168` (`get_dataset_definitions_for_instructions`):

```python
def get_dataset_definitions_for_instructions() -> str:
    dataset_definitions = "<DATASETS>\n"
    for dataset in _dataset_config["datasets"]:
        dataset_type = dataset["type"]
        dataset_definitions += f"""
<{dataset_type.upper()}>
<DESCRIPTION>
{dataset["description"]}
</DESCRIPTION>
<SCHEMA>
{_database_settings[dataset_type]["schema"]}
</SCHEMA>
</{dataset_type.upper()}>
"""
    dataset_definitions += "</DATASETS>\n"
    return dataset_definitions
```

Built **at agent-creation time** from a JSON config file (`flights_dataset_config.json`) plus a live BQ schema fetch. Then concatenated to the root prompt at `agent.py:191`:

```python
instruction=return_instructions_root() + get_dataset_definitions_for_instructions(),
```

**Layer B** — when the BQ subagent runs, the schema is also placed in `tool_context.state["database_settings"]["bigquery"]["schema"]` (see `data_science/sub_agents/bigquery/tools.py:84-103`). The `bigquery_nl2sql` tool reads this at line 210:

```python
schema = tool_context.state["database_settings"]["bigquery"]["schema"]
prompt = prompt_template.format(MAX_NUM_ROWS=MAX_NUM_ROWS, SCHEMA=schema, QUESTION=question)
```

**Why two places?** The root agent uses the schema for routing decisions ("is this question answerable from BQ?"). The subagent uses it for actual SQL generation. Separation of concerns.

## 🔎 2. How is SQL executed?

The sample uses ADK's first-class `BigQueryToolset` for execution (page 03):

`data_science/sub_agents/bigquery/agent.py:67-72`:

```python
bigquery_tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED, application_name=USER_AGENT
)
bigquery_toolset = BigQueryToolset(
    tool_filter=bigquery_tool_filter, bigquery_tool_config=bigquery_tool_config
)
```

Note `WriteMode.BLOCKED` and the tool filter — exactly the production pattern from page 03. The BQML subagent (`sub_agents/bqml/agent.py:82-85`) bumps to `WriteMode.ALLOWED` because it needs to `CREATE MODEL`. Per-subagent write-mode discipline.

## 🔎 3. How are results formatted back?

`data_science/sub_agents/bigquery/agent.py:51-63`:

```python
def store_results_in_context(tool, args, tool_context, tool_response):
    if tool.name == ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL:
        if tool_response["status"] == "SUCCESS":
            tool_context.state["bigquery_query_result"] = tool_response["rows"]
    return None
```

An `after_tool_callback` stuffs the rows into state where the Python analytics subagent can pick them up. **State is the inter-agent bus.**

The final formatting is the root agent's job — `prompts.py:109-117` mandates:

> "Return RESULT AND EXPLANATION... Use MARKDOWN format... Result: Natural language summary of the data agent findings."

## 🔎 4. How is cost capped?

Honestly: **less aggressively than we'd recommend.** The sample relies on:

- `MAX_NUM_ROWS=10000` in the NL2SQL prompt (a row guideline, not a bytes cap).
- `WriteMode.BLOCKED` (prevents writes but not expensive reads).
- The schema-grounding guideline: "filter aggressively to minimize total rows."

The sample does **not** add a `before_tool_callback` with `dry_run`. **In production, you should.** The cost-guard pattern from page 03 is your addition to make this sample production-safe.

> 🚀 **In Production**
> Treat the sample as a starting point. Add cost-guard before any real deployment. The pattern from page 03 layers cleanly on top.

## 🔎 The ChaseSQL detour

If you peek at `sub_agents/bigquery/chase_sql/`, that's a research-grade NL2SQL technique (multi-step chain-of-thought SQL generation with self-correction). Configurable via `NL2SQL_METHOD=CHASE`. **Read it for inspiration**; the baseline `bigquery_nl2sql` is enough for most use cases.

## 🔎 Trace: "what are the busiest stations?"

1. User → root agent.
2. Root agent reads question, picks `call_bigquery_agent` (it's a SQL question).
3. `call_bigquery_agent` invokes the BQ subagent.
4. BQ subagent's `before_agent_callback` loads schema into state.
5. LLM calls `bigquery_nl2sql(question)` → returns SQL string.
6. LLM calls `execute_sql(sql)` → BQ runs, rows come back.
7. `after_tool_callback` saves rows into state.
8. LLM (BQ subagent) summarizes rows → returns to root.
9. Root formats final markdown response.

Nine steps. **Every one of them is visible in the event log.** Have the student trace it.

## ❓ Check

> ❓ **Ask the student:** "If you wanted to add a strict `MAX_BYTES_BILLED=1GB` cap to this sample, in which file would you add the `before_tool_callback`?"
>
> Expected: `data_science/sub_agents/bigquery/agent.py` — same place where `bigquery_toolset` is defined, attach the callback to the BQ subagent.

## 🛠 Have the student run

> 🛠 If they have a billable project and the flights dataset loaded: `adk run` this sample, ask "What were the busiest 5 airports last month?", and trace the 9-step event log. Then add a cost-guard and intentionally break it with "show me all flights ever" — the guard should reject.

## 🤖 Tutor

> Three things the student should walk away with: (1) schema-grounding in TWO places; (2) WriteMode discipline per subagent; (3) cost-guard is the missing production wart — they should be able to add it from page 03 verbatim.

---

[← Prev: 10C_BigQueryAgents/05_BigQueryAgentAnalyticsPlugin] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/07_InProduction →]
