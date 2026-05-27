# AGENTS.md — Module 12 Code Execution (teaching notes for the AI tutor)

## What the student should walk away knowing

- Code execution is a parallel mechanism to tools, attached as `code_executor` on the agent.
- The six executors and the matrix of (isolation × infra × cost) trade-offs.
- `UnsafeLocalCodeExecutor` is a footgun. The student should be able to articulate why in one sentence.
- For Vertex deploys: `VertexAiCodeExecutor` or `AgentEngineSandboxCodeExecutor`.
- For self-hosted: `ContainerCodeExecutor` or `GkeCodeExecutor`.
- Sandbox ≠ safety: you still need resource limits, egress policy, audit logging, package policy.

## Pacing

- **Easy if:** student has Docker experience and a working notion of sandboxing. Cruise.
- **Hard if:** student has never thought about sandbox boundaries. Spend extra time on page 02 and the prod checklist. The package-install question (page 08, point 4) is the best probe.

## Watch for these mistakes

- Reaching for `UnsafeLocal` "to keep it simple." The whole module pushes back on this.
- Confusing `BuiltInCodeExecutor` (model-side, no executable_code on the wire) with `VertexAiCodeExecutor` (runtime-side, real round trip). The trace looks different.
- Wiring code execution as a tool. It's an agent-level field, `code_executor=...`.
- Treating "I picked the executor" as the end of security work. Resource limits, egress, audit logging are separate concerns.

## When to suggest a detour

- Student asks about prompt injection in detail → 16_ProductionSecurity (especially `02_CodeExecSafety` if it exists).
- Student asks about observability of executed code → 15_Observability + 13_Plugins (BigQueryAgentAnalyticsPlugin).
- Student asks about containers in general → not a detour topic in this course; assume they bring Docker context or skip the Container/GKE pages briefly.

## Mini-drill grading

- **Step 1 pass:** all three algebra answers correct AND event log shows executable_code parts.
- **Step 2 pass:** one-line executor swap, same correct answers.
- **Bonus:** student notes the *visible difference* — e.g. "with BuiltIn, the executable_code part disappears from my trace because Gemini ran it model-side."

## Sample anchor reminders

- `adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py` — `VertexAiCodeExecutor(optimize_data_file=True, stateful=True)`. Canonical shape.
- `adk-samples/python/agents/machine-learning-engineering/` is the heavier example; refer if the student wants to see a full ML pipeline.
