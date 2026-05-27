---
module: 09_Skills
page: 02_SkillAnatomy
title: Skill anatomy — Frontmatter, instructions, Resources, Scripts
estimated_minutes: 25
prereqs: [09_Skills/01]
concepts: [Skill, Frontmatter, Resources, Script, models, kebab-case]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 09_Skills/01_WhatIsASkill](01_WhatIsASkill.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/03_SkillToolset →](03_SkillToolset.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 02 Skill Anatomy

# 🛠 The four data classes

```python
from google.adk.skills import Skill, Frontmatter, Resources, Script
```

```
{{_figures/skill_anatomy.txt}}
```

## `Frontmatter` — the L1 contract

```python
class Frontmatter(BaseModel):
    name: str            # kebab-case, max 64 chars
    description: str     # max 1024 chars (this is what the LLM reads to decide)
    license: str | None
    compatibility: str | None
    allowed_tools: str | None   # space-delimited pre-approved tools
    metadata: dict       # client-specific extras (e.g. adk_additional_tools)
```

Two rules the framework enforces:

- `name` must match `^[a-z0-9]+(-[a-z0-9]+)*$` (kebab-case, no leading/trailing hyphens).
- `description` is the **load-or-don't decision surface** — write it for the LLM, not for humans.

## `Skill` — the bundle

```python
class Skill(BaseModel):
    frontmatter: Frontmatter         # L1
    instructions: str                # L2 (the SKILL.md body)
    resources: Resources = Resources()  # L3
```

Two convenience properties: `skill.name` and `skill.description` proxy to the frontmatter.

## `Resources` — the L3 lookup table

```python
class Resources(BaseModel):
    references: dict[str, str | bytes] = {}  # markdown docs
    assets: dict[str, str | bytes] = {}      # templates, schemas
    scripts: dict[str, Script] = {}          # executable shell scripts
```

Each key is a relative path (e.g. `"references/style-guide.md"`), each value is the file content. When the LLM calls `load_skill_resource("references/style-guide.md")`, ADK reads from this dict.

## `Script` — wrappable executable

```python
class Script(BaseModel):
    src: str   # the script source
```

Trivially a string wrapper. The reason it's its own type: `run_skill_script` only runs entries in `scripts/`, not arbitrary text — the type marker is the affordance.

## Inline skill — defined in Python

You don't have to put a skill on disk. The simplest pattern:

```python
from google.adk.skills import models

seo_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="seo-checklist",
        description="SEO optimization checklist for blog posts.",
    ),
    instructions=(
        "When optimizing a blog post for SEO, check each item:\n\n"
        "1. **Title**: 50-60 chars, primary keyword near the start\n"
        "2. **Meta description**: 150-160 chars\n"
        "...\n"
    ),
)
```

Good for: stable rules that don't need reference files, code-as-config setups.

## File-based skill — `load_skill_from_dir`

```python
import pathlib
from google.adk.skills import load_skill_from_dir

blog_writer_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "blog-writer"
)
```

The directory must contain a `SKILL.md`. The directory name **must match** the frontmatter `name` field. Subdirectories (`references/`, `assets/`, `scripts/`) are picked up automatically.

## GCS-hosted skill — `load_skill_from_gcs_dir`

Same shape, source is a `gs://` URI:

```python
from google.adk.skills import load_skill_from_gcs_dir

shared_skill = load_skill_from_gcs_dir("gs://my-org-skills/seo-checklist")
```

Great for cross-team sharing without forking a repo.

## The four invocation patterns at a glance

| Pattern         | How                                                  | Best for                                     |
| --------------- | ---------------------------------------------------- | -------------------------------------------- |
| Inline          | `models.Skill(...)` in Python                        | Simple stable rules                          |
| File-based      | `load_skill_from_dir("path/to/skill")`              | Complex skills with references               |
| External / GCS  | `load_skill_from_gcs_dir("gs://...")`               | Cross-org sharing, central registries        |
| Meta            | An inline/file skill whose body is "create a skill" | Self-extending agents                        |

We see all four in the sample dissection (page 05).

> 🛠 **Have the student run:** create a `Skill` inline with name `pirate-style` and description "respond like a pirate". They'll use it in 03.

> ⚠️ **Gotcha** — if the directory name doesn't match the frontmatter name, `load_skill_from_dir` raises immediately. Same if `description` is empty or > 1024 chars.

[← Prev: 09_Skills/01_WhatIsASkill](01_WhatIsASkill.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/03_SkillToolset →](03_SkillToolset.md)
