# AGENTS.md — Module 13 Plugins (teaching notes for the AI tutor)

## What the student should walk away knowing

- A Plugin is a runner-scoped, composable bundle of cross-cutting logic.
- The five built-in plugins and when to reach for each.
- How to write a custom plugin: subclass BasePlugin, override hooks, keep state on `self`, async signatures, return None for observe-only.
- The four prod gotchas: ordering matters, hot-path latency, silent error swallowing, telemetry must be async/batched.
- The plugin-vs-callback decision rule (per-agent → callback, cross-cutting → plugin).

## Pacing

- **Easy if:** student is comfortable with callbacks (07). Just a "same hooks, different scope" reframe.
- **Hard if:** student hasn't done 07. The hook vocabulary won't be familiar. Detour to 07 first.

## Watch for these mistakes

- Confusing "plugin" with "tool" or "callback." The distinction is scope.
- Writing a synchronous hook (`def` not `async def`). It silently never fires.
- Mutating shared state across requests without thinking about it (`self._counts` in a multi-tenant deployment).
- Reaching for a plugin when one callback on one agent is enough.
- Silently swallowing errors inside a hook.

## When to suggest a detour

- Student wonders about Python logging config → [[PY_logging]].
- Student wonders about callbacks again → 07_Callbacks.
- Student asks about telemetry beyond plugins → 15_Observability.
- Student asks about OpenTelemetry / Cloud Trace specifically → 15_Observability.

## Mini-drill grading

- **Pass:** counter prints at session end and matches actual tool-call counts.
- **Stretch pass:** state-backed counter shows up in `session.state["app:tool_counts"]`.
- **Probe:** ask "what happens if two requests hit this runner concurrently?" — pulls out the shared-state hazard.

## Sample anchor reminders

- `adk-samples/python/agents/safety-plugins/safety_plugins/plugins/agent_as_a_judge.py` — best canonical example of a custom plugin that uses an inner LlmAgent as a judge.
- `adk-samples/python/agents/agent-observability-bq/agent_observability_bq/agent.py` — canonical BigQueryAgentAnalyticsPlugin wiring.
