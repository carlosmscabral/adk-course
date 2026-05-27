---
module: 10C_BigQueryAgents
page: 02_NL2SQLPattern
title: 🧠 NL2SQL — schema-grounding & prompt structure
estimated_minutes: 25
prereqs: [10C_BigQueryAgents/01]
concepts: [NL2SQL, schema-grounding, sample-rows, gemini-2.5-pro, prompt-template]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 10C_BigQueryAgents/01_BigQueryForAgents] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/03_BigQueryAsTool →]

You are here: 🗺 Data & GCP Track ▸ 10C BigQuery for Agents ▸ 02 NL2SQL pattern

---

## 🧠 The pattern

> **NL2SQL** = the LLM generates SQL from natural-language input. The agent executes it. The agent then formats the result for the user.

Three steps, three responsibilities:

```
user ──► LLM (generate SQL) ──► you (execute SQL) ──► LLM (format result)
```

The LLM is doing **translation** at step 1 and **summarization** at step 3. Execution is *not* delegated to the LLM — code runs it. This separation is why NL2SQL works in practice.

## ⚠️ The schema-grounding problem

The LLM doesn't know your tables. It will hallucinate column names. It will guess "users.email" when you have `member_email`. It will invent join keys.

**Fix**: hand the schema to the LLM. Two places:

1. **In the agent instruction** (static — schema embedded at agent creation).
2. **As a tool result** (dynamic — agent calls a `get_schema()` tool first).

For most projects, option 1 is enough. Schema doesn't change often.

## 🛠 Schema block — what to include

```text
<TABLE: bigquery-public-data.london_bicycles.cycle_hire>
  rental_id                INT64       -- unique rental id
  duration                 INT64       -- seconds
  bike_id                  INT64
  end_date                 TIMESTAMP
  end_station_id           INT64
  start_date               TIMESTAMP
  start_station_id         INT64
  ...
PARTITIONED BY: DATE(start_date)
CLUSTERED BY: start_station_id, end_station_id
SAMPLE ROW: rental_id=42, duration=720, bike_id=11, ...
</TABLE>
```

Three things the LLM **needs**:

- **Column name + type** (avoid type-confusion bugs).
- **Partition column** (so it generates partition-pruning predicates → cheap queries).
- **Sample row** (a single example beats five paragraphs of description for grounding).

Optional but nice: a one-line description per column, especially for cryptic names.

## 🛠 Prompt template — anatomy

This is the template the `data-science` sample uses, distilled (from `data_science/sub_agents/bigquery/tools.py:158-208`):

```
You are a BigQuery SQL expert.

Guidelines:
- Use fully qualified names: `project.dataset.table` (backticks).
- Join as few tables as possible. Same data types on join columns.
- All non-aggregated columns in SELECT must be in GROUP BY.
- LIMIT to fewer than {MAX_ROWS} rows.
- Filter aggressively to minimize bytes scanned.

Schema:
```
{SCHEMA}
```

Question:
{QUESTION}

Generate the SQL only, no commentary.
```

The actual sample is more elaborate; the bones above are what matters. **Always** include:

- Dialect hint ("BigQuery Standard SQL").
- Table naming convention.
- Row cap.
- Schema block.
- The user's question, last.

## 🤖 Model choice

For NL2SQL:

- **gemini-2.5-flash** — works for simple/medium schema; cheap; default.
- **gemini-2.5-pro** — use when Flash hallucinates or schema is gnarly (50+ tables, deep joins). Slower, more expensive, much better SQL.

Start with Flash. Upgrade to Pro when eval shows the lift.

## ⚠️ Common failures

1. **Hallucinated column** — schema not in prompt, or schema too vague.
2. **Cross-product joins** — LLM joined two huge tables without a filter. Cost-guard (page 03) catches this.
3. **No LIMIT** — LLM returns whole table. Always add `LIMIT 1000` in the prompt template.
4. **`SELECT *`** — scans every column. Discourage explicitly in guidelines.
5. **Wrong dialect** — generated MySQL or Postgres syntax. Pin the dialect in the prompt.

## ❓ Check

> ❓ **Ask the student:** "Your NL2SQL agent keeps generating queries without a `WHERE` clause on partitioned tables, scanning the whole table. Where do you fix it — in the prompt or in code?"
>
> Expected: BOTH. The prompt should describe the partition column (so the LLM *can* generate the predicate). The cost-guard callback (page 03) should reject queries that scan more than X GB (so it *must*).

## 🛠 Have the student run

> 🛠 In a REPL, format the schema for `bigquery-public-data.london_bicycles.cycle_hire` and embed it into the prompt template above. Ask the LLM (Gemini Flash) for "what was the busiest station in 2017?". Inspect the SQL. Did it pick the partition column? Did it `LIMIT`?

## 🤖 Tutor

> The schema-grounded prompt is the single biggest quality lever. Make the student *type* the schema block by hand once. Then they can use a helper function (which the drill provides).

---

[← Prev: 10C_BigQueryAgents/01_BigQueryForAgents] [↑ Map](../../MAP.md) [Next: 10C_BigQueryAgents/03_BigQueryAsTool →]
