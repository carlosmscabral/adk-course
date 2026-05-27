---
module: 09_Skills
page: 01_WhatIsASkill
title: What is a Skill (and why we needed a new primitive)
estimated_minutes: 15
prereqs: [09_Skills/00]
concepts: [Skill, progressive disclosure, file-based capability, frontmatter]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 09_Skills/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/02_SkillAnatomy →](02_SkillAnatomy.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 01 What Is A Skill

# 🧠 The skill = bundle pivot

## The problem skills solve

You wrote an agent with 30 prompt instructions. Half of them are "when reviewing a blog post for SEO, check title length, meta description, heading hierarchy, ..." — useful knowledge, but **only on the 1 in 50 turns the user actually asks for SEO review**. The other 49 turns, those tokens are paying rent for nothing.

Worse: you copy the same SEO checklist into your other three agents. Now there are four versions drifting apart.

A **Skill** is the fix: a file-based bundle of instructions + reference material that the agent **loads on demand**.

## File layout

```
my-skill-name/
  SKILL.md           ← required: frontmatter + instructions
  references/        ← optional: long-form reference docs
  assets/            ← optional: templates, data files
  scripts/           ← optional: executable shell scripts
```

The `SKILL.md` is the heart:

```markdown
---
name: seo-checklist
description: SEO optimization checklist for blog posts.
---

# SEO Instructions

When asked to review a blog post for SEO:

1. **Title**: 50-60 chars, primary keyword near the start.
2. **Meta description**: 150-160 chars.
3. ...
```

YAML frontmatter on top (the metadata the LLM uses to decide whether to load), Markdown below (the instructions the LLM follows once loaded).

## Progressive disclosure (L1 / L2 / L3)

This is the design ADK formalizes:

| Level | What the LLM sees                                                | When                                |
| ----- | ---------------------------------------------------------------- | ----------------------------------- |
| **L1**| `name` + `description` from frontmatter                          | Always — listed via `list_skills`.  |
| **L2**| Full Markdown body of `SKILL.md`                                 | Loaded via `load_skill(name)`.      |
| **L3**| Files in `references/`, `assets/`, `scripts/`                    | Loaded via `load_skill_resource(...)`. |

A 30-skill catalog can stay under 1 KB of context (just the L1 frontmatter). The LLM picks the skill it needs, calls `load_skill`, gets the body. If the body says "check `references/style-guide.md` for the full rules", the LLM calls `load_skill_resource("references/style-guide.md")`.

The result: **massive capability, tiny prompt.**

## Skill vs tool vs prompt rule

| If you have...                                  | Pick                              |
| ----------------------------------------------- | --------------------------------- |
| A function with side effects (send email, FX)   | **Tool** (Module 03 / MCP)        |
| A behavior rule that always applies             | **Prompt instruction**            |
| A behavior rule that's only sometimes needed    | **Skill** (this module)           |
| A bundle of rules + reference docs              | **Skill** (with resources)        |
| A capability that should be shared cross-agent  | **Skill** (with a registry)       |

> ❓ **Ask the student:** in their agent so far, name one prompt rule that would make more sense as a skill. (Common answer: "only translate to French if asked" — that's a skill-worthy bundle once it grows past one sentence.)

> 🚀 **In Production**
>
> Skills are Markdown. They version-control beautifully — diff your skill PRs the same way you diff code. The corollary: **a leaked skill registry leaks capability**. Treat skill repos as auth surface; see `06_InProduction.md`.

[← Prev: 09_Skills/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/02_SkillAnatomy →](02_SkillAnatomy.md)
