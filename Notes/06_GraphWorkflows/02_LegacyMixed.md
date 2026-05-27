---
module: 06_GraphWorkflows
page: 02_LegacyMixed
title: Templates mix — reading story_teller
estimated_minutes: 25
prereqs: [06_GraphWorkflows/01]
concepts: [nested-templates, SequentialAgent, LoopAgent, ParallelAgent]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 06_GraphWorkflows/01_LegacyTemplates]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/03_WhyGraphWorkflows →]

You are here: 🗺 Composition Track ▸ 06 Graph Workflows ▸ 02 Legacy Mixed

## 🛠 The artifact

`adk-samples/python/agents/story_teller/story_teller_agent/agent.py` — a single ~140-line file that nests all three legacy templates. We'll read it top-down.

## 📁 The agents (five LLM agents)

```python
prompt_enhancer  = LlmAgent(...)   # expand user idea into a full premise
creative_writer  = LlmAgent(... temperature=0.9 ...)   # wild draft
focused_writer   = LlmAgent(... temperature=0.2 ...)   # safe draft
critique_agent   = LlmAgent(...)   # pick the better draft, append to story
editor_agent     = LlmAgent(...)   # final polish
```

Each writes its own `output_key`: `enhanced_prompt`, `creative_chapter_candidate`, `focused_chapter_candidate`, `current_story` (overwrites), `final_story`.

## 📁 The orchestration — three nested templates

```python
# 1. Run two writers concurrently (different temperatures).
parallel_writers = ParallelAgent(
    name="ParallelChapterGenerators",
    sub_agents=[creative_writer, focused_writer],
)

# 2. One chapter cycle = parallel drafts, then critique picks the winner.
chapter_cycle = SequentialAgent(
    name="ChapterGenerationCycle",
    sub_agents=[parallel_writers, critique_agent],
)

# 3. Loop the cycle N times to build a 3-chapter story.
story_loop = LoopAgent(
    name="StoryBuildingLoop",
    sub_agents=[chapter_cycle],
    max_iterations=N_CHAPTERS,    # = 3
)

# 4. Outer: enhance prompt → loop chapters → final edit.
root_agent = SequentialAgent(
    name="CollaborativeStoryWorkflow",
    sub_agents=[prompt_enhancer, story_loop, editor_agent],
)
```

## 🧠 The shape, drawn

```
SequentialAgent (root)
├── prompt_enhancer          (LlmAgent)
│
├── LoopAgent  ×N_CHAPTERS
│   └── SequentialAgent  ("chapter_cycle")
│       ├── ParallelAgent
│       │   ├── creative_writer   (temp 0.9)
│       │   └── focused_writer    (temp 0.2)
│       └── critique_agent        (picks winner, appends to story)
│
└── editor_agent              (LlmAgent)
```

See [`_figures/legacy_templates.txt`](_figures/legacy_templates.txt).

## 🧠 Why this still works in 2.0

Every nesting is just `SequentialAgent(sub_agents=[...other agent...])`. There's no graph, no `WorkflowAgent`, no edges. The composition is the **tree structure**. The runtime executes by depth-first walk: enter the outer Sequential → enter the Loop → enter the inner Sequential → enter the Parallel → run both writers → exit → run critique → exit Sequential → next loop iteration → ...

## ⚠️ Where this style hits its ceiling

- **No conditional routing.** What if the editor wants to send the story *back* to the loop for one more chapter? Templates can't express that — the only loop is the fixed `LoopAgent` with a counter.
- **No partial joins.** What if 2 of 3 parallel writers finish and the third is slow — can we move on? No.
- **No HITL pause.** Can't pause mid-pipeline for human input. (You could fake it with a callback, but messy.)
- **No dynamic node count.** The number of parallel children is fixed at definition.

When any of those bites, you upgrade to the graph API. That's the next page.

## 🛠 Read-along checks

> 🛠 **Have the student open** `adk-samples/python/agents/story_teller/story_teller_agent/agent.py` and identify:
>
> 1. Which `output_key` does the `critique_agent` overwrite each iteration?
> 2. Why is `before_model_callback=set_initial_story` on `prompt_enhancer` and not somewhere else?
> 3. What happens to `creative_chapter_candidate` and `focused_chapter_candidate` after the critique picks — are they cleared?

(Answers in this module's `AGENTS.md`.)

---

[← Prev: 06_GraphWorkflows/01_LegacyTemplates]  [↑ Map](../../MAP.md)  [Next: 06_GraphWorkflows/03_WhyGraphWorkflows →]
