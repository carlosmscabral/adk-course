---
module: 09_Skills
page: 06_InProduction
title: Skills in production — versioning, governance, description hygiene
estimated_minutes: 15
prereqs: [09_Skills/05]
concepts: [skill_versioning, registry_governance, description_hygiene, audit]
icon: 🚀
in_production: true
detours_suggested: [VisualBuilder]
---

[← Prev: 09_Skills/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/07_KnowledgeCheck →](07_KnowledgeCheck.yml)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 06 In Production

# 🚀 Production checklist for skills

## Skills version-control beautifully — use that

A `SKILL.md` is text. Put your skills in git, code-review every change. Two practical tips:

- **One PR = one skill change.** A skill is a contract — the description is the contract surface. Don't tweak it casually.
- **Diff the description like an API change.** A new word in the description changes what the LLM loads. Test before merging.

## Description hygiene rules

Every L1 description is a recurring cost (it sits in every LLM call when listed). Keep them:

- **Short** — under 200 chars in practice (the framework allows 1024).
- **Discriminative** — name the *exact* scenarios this skill applies to.
- **Free of hedging** — "may help with..." is noise; the LLM ignores fuzzy descriptions.

Bad: `"A useful tool for writing things."`
Good: `"SEO checklist for blog posts. Covers title tags, meta descriptions, heading hierarchy, keyword density."`

## Registries are auth surface

When skills come from a shared registry, **anything that publishes a skill can change agent behavior**. Treat the registry as you would a CI/CD pipeline: signed commits, restricted publishers, audit log.

```python
def audit_skill_loads(tool, args, tool_context):
    if tool.name == "load_skill":
        logging.info("skill.load name=%s user=%s",
                     args.get("skill_name"),
                     tool_context.state.get("user:id"))
    return None

agent = Agent(..., before_tool_callback=audit_skill_loads, ...)
```

That's a one-line audit log for every skill access.

## Frontmatter conventions to enforce in CI

A pre-commit hook (or a CI step) should check every `SKILL.md` for:

- `name` matches the directory name.
- `name` is kebab-case, `len(name) <= 64`.
- `description` is non-empty and `<= 1024 chars`.
- `description` doesn't include forbidden tokens (PII patterns, internal codenames).
- Optional: `description` is < 250 chars (your house rule).

The framework checks the first three at load time. The last two are yours.

## Skill discovery pattern

When you have many skills, two pre-call hops happen on every LLM turn: list, then load. To minimize them:

- **Compose** related skills into one when they always load together.
- **Split** monolithic skills when only part is usually needed (then progressive disclosure pays off).

## Visual composition

ADK 2.0 also ships **Visual Builder** for assembling skills + agents in a drag-and-drop UI. Authoring a skill there generates the same Markdown you'd write by hand. See [[VisualBuilder]] when you're ready.

## Cross-link

- The recurring guardrails example continues in [[16_ProductionSecurity/00_Overview]].
- For mixing skills with MCP tools in one toolset, recap [[08_MCP/06_DissectingSample]] and look at `travel-planner-google-maps-mcp/agent.py`.
- Milestone M3 (Federated Travel Planner) packages your booking sub-agent as a skill.

> 🤖 **Tutor:** if the student starts naming skills with verbs ("write-the-blog"), nudge to nouns or noun-phrases ("blog-writer"). Skills are capabilities, not commands.

[← Prev: 09_Skills/05_DissectingSample](05_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/07_KnowledgeCheck →](07_KnowledgeCheck.yml)
