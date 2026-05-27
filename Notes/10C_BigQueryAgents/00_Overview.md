---
module: 10C_BigQueryAgents
page: 00_Overview
title: BigQuery for Agents — Overview
estimated_minutes: 15
prereqs: [03_Tools/05, 07_Callbacks/03]
concepts: [BigQuery, NL2SQL, BigQueryToolset, VECTOR_SEARCH, cost-guard]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/09_MiniDrill] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/01_BigQueryForAgents →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 00 Overview

---

## 🧠 What you'll learn

Treat BigQuery as a **first-class data source for agents** — for analytics (NL2SQL), for vector retrieval at scale (`VECTOR_SEARCH`), and as a sink for agent telemetry.

Specifically:

- When BQ makes sense over Cloud SQL / AlloyDB / Firestore.
- The **NL2SQL pattern** and its schema-grounding problem.
- ADK's first-class `BigQueryToolset` and `BigQueryToolConfig.write_mode`.
- BigQuery's native `VECTOR_SEARCH(...)` and `ML.GENERATE_EMBEDDING(...)`.
- BigQuery as an **observability sink** via `BigQueryAgentAnalyticsPlugin`.
- The cost & safety story: dry runs, byte limits, SQL injection, partitioned tables.

## 📦 Time

~2 days (concept pages + drill on public dataset).

## 🧭 Prereqs

- 03 (Tools) — you'll wrap BigQuery calls as tools.
- 07 (Callbacks) — the cost-guard pattern uses `before_tool_callback`.
- GCP project with **BigQuery API enabled** (separate from Vertex AI).
- ADC configured. Same as 10A.

## ☁️ GCP prereqs — check before drilling

```bash
gcloud services list --enabled --filter="name:bigquery.googleapis.com"
bq ls                                   # smoke test — should not error
```

If `bigquery.googleapis.com` is not listed:

```bash
gcloud services enable bigquery.googleapis.com
```

> ⚠️ **Cost warning**
> BigQuery is **billed by bytes scanned**. A poorly-written agent can scan TB and rack up real charges. This module's biggest concept is the **cost guard** (page 03 and page 07). Read it twice.

## 🔎 Sample anchors

- **Primary**: `/home/carloscabral/study/adk-samples/python/agents/data-science/` — NL2SQL over BigQuery (and AlloyDB) with a multi-agent architecture.
- **Secondary**: `/home/carloscabral/study/adk-samples/python/agents/fomc-research/` — BQ analytics for financial research.
- **Plugin example**: `/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/` — `BigQueryAgentAnalyticsPlugin` writing agent events to BQ.

## 🗺 Page order

| # | Page | What |
|---|---|---|
| 01 | `BigQueryForAgents` | When BQ vs Cloud SQL / AlloyDB. ☁️ |
| 02 | `NL2SQLPattern` | Schema-grounding & prompt structure. 🧠 |
| 03 | `BigQueryAsTool` | `BigQueryToolset`, cost cap, `dry_run`. 🛠 |
| 04 | `BigQueryVectorSearch` | `VECTOR_SEARCH()` + `ML.GENERATE_EMBEDDING()`. ☁️ |
| 05 | `BigQueryAgentAnalyticsPlugin` | BQ as telemetry sink (teaser). 🚀 |
| 06 | `DissectingDataScience` | Read the data-science sample end-to-end. 🔎 |
| 07 | `InProduction` | Cost, SQL injection, result-size guards. 🚀 |
| 08 | `KnowledgeCheck` | 6 questions. ❓ |
| 09 | `MiniDrill` | `nl_to_bq` agent on `london_bicycles`. 🛠 |

## 🤖 Tutor

> Open `00_Overview`, verify BigQuery API is enabled and `bq ls` works, then page 01.
> The drill on `bigquery-public-data.london_bicycles` is free under the free tier for the volume we touch — but enforce the cost-cap pattern from page 03 *in the drill*.

---

[← Prev: 10B_RAGPipeline/09_MiniDrill] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/01_BigQueryForAgents →]
