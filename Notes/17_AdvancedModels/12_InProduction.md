---
module: 17_AdvancedModels
page: 12_InProduction
title: Models in production — routing, lock-in, rate limits
estimated_minutes: 20
prereqs: [17_AdvancedModels/11]
concepts: [routing, fallback, rate limits, prompt caching, cold start, model bumps]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 17_AdvancedModels/11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/13_KnowledgeCheck →](13_KnowledgeCheck.yml)

You are here: 🗺 Production Track ▸ 17 Advanced Models ▸ 12 In Production

---

## 🚀 The checklist

### 1. Route per task; do not single-model

A Pro-everywhere agent is the most expensive bad design. A Flash-Lite-everywhere agent is the second.

- Use a Flash-Lite *router* to classify intent.
- Send the request to the cheapest sub_agent that can handle it.
- Escalate only on uncertainty.

Cross-link page 08 for the patterns and `_figures/model_matrix.txt` for the decision rule.

### 2. Pin model versions

`gemini-2.5-flash` is an alias. `gemini-2.5-flash-002` is a pinned version. Aliases drift; pinned versions are reproducible.

- Pin in code or in a config file.
- Re-run your eval suite (module 14) when you consider bumping.
- Treat a model bump like a dependency upgrade — review, test, ship behind a feature flag.

### 3. Vendor lock-in is real, even with `LiteLlm`

`LiteLlm` hides the API differences. It does **not** hide:

- Tokenizer differences (your token cost models break).
- Prompt-tuning differences (a 90-percentile prompt on OpenAI may be 70-percentile on Anthropic).
- Tool-call shape edge cases.
- Streaming semantics.
- Billing currencies and rate-limit conventions.

Plan for *vendor optionality*, not vendor agnosticism. The cheapest path to genuine portability is *measure-everything*.

### 4. Rate limits hit per provider

Each provider has its own quota and its own outage windows.

- Track 429s and 5xx by provider in your metrics (module 15).
- Implement a fallback chain: primary → fallback → cached degraded response.
- Use `ReflectAndRetryToolPlugin` (module 13) for tool retries; build a similar pattern for model retries.
- Backpressure: when you see 429 storms, slow your *own* retry rate before the provider further throttles you.

### 5. Prompt caching is provider-specific

- Anthropic supports `cache_control` annotations on prompt blocks (huge win for repeated system prompts).
- Google has *context caching* for Gemini Pro (cache long context blobs, charge less).
- OpenAI handles caching mostly behind the scenes.

Each is *configured differently*. If you switch providers, your effective cost may move by 2-5× from caching alone. **Measure, don't assume**.

### 6. Gemma cold start matters

- Keep at least one worker warm with a periodic tiny prompt.
- Auto-scale on queue depth, not GPU utilization (utilization lags).
- Plan capacity per concurrent user, not per RPS — long replies hold the GPU.
- Page 04 § warmup ping is the cheapest implementation.

### 7. Apigee / gateway is itself a SPOF

If your enterprise routes everything through Apigee, the gateway team is on your incident pager. Have a *client-side fallback* for tier-1 traffic that bypasses the gateway in case of failure (behind a feature flag).

### 8. Track cost per model AND per task

Cost per model is a finance metric.
Cost per resolved task (model × turns × tools) is the *engineering* metric.

A Pro that solves it in 1 turn beats a Flash that fumbles for 5 turns. Build dashboards that show both.

### 9. Eval suite is the source of truth for "which model"

Don't pick a model on vibes. Build a representative eval set (module 14) and rerun on every model candidate. The matrix of (model × eval-pass-rate × cost × p95-latency) is the answer.

### 10. Document your model choices

Each `LlmAgent` in your codebase should have a comment or doc explaining *why* this model was picked. New engineers will otherwise flip them to whatever was discussed in last week's tech talk.

```python
# Why gemini-2.5-flash-lite: router-only; classifies in < 200ms; quality
# sufficient because the sub_agent does the heavy lifting. Last benchmarked
# against gpt-4o-mini on 2026-04-01; flash-lite was 60% cheaper, same accuracy.
router = LlmAgent(model="gemini-2.5-flash-lite-002", ...)
```

> 🤖 **Tutor:** ask the student to draft this comment for *each* model choice in their M4 auditor. If they can't justify it, that is the lesson.

---

[← Prev: 17_AdvancedModels/11_DissectingSample](11_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 17_AdvancedModels/13_KnowledgeCheck →](13_KnowledgeCheck.yml)
