# AGENTS.md — Module 17 Advanced Models (teaching notes for the AI tutor)

## What the student should walk away knowing

- ADK's model abstraction is `BaseLlm` resolved through `LLMRegistry` from a string or instance.
- The Gemini Flash-Lite / Flash / Pro tradeoff matrix, and the router-worker pattern.
- How to wire Claude (Vertex or direct), Gemma (AI Studio, vLLM, Ollama), OpenAI, and arbitrary providers via `LiteLlm`.
- **Planners** — when to attach `BuiltInPlanner` (Gemini 2.5+ native thinking via `ThinkingConfig`) vs `PlanReActPlanner` (model-agnostic plan→reason→act tags, used by the supply-chain sample family). Page 05 and 06.
- When an enterprise wants `ApigeeLlm` and what it costs.
- That different sub_agents in one graph can use different models — and how to verify in a trace.
- **The five model-selection patterns** (page 10A): tier-by-task, model-from-config, 429 fallback in `on_model_error_callback`, cost-aware swap in `before_model_callback`, model A/B in eval. This is the canonical "how to pick / route / govern models" page — resist re-teaching this on 02 or 10.
- That model choice is a measured decision, not a vibe.

## Pacing

- **Easy if:** student has multi-provider experience already. Skim 03-06; focus on 08 (per-agent model) and the mini-drill.
- **Hard if:** student has only ever used `model="gemini-2.5-flash"`. Spend extra time on 01 (the abstraction), 02 (the variants), and the matrix figure.

## Watch for these mistakes

- **"Pro is always better."** No — measure on your eval suite. A Pro that needs 5 turns to converge can cost more than a Flash that needs 2.
- **"LiteLlm makes me vendor-agnostic."** It makes you vendor-*optional*. The differences page 05 calls out are real.
- **Mixing the system instruction across model families and assuming parity.** Re-tune per family; re-eval.
- **Forgetting to pin model version.** A bare `gemini-2.5-flash` drifts under their feet.
- **Cold-starting Gemma per request.** The student writes a Flask handler that instantiates a fresh vLLM client every call. Coach the warmup-ping pattern.
- **Using the same model for `LlmAsAJudge` as the agent itself.** Cost and injection risk; see module 16 page 06.

## When to suggest a detour

- Student asks about MCP toolsets (gemma sample uses one) → [[08_MCP/00_Overview]].
- Student asks how to write a custom `BaseLlm` → [[19_Internals/00_Overview]].
- Student asks "what's a good eval set for picking a model?" → [[14_Evaluation/00_Overview]].

## Mini-drill grading

- **Pass** = trace has two distinct `model.name` values, events show two distinct authors.
- **Stretch** = student wired a fallback chain that triggers on an injected Claude exception.
- **Common stumble** = student picks a prompt that triggers only one sub_agent. Have them re-frame as "draft then critique" or "research then write."

## Cross-link reminders

- 02 FirstAgent — `LlmAgent(model=...)` ground truth.
- 05 MultiAgent — `sub_agents=[...]` mechanics.
- 13 Plugins — `ReflectAndRetryToolPlugin` pattern, also useful for model retries.
- 14 Evaluation — required to pick models rigorously.
- 15 Observability — to see `model.name` attributes in the trace (mini-drill verification).
- 16 ProductionSecurity — gateway pattern, fallback discipline, secrets for provider keys.
- 19 Internals — for writing a custom BaseLlm if the student wants to go deeper.
