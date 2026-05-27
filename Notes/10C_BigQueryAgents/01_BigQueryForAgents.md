---
module: 10C_BigQueryAgents
page: 01_BigQueryForAgents
title: ☁️ When BigQuery makes sense for an agent
estimated_minutes: 15
prereqs: [10C_BigQueryAgents/00]
concepts: [OLAP, OLTP, federated-query, public-datasets, partitions]
icon: ☁️
in_production: false
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/00_Overview] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/02_NL2SQLPattern →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 01 BigQuery for agents

---

## 🧠 The three things BQ is great at

1. **Analytical queries at scale** — OLAP. Aggregates over TB. Sub-second on billion-row tables (when partitioned + clustered well).
2. **Federated data** — `EXTERNAL_QUERY(...)` reaches into Cloud SQL, AlloyDB, BigLake (Parquet on GCS), Sheets. One SQL, many sources.
3. **Native ML + vector search** — `ML.GENERATE_EMBEDDING(...)`, `VECTOR_SEARCH(...)`, `ML.PREDICT(...)`. Your embedding pipeline can live entirely in SQL.

## ⚖️ BQ vs other GCP databases

| Need | Pick | Why |
|---|---|---|
| User session storage (CRUD, low latency) | Cloud SQL / Firestore | BQ is OLAP; per-row reads are wrong tool |
| Transactional with PostgreSQL extensions | AlloyDB | OLTP + analytics hybrid |
| Aggregates over years of events | **BigQuery** | Partitioned scans, columnar, fast |
| Vector search at >100M vectors with SQL alongside | **BigQuery** (`VECTOR_SEARCH`) or Vertex AI VS | BQ if data already in BQ |
| Time-series at scale | BigQuery (or BigTable) | BQ for analytical; BT for write-heavy |

> 🧭 **Rule of thumb**
> If the agent's question starts with "how many", "what's the trend", "average", "top N", "compared to last year" — BQ. If it starts with "fetch user 42's profile" — not BQ.

## 🎁 Public datasets — your free playground

GCP hosts ~200 public BQ datasets. Free to query (you pay only for your scan). Pick from `bigquery-public-data.*`:

- `london_bicycles` — bike rentals. The drill uses this.
- `samples.shakespeare` — every word in Shakespeare. Classic tutorial.
- `chicago_crime`, `new_york_taxi_trips`, `usa_names`.
- `covid19_open_data` — pandemic data.
- `stackoverflow.posts_questions` — for Q&A retrieval examples.

```bash
bq ls bigquery-public-data:london_bicycles
```

These are the perfect target for "build an agent that answers questions over real data" exercises without burning your budget.

## ⚠️ Cost model — the one paragraph you must internalize

BigQuery charges for **bytes scanned** (not rows returned). A `SELECT * FROM big_table` scans every column of every row. `SELECT col1 FROM big_table WHERE partition = '2025-05-27'` scans one column from one partition — possibly 10000× cheaper.

| Bad query | Good query |
|---|---|
| `SELECT * FROM big_table` | `SELECT col1, col2 FROM big_table` |
| `WHERE date > '2020-01-01'` (no partition pruning) | `WHERE _PARTITIONDATE > '2025-01-01'` |
| no `LIMIT` | `LIMIT 1000` |

The LLM-generated SQL **must learn these patterns**. Page 02 explains how (schema-grounded prompting). Page 03 enforces it (cost-guard callback).

## ❓ Check

> ❓ **Ask the student:** "Why isn't BigQuery the right backend for an agent's session storage (chat history, user state)?"
>
> Expected: BQ is OLAP — high per-query startup latency, no per-row primary-key reads, billed by scan not row. Sessions are OLTP: low-latency CRUD on small rows. Use Firestore / Cloud SQL / `DatabaseSessionService` for sessions.

## 🛠 Have the student run

> 🛠 Open the BQ console (or `bq query --dry_run --use_legacy_sql=false 'SELECT * FROM \`bigquery-public-data.london_bicycles.cycle_hire\`'`) and note the estimated bytes scanned for that wildcard query vs `SELECT bike_id, duration FROM ... LIMIT 100`. Internalize the order of magnitude.

## 🤖 Tutor

> The student should leave this page knowing that BQ is the **right tool for analytical agent questions** and the **wrong tool for state**. Plus a healthy fear of bytes-scanned. Set this up so page 03 (cost guard) lands as a relief, not paranoia.

---

[← Prev: 10C_BigQueryAgents/00_Overview] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/02_NL2SQLPattern →]
