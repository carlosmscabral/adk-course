---
module: 4B_HumanInTheLoop
page: 00_Overview
title: Human-in-the-Loop & Resume/Cancel — pause an agent for a human, then resume
estimated_minutes: 12
prereqs: [04A_ArtifactsHeavyData/11, 06_GraphWorkflows/04]
concepts: [HITL, request_confirmation, RequestInput, resume, cancel, ambient-agents]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 04A_ArtifactsHeavyData/11_MiniDrill](../04A_ArtifactsHeavyData/13_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyHITL →](01_WhyHITL.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 00 Overview

# 🛠 Module 4B — Human-in-the-Loop & Resume/Cancel

You've built agents that run end-to-end. Now we teach the agent to **stop, wait for a human, and resume** — without losing its working memory. This is the canonical home for HITL in the course; other modules link here.

## 🎯 Goals

By the end of this module you can:
- Explain the three canonical cases for HITL (irreversible, ambiguous, gated).
- Pause a tool call with `ctx.request_confirmation(hint=..., payload=...)`.
- Surface the pending approval to a client by reading `event.actions.requested_tool_confirmations`.
- Resume the invocation by calling `runner.run_async(invocation_id=..., new_message=<function_response>)` with a `ToolConfirmation` payload.
- Cancel a pending invocation cleanly.
- Pick `LongRunningFunctionTool` vs. `request_confirmation` vs. graph `RequestInput` — three pause primitives, three different trade-offs.
- Recognize when to step outside ADK to **durable execution** (Temporal, Dapr) for multi-day pauses.

## 📋 Prereqs

- Module **04 Sessions & State** complete — pause/resume relies on a durable session.
- Module **06 Graph Workflows** at least through page 04 — `RequestInput` is the workflow flavor of HITL.
- App container concept from **Module 1A** — `resumability_config=ResumabilityConfig(is_resumable=True)` is wired there.

## ⏱ Estimated time

- **Total**: ~4 hours over 2 sessions.
- Per-page estimates live in each page's frontmatter.

## 🧪 Sample anchor

This module dissects **`ambient-expense-agent`** at `/home/carloscabral/study/adk-samples/python/agents/ambient-expense-agent/` in [11_DissectingSample](11_DissectingSample.md). It's the cleanest published example of an ambient (Pub/Sub-triggered) workflow that pauses on `RequestInput` for human approval, then resumes from a frontend.

> 🤖 **Tutor:** before the dissection page, confirm the student can `ls` the sample directory and that `expense_agent/agent.py` opens. If not, the sample may be missing — fetch it before the read-through.

## 🛣 Plan

1. **01 Why HITL** — irreversible / ambiguous / gated, the three cases.
2. **02 Request Confirmation** — `ctx.request_confirmation()` inside a tool.
3. **03 Requested Tool Confirmations** — the event the runtime emits when a tool pauses.
4. **04 Runner Resume & Cancel** — the resume API, lifecycle semantics, idempotency.
5. **05 LongRunningFunctionTool** — pause for external completion (the second flavor).
6. **06 Request Input in Graphs** — `RequestInput` node — the third flavor (links to 06).
7. **07 Ambient Agents** — event-triggered runs (Pub/Sub, GCS, Scheduler) and where HITL composes.
8. **08 Frontend-Driven Approvals** — client reads the pending event, renders UI, calls back.
9. **09 Chat-Platform Approvals** — Slack & Google Chat as the approval surface.
10. **10 Durable Execution Integrations** — Temporal / Dapr for when ADK's built-in resume is not enough.
11. **11 Dissecting Sample — `ambient-expense-agent`**.
12. **12 In Production** — TTL on pending approvals, who can approve, audit log.
13. **13 Knowledge Check** — 7 questions.
14. **14 Mini-Drill** — build a `delete_file` tool that always requests confirmation, then drive approve/reject from a CLI.

After this module: → [23 Frontend Integration](../23_FrontendIntegration/) (UI patterns) and → [24 Channel Integrations](../24_ChannelIntegrations/) (Slack, Google Chat as approval surfaces).

---

[← Prev: 04A_ArtifactsHeavyData/11_MiniDrill](../04A_ArtifactsHeavyData/13_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 01_WhyHITL →](01_WhyHITL.md)
