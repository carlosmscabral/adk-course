# AGENTS.md — Module 09 Skills (teaching notes for the AI tutor)

## What the student should walk away knowing
- Skills are NEW in 2.0 and they are NOT tools — they're file-based instruction bundles.
- The L1/L2/L3 progressive-disclosure model.
- The four patterns (inline, file-based, external/GCS, meta).
- `SkillToolset` exposes `list_skills` / `load_skill` / `load_skill_resource` / `run_skill_script` for free.
- `SkillRegistry` adds semantic discovery for large catalogs.
- The frontmatter `description` is the LLM's load-or-don't decision surface — treat it like an API.

## Pacing
- Easy if: student already used `FunctionTool` (Module 03) — they'll see "tool vs skill" as a contrast.
- Easy if: student has used Jekyll / Hugo / any frontmatter-driven SSG — the syntax is familiar.
- Hard if: student keeps trying to put Python code in the SKILL.md body. They want to write commands; skills are *instructions for the LLM*, not commands.
- Hard if: student fuzzy on YAML — push a brief refresher before page 02.

## Watch for these mistakes
- Directory name mismatched to `name` field — the loader rejects.
- Description shorter than name, or "helpful skill" → useless to the LLM. Demand specificity.
- Putting side-effecting code in `SKILL.md`. Side effects belong in tools. The skill says WHAT to do; the tool DOES it.
- Forgetting `additional_tools=` when migrating from a tool-only agent. The skill replaces *instructions*, not the underlying function.
- Confusing skills with MCP servers. Skills are local instruction bundles; MCP is cross-process tool/resource exposure. They compose (travel-planner sample), but they're not interchangeable.

## When to suggest a detour
- "I want to assemble skills visually" → preview [[VisualBuilder]] (when ready).
- "How do I deploy a skill registry?" → preview [[16_ProductionSecurity/00_Overview]] for governance, [[15_Observability/00_Overview]] for audit.
- "Can a skill call another skill?" — Indirectly: by telling the LLM to `load_skill("other-skill")` in its instructions. There's no skill-to-skill direct call.

## Mini-drill grading
- Pass = the agent run output shows `load_skill("todo-manager")` getting invoked AND the underlying tool calls succeeded.
- Common failure: student wires only `skills=[todo_skill]` with no `additional_tools=`. The agent loads the skill, follows the instructions, then has no tool to call. Make them fix it.

## Common follow-up questions
- "When should a tool become a skill?" — When the *instructions for using it* are non-trivial, reused, and bundle-able with reference docs.
- "Can I version skills?" — Yes, by repo / branch / tag. The frontmatter has no built-in version field, but you can stash a version in `metadata`.
- "Is there a Python registry for skills?" — Yes: `SkillRegistry` (ABC) + GCS implementation. Roll your own for custom backends.
