---
module: 14_Evaluation
page: 10_InProduction
title: Evaluation in production
estimated_minutes: 25
prereqs: [14_Evaluation/09]
concepts: [CI gating, cost, flakiness, golden set curation, drift tracking]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 14_Evaluation/09_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/11_KnowledgeCheck →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 10 In Production

# 🚀 What "evals in prod" actually looks like

## 1. Evals as a CI gate

Block release on eval failure. Pattern:

- Run a small fast suite (≈10 cases, `num_runs=1`) on every PR. Surface failures inline.
- Run the full suite (50-500 cases, `num_runs=5+`) nightly. Block the next release if it regresses.

If you're not gating on evals, every prompt change is a coin flip.

## 2. Cost is a real constraint

- 50 cases × 5 runs × 2 (judge + agent calls) × ~$0.01/call = ~$5 per nightly run. Cheap.
- 500 cases × 10 runs × LLM-as-judge with pro = ~$500/run. Add up over a quarter.

Mitigations:

- Use cheaper models for low-stakes metrics (FinalResponseMatchV1 needs no LLM).
- Cap LlmAsJudge to high-stakes cases.
- Cache eval runs that are deterministic (no temp) — same input + same model version = same result.

## 3. Flakiness is real, especially for LlmAsJudge

LLM judges are non-deterministic. Mitigate:

- `num_runs ≥ 5` for any LlmAsJudge metric.
- Lower temperature on judge calls (0.0 if the framework allows).
- Track per-case variance — if one case has 0.5 stdev across runs, the case is ambiguous; rewrite it.
- Watch for "passing by luck" — set thresholds slightly above noise floor.

## 4. Curated golden set vs auto-generated cases

You'll be tempted to auto-generate cases from production traffic. Tempting because:

- Free training signal.
- Reflects real distribution.

But:

- Production traffic is noisy. Auto-cases inherit user mistakes, off-topic queries.
- You don't know the *gold* answer for production traffic without human review.

Best of both worlds: auto-collect candidate cases from production → human-curate to a golden set → version the golden set.

## 5. Track score over time

A single eval run is a point. Trends are the signal. Persist eval results to a queryable store:

- `response_match_avg` per metric per case over time.
- `tool_trajectory_pass_rate` over time.
- LlmAsJudge mean per rubric criterion over time.

Cross-link: `BigQueryAgentAnalyticsPlugin` (module 13) gives you the runtime-events warehouse; consider a parallel `eval_runs` table for eval results.

## 6. The "untested" failure modes

Things evals won't catch unless you write cases for them:

- Brand voice / tone (covered by rubric criteria, but you have to write them).
- Refusal accuracy ("did it refuse the right things and only those?").
- Latency / cost regressions (these need separate observability — see 15).
- Multi-turn coherence (most cases are single-turn — write multi-turn explicitly).

## Quick checklist before launch

- [ ] At least 20 EvalCases covering happy path, edge case, failure mode, refusal.
- [ ] PR-time fast suite green; nightly stable-signal suite green.
- [ ] `num_runs` chosen explicitly per CI stage.
- [ ] Eval results persisted to a queryable store.
- [ ] Score-over-time dashboard exists.
- [ ] Per-case ambiguity audited (no high-variance cases).
- [ ] Golden set under version control.

> 🤖 **Tutor:** The student's instinct is to write 5 happy-path cases and call it done. Push for the failure modes and the refusal cases — those catch regressions that happy paths miss.

---

[← Prev: 14_Evaluation/09_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/11_KnowledgeCheck →]
