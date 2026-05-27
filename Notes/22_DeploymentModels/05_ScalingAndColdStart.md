---
module: 22_DeploymentModels
page: 05_ScalingAndColdStart
title: Scaling, cold start, concurrency
estimated_minutes: 20
prereqs: [22_DeploymentModels/04]
concepts: [autoscaling, cold start mitigation, concurrency, Live API constraints]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionPersistenceComparison](04_SessionPersistenceComparison.md)  [↑ Map](../../MAP.md)  [Next: 06_AuthAndIAM →](06_AuthAndIAM.md)

You are here: 🗺 Deployment & Integration Track ▸ 22 Deployment Models ▸ 05 Scaling & cold start

---

## ☁️ The three numbers

| Knob              | Cloud Run                          | Agent Engine                  | GKE                                  |
|-------------------|------------------------------------|-------------------------------|--------------------------------------|
| **Concurrency**   | per-instance (`--concurrency=20`)  | Managed                       | Per-pod, you set                     |
| **Min instances** | `--min-instances=N` (0..N)         | Managed                       | HPA `minReplicas`                    |
| **Max instances** | `--max-instances=N` (cap)          | Managed                       | HPA `maxReplicas`                    |

For ADK agents, the **concurrency** number is the one most teams get wrong. The Cloud Run default of 80 assumes short HTTP responses. An agent turn with one tool call is ~3-8s; 80 concurrent on one CPU thrashes. Drop to **10-25 per instance** for agent workloads.

## ☁️ Cold start — the real cost

A Cloud Run cold start for an ADK agent costs:

- ~500ms-1s container start.
- 1-3s Python import (Vertex SDK, ADK, your tools).
- 0.5-2s first-tool-call-only initialisation (if you lazy-init clients).
- 0.5-1s first LLM call (Vertex SDK warmup).

Total: **3-8 seconds** for a cold pod's first user. Mitigations from cheapest to most invasive:

### 1. Keep one instance warm

```bash
--min-instances=1
```

Costs ~$10/month on an idle CPU. Eliminates cold start for the **first** request after idle. Doesn't help if all instances are busy and a new one spins up.

### 2. CPU boost during startup (Cloud Run only)

```bash
--cpu-boost
```

Doubles CPU during cold start. Doesn't reduce the *number* of cold starts but cuts each one ~30%.

### 3. Lazy-import heavy deps

```python
# instead of:
import vertexai                  # at module top

# do:
def _get_vertex():
    import vertexai
    return vertexai

# call _get_vertex() inside the request handler
```

This trades **first request** latency for **subsequent boots are faster** — the heavy import is amortised across requests on the same instance.

### 4. Pre-warm the LLM client

Cold start often hides as "first LLM call slow." Make a no-op LLM call in `set_up()` / startup:

```python
async def warmup():
    runner = ...  # build once at startup
    async for _ in runner.run_async(user_id="warmup", session_id="warmup",
                                    new_message=types.Content(role="user",
                                                              parts=[types.Part.from_text("ping")])):
        break
```

Costs one LLM call per cold start (~$0.0001 with flash). Saves 1-2s on the first real request.

### 5. Move to Agent Engine

Agent Engine manages cold start for you. If you're spending engineering time on it, consider whether platform choice is the answer.

## ☁️ Concurrency tuning

A concrete recipe for Cloud Run:

1. Start at `--concurrency=10`.
2. Run a load test: 50 RPS, mixed turns (short + tool-call + long).
3. Measure p95 latency at 10 concurrent.
4. If CPU is < 60% utilised at p95, raise concurrency to 20.
5. Iterate until p95 latency starts climbing — that's your inflection point. Use **half** of that as your prod setting.

For GKE, the same idea but the concurrency is per-pod. `HorizontalPodAutoscaler` should scale on a custom metric like `agent_requests_in_flight` (set this via a Prometheus exporter), not just CPU. CPU as a scaling signal under-provisions for tool-call-heavy turns where the agent is mostly waiting on I/O.

## ☁️ Live API and long connections

`/run_live` WebSockets are **stateful**. They constrain how you autoscale:

| Platform     | WS cap                  | Reconnect mid-stream needed?   |
|--------------|-------------------------|--------------------------------|
| Cloud Run    | 15min idle / 60min max  | Yes — for sessions > 15min     |
| Agent Engine | Managed (extended)      | Rarely                         |
| GKE          | You set the LB cap      | Depends on your config         |

For voice agents that target multi-hour conversations, Agent Engine is the path of least resistance.

For Cloud Run / GKE voice: implement a **reconnect protocol**. On the server, persist enough state (last N audio frames, last model state) to resume. On the client, automatically reconnect on disconnect, replay state, resume. This is real engineering — budget a sprint.

## ☁️ Scale-to-zero — when it's a trap

Cloud Run scales to zero by default. **Zero instances** means **next request is a cold start**. For consumer apps with sporadic traffic, that's painful. Two patterns:

- **Always-warm fleet**: `--min-instances=1` (or more). Pays ~$10/instance/month idle.
- **Predictive warming**: a cron that hits `/health` from a different region every 5 min to keep one instance up. Free, fragile (Cloud Run may still recycle).

For internal apps used only during working hours, scale-to-zero overnight is genuinely great. Don't over-engineer warmness if your traffic pattern doesn't justify it.

## ⚠️ Gotcha — autoscaling on tokens

Agent latency is dominated by LLM tokens, which are network-bound, not CPU-bound. CPU-based autoscaling under-reacts to traffic spikes. **Symptom**: latency climbs to 30s; CPU is at 20%; new pods don't spin up. **Fix**: scale on a custom metric — `requests_in_flight` is the simplest, `tokens_per_second` is more accurate. Both require a Prometheus exporter you write.

## ⚠️ Gotcha — request-budget timeout vs LLM timeout

Cloud Run's request timeout caps the whole request, including tool calls and LLM round-trips. If your timeout is 60s and a tool call hits 70s, the client sees a 504 — but **the agent's session state is in an inconsistent half-finished state**.

Mitigations:
- Set Cloud Run timeout > sum of expected tool latencies + LLM call.
- For tools that *might* exceed budget, use `LongRunningFunctionTool` (module 03) and yield to the user.
- Hard-cap individual tool calls in your tool code (`asyncio.wait_for(..., timeout=30)`).

## 🚀 In Production

> **🚀 In Production**
>
> "It's slow" is the most common agent complaint and the **least** likely to be a code bug. It's almost always: cold start, undersized container, concurrency too high, or the LLM region not co-located with the agent region. Instrument **p50, p95, p99 latency by route** before you start tuning — without those numbers you'll fix the wrong thing.

> ❓ **Ask the student:** "Your Cloud Run agent's p50 is 3s but p99 is 30s. What's the most likely cause?" *(Cold starts hitting the p99 tail. Confirm with the `--min-instances` knob: set it to 1 for an hour; p99 should drop.)*

---

[← Prev: 04_SessionPersistenceComparison](04_SessionPersistenceComparison.md)  [↑ Map](../../MAP.md)  [Next: 06_AuthAndIAM →](06_AuthAndIAM.md)
