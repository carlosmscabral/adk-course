---
module: 99_Capstone
page: 05_BuildingPlan
title: Suggested 5-day build plan
estimated_minutes: 15
prereqs: [99_Capstone/04]
concepts: [planning, build-order]
icon: 🏁
in_production: false
---

[← Prev: 99_Capstone/04A_DissectingACapstone]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/06_SelfReviewChecklist →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 05 Building Plan

# 🏁 The 5-day build order

A suggested sequence. Adjust to your reality; the order matters more than the timeline.

## Day 1 — Scaffold & decide

- Pick your track. Commit. Don't track-shop after hour 1.
- `adk create capstone-<track>` → strip to a single root agent that says "hello".
- Write the README **architecture section** first. Forces clarity before code.
- Run `adk run` — confirm "hello" works.

**End-of-day**: scaffold runs; README has architecture + run commands.

## Day 2 — Agent skeletons & tools

- Build the 3 agents as **stubs** (instruction + tools but no logic). They should each respond to a trivial prompt.
- Wire one real tool per agent.
- Wire composition (`sub_agents` OR `Workflow` graph).

**End-of-day**: `adk run` produces a multi-agent conversation, even if the answers are weak.

## Day 3 — State, memory, observability

- Swap `InMemorySessionService` → `SqliteSessionService` or `DatabaseSessionService`. Verify state survives restart.
- Wire memory service. Verify a captured fact is recalled in a new session.
- Wire OpenTelemetry. Spin up Jaeger locally if you can't get Cloud Trace working yet. **Look at one trace before moving on.**

**End-of-day**: persistent state, working memory, ≥1 trace visible.

## Day 4 — Evals & guardrails & A2A

- Write 5 eval cases. Run `adk eval` — accept whatever pass rate you get.
- Add the 2 callbacks (≥1 a guardrail). Re-run evals.
- Add the plugin.
- Run `to_a2a(root)` → start the server → call it with `RemoteA2aAgent` from a tiny script.

**End-of-day**: evals run, A2A works end-to-end, guardrails in place.

## Day 5 — Polish & self-review

- Fix the worst eval failures. Aim for ≥80% pass.
- Re-read your README. Have a friend read it. Edit for clarity.
- Walk the `06_SelfReviewChecklist.md`. Fix anything red.
- Deploy a smoke version (Cloud Run / Agent Engine / your local server).
- Write the **module 20 self-review paragraph**.

**End-of-day**: deployable artifact, complete checklist, honest self-review.

## Anti-patterns to avoid

- **Polishing on Day 2.** You'll spend the week perfecting the researcher prompt and never get to A2A.
- **Skipping evals.** They are the contract. Without them, "done" is opinion.
- **Wiring everything in Day 5.** A2A and observability will reveal architectural mistakes — give yourself time to fix them.
- **Over-scoping.** If you finish ahead of schedule, ADD an eval case. Don't add a feature.

## When you're stuck

- Stuck on integration? Re-read the relevant module's `In Production` page.
- Stuck on a stack trace inside ADK? Open `19_Internals/` for the call map.
- Stuck on which framework feature to use? Open `20_FrameworkComparison/` and re-check the moat.

> 🛠 **Have the student run:** an end-of-day demo to themselves every day. If they can't `adk run` and show something working, they shipped no progress.

> ❓ **Ask the student:** "Which day are you most likely to overspend? Set a hard timer for that day."

[← Prev: 99_Capstone/04A_DissectingACapstone]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/06_SelfReviewChecklist →]
