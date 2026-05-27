# AGENTS.md — Module 12 Code Execution (teaching notes for the AI tutor)

## What the student should walk away knowing

- Code execution is a parallel mechanism to tools, attached as `code_executor` on the agent — never as a tool.
- The six executors and the matrix of (isolation × infra × cost) trade-offs.
- The four sandbox-bypass classes from page 02A (filesystem, env, network, priv-esc), with verdicts per executor.
- `UnsafeLocalCodeExecutor` is a footgun. The student should be able to articulate why in one sentence and name the multiprocessing-spawn-is-not-a-sandbox fact in two.
- For Vertex deploys: `VertexAiCodeExecutor` or `AgentEngineSandboxCodeExecutor`.
- For self-hosted: `ContainerCodeExecutor` or `GkeCodeExecutor` (and that GKE-job ships hardened, Container ships open).
- Sandbox ≠ safety: resource limits, egress policy, audit logging, package policy, retry-math awareness — all still required.
- The prompt and the executor are coupled (page 07's File 2 — the `stateful=True` ↔ "variables stay in the environment" contract).

## Pacing

- **Easy if:** student has Docker experience and a working notion of sandboxing. Cruise pages 01-04, slow on 02A and the prod checklist.
- **Hard if:** student has never thought about sandbox boundaries. Spend extra time on page 02 (the visceral "this runs in YOUR process" demo) and 02A (the four threat classes). The package-install question (page 08, item 5) and the retry-math question (item 4) are the best probes for "did this land?"
- **GKE/Container experience matters most on 05/05A.** If the student has shipped k8s before, the hardened-pod-spec table on 05A is fast; if not, walk it cell by cell.
- **Pacing trap on page 07:** the dissection is 200+ lines and feels long. It is meant to be read across two sittings — File 1+2 first (the executor + prompt coupling), then File 3+4 + the wire trace + the migration table. Don't try to consume in one go.

## Watch for these mistakes

- Reaching for `UnsafeLocal` "to keep it simple." The whole module pushes back on this.
- Confusing `BuiltInCodeExecutor` (request-side mutation, no `executable_code` part on YOUR wire) with `VertexAiCodeExecutor` (response-side handler, real round trip you can observe). The trace looks different — that's the teaching, not a bug.
- Wiring code execution as a tool. It's an agent-level field: `code_executor=...`.
- Constructor-time vs first-call-time errors:
  - `AgentEngineSandboxCodeExecutor()` with no env vars: blows up at first call, not at construction (page 06 Gotcha #1).
  - `VertexAiCodeExecutor(stateful=True)` instantiated wrong: there's a frozen-Field ValueError path via Pydantic at `base_code_executor.py:69-74` if the student tries to mutate a field after construction. Surface it if it happens; otherwise don't preview.
  - `GkeCodeExecutor(service_account=...)`: not a kwarg — raises Pydantic ValidationError. Identity is bound via Workload Identity at the cluster level, not as a constructor arg (page 05A).
- Treating "I picked the executor" as the end of security work. Resource limits, egress, audit logging, retry pinning, package policy are separate concerns.
- Pre-imports drift: editing the prompt to add a library the executor doesn't have, or vice versa. Page 07's File-2 lesson.
- Skipping page 02A as "just a reference page." It IS a reference page, but every later page forward-links to it for bypass verdicts. The student must hold the four classes in their head before pages 03-06 make sense.

## When to suggest a detour

- Student asks about prompt injection in detail → [[16_ProductionSecurity/02_PromptInjectionDefense]] + [[16_ProductionSecurity/05_GuardrailsCookbook]] Recipe 6.
- Student asks about observability of executed code → [[15_Observability]] + [[13_Plugins]] (BigQueryAgentAnalyticsPlugin reads `_CODE_EXECUTION_RESULTS_KEY`).
- Student asks about containers in general → not a detour topic in this course; assume they bring Docker context or skim the Container/GKE pages briefly.
- Student asks about k8s NetworkPolicy syntax → out of scope; point at the official k8s docs and the GKE-job network-egress DEPENDS verdict in 02A as the why.

## Mini-drill grading (page 10)

- **Step 1 pass:** all three algebra answers correct AND event log shows `executable_code` parts.
- **Step 2 pass:** student's inspection code prints both `executable_code` and `code_execution_result` parts in the right order. They name `code_execution_result.output` as the field carrying stdout into the model's next turn.
- **Step 3 pass:** one-line executor swap, same correct answers. Student names the *visible difference* — e.g. "with BuiltIn, the `executable_code` part disappears from my trace because Gemini ran it model-side."
- **Step 4 pass:** student captures the host-vs-sandbox difference for `os.uname()`/`sys.path`/`getpid()`. If they try to escalate to `$HOME` or env vars, redirect (per the page-02A safety note). The point is to feel the boundary, not to teach exploitation.
- **Step 5 bonus (Vertex only):** turn 2 references `x` without recomputation — confirms `stateful=True` kernel reuse.
- **Stretch (SHA-256):** opens the package-availability discussion across executors.

## Sample anchor reminders

- `adk-samples/python/agents/data-science/data_science/sub_agents/analytics/agent.py` — `VertexAiCodeExecutor(optimize_data_file=True, stateful=True)`. Canonical shape. Used by page 07.
- `adk-samples/python/agents/data-science/data_science/sub_agents/analytics/prompts.py:40-55` — the statefulness + imports contract. Make sure the student reads it line-by-line against `vertex_ai_code_executor.py:36-85` (`_IMPORTED_LIBRARIES`).
- `adk-samples/python/agents/data-science/data_science/tools.py:59-126` — `call_analytics_agent` as `AgentTool`; the state-passing pattern.
- `adk-samples/python/agents/machine-learning-engineering/` is the heavier example; refer if the student wants to see a full ML pipeline (but it's a side trip — not required for module completion).
