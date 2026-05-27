---
module: 15_Observability
page: 01_WhyObservability
title: Why agents need observability more than ordinary services
estimated_minutes: 15
prereqs: [15_Observability/00]
concepts: [non-determinism, debugging, traces vs logs]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/02_StructuredLogging →](02_StructuredLogging.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 01 Why

---

## 🧠 The problem

A normal web service is deterministic. Same input → same output → same code path. When something breaks, you `print` your way to the bug.

An agent is **not** deterministic.

```
same prompt → different tool choice → different sub_agent transfer
            → different number of LLM calls → different output
```

Run it twice; get two different traces. The bug from yesterday may not reproduce today. Without recording *what happened*, you cannot debug, improve, cost-account, or audit.

## 🧠 Three things observability must answer

1. **What did the agent do?** Which tools fired, in what order, with what args, with what results.
2. **Why did it take so long?** Where in the trace was the latency — tool, model, sub_agent loop?
3. **What did it cost?** Tokens in, tokens out, per model, per turn, per user.

Without 1 you cannot reproduce. Without 2 you cannot optimize. Without 3 you will get a finance incident.

## 🧠 Logs vs traces vs metrics

| Signal | What it tells you | When to use |
|---|---|---|
| 🪵 **Logs** | One line per event. Easy to grep, hard to correlate. | "Did this error happen?" |
| 🧵 **Traces** | A causally-ordered tree of spans. | "What did the agent *do* on this request?" |
| 📊 **Metrics** | Aggregates over time. | "Is p99 latency rising?" |

All three are necessary. Skipping traces — the most agent-specific signal — is the most common mistake. ADK has first-class OpenTelemetry hooks specifically so you don't have to.

> ❓ **Ask the student:** Of the three signals, which one would tell you "user X's session is costing 10× the average"? *(Metrics, with per-user dimension.)*

## ⚠️ Gotcha — "I'll just read the events"

Yes, `runner.run_async()` yields `Event` objects with full content. In dev that is enough. In prod:

- Events are *transient* — once consumed, gone.
- Events are *per-session* — you can't aggregate across users.
- Events have no automatic latency stamps for sub-operations.

Observability is the *durable, queryable, aggregate* view of the same data.

> 🚀 **In Production**
>
> The cheapest mistake is to ship without observability and add it after the first incident. The most expensive mistake is to log so much that the bill exceeds the agent's revenue. **Trace 100% in dev, sample in prod** (page 08).

---

[← Prev: 15_Observability/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/02_StructuredLogging →](02_StructuredLogging.md)
