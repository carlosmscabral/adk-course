# AGENTS.md — Module 15 Observability (teaching notes for the AI tutor)

## What the student should walk away knowing

- Why agents need observability *more than* ordinary services (non-determinism).
- The three signals — logs, traces, metrics — and what each one answers.
- How a single `Runner.run_async()` becomes one OpenTelemetry trace with many spans.
- The four metrics that matter: tokens per turn, latency per tool, error rate per tool, cost per model.
- How `BigQueryAgentAnalyticsPlugin` wires BigQuery as a long-term analytics sink.
- The eight in-production hardening items on page 08.

## Pacing

- **Easy if:** student has used OpenTelemetry in another stack. Skim 03; spend most time on 04 (agent-shaped traces) and 08 (in-prod).
- **Hard if:** student has only ever used `print` for debugging. Slow down at 01 (motivation) and 03 (vocabulary). Suggest the [[OpenTelemetry]] detour before page 04.

## Watch for these mistakes

- **Treating logs and traces as the same thing.** Have them re-read the table on page 01 if they conflate.
- **Calling `set_tracer_provider` after creating the `App`.** Spans go nowhere; the bug looks like "OTel doesn't work." Always wire the provider first.
- **Using `session.id` as a metric label.** Will cost real money in cardinality. Flag immediately.
- **Logging the raw prompt without redaction.** PII / secrets leak — cross-link them forward to 16's PII redaction recipe.
- **Forgetting `BatchSpanProcessor`.** `SimpleSpanProcessor` blocks the agent on every span. Fine in a notebook, dangerous in prod.

## When to suggest a detour

- Student asks "what does `getLogger(__name__)` even do?" → suggest [[PY_logging]].
- Student asks "what is OTLP, BSP, W3C TraceContext?" → suggest [[OpenTelemetry]].
- Student asks about per-tool retries → that is module 13 plugins (`ReflectAndRetryToolPlugin`), not observability — redirect.

## Mini-drill grading

- **Pass** = student's trace shows nested spans for critic + reviser + at least one tool, and JSON logs carry a session_id that matches a span attribute.
- **Stretch** = student added a `request.id` custom attribute via callback and can search the trace by it.
- **Common stumble** = student picks a prompt that doesn't trigger the reviser. Prompt them to give the critic something obviously wrong so it escalates.

## Cross-link reminders

- 13 Plugins — `LoggingPlugin`, `BigQueryAgentAnalyticsPlugin` mechanics.
- 14 Evaluation — the M4 auditor that we wire OTel into.
- 16 ProductionSecurity — PII redaction recipe used on page 02 and page 08.
- 10C BigQueryAgents — scan-byte cap pattern referenced on page 06 and page 08.
