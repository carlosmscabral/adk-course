---
module: 4B_HumanInTheLoop
page: 10_DurableExecutionIntegrations
title: Durable execution — Temporal, Dapr for when ADK's built-in resume isn't enough
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/04]
concepts: [durable-execution, Temporal, Dapr, sagas, retry-policy, multi-day-workflows]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 09_ChatPlatformApprovals](09_ChatPlatformApprovals.md)  [↑ Map](../../MAP.md)  [Next: 11_DissectingSample →](11_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 10 Durable Execution

# 🛠 When ADK's built-in resume isn't enough

ADK's resumability is designed for **operator-friendly pauses**: minutes to hours, occasionally a day or two, with a small handful of human gates per workflow. Past that envelope, **durable execution platforms** (Temporal, Dapr Workflows, AWS Step Functions, Azure Durable Functions) start to win on the dimensions ADK doesn't ship:

| Concern | ADK resume | Durable execution |
|---|---|---|
| Pause duration | hours, occasionally days | unbounded — months, years |
| Retry policy per step | manual code | declarative (exponential backoff, jitter, max attempts) |
| Versioning of in-flight workflows | none — schema drift breaks | first-class — old workflows finish on old code, new ones on new |
| Compensation / saga (rollback chain) | hand-rolled | first-class |
| Cross-workflow signals (one workflow nudges another) | manual via session writes | first-class signal API |
| Observability | OpenTelemetry spans | dedicated UI showing every step + timestamps |

**Rule of thumb:** if the pause envelope is < 24h with 1-2 human gates, ADK's resume is the answer. Past that, look at Temporal or Dapr.

## What durable execution gives you that ADK can't

The killer features are **deterministic replay** and **versioning**:

- **Deterministic replay** — Temporal/Dapr re-execute your workflow code from scratch on resume, replaying recorded event history. Side-effecting steps (your "activities") are looked up in history and *not re-executed*. ADK does the simpler thing — re-runs the tool. Determinism gives you the at-most-once on activities that idempotency keys give you in ADK, without you wiring them.

- **Versioning** — a workflow paused 6 months ago resumes on the code that was deployed 6 months ago. ADK simply runs your current tool function — schema drift can crash a resume mid-stream. (Page 11 in the 06 module names this gotcha for `RequestInput` `response_schema`.)

## When to choose ADK + a durable execution layer

The composition is **ADK on the inside, durable engine on the outside.** Think:

```
  Temporal workflow                          ADK Runner
  ───────────────                             ──────────
  step 1: enqueue review job                  (called as a Temporal "activity")
  step 2: WAIT for human (Temporal signal)
  step 3: ADK runner.run_async to summarize   (called as a Temporal "activity")
  step 4: WAIT 30 days (Temporal timer)
  step 5: send follow-up email
  ─ entire workflow durable for 6 months ──
```

The durable engine owns the **long arc**; ADK owns each individual **agent call**. Each ADK call is short-lived (minutes), so ADK's lighter resume isn't strained.

## Sketch — Temporal calling an ADK agent

```python
# Work/4B_10_temporal_sketch.py — illustrative; assumes temporalio installed
from temporalio import activity, workflow
from datetime import timedelta


@activity.defn
async def run_adk_summarize(doc_text: str) -> str:
    """A Temporal *activity* that wraps an ADK Runner call."""
    runner = InMemoryRunner(app=summarizer_app)
    sess = await runner.session_service.create_session(
        app_name="summarizer", user_id="temporal"
    )
    out = ""
    async for ev in runner.run_async(
        user_id="temporal", session_id=sess.id,
        new_message=types.Content(role="user",
                                  parts=[types.Part(text=doc_text)]),
    ):
        for p in (ev.content.parts if ev.content else []):
            if p.text: out += p.text
    return out


@workflow.defn
class DocumentReviewWorkflow:
    @workflow.run
    async def run(self, doc_text: str) -> str:
        # Step 1: ADK summarize (durable — Temporal records the result).
        summary = await workflow.execute_activity(
            run_adk_summarize, doc_text,
            start_to_close_timeout=timedelta(minutes=5),
        )
        # Step 2: WAIT for human signal — durable for as long as it takes.
        decision = await workflow.wait_condition(lambda: self._decision is not None)
        # Step 3: 30-day follow-up timer.
        await workflow.sleep(timedelta(days=30))
        # Step 4: ADK draft follow-up.
        return await workflow.execute_activity(
            run_adk_draft_followup, summary, decision,
            start_to_close_timeout=timedelta(minutes=5),
        )

    @workflow.signal
    def submit_decision(self, decision: str) -> None:
        self._decision = decision
```

Two activities (ADK calls), one human signal (Temporal-managed), one 30-day timer. The workflow can survive every process restart, library upgrade, and region failover. ADK never sees the 30-day pause — it only sees two short-lived calls.

## Dapr Workflows — same idea, different syntax

Dapr offers a similar workflow primitive (`@workflow.workflow` + `ctx.call_activity` + `ctx.wait_for_external_event`) with a Kubernetes-native deploy story. The pattern of "durable engine outside, ADK inside" is identical.

## When NOT to reach for this

- One human gate, decided within the hour. ADK alone.
- Workflow re-runs every night with the same shape (cron). Cloud Scheduler + ADK alone — see page 07 (ambient agents).
- No external pauses; it's just slow inference. Make the inference async, don't reach for Temporal.

The cost of durable execution is real: another service to run, another mental model for the team. Don't pay it unless the workflow shape demands it.

> ❓ **Ask the student:** "Could you reproduce Temporal's versioning in ADK by branching your codebase per pause-cohort?" (In theory yes, in practice no — you'd need a different deployment per active in-flight schema. Durable engines do this with one binary by recording the workflow's logical version per execution.)

> 🛠 **Have the student:** if their team currently uses Temporal or Airflow, sketch one current workflow and identify which **steps** could be replaced with ADK activities. The seam is almost always around a step where the activity is "summarize X" or "decide Y" — both fit ADK's strengths.

## 🚀 In Production

> **🚀 In Production**
>
> Reach for durable execution as soon as the workflow needs **(a)** multi-day pauses, **(b)** compensation/saga semantics, or **(c)** in-flight versioning. Trying to push ADK's resume into that envelope ends with a 4am alert that says "all in-flight workflows are wedged after the deploy" — you've changed the tool function shape and 200 invocations are now un-resumable. Migrate before that, not after.

---

[← Prev: 09_ChatPlatformApprovals](09_ChatPlatformApprovals.md)  [↑ Map](../../MAP.md)  [Next: 11_DissectingSample →](11_DissectingSample.md)
