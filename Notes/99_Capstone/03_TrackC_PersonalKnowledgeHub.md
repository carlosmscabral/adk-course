---
module: 99_Capstone
page: 03_TrackC_PersonalKnowledgeHub
title: Track C — Personal Knowledge Hub
estimated_minutes: 30
prereqs: [99_Capstone/00]
concepts: [personal-knowledge, memory, Skills]
icon: 🛠
in_production: true
---

[← Prev: 99_Capstone/02_TrackB_CodeReviewer]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/04_SharedRequirements →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 03 Track C

# 🛠 Track C — Personal Knowledge Hub

See `_figures/track_c.txt` for the architecture diagram.

## The pitch

A lifelong assistant that **captures** notes, **recalls** them later by semantic search, and **synthesizes** across them on demand. Capabilities packaged as ADK **Skills** so other people / agents can install your "knowledge hub skillpack."

## The spec

### Agents (3 minimum — sub_agents)

1. **`Root` / Router** (`LlmAgent`)
   - Reads the user message; routes to Capture / Recall / Synthesize.
   - `sub_agents=[capture, recall, synthesize]`.

2. **`CaptureAgent`** (`LlmAgent`)
   - Skill-driven: uses `SkillToolset` from a `skills/capture/` directory.
   - Skills: `save-note`, `tag-note`, `link-note`.
   - Writes to `VertexAiMemoryBankService` AND `VertexAiRagMemoryService`.

3. **`RecallAgent`** (`LlmAgent`)
   - Tool: `load_memory` (built-in) → reads from `VertexAiMemoryBankService` (curated).
   - Tool: custom RAG tool reading `VertexAiRagMemoryService` (vector search).
   - Returns top-K relevant notes.

4. **`SynthesizeAgent`** (`LlmAgent`)
   - Input: a question + set of retrieved notes.
   - Output: a synthesis with explicit per-claim citations to the note IDs.

### Tools (≥2)

- `SkillToolset` (from `skills/capture/`).
- `load_memory` (built-in).
- Custom `FunctionTool(retrieve_rag(query, top_k))`.

### Skills package (Track C's headline)

```
skills/capture/
  save-note.skill         ← frontmatter + body
  tag-note.skill
  link-note.skill
skills/recall/
  fuzzy-find.skill
```

Each `.skill` file has YAML frontmatter (name, description, parameters) plus a body of instructions. Bundle them with `SkillToolset.from_dir("skills/capture")`.

### Persistent state

`DatabaseSessionService`.

### Memory services (BOTH)

- `VertexAiMemoryBankService` — curated, low-volume, agent-edited.
- `VertexAiRagMemoryService` — high-volume, vector-indexed, all raw note text.

Track C is the only track that **requires both** because the contrast (curated vs vector) is the lesson.

### Eval cases (≥5)

- Capture a note about "I like dark roast coffee" → later, recall correctly answers "what coffee do I like?".
- Capture 5 notes on a project → synthesize correctly highlights themes.
- Recall on a topic with no captured notes → graceful "I don't have notes on that" (NOT hallucinated).
- Capture with PII (`SSN: 123-45-6789`) → before_model_callback scrubs it.
- Synthesize with explicit "cite every claim" — output has citation markers.

Use `HallucinationsV1` evaluator for the "no notes → no answer" case.

### Plugins (≥1) and callbacks (≥2)

- `LoggingPlugin`.
- `GlobalInstructionPlugin` for "you are Carlos's knowledge hub; speak in first person about him."
- `before_model_callback` → PII scrubber (regex-based; SSNs, phone numbers, emails).
- `before_tool_callback` on `save-note` → auth check (only the right user can write).

### A2A interface

`to_a2a(root)`. Run `adk web` for a UI; also expose A2A for programmatic access.

### Observability

OpenTelemetry → Cloud Trace. Every capture/recall is a top-level span.

### README

Architecture, run, eval, plus a section "How to install the Skills pack" — because Skills are the headline.

## Suggested file layout

```
capstone-pkh/
├── personal_knowledge_hub/
│   ├── agent.py              ← Root + routing
│   ├── sub_agents/
│   │   ├── capture/agent.py
│   │   ├── recall/agent.py
│   │   └── synthesize/agent.py
│   ├── tools/
│   │   └── rag.py
│   ├── plugins/
│   │   └── pii_scrub.py
│   └── skills/
│       ├── capture/
│       │   ├── save-note.skill
│       │   └── tag-note.skill
│       └── recall/
│           └── fuzzy-find.skill
├── tests/
│   └── eval_set.json
├── README.md
└── pyproject.toml
```

> 🚀 **In Production**
>
> Long-term memory accumulates. Plan now for: deletion (GDPR-style "forget me"), versioning (a note can be edited), and conflict resolution (two captures contradict each other — which wins?). Address all three in your README's "limitations" section.

> 🛠 **Have the student run:** `cat skills/capture/save-note.skill` after they write the first skill. The frontmatter + body shape should be familiar from module 09.

[← Prev: 99_Capstone/02_TrackB_CodeReviewer]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/04_SharedRequirements →]
