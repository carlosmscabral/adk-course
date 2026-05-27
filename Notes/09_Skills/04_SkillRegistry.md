---
module: 09_Skills
page: 04_SkillRegistry
title: SkillRegistry — sharing skills across agents
estimated_minutes: 20
prereqs: [09_Skills/03]
concepts: [SkillRegistry, search_skills, GCS, cross-agent reuse]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 09_Skills/03_SkillToolset](03_SkillToolset.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/05_DissectingSample →](05_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 04 Skill Registry

# 🧠 Going from "agent owns its skills" to "org owns its skills"

When 5 agents share 20 skills, hard-coding `skills=[skill_a, skill_b, ...]` in every agent gets old fast. The `SkillRegistry` is the abstraction that lets agents **discover** skills from a shared catalog.

```python
from google.adk.skills import SkillRegistry
```

`SkillRegistry` is an abstract base class (`ABC`). ADK ships at least one concrete implementation (GCS-backed); you can write your own for a custom catalog (Postgres, S3, a corporate API).

## What a registry adds

```python
toolset = SkillToolset(
    skills=[],                  # nothing local
    registry=my_registry,       # but here's the catalog
)
```

When `registry` is set, the toolset auto-adds a fifth tool:

- `search_skills(query: str)` — semantic / keyword search across the registry.

So a 200-skill registry never bloats the prompt. The LLM searches for what it needs, sees only relevant hits, then `load_skill`s.

## The flow

```
User: "Optimize my blog post for SEO and check brand voice."
LLM:  search_skills("SEO optimization brand voice")
        ↳ ["seo-checklist", "brand-voice-guide"]
LLM:  load_skill("seo-checklist")
LLM:  load_skill("brand-voice-guide")
LLM:  [applies both]
```

## Local + registry

You can combine: the local `skills=[...]` are always L1-listed; the registry hits show up via `search_skills`. Conflicts (same name in both) are resolved local-first, with a warning. This lets a team override an org-wide skill with a local variant for testing.

## Building your own registry

Inherit from `SkillRegistry` and implement the abstract methods. The framework calls into your class; you decide where the bytes come from.

```python
from google.adk.skills import Skill, SkillRegistry

class CorpRegistry(SkillRegistry):
    async def search_skills(self, query: str) -> list[Skill]: ...
    async def get_skill(self, name: str) -> Skill | None: ...
    def search_tool_description(self) -> str | None:
        return "Searches our corporate skill catalog by capability."
    # ... (implement the rest per the ABC)
```

This is how you wire a private knowledge platform into an ADK agent without copying every skill into every repo.

## Why this matters for governance

A registry is also a **gate**. You can:

- Restrict who can publish skills.
- Sign skills (frontmatter `license`, plus your own signature in `metadata`).
- Audit skill loads (every `load_skill` is a tool call; route it through a `before_tool_callback`).

That last one is the link back to Module 07: **the skill toolset is just tools. Your guardrails work unchanged.**

> ❓ **Ask the student:** if their org had a registry with a `payments-refund` skill, who should be allowed to load it from a customer-service agent vs from a marketing agent? (The answer turns into a `before_tool_callback` on `load_skill`.)

> 🚀 **In Production**
>
> Registries are powerful and dangerous. A bad skill description in the registry (or a malicious one in a misconfigured shared catalog) can hijack agent behavior. Treat your skill registry as code: code-review every PR, sign every skill, audit every load. See [[16_ProductionSecurity/00_Overview]].

[← Prev: 09_Skills/03_SkillToolset](03_SkillToolset.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/05_DissectingSample →](05_DissectingSample.md)
