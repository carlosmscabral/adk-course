---
module: 09_Skills
page: 00_Overview
title: Module 09 — Skills (reusable capability bundles, NEW in 2.0)
estimated_minutes: 10
prereqs: [03_Tools/00]
concepts: [Skill, SkillToolset, Frontmatter, progressive disclosure]
icon: 🗺
in_production: true
detours_suggested: [VisualBuilder]
---

[← Prev: 08_MCP](../08_MCP/09_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 09_Skills/01_WhatIsASkill →](01_WhatIsASkill.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 00 Overview

# 🗺 Module 09 — Skills

A **Skill** is a unit of agent capability packaged as files (frontmatter + Markdown + optional scripts/resources) instead of as Python code. Skills are **NEW in ADK 2.0** — they answer "how do I share, version, and review agent behavior the same way I do code or content?"

## 🎯 What you'll walk away knowing

- The four primitives: `Skill`, `Frontmatter`, `Resources`, `Script`.
- The four invocation patterns: inline, file-based, external (GCS / repo), meta.
- How `SkillToolset` exposes skills to the agent (and the auto-generated `list_skills` / `load_skill` / `load_skill_resource` tools).
- Progressive disclosure (L1 / L2 / L3) — why your prompt doesn't bloat.
- When to write a tool vs when to write a skill.

## 🧰 Prereqs

- 03 (FunctionTool — to see what skills replace).
- Optional but useful: 07 (callbacks) for skill-gated guardrails.

## ⏱ Time

~2 days. Conceptually small, but the *mental shift* from "tool = function" to "skill = bundle" takes practice.

## 📦 Sample anchor

The canonical one and only — read it from end to end:

- `adk-samples/python/agents/agent-skills-tutorial/` — every pattern in this module is demonstrated here. Page 05 dissects it.

Files of interest:

- `app/agent.py` — wires four skills (inline, file-based, external, meta).
- `app/skills/blog-writer/SKILL.md` — minimal file-based skill.
- `app/skills/content-research-writer/SKILL.md` — file-based skill with a `references/` directory.

## 🗺 Map of this module

```
00 Overview            ← you are here
01 What Is A Skill
02 Skill Anatomy
03 SkillToolset
04 Skill Registry
05 Dissecting Sample (agent-skills-tutorial)
06 In Production
07 Knowledge Check
08 Mini Drill
```

> 🤖 **Tutor:** the easiest mental model is "Skills are to agents what packages are to Python — a way to ship capability with metadata." If the student is a working dev, lead with that.

[← Prev: 08_MCP](../08_MCP/09_MiniDrill.yml)  [↑ Map](../../MAP.md)  [Next: 09_Skills/01_WhatIsASkill →](01_WhatIsASkill.md)
