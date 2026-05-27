# 🤖 AGENTS.md — Module 3A Project Structure (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening the first concept page in this module.

## Core stance — read this twice

**Pragmatic, not dogmatic.** This module's entire pedagogical value collapses if the tutor turns into a "you must structure your project like X" voice. The user-requested framing was:

> "let's not overcomplicate here, but it is something of a best practice as our agent project grows, also understand how we can align this structure for deployment vs local testing tools such as ADK web and what they expect"

Translation: **show the layouts that exist, name the pressure that justifies each escalation, then shut up and let the student pick.** Never prescribe the growing layout for a 30-line agent. Never tell the student their fun-facts-clone is "missing" `eval/` and `tests/`.

If the student is building something genuinely small, the answer is **page 02 (Minimal) + page 05 (CLI expectations)**, and we are done. Skip 03–04 entirely. Come back when they have a sub-agent or third tool.

## What the student should walk away knowing

- Three layouts (minimal, small, growing) and the **specific pressure** that pushes you from one to the next.
- The `root_agent` / `app` discovery rule, the `__init__.py` rule, the parent-dir rule.
- What Cloud Run needs (FastAPI `main.py` + Dockerfile) vs what Agent Engine needs (`deployment/deploy.py`).
- Where `eval/` and `tests/` live and why they are separate.
- How to read a real sample's tree and predict where each concept lives.

## Pacing

- **Easy if**: student has Python packaging fluency (knows what `__init__.py` does and how relative imports work). → cruise; spend extra time on the dissection page (09) walking the two samples in parallel.
- **Hard if**: student hand-waves through `__init__.py` or asks "why do I need this?" → drill [[PY_packaging]] before page 02. The rest of this module assumes the student can read `from .tools import X` and predict what it does.
- Expected total time for an on-pace student: ~2 hours (sum of `estimated_minutes` in the page frontmatters).

## Watch for these mistakes

1. **Skipping ahead to the growing layout** for a toy. Symptom: student creates `Work/calc_agent/sub_agents/` for their 30-line calculator. **Push back**: "What's the pressure? Where's the second LlmAgent?" Refer to [01_WhyStructureMatters](01_WhyStructureMatters.md).

2. **Empty `__init__.py`**. Symptom: `adk web` shows the agent in the dropdown but it never responds. The error in stderr is unhelpful. **Fix**: confirm `from . import agent` is in there. This is THE ADK CLI gotcha; the mini-drill explicitly probes for it.

3. **Running `adk web` from the wrong directory.** Symptom: empty dropdown. **Fix**: `cd ..` to the parent of the agent package.

4. **`python my_agent/agent.py` instead of `adk run my_agent`.** Symptom: `ImportError: attempted relative import with no known parent package`. **Fix**: use the ADK CLI, not bare Python — the script is part of a package, not a standalone module.

5. **`extra_packages=["./"]` in Agent Engine deploy.** Symptom: deploy succeeds but takes 10× longer and ships the whole repo (including `.git`). **Fix**: point at the **package directory** specifically, `extra_packages=["./my_agent"]`.

6. **Merging `eval/` into `tests/data/`.** Symptom: CI runs unit tests but never runs evals; behavior regressions ship undetected. **Fix**: `eval/` is a separate top-level directory; `pyproject.toml` should have `testpaths = ["tests", "eval"]`.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "I'm fuzzy on `__init__.py` / relative imports" | [[PY_packaging]] — covers `__init__.py`, package vs module, relative imports in 20 min. |
| "Wait, what's `pyproject.toml` for?" | [[PY_packaging]] — same detour. |
| "How does FastAPI fit in with ADK?" | [[FastAPI_for_ADK]] — wraps the agent for Cloud Run. |
| "What's Cloud Run specifically?" | [[Cloud_Run]] — the deployment surface; revisited in [22 Deployment Models](../22_DeploymentModels/). |
| "Agent Engine vs Cloud Run?" | [[AgentEngine]] — the alternative; full coverage in [22_DeploymentModels](../22_DeploymentModels/). |

