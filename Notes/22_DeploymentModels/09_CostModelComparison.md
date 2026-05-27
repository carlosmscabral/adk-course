---
module: 22_DeploymentModels
page: 09_CostModelComparison
title: Cost model — what actually moves the bill
estimated_minutes: 20
prereqs: [22_DeploymentModels/08]
concepts: [cost dominance, token cost, compute cost, ops weight]
icon: 💰
in_production: true
detours_suggested: []
---

[← Prev: 08_SecretsAcrossPlatforms](08_SecretsAcrossPlatforms.md)  [↑ Map](../../MAP.md)  [Next: 10_DissectingSample →](10_DissectingSample.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 09 Cost model

---

## 💰 The honest ranking

For 99% of ADK agents, the bill ordering is:

```
LLM tokens       (60-90% of the bill)
  > Tool costs   (10-30% — BigQuery scans, Search, third-party APIs)
    > Compute    (5-15% — Cloud Run/GKE/Agent Engine)
      > Storage  (1-5% — sessions, artifacts, logs)
        > Network (1-2%)
```

Optimisations that don't move the top of the stack are theatre. **First, reduce tokens.** Then think about everything else.

## 💰 The math at concrete scales

Assume an agent that handles 100k turns/month, each turn:

- 2 LLM calls (one for tool decision, one for final answer).
- Average 1500 input tokens + 400 output tokens per call.
- One tool call (cheap).
- ~5 seconds of compute, light CPU.

### LLM tokens (Gemini 2.5 Flash)

- Input: 100k × 2 × 1500 = 300M tokens × $0.075/M = **$22.50**
- Output: 100k × 2 × 400 = 80M tokens × $0.30/M = **$24**
- **Total LLM: ~$46.50/month**

Switch to **Gemini 2.5 Pro** for the same workload:
- Input: 300M × $1.25/M = $375
- Output: 80M × $5/M = $400
- **Total LLM: ~$775/month** (16x more)

Choice of model is by far the biggest cost lever. Cross-link **17 Advanced Models** for when Pro is genuinely needed.

### Compute — Cloud Run

100k × 5s = 500k vCPU-seconds.

- Cloud Run pricing (2026, us-central1): ~$0.000018/vCPU-second + memory.
- 500k × $0.000018 = **$9/month** at full utilization.
- With `--min-instances=1`: +$8/month for the always-warm CPU.
- **Total Cloud Run: ~$17/month**.

### Compute — Agent Engine

Agent Engine charges per "reasoning engine hour" — roughly a 20-50% premium over Cloud Run-equivalent.

- Same workload, **~$25-35/month**.

### Compute — GKE

If you already run GKE and the agent fits in existing capacity, **marginal cost ≈ $0** (you pay for the cluster regardless). If you spin up a dedicated node for the agent: $30-100/month per `e2-standard-2` node.

### Sessions — Cloud SQL

For 100k turns and ~10 turns per session: ~10k active sessions/month.

- Cloud SQL Postgres `db-f1-micro`: ~$10/month + storage (~$1/month).
- **Total sessions: ~$11/month**.

Agent Engine: included.

### BigQuery analytics sink

100k turns × ~5 events × ~1KB = ~500MB of event data per month.

- Storage: 500MB × $0.02/GB = $0.01 (rounding error).
- Query: depends on usage; analytics queries scanning 90 days of data ~5GB × $5/TB = ~$0.03 per query.
- **Total BQ sink: <$1/month** for typical analytics usage.

### Observability

- Cloud Trace: with 5% sampling at 100k traces, 5k stored traces/month, free tier covers it.
- Cloud Logging: stdout-driven, ~10GB/month, ~$5.

## 💰 The summary table — at this scale

| Item                 | Cloud Run + Postgres | Agent Engine    | GKE (in existing cluster) |
|----------------------|----------------------|-----------------|---------------------------|
| LLM (Flash)          | $47                  | $47             | $47                       |
| Compute              | $17                  | $30             | ~$0 (marginal)            |
| Sessions             | $11 (Cloud SQL)      | Included        | $11                       |
| BQ analytics         | $1                   | $1              | $1                        |
| Observability        | $5                   | Included        | $5                        |
| **Total**            | **~$80/month**       | **~$80/month**  | **~$65/month**            |

LLM dominates. Platform differences shift the bill by 10-30% at this scale.

## 💰 Where the ranking flips

**At very high RPS (1000+ RPS)**: compute matters more. Agent Engine's per-request premium compounds; Cloud Run with custom auto-scaling wins on cost. GKE wins if the cluster is amortized.

**At very low usage (< 1000 turns/month)**: Cloud Run scale-to-zero wins decisively (~$0 if no traffic). Agent Engine has a small floor cost regardless. GKE pays for the cluster regardless.

**For multi-region / global**: Agent Engine handles it; Cloud Run + Cloud SQL HA gets expensive; GKE multi-cluster is engineering-heavy.

## 💰 Ops weight — the hidden cost

| Path             | Engineer-hours per month (steady state) |
|------------------|------------------------------------------|
| Agent Engine     | ~2 hours                                 |
| Cloud Run        | ~5 hours (deploys, log review)           |
| GKE              | ~20+ hours (cluster ops, upgrades, security patches, on-call) |

At $150/hour fully loaded, GKE's 18-hour delta is **~$2,700/month** in engineering cost. That dwarfs any per-platform GCP bill difference. Account for this honestly when picking.

## 💰 Token-cost optimisations (the ones that matter)

In order of impact:

1. **Use Flash by default.** Switch to Pro only for tasks Flash fails on.
2. **Cache the system prompt.** Gemini Vertex caching cuts re-billing the same instruction every turn (cross-link **17 page 06**).
3. **Trim history aggressively.** A turn 50 messages deep re-bills all 50. Summarise old turns into one digest message.
4. **Don't re-feed tool outputs.** If a tool returns 10KB, your next turn shouldn't include the full result — summarise it.
5. **Set `max_output_tokens`.** A bug in the prompt can cause the model to ramble for 4000 tokens of unwanted output.

> ❓ **Ask the student:** "You shave 30% off compute cost by switching from Cloud Run to GKE. Worth it?" *(Almost never. 30% of $17 is $5. One engineer-week of GKE ops is $1500. The math doesn't math unless you have other reasons.)*

## ⚠️ Gotcha — cost spikes from runaway agents

A loop bug (agent calls itself, transfer_to_agent cycle) can burn through tokens at the agent's RPS × N turns per loop. Without a guard:

- 10 loop turns × 100 RPS × 2 LLM calls × 2K tokens = 4M tokens/sec.
- At $0.30/M for output: **$1.20/second**. **$4,300/hour**.

You will spot this in **billing alerts** if you set them, in **token-rate metrics** if you log them, in **service degradation** when Vertex quotas trip. Set the alerts. Module 15 page 08 item #6.

## 🚀 In Production

> **🚀 In Production**
>
> Set a **monthly budget alert** in GCP Billing (`gcloud billing budgets create ...`) at 50%, 80%, 100% of your monthly expectation. Set a **token-rate metric** (tokens per minute, per agent) and alert when it exceeds 2x baseline. Both alerts together catch the two real cost incidents: (1) a slow leak (more users than expected), (2) a runaway bug (catastrophically more tokens than expected). The annual cost of these two alerts is zero; the cost of *not* having them is anyone's guess.

---

[← Prev: 08_SecretsAcrossPlatforms](08_SecretsAcrossPlatforms.md)  [↑ Map](../../MAP.md)  [Next: 10_DissectingSample →](10_DissectingSample.md)
