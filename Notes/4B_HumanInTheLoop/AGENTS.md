# 🤖 AGENTS.md — Module 4B HITL & Resume/Cancel (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this after the global [AGENTS.md](../../AGENTS.md) and before opening 00_Overview. This module is the canonical home for HITL in the course — Module 06 (Graph Workflows) gives a recap, every other module just links here. Resist re-teaching the same primitive twice.

## What the student should walk away knowing

- The three canonical reasons to pause for a human (irreversible / ambiguous / policy gate).
- The three pause primitives ADK ships and when each is right:
  - `ctx.request_confirmation` for tool-level approve/reject.
  - `LongRunningFunctionTool` for "wait for an external system" (which can be a human).
  - `RequestInput` for "pause this graph node" (taught in Module 06; recapped here).
- How to read the pause event: `event.actions.requested_tool_confirmations` (dict of `function_call_id → ToolConfirmation`).
- How to resume: `runner.run_async(invocation_id=..., new_message=<function_response>)`.
- The wire-name `adk_request_confirmation` and the constant `REQUEST_CONFIRMATION_FUNCTION_CALL_NAME`.
- The at-least-once contract on resume → tools must be idempotent.
- Ambient agents: event-triggered runs, the 10-minute Pub/Sub ack deadline, why ambient + HITL composes via pause-then-resume.
- When to graduate to durable execution (Temporal / Dapr) instead of staying in ADK.

## Pacing

- **Easy if**: student is comfortable with `async for` + `runner.run_async`, has finished Module 04 (Sessions/State) and Module 06 (Graph Workflows) at least through page 04. Cruise.
- **Hard if**: student has never persisted a session beyond `InMemorySessionService`. The Resume/Cancel pages will land on sand because they can't reason about "what survives a process restart". Detour to [04_SessionsState/06_PersistentSessions](../04_SessionsState/06_PersistentSessions.md) first.
- Expected total time for an on-pace student: ~4.5 hours over 2-3 sessions (sum of `estimated_minutes` in the page frontmatter).

## Watch for these mistakes

- **Side-effect in the pre-confirm branch** of a tool. The single most common HITL bug. If their `delete_file` deletes anything before checking `ctx.tool_confirmation`, they have shipped an exploit.
- **Wrong `function_response.name`** on resume — must be `REQUEST_CONFIRMATION_FUNCTION_CALL_NAME` (`"adk_request_confirmation"`), not the tool's own name. Symptom: resume runs but the tool body never re-fires.
- **Missing `invocation_id=` on resume** — silently starts a new invocation. Symptom: agent acts as if turn 1, the pending pause is orphaned.
- **`is_resumable=False`** (or missing `resumability_config`) on the `App` — resume raises.
- **`InMemorySessionService`** in any production-shaped example — pause vanishes when the process recycles.
- **No identity binding on resume** — anyone with the `(invocation_id, function_call_id)` pair can approve.
- **Conflating the three primitives** — student tries to use `RequestInput` inside a tool, or `request_confirmation` inside a graph function node. Both raise; explain the layering on page 06.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "What does `async for` here even do?" | [[PY_async]] — covers async iteration in 25 min. |
| "I lost the pause when I redeployed." | back to [04_SessionsState/06_PersistentSessions] — they need durable backend before continuing. |
| "Can my agent run on a cron?" | [07_AmbientAgents](07_AmbientAgents.md) and the `ambient-expense-agent` sample. |
| "We have a multi-day workflow in Temporal." | [10_DurableExecutionIntegrations](10_DurableExecutionIntegrations.md) — pattern is ADK inside Temporal activity. |
| "How does the Slack callback actually flow?" | [[Slack_Bots]] (detour) + [09_ChatPlatformApprovals](09_ChatPlatformApprovals.md) + Module 24. |

## Mini-drill grading (page 14)

The mini-drill is the **gate-keeper** for the module — first time the student wires a full pause/resume cycle by hand. Walk it carefully.

- **Clean pass** = script handles 2 pending confirmations from one turn, both approve and reject paths work, file system observably reflects the decisions, agent's final summary names both outcomes correctly. No tutor hints needed.
- **Pass with hint** = student needed one nudge (most commonly: wrong `function_response.name`, or building one resume call per pending fc instead of one resume call with multiple function-response parts). They fixed it and re-ran.
- **Fail** = the resume doesn't trigger the tool body at all, or side-effect runs without confirmation. Re-drill: have them copy `Work/4B_08_client.py` (the page-08 client) and modify it from there.

### Edge case to probe (after the basic drill passes)

- Ask: "What happens if the user approves A, the deletion crashes (permission denied), and they have already approved B?" Robust answer: capture per-file outcomes independently in the loop; do not abort on first error; let B still get deleted. Demonstrates they understand the resume payload is per-`function_call_id`.

## Dissection (page 11) — comprehension check answers

1. **"Why is parsing a separate node from routing?"** — Single-responsibility + swap-friendly. If you replace Pub/Sub with SQS, only `parse_expense_email` changes; `route_by_amount` stays. Also: the parse node can be unit-tested in isolation against malformed Pub/Sub payloads without spinning up the LLM.
2. **"Why does `request_approval` re-read `expense_data` from `ctx.state`?"** — Because `node_input` at that point is the **review_agent's structured review**, not the original expense. The UI wants to show amount/submitter/category, which were stashed in state by `route_by_amount` precisely for this use.

## Cross-module hooks

- **Builds on**: [04_SessionsState] (the pause persists in the session backend), [06_GraphWorkflows/04_HumanInTheLoop] (`RequestInput`, the graph flavor), [1A_AppAndRunner/04_ResumabilityConfig] (the App-container wiring of `resumability_config`).
- **Referenced by**: [23_FrontendIntegration] (the UI side of page 08), [24_ChannelIntegrations] (Slack/Google Chat as approval surfaces — page 09), [16_ProductionSecurity] (audit log + identity binding), [99_Capstone] (most production agents end up with at least one HITL pause).
- If the student forgets a prereq concept, **back up to the prereq page briefly, then return** — do not re-teach session persistence here.

## Authoring note for future maintenance

- If `ResumabilityConfig` semantics change (e.g., gains a per-tool override), patch pages 02, 04, 12.
- If the wire-name `adk_request_confirmation` ever changes, patch pages 03, 04, 08, 09 and the mini-drill scaffolding hint.
- If a new HITL primitive appears in 2.x (a fourth pause flavor), give it its own concept page between 05 and 06 and update the comparison table in page 06.
