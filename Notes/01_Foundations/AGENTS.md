# AGENTS.md — Module 01 Foundations (teaching notes for the AI tutor)

## What the student should walk away knowing

- The **agent loop**: LLM picks tool-or-reply, on tool calls feed the result back and re-prompt, terminate on a text reply.
- Three runtime primitives — **Runner** (orchestrator), **Session** (history + state), **Event** (one row in the log).
- Tools are just **Python functions** with type hints + a docstring. Docstring → description, hints → schema. Deep dive in Module 03.
- State lives on the Session, mutated via **state_delta** attached to events. Four prefixes: (none), `user:`, `app:`, `temp:`. Deep dive in Module 04.
- The student can re-read `fun-facts/agent.py` and locate every concept by name, knowing what the `adk run` CLI provides.

## Pacing

- **Easy if** the student finished Module 00 cleanly and is comfortable thinking in dataflow diagrams. Should breeze through in one sitting.
- **Hard if** the student wants to *write* code immediately. This module is deliberately read-and-draw — the mini-drill is a paper exercise. Hold the line; Module 02 is all hands-on.
- **Hard if** the student is fuzzy on what "stateless" means for the agent vs "stateful" for the session. Re-walk page 02 with the recipe/cook/plate metaphor.

## Watch for these mistakes

- Confusing **agent** (config) with **runner** (machinery).
- Thinking the LLM "remembers" prior turns autonomously — it doesn't; the Runner re-stuffs the history on each call.
- Conflating tool-call event and tool-result event into one box.
- Reading the prefix table as convention. The prefixes are parsed by the framework — `user:` actually changes where the value persists.

## When to suggest a detour

- Student asks "what's an async generator?" → suggest [[PY_async]] (or note "Module 02 page 03 explains this in context — you can wait").
- Student asks "what's a JSON schema?" → 60-second explainer, no detour needed yet.
- Student asks "how do plugins fit in?" → defer to Module 13 ("we'll see they observe the event stream — that's why uniform Event schema matters").

## Mini-drill grading

- The deliverable is a **drawing**, not code. Pass = all six nodes present, arrows labeled, tool-call + tool-result rendered as two events.
- Probe: "if the user sends a follow-up turn, what happens to the events from the previous turn?" (Answer: they stay in the Session; the Runner reads them on the next `run_async`.)

## After this module

- The student is now armed with vocabulary. Module 02 immediately exercises it by hand: they'll instantiate `LlmAgent`, `InMemorySessionService`, and `Runner` themselves and call `run_async`. The sample anchor changes from `fun-facts` to `currency-agent`.
- If the student wants to peek at code first, point them at the `Solutions/02_FirstAgent/hello_agent.py` gate-keeper — but only AFTER they've drawn the diagram.
