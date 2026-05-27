---
module: 10C_BigQueryAgents
page: 05_BigQueryAgentAnalyticsPlugin
title: 🚀 BQ as a telemetry sink — `BigQueryAgentAnalyticsPlugin` (teaser)
estimated_minutes: 15
prereqs: [10C_BigQueryAgents/04]
concepts: [Plugin, BigQueryAgentAnalyticsPlugin, agent-telemetry, observability]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/04_BigQueryVectorSearch] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/06_DissectingDataScience →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 05 BQ as telemetry sink (teaser)

---

## 🧠 The inverse use case

Pages 01-04: agent **reads from** BQ.
This page: agent **writes telemetry to** BQ.

ADK ships a first-class plugin for it: `BigQueryAgentAnalyticsPlugin`. It captures agent events (every tool call, every LLM response, every state mutation) and streams them into a BQ table. Then you can query your agent's behavior with SQL.

## ☁️ The 10-line setup

From the canonical sample (`adk-samples/python/agents/agent-observability-bq/agent_observability_bq/agent.py:54-62`):

```python
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
)
from google.adk.apps import App

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id="adk_agent_analytics",
    table_id="agent_events",
    location="us-east1",
)

app = App(
    name="my_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)
```

That's it. Every event the runner emits lands in `project.adk_agent_analytics.agent_events`.

> **🚀 In Production**: `agent-observability-bq` is the canonical sample that wires this plugin into a real BigQuery analytics agent — the agent *uses* BigQuery as a tool **and** *emits* its own telemetry to BigQuery (same warehouse on both sides). Dissected end-to-end from the observability angle in [[15_Observability/07_DissectingSample]]; read it once you've cleared the plugin mechanics.

## 🔎 What ends up in BQ

Roughly (schema may vary by SDK version):

| Column | Example |
|---|---|
| `event_id` | UUID |
| `app_name` | "my_agent" |
| `user_id`, `session_id` | for grouping |
| `timestamp` | when the event fired |
| `author` | "user" / "agent_name" / tool name |
| `event_type` | "tool_call", "tool_response", "llm_response", "state_delta" |
| `content` | the actual payload (JSON / text) |
| `tool_name`, `tool_args`, `tool_response` | when applicable |
| `model`, `usage_metadata` | for LLM events — tokens, cost |

Once it's in BQ, you can answer:

- "What's our p95 latency by tool?"
- "Which tool errors most often in the last 7 days?"
- "Total tokens used per user this month?"
- "Show me the 10 most expensive sessions."

```sql
-- Top 10 most-expensive sessions (last 30 days):
SELECT
  session_id,
  SUM(usage_metadata.total_token_count) AS total_tokens
FROM `proj.adk_agent_analytics.agent_events`
WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 30 DAY
  AND event_type = 'llm_response'
GROUP BY session_id
ORDER BY total_tokens DESC
LIMIT 10;
```

## 🧭 This is just the teaser

`BigQueryAgentAnalyticsPlugin` is covered in depth in:

- [13_Plugins](../13_Plugins/00_Overview.md) — plugin mechanics and lifecycle.
- [15_Observability](../15_Observability/00_Overview.md) — full observability stack (BQ + OpenTelemetry + tracing UIs).

You don't need to drill it here. **Know it exists. Wire it once.** The full story is in those modules.

## 🚀 In Production

> **🚀 In Production**
> Schema-evolution: pin the SDK version, or schedule a check that the table schema matches the SDK's expectation. SDK upgrades occasionally add fields; BQ tables don't auto-evolve.
> Cost: it's a streaming insert — counted in bytes. For high-volume agents, batch and use load jobs instead. Plugin defaults are tuned for moderate volume.

## ❓ Check

> ❓ **Ask the student:** "Why is BQ a good destination for agent telemetry vs Cloud Logging?"
>
> Expected: Cloud Logging is great for grep-style debug; BQ is great for **aggregate analysis** (tokens-per-session, errors-per-tool, latency percentiles). For agent observability you usually want both — Logging for the trail, BQ for the dashboard.

## 🤖 Tutor

> Keep this page short. The point is awareness — "this exists, it's one plugin line, the table you read in page 03 might be the table you wrote in page 05." Move on to the sample dissection (06).

---

[← Prev: 10C_BigQueryAgents/04_BigQueryVectorSearch] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/06_DissectingDataScience →]
