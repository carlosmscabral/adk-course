# AGENTS.md — Module 10C BigQuery for Agents (teaching notes for the AI tutor)

## What the student should walk away knowing

- When BigQuery is the right backend for an agent (analytical workloads) and when it isn't (OLTP / sessions).
- The NL2SQL pattern: LLM generates, code executes, LLM formats. Three responsibilities.
- The schema-grounding problem and how to fix it (schema block in the prompt, sample rows, partition info).
- ADK's `BigQueryToolset` with `BigQueryToolConfig` — `WriteMode.BLOCKED`, `application_name`, `max_query_result_rows`.
- The cost-guard pattern: `before_tool_callback` with `dry_run` + `maximum_bytes_billed`.
- BigQuery's native vector search (`VECTOR_SEARCH` + `ML.GENERATE_EMBEDDING`) and when it beats Vertex AI Vector Search.
- `BigQueryAgentAnalyticsPlugin` as a one-line telemetry sink (teaser — full coverage in 13 and 15).
- Production concerns: cost, SQL injection / exfiltration, IAM narrowing, audit logging, result-size guards.

## ☁️ GCP cost concern

The drill uses `bigquery-public-data.london_bicycles` which is free under the BQ free tier (the table is small enough for typical drill queries to stay under the 1 TB/month free quota easily).

That said: **the entire point of this module is teaching cost discipline.** Even on the public dataset, drill the cost-guard. If the student skips wiring the cost-guard in the drill, that's a fail — not because they'll bankrupt themselves on `london_bicycles`, but because the muscle memory matters when they later hit a TB-scale table.

## Pacing

- **Easy if** student is fluent in SQL and read 10A/10B carefully: cruise through 01-04, slow on 06 (the sample is big).
- **Hard if** student is new to BQ partition/clustering concepts: pause on page 01 for a hands-on `bq query --dry_run` exercise, *then* continue.

## Watch for these mistakes

- **Default WriteMode** — the SDK default *is* `BLOCKED` (see `src/google/adk/integrations/bigquery/config.py:56`), but always set it explicitly for clarity and to guard against future changes. Students who skip the explicit setting are relying on a default they did not verify.
- **`use_query_cache=True` in dry_run** — silently returns 0 bytes for cached queries → cost-guard always passes → false sense of safety.
- **Forgetting partition info in the schema** — LLM generates queries that scan the whole table.
- **`SELECT *`** — LLM defaults to it. Forbid in the prompt.
- **Schema fetched from one project, executed against another** — they don't match. Pin both projects in env vars.
- **Mixing this with 10A's task-type sin** — `ML.GENERATE_EMBEDDING` takes `task_type`. Wrong type = bad vectors. Same rule.

## When to suggest a detour

- "What's `_PARTITIONDATE` / `_PARTITIONTIME`?" — quick aside about BQ pseudo-columns.
- "How do I make my own dataset?" — `bq mk`. Not a formal detour, just show the command.
- "What about Apache Beam / Dataflow for ingest?" — out of scope for 10C; flag as "production data engineering, separate course."
- "What about Looker Studio for visualizing agent outputs?" — out of scope; mention but don't drill.

## Mini-drill grading

- **Pass** = correct station name returned AND cost-guard wired AND SQL uses a partition predicate.
- **Strong pass** = bonus (cost-guard rejects "show me everything", LLM recovers with a sane retry).
- **Fail** = WriteMode left default, no cost-guard, or LLM returns a hallucinated station name (means schema-grounding wasn't done right).
- **Edge probe**: ask the student "what would happen if you accidentally set `use_query_cache=True` in the dry_run?" — answer: cost-guard would pass even on expensive queries that are cached. Discuss why this is dangerous.

## Cross-link reminders

- 10C connects to 13 (Plugins) — `BigQueryAgentAnalyticsPlugin` teaser in page 05; deep dive in 13.
- 10C connects to 15 (Observability) — BQ as telemetry destination plus OpenTelemetry export.
- 10C connects to 07 (Callbacks) — cost-guard is `before_tool_callback`.
- 10C connects to 03 (Tools) — `BigQueryToolset` is one of the canonical built-in toolsets.
- 10C connects to 16 (Production & Security) — the IAM narrowing + authorized views pattern is expanded there.
