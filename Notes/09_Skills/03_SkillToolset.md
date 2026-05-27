---
module: 09_Skills
page: 03_SkillToolset
title: SkillToolset — wiring skills into an agent
estimated_minutes: 25
prereqs: [09_Skills/02]
concepts: [SkillToolset, list_skills, load_skill, load_skill_resource, additional_tools]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 09_Skills/02_SkillAnatomy](02_SkillAnatomy.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/04_SkillRegistry →](04_SkillRegistry.md)

You are here: 🗺 Integration Track ▸ 09 Skills ▸ 03 Skill Toolset

# 🛠 `SkillToolset` — the agent-facing surface

A `Skill` on its own doesn't talk to the LLM. You hand it to the agent through a **`SkillToolset`**, which auto-generates the four tools the LLM uses to discover and load skills.

```python
from google.adk.tools.skill_toolset import SkillToolset

toolset = SkillToolset(
    skills=[blog_writer_skill, seo_skill, content_researcher_skill],
)
```

## The tools the LLM gets, for free

When you wire the toolset into an agent, the LLM sees:

| Tool name            | Purpose                                                          |
| -------------------- | ---------------------------------------------------------------- |
| `list_skills`        | Returns L1 metadata (`name` + `description`) for every skill.   |
| `load_skill`         | Returns the L2 body of one skill by name.                       |
| `load_skill_resource`| Returns an L3 file by path (`references/foo.md`, `assets/...`). |
| `run_skill_script`   | Executes an L3 script (`scripts/foo.sh`) via bash.              |

The LLM is also given a built-in **system instruction** that teaches it the workflow:

> "If a skill seems relevant to the user query, you MUST use `load_skill(skill_name=...)` to read its full instructions before proceeding."

That comes from ADK; you don't have to write it.

## Plugging it into the agent

```python
from google.adk import Agent
from google.adk.tools.skill_toolset import SkillToolset

agent = Agent(
    model="gemini-2.5-flash",
    name="blog_skills_agent",
    description="A blog-writing agent powered by reusable skills.",
    instruction=(
        "You are a blog-writing assistant. Use list_skills to discover "
        "your skills, then load_skill to read instructions when needed."
    ),
    tools=[toolset],   # one toolset, N skills inside
)
```

That's it. Run the agent and ask "review this blog post for SEO" — the LLM will call `list_skills`, see `seo-checklist`, call `load_skill("seo-checklist")`, get the L2 body, and apply it.

## Mixing skills and regular tools

`SkillToolset` accepts `additional_tools=[...]` for plain tools that should sit alongside skills:

```python
from google.adk.tools.mcp_tool import MCPToolset

toolset = SkillToolset(
    skills=[travel_skill],
    additional_tools=[maps_mcp_toolset, send_email_tool],
)
```

This is what `travel-planner-google-maps-mcp` does: one toolset exposes a skill + Google Maps' MCP tools. The LLM sees everything in one place.

## What the LLM call looks like

A typical turn:

```
User: "Review this blog draft for SEO."
LLM tool call: list_skills()
        ↳ returns [{"name":"seo-checklist","description":"..."}, ...]
LLM tool call: load_skill(skill_name="seo-checklist")
        ↳ returns the SKILL.md body
LLM reply: "Here's my SEO review — [follows the checklist]..."
```

Notice: the L2 body never appears in the *initial* prompt. It only enters the conversation after `load_skill` is called. That's progressive disclosure paying off.

> 🛠 **Have the student run:** wire a `SkillToolset` with one inline skill, ask the agent a question that needs it, and inspect the trace to see `list_skills` → `load_skill` actually fire. (Skip the trace if you're short on time; the agent's reply will reference the skill.)

> ⚠️ **Gotcha** — if your toolset is empty (`skills=[]` and no `additional_tools`), the agent has nothing to call and falls back to its base instruction. Add at least one skill before testing.

> 🚀 **In Production**
>
> The L1 list goes into every LLM call. Keep your `description` text short and discriminative — bad descriptions cause the LLM to load the wrong skill (or none). When you have 20+ skills, switch to a `SkillRegistry` with semantic search (next page).

[← Prev: 09_Skills/02_SkillAnatomy](02_SkillAnatomy.md)  [↑ Map](../../MAP.md)  [Next: 09_Skills/04_SkillRegistry →](04_SkillRegistry.md)
