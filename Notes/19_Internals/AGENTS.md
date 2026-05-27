# AGENTS.md — Module 19 Internals (teaching notes for the AI tutor)

## What the student should walk away knowing
- A mental map of `adk-python/src/google/adk/` — which subdir does what.
- The call chain `Runner.run_async → build_node → LlmAgent.run_async → _llm_flow.run_async → LLM`.
- Where `state_delta` is applied (`base_session_service.py::append_event`).
- The dispatch chain for tool calls (LLM response → `_postprocess_handle_function_calls_async` → `tool.run_async` → `FunctionResponse` event).
- The two flow classes (`SingleFlow`, `AutoFlow`) and when each is selected.
- The `LLMRegistry` and lazy-import pattern.
- When to read the source (debugging, extending, contributing) and when not to (substitute for docs).

## Pacing
- Easy if: student is comfortable reading async Python and pydantic models. They can fly through 01-08 in one sitting.
- Hard if: student has never used a debugger / never traced an async generator. Slow down on pages 09-11; have them open the actual files and follow along.

## Watch for these mistakes
- Treating private (`_*`) functions as stable API.
- Reading the source instead of the version-pinned docs at https://adk.dev — source is "what 2.0.0 does," docs are "what to write."
- Trying to memorize line numbers — they will drift. The student needs to remember **landmarks** (file + method name), not addresses.
- Copy-pasting from `_session_util.py` into their own code instead of using the public State / append_event surface.

## When to suggest a detour
- Student fuzzy on `async for` / generators → suggest `[[PY_async]]` and `[[PY_generators]]`.
- Student fuzzy on pydantic-as-class → suggest `[[PY_pydantic]]`.

## Mini-drill grading
- Pass = subclassed `BaseAgent`, override yields events with the final response mutated, output contains "arrr".
- Probe: ask the student to break their solution by setting `instruction="Do not use 'arrr'."` on the inner agent. The pirate suffix should still appear (it's added AFTER the model). This proves the override is at the right layer.
- Bonus probe: ask "what if the LLM streams partials — does each partial get '— arrr.' appended?" The correct answer is **no**: only the final event should be mutated; partials should pass through unmodified to avoid garbling the stream.

## Talking points if the student asks "why so many private files?"
- Public surface = stability promise. Private = "we'll refactor when needed."
- The 2.0 GA is the first release where the surface is frozen; lots of churn is hidden behind underscore-prefixed names.
