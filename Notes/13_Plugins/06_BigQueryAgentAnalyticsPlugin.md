---
module: 13_Plugins
page: 06_BigQueryAgentAnalyticsPlugin
title: BigQueryAgentAnalyticsPlugin
estimated_minutes: 25
prereqs: [13_Plugins/05]
concepts: [BigQueryAgentAnalyticsPlugin, offline analytics, event ingestion]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 13_Plugins/05_GlobalInstructionPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/07_WritingACustomPlugin →]

You are here: 🗺 Runtime Track ▸ 13 Plugins ▸ 06 BigQueryAgentAnalyticsPlugin

# ☁️ Every event in BigQuery for offline analysis

This is the plugin most prod deployments wire eventually. Every event the runner yields gets persisted as a row in a BigQuery table you specify. From there: SQL it for cost analysis, latency p95, error rates, agent transfer flows, eval gold-set extraction, anything.

```python
# from agent-observability-bq sample
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
)

bq_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id="adk_agent_analytics",
    table_id="agent_events",
    location="us-east1",
)

runner = Runner(
    app_name="prod",
    agent=root_agent,
    plugins=[bq_plugin],
)
```

## What gets logged

For every event:

- `app_name`, `user_id`, `session_id`, `invocation_id`
- `agent_name` (which agent produced it)
- `event_type` (model response, tool call, tool response, transfer, error, ...)
- `content` (parts, with whatever structure they have)
- `tool_name`, `tool_args`, `tool_response`
- `model_name`, `latency_ms`, `token_counts`
- timestamp

The exact schema is the plugin's responsibility; check the live table with `bq show project:dataset.table` after a few turns.

## The bridge to 15_Observability

This is *the* bridge from the plugin module to the observability module. Live tracing (OpenTelemetry, Cloud Trace) gives you per-request flame graphs; BigQuery analytics gives you the population-level dataset to query. You want both:

- Trace tells you: "this one request was slow because tool X took 8s."
- Analytics tells you: "tool X is slow on 14% of requests this week, mostly for users in region Y."

## Sampling and cost

By default the plugin writes every event. For high-traffic agents, you'll want to sample (configure at the plugin or upstream). The BigQuery cost model is mostly storage + occasional queries, so a few million events/day is cheap. A few billion is not.

## When NOT to use it

- Offline / no GCP environment.
- You already log to a different warehouse (Snowflake, Redshift, Databricks). Write the equivalent custom plugin in page 07 style.

> ⚠️ **Gotcha.** Plugin writes are *synchronous* by default in the simplest case. A slow BQ insert can slow every event. Configure for **async / batched** ingestion in prod (the plugin supports it; check the constructor kwargs). See production callout below.

> ❓ **Ask the student:** "What SQL would you write to find which tool errors most in the last 24h?" *(Expected: SELECT tool_name, COUNT(*) FROM events WHERE event_type='tool_error' AND ts > NOW() - INTERVAL 1 DAY GROUP BY tool_name ORDER BY COUNT(*) DESC. Discuss what schema field the plugin uses.)*

> **🚀 In Production**
>
> Configure async/batched writes. Set an ingestion-side filter to drop ultra-noisy event types if cost is an issue. Set table partition by day and cluster by `user_id` for cheap user-level queries. Cross-link `15_Observability` for the full telemetry strategy.

---

[← Prev: 13_Plugins/05_GlobalInstructionPlugin]  [↑ Map](../../MAP.md)  [Next: 13_Plugins/07_WritingACustomPlugin →]
