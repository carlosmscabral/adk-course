---
module: 15_Observability
page: 00_Overview
title: Observability — seeing what your agent is doing in production
estimated_minutes: 10
prereqs: [13_Plugins/06, 14_Evaluation/06]
concepts: [logging, tracing, metrics, OpenTelemetry, BigQuery sink]
icon: 🔭
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/10_MiniDrill](../14_Evaluation/10_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 15_Observability/01_WhyObservability →](01_WhyObservability.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 00 Overview

---

## 🔭 What you'll learn

By the end of this module you will:

- Know why agents are *especially* hard to debug without traces.
- Wire `LoggingPlugin` for structured JSON logs.
- Understand OpenTelemetry traces, spans, and attributes.
- Read a single `Runner.run_async()` as **one trace** of many spans.
- Define the metrics that matter: **tokens per turn, latency per tool, error rate per tool, cost per model**.
- Wire `BigQueryAgentAnalyticsPlugin` as a long-term analytics sink.
- Dissect `agent-observability-bq/` end-to-end.

## 🧭 Prereqs

- **13 Plugins** — `LoggingPlugin` and `BigQueryAgentAnalyticsPlugin` live here. We only re-use them; the plugin mechanics are upstream.
- **14 Evaluation** — your M4 auditor exists. We will *wire* observability into it in the mini-drill.

## ⏱ Time budget

**2 days.** One day to read pages 01-07; one day for the dissection plus mini-drill.

## 📦 Sample anchor

`/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/` — a BigQuery analytics agent that *also* uses BigQuery as its observability sink. We will read every file in `09_DissectingSample.md`.

## 🗺 Page map

| # | Page | Why |
|---|---|---|
| 01 | WhyObservability | The motivating problem. |
| 02 | StructuredLogging | `LoggingPlugin` + JSON shape. |
| 03 | OpenTelemetryBasics | Traces / spans / attributes. |
| 04 | TracingAnAgentRun | One run = one trace. |
| 05 | Metrics | Tokens, latency, errors, cost. |
| 06 | BigQueryAsSink | Long-term storage and SQL. |
| 07 | DissectingSample | Read the real sample. |
| 08 | InProduction | The hardening checklist. |
| 09 | KnowledgeCheck | 6 questions. |
| 10 | MiniDrill | Wire OTel into your M4 auditor. |

> 🤖 **Tutor:** Before page 01, ask the student to recall the last time they had to debug a non-deterministic program. Their war story is the hook for *why* observability matters.

---

[← Prev: 14_Evaluation/10_MiniDrill](../14_Evaluation/10_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 15_Observability/01_WhyObservability →](01_WhyObservability.md)
