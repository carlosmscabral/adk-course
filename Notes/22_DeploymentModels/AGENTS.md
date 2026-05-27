# 🤖 AGENTS.md — Module 22 Deployment Models (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this after the global [AGENTS.md](../../AGENTS.md) and after [Module 21's AGENTS.md](../21_AdkApiSurface/AGENTS.md). Module 22 is where the student stops writing agents and starts **operating** them. The mindset shift matters more than any single command.

## What the student should walk away knowing

- The three deployment paths (Cloud Run, Agent Engine, GKE) and **how to choose**.
- That the agent code is **transport-agnostic** — same `agent.py` ships everywhere; the deployment artifact differs.
- The `AgentEngineApp(AdkApp)` subclass pattern and why `set_up()` ordering matters.
- Session persistence is **the** durability choice — and the default loses everything on restart.
- Cold start, concurrency, and Live API scaling constraints per platform.
- Service identity vs end-user identity — never confuse them.
- Observability wiring per platform (logs free, traces require setup, metrics are custom work).
- Secrets across platforms — Secret Manager + the platform-native binding.
- The honest cost model: LLM tokens dominate (60-90%), platform differences shift the bill by 10-30%.
- The 12-item production checklist on page 11.

## Pacing

- **Easy if:** the student has shipped a containerised service to Cloud Run or similar before. Pages 02/03 feel familiar; spend most time on 04 (session persistence — the trap most teams hit), 06 (auth identity model — easy to get wrong), and 11 (the checklist).
- **Hard if:** they've never deployed anything to GCP. Walk them through [[Cloud_Run]] detour before page 02 and [[AgentEngine]] detour before page 03. Page 03A GKE can be **skipped** for first-pass — only return to it if the student's org actually runs GKE.
- Expected total time for an on-pace student: ~5.5 hours (sum of `estimated_minutes`).

## Watch for these mistakes

- **"I'll just use GKE because we use K8s elsewhere."** Push back hard. The ops-weight math on page 09 (18 engineer-hours/mo × $150 = $2700/mo) usually dwarfs any infra savings. GKE is only right if the cluster already exists with on-call.
- **`InMemorySessionService` in production.** They deploy, demo works, ship — first pod restart loses every conversation. Symptom: "where did my session go?" Fix: page 04's recipe.
- **Default compute SA on Cloud Run.** They use `gcloud run deploy` without `--service-account=`. Now their agent runs with `roles/editor` project-wide. Audit-finding waiting to happen. Push them on page 06's least-privilege list.
- **Forgetting `set_up()` ordering on Agent Engine.** They call `super().set_up()` before `setup_telemetry()`. Symptom: traces don't show up. Fix: page 07's gotcha — telemetry first.
- **Cloud Run default `--concurrency=80`.** The number is for fast HTTP. Agent turns are 3-8s. Symptom: p99 climbs to 30s under load. Fix: page 05's tuning recipe — start at 10.
- **No budget alert until after the incident.** They get a $4000 monthly bill from a loop bug. Wire **both** budget alerts AND token-rate alerts (page 09 § In Production).
- **Secrets in `--set-env-vars`.** Visible in deploy logs and `gcloud run services describe`. Use `--set-secrets` instead (page 08).
- **Mixing service identity with end-user identity.** Agent's SA used to access user data → no per-user audit trail. End-user OAuth used for agent's own infra calls → rate limits hit. Page 06 has the decision frame; demand they write it down.

## When to suggest a detour

| Student says / shows                                  | Suggest                                            |
|-------------------------------------------------------|----------------------------------------------------|
| "What's the difference between Cloud Run and Functions?" | [[Cloud_Run]] — primitives + when to choose.    |
| "Agent Engine — is that just a managed Cloud Run?"    | [[AgentEngine]] — what it actually buys you.       |
| "Why a Dockerfile if `adk deploy cloud_run` exists?"  | [[Cloud_Run]] § "when you outgrow the wrapper."    |
| "I need OAuth — how does that even work?"             | Module 18 (Auth flows) first; come back.           |
| "What's OTel? What's a span?"                         | [[OpenTelemetry]] — 30 min on traces.              |
| "What's Workload Identity for, exactly?"              | Cross-link page 03A § Workload Identity step-by-step. |

If the same detour is suggested and declined twice, stop offering it.

## Mini-drill grading

- **Clean pass** = both deploys live and responsive; same `agent.py` on both; custom SA + secrets on Cloud Run; `AgentEngineApp` subclass on Agent Engine; postmortem identifies the rule violated.
- **Pass with hint** = student needed help with one of: writing the Dockerfile, structuring `agent_engine_app.py`, or finding which rule from page 11 they violated.
- **Fail** = they forked `agent.py` into a Cloud Run version and an Agent Engine version. Stop them and re-do — the *whole point* of ADK is that the agent is transport-agnostic.

### Edge case to probe (after the basic drill passes)

- Measure cold-start latency on the Cloud Run deploy (first request after 10min idle), then add `--min-instances=1` and re-measure. The 3-8s delta should match page 05's table — bring the abstract numbers to life.

## Cross-module hooks

- **This module is referenced from**: 23 Frontend Integration (the SPA points at the deployed endpoint), 24 Channel Integrations (Slack/Chat webhooks call the deployed endpoint), 99 Capstone (must ship).
- **This module references**: 21 ADK API Surface (the API this module deploys), 15 Observability (the telemetry plumbing — pages 02/03/06/07 of 15), 16 Production & Security (secrets, PII, guardrails), 17 Advanced Models (cost lever in § 09), 18 Auth flows (the OAuth pattern in § 10), 02A Agent Config (YAML — touched in § 03A).
- If the student forgets what `App` vs `Runner` does, back up to **1A page 02** briefly — don't re-teach inline.

## Connection to deeper Phase 5 modules

This module ends the "ship it" phase. Modules 23 and 24 are about the **consumer side**:
- 23 Frontend Integration: how a React app talks to the agent's `/run_sse`.
- 24 Channel Integrations: Slack, Google Chat, webhooks — each is a thin adapter over the API surface from module 21, served by a deployment from this module.

If the student gets to the end of M5 capstone and can't choose a deployment, send them back to **page 01's flowchart** and **page 11's checklist** — those two pages contain the operational decision frame they're missing.
