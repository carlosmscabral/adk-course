---
module: 15_Observability
page: 06_BigQueryAsSink
title: BigQuery as the long-term observability sink
estimated_minutes: 15
prereqs: [13_Plugins/06, 15_Observability/05]
concepts: [BigQueryAgentAnalyticsPlugin, analytics, retention]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/05_Metrics](05_Metrics.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/07_DissectingSample →](07_DissectingSample.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 06 BigQuery Sink

---

## ☁️ Why BigQuery for agents

Cloud Trace and Cloud Logging are great for *immediate* debugging. They are not great for *what's our 90-day weekly cost trend by tenant?* or *which tools have a worsening error rate quarter-over-quarter?*

BigQuery is built for that. Long retention, SQL, joins to your business tables, no per-query infra.

`BigQueryAgentAnalyticsPlugin` (covered in module 13) is the official wiring. Each agent event becomes one row in a BQ table you can `SELECT` from.

## 🛠 The wiring (recap)

```python
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
)
from google.adk.apps import App

bq_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id="adk_agent_analytics",
    table_id="agent_events",
    location="us-east1",
)

app = App(name="research_assistant", root_agent=root_agent, plugins=[bq_plugin])
```

Plugin mechanics live in [[13_Plugins/06_BigQueryAgentAnalyticsPlugin]]. This page only covers the *observability use*.

## 🧠 Schema (informational)

The plugin auto-provisions a table with columns like:

- `event_ts` (TIMESTAMP)
- `session_id` (STRING)
- `user_id` (STRING)
- `agent_name` (STRING)
- `event_type` (STRING)  — `model_call`, `tool_call`, `tool_result`, …
- `tool_name` (STRING, nullable)
- `model_name` (STRING, nullable)
- `tokens_in` / `tokens_out` (INT64, nullable)
- `latency_ms` (INT64, nullable)
- `status` (STRING, nullable)
- `payload` (JSON) — full event for replay

The shape is generic; queries are where the value lives.

## 🛠 Example: slowest tool, last 7 days

```sql
SELECT tool_name,
       APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)] AS p95_ms,
       COUNT(*) AS calls
FROM `myproj.adk_agent_analytics.agent_events`
WHERE event_type = 'tool_result'
  AND event_ts > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY tool_name
ORDER BY p95_ms DESC;
```

## 🛠 Example: cost per session, last 24 hours

```sql
SELECT session_id,
       SUM(tokens_in * 0.075/1e6 + tokens_out * 0.30/1e6) AS usd
FROM `myproj.adk_agent_analytics.agent_events`
WHERE event_type = 'model_call'
  AND event_ts > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY session_id
ORDER BY usd DESC
LIMIT 20;
```

(Substitute your actual model pricing — these numbers are illustrative.)

> ❓ **Ask the student:** if a customer support agent needs "what did session X do yesterday at 3pm?" — which signal answers it best: BQ rows, OTel traces, or stdout logs? *(All three contain the data; BQ is the easiest to query by exact session_id over a date range.)*

> 🚀 **In Production**
>
> Set a BigQuery **scan-byte cap** on observability queries (see [[10C_BigQueryAgents/07_InProduction]]). A naive `SELECT * FROM agent_events` against a TB-sized table can cost hundreds of dollars per query.

---

[← Prev: 15_Observability/05_Metrics](05_Metrics.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/07_DissectingSample →](07_DissectingSample.md)
