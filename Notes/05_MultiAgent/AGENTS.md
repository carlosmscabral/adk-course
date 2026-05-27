# AGENTS.md — Module 05 Multi-Agent (teaching notes for the AI tutor)

## What the student should walk away knowing

- Three composition primitives exist and they are *not* interchangeable: `sub_agents=`, `AgentTool(agent=...)`, `transfer_to_agent`.
- `SequentialAgent` is a deterministic *orchestrator*, not an `LlmAgent`. Use it when order is fixed.
- The `description=` field on a sub-agent is *the* routing prompt — write it like a docstring.
- State (`Session.state`) is the de-facto bus: `output_key="x"` upstream → `{x}` in downstream instructions.
- Sub-agents inherit only state. Not instructions, not tools, not models.

## Pacing

- Easy if: student wrote a working `LlmAgent` in module 02 and felt comfortable with `output_key` in module 04. Cruise.
- Hard if: student fuzzy on what an `Event` is or on `Session` vs `State`. Bounce back to `04_SessionsState/01` and `02`.
- The dissection page (07) is long — give it real time, ~60-90 min. Reading 5 real files is the point.

## Watch for these mistakes

- Vague `description=` → student blames "the LLM is bad", actually they wrote "handles stuff."
- Confusing `sub_agents` and `tools=[AgentTool(...)]` semantically — they think they're the same.
- Forgetting `{key}` substitution in downstream instructions.
- Naming two sub-agents the same.
- Trying to put `sub_agents=` on a `SequentialAgent` and a router prompt — `SequentialAgent` has no LLM, so no router prompt is needed.

## When to suggest a detour

- Student asks "what's `after_model_callback` doing?" → suggest detour to `07_Callbacks` overview (or, if module 07 not yet authored, give a one-liner: "a hook that runs after the LLM responds; we'll cover it next module").
- Student asks "why no `output_key` on the auditor's critic?" → explain the implicit conversational handoff (page 07), contrast with explicit pattern.
- Student wants to do branching / loops → tell them that's module 06 (graph workflows). Don't try to hack it with `sub_agents`.

## Mini-drill grading (page 11)

- Pass = script runs end-to-end and prints a French sentence that mentions Apollo/Moon. Bonus if `session.state` shows both `summary` and `translation` keys at the end.
- If they used a single `LlmAgent` with `sub_agents=` instead of `SequentialAgent`, that's a yellow card — works most of the time, but the order isn't guaranteed. Have them refactor.
- Common fix needed: substituting `{summary}` correctly in the translator's instruction.

## Dissection (page 07) — comprehension check answers

1. Without `_render_reference` the user loses the URL citations — answers become unverifiable.
2. Because order is fixed (critic must run before reviser). A `SequentialAgent` enforces that with zero ambiguity; an `LlmAgent` with `sub_agents=` would let the LLM decide and could skip the critic.
3. Because the reviser doesn't need to fact-check; it just edits. Tools are independent per agent.

## Cross-references back

- Reminds 03 (`AgentTool` preview is here in full).
- Reminds 04 (`output_key` and brace substitution).
- Sets up 06 (graph workflows — the natural next step when sequential/parallel templates aren't enough).
- Sets up 07 (callbacks — the auditor uses two).
- Will be re-visited in 14 (evals) and 16 (guardrails).