If the same detour is suggested and declined twice (check `student_profile.md`), stop offering it.

## Mini-drill grading

- **Clean pass** = refactor done in <15 min, `adk web` shows `calc_agent` on first try, `7 * 5` still returns 35. No prompting needed beyond the spec.
- **Pass with hint** = needed to be told about the empty `__init__.py`, OR was running `adk web` from the wrong directory, OR forgot the dot in `from .prompts import ...`. Fixed after one nudge, drill passes.
- **Fail** = drill still doesn't work after 30 min and 2 hints. Re-walk page 03 with them, then have them redo from scratch. Don't reveal a solution — there isn't one.

### Edge cases to probe (after the basic drill passes)

1. **Two-agent picklist**: have them add a `Work/research_agent/` next to `calc_agent/` (minimal layout, different tools/prompt). Run `adk web` from `Work/`. Both should appear in the dropdown. Confirms the parent-dir rule from page 05.

2. **Wrong variable name**: have them rename `root_agent` to `my_agent` in `agent.py`. Re-run `adk web`. The agent should no longer respond. Probe: "What just broke?" (Answer: discovery rule #3.) Then have them rename back.

3. **Move `INSTRUCTION` back inline**: have them inline the prompt into `agent.py`. Note the file is now harder to scan. Discussion: when does this become genuinely worth it to split? (Answer: whenever the prompt fits on one screen, it doesn't — page 03 is for when it doesn't.)

## Cross-module hooks

- **References from this module**:
  - [Module 02 FirstAgent](../02_FirstAgent/) — the prerequisite that establishes `LlmAgent`.
  - [Module 03 Tools](../03_Tools/) — establishes function-as-tool (`02_FunctionTool`).
  - [Module 05 MultiAgent](../05_MultiAgent/) — when sub-agents become real, the growing layout (page 04) becomes obviously necessary.
  - [Module 1A App & Runner](../1A_AppAndRunner/) — for the `App` wrapper introduced on page 05.
  - [Module 14 Evaluation](../14_Evaluation/) — for the actual eval discipline that consumes the `eval/` directory on page 08.
  - [Module 22 Deployment Models](../22_DeploymentModels/) — for the deep dive on Cloud Run vs Agent Engine.

- **Modules that reference this one**:
  - [Module 05 MultiAgent](../05_MultiAgent/) — when the student adds a real sub-agent, point back to page 04.
  - [Module 14 Evaluation](../14_Evaluation/) — when the student writes their first eval, point back to page 08 for layout.
  - [Module 16 Production & Security](../16_ProductionSecurity/) — when shipping, point back to page 10's checklist.
  - [Module 22 Deployment Models](../22_DeploymentModels/) — when deploying, page 06 is the layout half of the conversation.

- If the student forgets a prerequisite concept (e.g., "what's a `FunctionTool`?"), back up to the prereq page briefly, then return — do not re-teach it inline.

## Knowledge-check answer keys

- **q1**: Prompt sprawl (instruction grows too long), tool reuse (two agents want the same function), testability (tools can't be imported without side effects).
- **q2**: `root_agent` (plain agent instance) and `app` (`App` wrapper with lifecycle config). Both work; `app` is preferred once past prototype because it's the future-proof container.
- **q3**: Empty (or missing) `__init__.py`. Fix: `from . import agent`.
- **q4**: `[tool.hatch.build.targets.wheel] packages = ["my_agent"]`.
- **q5**: The agent **package directory** (e.g., `"./my_agent"`), not the project root, not a file. Beginners try `"./"` (ships the whole repo) or `"./agent.py"` (ships nothing useful).
- **q6**: `pytest` and `adk eval` both have layout-sensitive discovery; merging them muddies CI gating (you want unit tests on every push but expensive evals only pre-release).
- **q7**: When a second caller appears — a sub-agent or another tool actually needs the helper. Premature `shared/` directories are the most common over-structuring mistake.
