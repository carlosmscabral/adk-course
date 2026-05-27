# AGENTS.md — Module 07 Callbacks (teaching notes for the AI tutor)

## What the student should walk away knowing
- The 6 sync hook points (`before/after_agent|model|tool`) and the 2 error hooks.
- The return-value contract: `None` = passthrough, non-None = override / short-circuit / recover.
- Three idioms — filter, guard, decorate — and the canonical hook for each.
- Why production guardrails belong in callbacks, not in prompts.
- The plugin vs callback distinction (one-agent vs runner-wide).

## Three pages added in the expansion (05, 06, 07)
- **Page 05 — CallbackContext anatomy**: full surface of `CallbackContext` and `ToolContext`, what's read-only, what's mutable, common gotchas (container mutation, `temp:` scope across sub-agents, async artifact calls, `invocation_id` as the tracing key).
- **Page 06 — Recipe cookbook**: 7 production-grade snippets (response cache, per-user rate limit, PII redaction, source citations, latency budget, feature gate, audit log) plus the composition pattern for stacking.
- **Page 07 — Callbacks vs Plugins**: decision rubric and the "rule of three" promotion path from per-agent callback to runner-wide plugin. Both stack — callbacks stack per-agent (every `*_callback` field on `LlmAgent` accepts `Union[Callable, list[Callable]]` per `llm_agent.py:75-87`), plugins stack runner-wide (LIFO on the "after" side).

## Pacing
- Easy if: student already wrote a Python decorator. The signature pattern feels familiar.
- Hard if: student is fuzzy on `async def` / `await` — drill [[PY_async]] before 02 or 05.
- Hard if: student has not internalized `CallbackContext.state` (and the prefixes from 04). Send them back to `04_SessionsState/02_StateScopes` for 10 minutes.

## Watch for these mistakes
- Returning the *original* `llm_response` from `after_model_callback` thinking it's a passthrough — that's also a passthrough (works), but confuse vs `None` if you're showing both forms. Pick one and stay consistent in their code.
- Using `tool is some_function` for dispatch in `before_tool_callback`. The arg is a `BaseTool` wrapper, not the function. Use `tool.name`.
- Adding network I/O in a sync callback. Force them to `async def` it.
- Writing an `on_*_error_callback` that itself raises. Always require a try-around-the-recovery path.

## When to suggest a detour
- "Why is this async?" → [[PY_async]].
- "How do I log this?" → [[PY_logging]].
- "What about doing this for ALL my agents at once?" → preview [[13_Plugins/00_Overview]].
- "How do I test these without running the whole agent?" → [[PY_testing]].

## Mini-drill grading
- Pass = both prompts produce the expected output (block reason + Sources block).
- Pass requires the shell function literally never being entered for the dangerous prompt. Make them print a marker inside `run_shell` and confirm it does NOT appear in the run output for prompt A.
- Edge case to probe: what if the LLM tries to obfuscate (`rm -r -f`)? Their regex must catch it OR they must articulate the limitation. Don't fail them — make them name the gap.

## Common follow-up questions
- "Can I have two `after_model_callback`s?" — Yes. Pass a list: `after_model_callback=[redact_pii, inject_citations]`. ADK runs them in declared order; first to return non-`None` short-circuits. (You can still compose by hand when one step's behavior depends on another's output.)
- "Does a callback fire for sub-agents?" — Yes, per-agent — each child's callbacks fire when that child runs.
- "What's `CallbackContext` vs `ToolContext`?" — They are aliases of the SAME class (`google.adk.agents.context.Context`). `tools/tool_context.py:29` and `agents/callback_context.py:22` both assign `= Context`. The two names exist for self-documenting parameter types; the surface is identical (same `state`, same `function_call_id`, same `actions`).
