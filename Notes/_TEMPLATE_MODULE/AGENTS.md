# 🤖 AGENTS.md — Module NN <Topic> (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening the first concept page in this module. It captures module-specific pacing notes that do not fit in page frontmatter.

## What the student should walk away knowing

- (Bullet — one concrete capability.)
- (Bullet — one concrete capability.)
- (Bullet — one concrete capability.)

## Pacing

- **Easy if**: the student (already knows X / has done Y in another framework). → cruise; compress the concept pages, focus time on the dissection.
- **Hard if**: the student (is fuzzy on Z / has not done W). → drill the detour [[<X>]] before page 02; otherwise the rest of the module will land on sand.
- Expected total time for an on-pace student: ~X hours (sum of `estimated_minutes` in the page frontmatters).

## Watch for these mistakes

- (Mistake 1 — what the wrong code looks like + the symptom the student will see.)
- (Mistake 2 — …)
- (Mistake 3 — …)

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "<what they say>" | [[<detour_name>]] — covers <reason> in <minutes>. |
| "<what they say>" | [[<detour_name>]] |

If the same detour is suggested and declined twice (check `student_profile.md`), stop offering it.

## Mini-drill grading

- **Clean pass** = (state the exact rubric outcome — e.g., "tool works on ≥3 of 4 operations on first run, no hint needed").
- **Pass with hint** = (e.g., "missed the type hint, tutor pointed it out, student fixed and re-ran successfully").
- **Fail** = (e.g., "tool not callable from the agent, or returns wrong type"). Re-drill: have them rebuild from `Work/_template_run.py`.

### Edge case to probe (after the basic drill passes)

- (One edge case the tutor should ask the student to handle. E.g., "Ask them to handle division by zero. If they raise, ask how that surfaces to the LLM — answer: an Event with the error in `content`.")

## Cross-module hooks

- This module is referenced from: <list of later modules that build on it>.
- This module references: <list of earlier modules whose concepts are reused>.
- If the student forgets a prerequisite concept, the tutor should NOT re-teach it inline — back up to the prereq page briefly, then return.
