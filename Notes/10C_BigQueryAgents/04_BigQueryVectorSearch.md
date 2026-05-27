---
module: 10C_BigQueryAgents
page: 04_BigQueryVectorSearch
title: ☁️ BigQuery vector search — SQL-native
estimated_minutes: 25
prereqs: [10C_BigQueryAgents/03, 10A_EmbeddingsVectorSearch/05]
concepts: [VECTOR_SEARCH, ML.GENERATE_EMBEDDING, vector-column, IVF-index]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/03_BigQueryAsTool] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/05_BigQueryAgentAnalyticsPlugin →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 04 BigQuery vector search

---

## 🧠 Two products, one decision

Two ways to do vector search on GCP:

| | Vertex AI Vector Search | BigQuery `VECTOR_SEARCH` |
|---|---|---|
| Data lives in... | A managed index | A BQ column |
| Query is... | Python SDK `find_neighbors` | SQL `VECTOR_SEARCH(...)` |
| Latency | <50ms p50 | ~1-3s (BQ query overhead) |
| Best for | Real-time RAG, agent retrieval | Batch / analytical retrieval, joins with OLAP |
| Cost | Endpoint serving + storage | Bytes scanned + storage |
| Scale | Billions, ms latency | Billions, slower latency |

**Rule of thumb**:

- Online agent retrieval at chat latency → **Vertex AI Vector Search** (10A).
- Vectors as one more column in an analytical pipeline ("show me top similar products by category, joined with sales last 30 days") → **BQ VECTOR_SEARCH**.

## ☁️ Generate embeddings in BQ (no Python)

```sql
-- Create or reference a connection to Vertex AI:
CREATE OR REPLACE MODEL `myds.text_embed_005`
REMOTE WITH CONNECTION `us.vertex_ai`
OPTIONS (ENDPOINT = 'text-embedding-005');

-- Embed a column straight into a new table:
CREATE OR REPLACE TABLE `myds.docs_with_vecs` AS
SELECT
  doc_id,
  body,
  ml_generate_embedding_result AS embedding
FROM ML.GENERATE_EMBEDDING(
  MODEL `myds.text_embed_005`,
  (SELECT doc_id, body AS content FROM `myds.docs`),
  STRUCT(TRUE AS flatten_json_output,
         'RETRIEVAL_DOCUMENT' AS task_type)
);
```

Notice `task_type='RETRIEVAL_DOCUMENT'` — same gotcha from 10A/02. **It applies here too.** The query side will use `RETRIEVAL_QUERY`.

## ☁️ Query — `VECTOR_SEARCH(...)`

```sql
SELECT
  base.doc_id,
  base.body,
  distance
FROM VECTOR_SEARCH(
  TABLE `myds.docs_with_vecs`,        -- the haystack
  'embedding',                           -- the vector column
  (
    SELECT ml_generate_embedding_result AS embedding
    FROM ML.GENERATE_EMBEDDING(
      MODEL `myds.text_embed_005`,
      (SELECT 'what are decorators?' AS content),
      STRUCT(TRUE AS flatten_json_output,
             'RETRIEVAL_QUERY' AS task_type)
    )
  ),
  top_k => 5,
  distance_type => 'COSINE'
);
```

One SQL. Embed the query inline, search the index, return top-5 with distances. Join with anything else in BQ.

## ⚡ Speed it up — `CREATE VECTOR INDEX`

The query above scans the table by default. For prod, create a vector index:

```sql
CREATE OR REPLACE VECTOR INDEX `idx_docs_embedding`
ON `myds.docs_with_vecs` (embedding)
OPTIONS (index_type = 'IVF',
         distance_type = 'COSINE',
         ivf_options = '{"num_lists": 100}');
```

After indexing, `VECTOR_SEARCH(...)` uses the index automatically (much faster, slight recall trade — like TreeAH).

## 🚀 Why this is great for analytical agents

```sql
-- "Show me the 5 product descriptions most similar to 'wireless headphones',
--  along with their total sales last 30 days, grouped by category."
SELECT
  v.category,
  COUNT(*)              AS n_similar,
  SUM(s.sales_amount)   AS sales_30d
FROM VECTOR_SEARCH(...) AS v
JOIN `myds.sales` AS s USING (product_id)
WHERE s.sale_date > CURRENT_DATE() - 30
GROUP BY v.category;
```

One query: semantic retrieval + OLAP aggregation + GROUP BY. **You cannot do this from Vertex AI Vector Search** without round-tripping to BQ. When your retrieval *and* your analytics live in the same warehouse, this is the right shape.

## ⚠️ When BQ vector is the wrong tool

- Sub-second chat latency required — BQ query overhead alone is ~1s.
- Vectors at high update frequency (streaming inserts) — works but expensive.
- No other BQ data — you're paying for the warehouse to get vector search; use Vertex AI VS instead.

## ❓ Check

> ❓ **Ask the student:** "Your customer support agent does fast chat-style retrieval. Vertex AI Vector Search or BigQuery VECTOR_SEARCH?"
>
> Expected: Vertex AI Vector Search — chat latency dominates the decision. BQ's query overhead makes it the wrong tool for sub-second retrieval.

## 🛠 Have the student run

> 🛠 In the BQ console, run the `VECTOR_SEARCH` query above against `bigquery-public-data` if a public embedded dataset exists; or, more realistically, embed 100 short docs into their own dataset using the `ML.GENERATE_EMBEDDING` snippet above, then query.

## 🤖 Tutor

> Don't let the student think there's ONE vector search product on GCP. There are two, with different shapes. The drill (page 09) is BQ-flavored analytical; the 10A drill was Vertex-flavored real-time. Both skills are needed.

---

[← Prev: 10C_BigQueryAgents/03_BigQueryAsTool] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/05_BigQueryAgentAnalyticsPlugin →]
