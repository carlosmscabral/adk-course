---
module: 09_Skills
page: 05_DissectingSample
title: Dissecting agent-skills-tutorial — the four patterns end-to-end
estimated_minutes: 30
prereqs: [09_Skills/04]
concepts: [inline skill, file-based skill, external skill, meta skill, SkillToolset]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 09_Skills/04_SkillRegistry](04_SkillRegistry.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/06_InProduction →](06_InProduction.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 05 Dissecting Sample

# 🧠 Reading `agent-skills-tutorial/` end to end

> 🛠 **Have the student run:** open the repo at `/home/carloscabral/study/adk-samples/python/agents/agent-skills-tutorial/` and read along.

## Directory layout

```
agent-skills-tutorial/
├── app/
│   ├── agent.py                         ← wires the 4 patterns
│   └── skills/
│       ├── blog-writer/
│       │   ├── SKILL.md                 ← file-based skill
│       │   └── references/style-guide.md
│       └── content-research-writer/
│           ├── SKILL.md                 ← file-based skill (external pattern)
│           └── references/seo-guidelines.md
├── assets/                              ← screenshots only
└── README.md
```

Two file-based skills on disk. Two more skills are defined inline in `app/agent.py`. So the four patterns are:

1. **Inline** — `seo_skill` (defined in Python).
2. **File-based** — `blog_writer_skill` (loaded from `app/skills/blog-writer/`).
3. **External (cloned repo / shared dir)** — `content_researcher_skill` (loaded from `app/skills/content-research-writer/`, treated as if pulled from an external source).
4. **Meta** — `skill_creator` (an inline skill whose job is to *create new skills*).

## Pattern 1 — inline `seo_skill`

```python
seo_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="seo-checklist",
        description="SEO optimization checklist for blog posts. ...",
    ),
    instructions=(
        "When optimizing a blog post for SEO, check each item:\n\n"
        "1. **Title**: 50-60 chars, primary keyword near the start\n"
        "..."
    ),
)
```

Three things to notice:

- The instructions live in a single Python string. Easy to edit, no file system, but harder to diff in PRs.
- No `resources=` — this skill is L1+L2 only. The LLM sees the description, calls `load_skill`, gets the body. Done.
- The description is **prescriptive**: it names exactly what the skill covers ("title tags, meta descriptions, heading structure..."). That's what makes the LLM pick it correctly.

## Pattern 2 — file-based `blog_writer_skill`

```python
blog_writer_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "blog-writer"
)
```

The skill's `SKILL.md`:

```markdown
---
name: blog-writer
description: Blog post writing skill with structure templates and style guidelines. ...
---

# Blog Writer Instructions

When asked to write a blog post, follow these steps:

## Step 1: Structure
Use `load_skill_resource` to read `references/style-guide.md` for the writing style rules.

## Step 2: Outline First
...
```

The body explicitly tells the LLM to call `load_skill_resource` to fetch `references/style-guide.md` — that's the L3 hop. Without it, the style guide stays unread.

## Pattern 3 — external `content_researcher_skill`

Mechanically identical to pattern 2:

```python
content_researcher_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "content-research-writer"
)
```

The pattern is what the directory **represents**: a skill not authored locally but pulled from a community repo or shared catalog. In a real setup this could be a git submodule, a GCS sync, or a `pip` install that drops files into a known location.

## Pattern 4 — meta `skill_creator`

```python
skill_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="skill-creator",
        description="Creates new ADK-compatible skill definitions from requirements. ...",
    ),
    instructions=(
        "When asked to create a new skill, generate a complete SKILL.md file.\n\n"
        "Read `references/skill-spec.md` for the format specification.\n"
        "Read `references/example-skill.md` for a working example.\n"
        "..."
    ),
    resources=models.Resources(
        references={
            "skill-spec.md": "...the spec text...",
            "example-skill.md": "...an example skill...",
        }
    ),
)
```

This skill bundles **resources inline** — the `references/` dict is in Python, not on disk. The agent calls `load_skill_resource("skill-spec.md")` to read it. The meta pattern: the skill teaches the LLM how to write more skills.

## Wiring

```python
skill_toolset = SkillToolset(
    skills=[seo_skill, blog_writer_skill, content_researcher_skill, skill_creator],
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="blog_skills_agent",
    instruction=(
        "You are a blog-writing assistant with specialized skills.\n\n"
        "When the user asks you to write, research, or optimize:\n"
        "1. Load the relevant skill(s) to get detailed instructions\n"
        "2. Use load_skill_resource to access reference materials\n"
        "3. Follow the skill's step-by-step instructions\n"
        "..."
    ),
    tools=[skill_toolset],
)
```

One toolset, four skills, four patterns. The agent's own instruction is short — the *behavior* lives in the skills.

> ❓ **Ask the student:** if the meta `skill_creator` generates a new skill at runtime, where would you persist it so the next session has it? (Answer: write the `SKILL.md` to a directory you `load_skill_from_dir(...)` next boot — or push to a registry.)

[← Prev: 09_Skills/04_SkillRegistry](04_SkillRegistry.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/06_InProduction →](06_InProduction.md)
