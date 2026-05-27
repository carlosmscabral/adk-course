---
module: 10C_BigQueryAgents
page: 03_BigQueryAsTool
title: 🛠 ☁️ BigQuery as a tool — with cost cap
estimated_minutes: 35
prereqs: [10C_BigQueryAgents/02, 07_Callbacks/03]
concepts: [BigQueryToolset, BigQueryToolConfig, WriteMode, dry_run, maximum_bytes_billed, before_tool_callback]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/02_NL2SQLPattern] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/04_BigQueryVectorSearch →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 03 BigQuery as a tool

---

## 🛠 The first-class ADK option — `BigQueryToolset`

ADK ships a built-in BigQuery toolset. You don't have to roll your own `FunctionTool`.

```python
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

bq_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED,             # read-only — the safe default
    application_name="my-adk-agent/0.1",      # shows in BQ audit logs
    max_query_result_rows=1000,                # cap the row count returned
)

bq_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],              # expose only what you need
    bigquery_tool_config=bq_config,
)

agent = Agent(
    model="gemini-2.5-pro",
    name="bq_analyst",
    instruction="...schema in here...",
    tools=[bq_toolset],
)
```

This gives the agent a SQL-execution tool with sensible defaults. The full toolset has:

- `execute_sql` — run a query.
- `get_dataset_info`, `list_dataset_ids`, `list_table_ids`, `get_table_info` — discovery.
- (Some versions) `forecast`, `analyze_contribution` — BQ ML primitives.

Use `tool_filter` to expose only what the agent should touch.

## 🔒 `WriteMode` — the killswitch

| Mode | Allows |
|---|---|
| `BLOCKED` | SELECT only. **Default for production.** |
| `ALLOWED` | Any DML (INSERT, UPDATE, DELETE, CREATE). |
| `PROTECTED` | Allows writes to a specific dataset only (some SDK versions). |

> ⚠️ **Gotcha**
> The default is `ALLOWED` on some versions of the toolset. **Always set it explicitly.** A pure-read agent should never be `WriteMode.ALLOWED`.

## 💸 The cost cap — `maximum_bytes_billed`

`google.cloud.bigquery.Client.query(...)` accepts a `job_config` with `maximum_bytes_billed`. **If the query would scan more than this, it errors out before it runs**. No "oops" $$$$.

The `BigQueryToolConfig` doesn't always expose this directly — for hardening, **wrap or guard with a callback**. This is the recommended production pattern.

## 🛠 Cost-guard via `before_tool_callback`

The pattern (recap from module 07):

```python
from google.adk.tools import BaseTool, ToolContext
from google.cloud import bigquery

MAX_BYTES = 5 * 1024**3   # 5 GB cap — adjust per project budget

bq_client = bigquery.Client()   # ADC

def cost_guard(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """Reject SQL whose dry_run estimates more than MAX_BYTES."""
    if tool.name != "execute_sql":
        return None
    sql = args.get("query", "")
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    try:
        job = bq_client.query(sql, job_config=job_config)
        bytes_estimated = job.total_bytes_processed
    except Exception as e:
        return {"status": "ERROR", "message": f"dry_run failed: {e}"}
    if bytes_estimated > MAX_BYTES:
        return {
            "status": "REJECTED",
            "message": (
                f"Query would scan {bytes_estimated/1e9:.2f} GB, cap is "
                f"{MAX_BYTES/1e9:.2f} GB. Add filters / partition predicates."
            ),
        }
    # No return = pass-through; tool runs normally.
    return None

agent = Agent(
    # ...
    tools=[bq_toolset],
    before_tool_callback=cost_guard,
)
```

What this gives you:

- **Dry run is free** — BigQuery doesn't charge for `dry_run=True`.
- The LLM sees a clear rejection message; it can rewrite the query and try again.
- You never accidentally scan a TB because the LLM forgot a WHERE clause.

> 🚀 **In Production**
> Pair the cost-guard with **`maximum_bytes_billed` on the actual execute**, too — belt and suspenders. The dry_run estimate can be slightly off; the hard cap on execute is the real firewall.

## 🛠 Putting it together

```python
agent = Agent(
    model="gemini-2.5-pro",
    name="bq_analyst",
    instruction=load_schema_grounded_prompt(),  # from page 02
    tools=[bq_toolset],                           # BigQueryToolset, BLOCKED writes
    before_tool_callback=cost_guard,              # dry_run cap
)
```

This is the **production-shape** of a BQ agent. Five lines.

## ⚠️ Result-size guards

`max_query_result_rows=1000` in the toolset config caps what comes back. The LLM doesn't need 100k rows to summarize "what's the busiest station" — it needs ~10. Set the cap *low* and let the LLM ask for more if needed.

## ❓ Check

> ❓ **Ask the student:** "Why is `dry_run` the right thing to put in `before_tool_callback` instead of just adding a `LIMIT 1000` to every generated SQL?"
>
> Expected: `LIMIT` doesn't reduce scan — BQ still scans the whole table, just returns the limited rows. `dry_run` actually estimates the scan size *before* the bill is incurred. LIMIT is a row cap; dry_run + cost-guard is a *bytes* cap.

## 🛠 Have the student run

> 🛠 Wire the snippet above to query `bigquery-public-data.london_bicycles.cycle_hire`. Ask: "show me all rentals" — observe the cost-guard rejects it. Then ask: "show me 10 rentals from 2017-01-01" — observe it passes (small scan with partition predicate).

## 🤖 Tutor

> The cost-guard pattern is the single most important production tool in this module. Drill it. Have the student deliberately ask an expensive question and watch the guard fire.

---

[← Prev: 10C_BigQueryAgents/02_NL2SQLPattern] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/04_BigQueryVectorSearch →]
