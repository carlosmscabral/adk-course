# ADK Course — Authoring Agent Brief

**Read this file first.** It contains the conventions every authoring agent must follow. Your specific deliverables are in the prompt that spawned you. The full course plan (read once for context, then come back here) is at `/home/carloscabral/.claude/plans/snazzy-sleeping-cerf.md`.

Course root: `/home/carloscabral/study/adk-course/`

---

## What this course is

A Practical-Python-style, MD-based course on **Google ADK Python 2.0 GA** (verified 2026-05-27 at https://adk.dev/). Engine-first teaching: low-level primitives by hand, then the abstraction. Student is a working Python developer aiming for deep ADK fluency. The student uses an AI coding assistant (Claude Code etc.) to drive the lessons interactively — so every page is **a script for that tutor to perform**, not an essay to passively read.

## ADK 2.0 surface to cover (the truth of the framework)

- **Agents**: `LlmAgent` (alias `Agent`), `BaseAgent`; `SequentialAgent`, `ParallelAgent`, `LoopAgent` (legacy workflow templates, still supported); **graph-based `WorkflowAgent` (2.0 primary)**; collaborative agents (NEW); `RemoteA2aAgent`; `LangGraphAgent`.
- **Runtime**: `Runner`, `InMemoryRunner`, `runner.run_async()` → async iterator of `Event`.
- **Session services**: `InMemorySessionService`, `DatabaseSessionService`, `VertexAiSessionService`, `SqliteSessionService`. Session rewind/migrate (NEW).
- **State prefixes**: no-prefix (session-scoped), `user:`, `app:`, `temp:`.
- **Events**: `author`, `content`, `actions` (`state_delta`, `artifact_delta`, `transfer_to_agent`, `escalate`, `skip_summarization`).
- **Tools**: `BaseTool`, `FunctionTool`, `LongRunningFunctionTool`, `AgentTool`, `ToolContext`, `MCPToolset`, `SkillToolset`. Built-ins: `google_search`, `load_memory`, `exit_loop`, `transfer_to_agent`.
- **Models**: Gemini, Claude (via Vertex), Gemma, `LiteLlm`, `OpenAILlm`, `ApigeeLlm`, `LLMRegistry`.
- **Memory**: `InMemoryMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`.
- **Callbacks**: `before/after_model_callback`, `before/after_tool_callback`, `before/after_agent_callback`, `on_model_error_callback`, `on_tool_error_callback`.
- **Plugins**: `LoggingPlugin`, `ReflectAndRetryToolPlugin`, `ContextFilterPlugin`, `GlobalInstructionPlugin`, `BigQueryAgentAnalyticsPlugin`.
- **Skills (NEW)**: `Skill`, `Script`, `Frontmatter`, `SkillToolset`, `SkillRegistry`.
- **A2A**: `AgentCard`, `to_a2a(root_agent)`, `RemoteA2aAgent`.
- **Code execution**: `UnsafeLocalCodeExecutor` (dev only), `BuiltInCodeExecutor`, `VertexAiCodeExecutor`, `ContainerCodeExecutor`, `GkeCodeExecutor`, `AgentEngineSandboxCodeExecutor`.
- **Evaluation**: `AgentEvaluator`, `EvalCase`, `EvalSet`, `LlmAsJudge`, `RubricBasedEvaluator`, `TrajectoryEvaluator`, `HallucinationsV1`, `FinalResponseMatchV1/V2`.
- **CLI**: `adk run`, `adk eval`, `adk web`, `adk create`, `adk deploy`.
- **Live**: Gemini Live API (bidi voice/video, gRPC under the hood).
- **NEW 2.0 surface**: graph workflows, collaborative agents, Visual Builder, Ambient Agents, Resume/Cancel, Agent Config, context caching/compression, session rewind/migrate.

## Reference repos (READ-ONLY context)

- `/home/carloscabral/study/adk-python/` — framework source (use only for Internals module and surgical detours).
- `/home/carloscabral/study/adk-samples/python/agents/` — **60+ canonical samples; your sample anchors live here**. Every module dissects 1-2 real samples.
- `/home/carloscabral/study/practical-python/Notes/` — pedagogical style reference. Mimic the file structure: numbered concept pages, breadcrumbs, terse prose, runnable scripts (pure-Python detours can keep REPL).

When you author a "Dissecting Sample" page, the example must be from a real sample directory above. Reference real file paths (e.g., `adk-samples/python/agents/llm-auditor/sub_agents/critic/agent.py`).

---

## Module folder skeleton (MANDATORY — every `Notes/NN_Topic/`)

```
NN_Topic/
├── 00_Overview.md             # what you'll learn, prereqs, time, sample anchor
├── 01_Concept.md              # numbered concept pages, one concept each
├── 02_Concept.md
├── ...
├── 05_DissectingSample.md     # real-sample read-through (every module has one)
├── 06_InProduction.md         # real-world best practices for THIS module
├── 07_KnowledgeCheck.yml      # machine-parseable Q+A (assistant asks one at a time)
├── 08_MiniDrill.yml           # exercise spec with verification rubric
├── AGENTS.md                  # module-local teaching notes for the AI tutor
└── _figures/                  # ASCII art used by this module
```

The numbered position of `05_DissectingSample`, `06_InProduction`, `07_KnowledgeCheck`, `08_MiniDrill` is **fixed by convention even if the module has more or fewer concept pages**. If a module has 7 concept pages, the dissection page becomes `08_DissectingSample.md`, In Production becomes `09_InProduction.md`, KC `10_KnowledgeCheck.yml`, MiniDrill `11_MiniDrill.yml` — i.e., the four "trailing" files always come last, in that order. Pick whichever feels natural; the canonical case is 1-2 concept pages then 03-04 more concept pages then the trailing four.

## Page frontmatter (MANDATORY — every concept `.md`)

```yaml
---
module: 03_Tools
page: 02_FunctionTool
title: Building your first FunctionTool
estimated_minutes: 25
prereqs: [02_FirstAgent/04, 03_Tools/01]
concepts: [FunctionTool, docstring-as-schema, ToolContext]
icon: 🛠
in_production: true
detours_suggested: [PY_typing, PY_dataclasses]
---
```

`prereqs` use the format `NN_Module/MM` (no extension). `detours_suggested` are bare names from `Notes/Detours/` (no `.md`). `icon` matches the emoji vocabulary below.

## Breadcrumbs (MANDATORY — top + bottom of every concept page)

```
[← Prev: 03_Tools/01_WhyTools]  [↑ Map](../../MAP.md)  [Next: 03_Tools/03_AgentAsTool →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 02 FunctionTool
```

For first page of a module: `[← Prev: (prior module last page)]`. For last page: `[Next: (next module overview) →]`. If no prior/next, write `—`.

---

## Pedagogical style guide (the 15 rules)

1. **Terse, declarative prose.** No more than 40 lines per concept page. If a concept needs more, split it.
2. **Runnable script examples lead.** ADK is async-only and session-bound — `>>>` REPL blocks are a lie for any ADK code. Show a real `.py` file the student runs from `Work/`. Open the block with a path-comment like `# Work/05_routing_agent.py — run with: uv run python Work/05_routing_agent.py`, then the file body, then the shell output below. **Pure-Python detours** (`PY_async`, `PY_typing`, `PY_dataclasses`, etc.) and **pure data manipulation** (chunking strings, slicing lists) can keep REPL `>>>` style — that's how Python is actually taught. Anything that touches `LlmAgent`, `Runner`, `Session`, `Vertex AI`, `BigQuery`, MCP, A2A, callbacks, or any async call → script style.
3. **One concept per file.** ~20-40 lines + 1-2 embedded exercises.
4. **Embedded exercises inline.** Solutions in `Solutions/` only for ~15% (gate-keepers).
5. **Inductive, then deductive.** Show 3 examples, then state the rule.
6. **Breadcrumbs top + bottom.** Mandatory.
7. **Cross-references are explicit.** "We saw X in `04_SessionsState/02_StateScopes` — here's the wrinkle."
8. **Spiral curriculum.** The recurring "research-assistant" mini-app is rebuilt across modules — 02 (single agent), 03 (with tools), 05 (multi-agent), 06 (graph), 10B (GCP RAG), 11 (memory), 14 (evals), 16 (guardrails), 99 (capstone).
9. **Knowledge checks: 5-7 questions, one-sentence answers each.** Live in `07_KnowledgeCheck.yml`.
10. **Mini-drills bridge concepts.** Live in `08_MiniDrill.yml`. Milestone drills (M1-M5) integrate across modules.
11. **ASCII art over text walls.** Anything that's a graph, lifecycle, or layered architecture gets ASCII in `_figures/` and embedded in the page with triple backticks.
12. **Emojis encouraged at section headers and callouts.** Vocabulary (consistent everywhere):
    - 🧠 concept / 🛠 hands-on / ⚠️ gotcha / 🚀 in-production / 🐍 Python detour
    - ☁️ GCP-specific / 🎙 Live/streaming / 🧪 test/eval / 🗺 navigation / 🏁 milestone
    - 🤖 tutor-instruction / ❓ check-question / 🧭 detour-suggestion / 📦 packaging / 📡 protocol
13. **Solutions are gate-keepers.** Don't put solutions in `Solutions/` unless the student genuinely needs to peek (typically first exercise of a new pattern).
14. **`> **In Production**` callouts inline.** Wherever a page introduces a tool/API/pattern with real-world gotchas, end with a `> **🚀 In Production**` blockquote naming the gotcha and the standard mitigation. **Every module also has a dedicated `06_InProduction.md` consolidating these.**
15. **Pages are scripts the tutor performs.** Include explicit pause-points:
    - `> ❓ **Ask the student:** ...`
    - `> 🛠 **Have the student run:** ...`
    - `> 🧭 **If the student looks stuck:** suggest detour [[PY_async]]`
    - `> 🤖 **Tutor:** ...` (meta-instruction for the AI tutor)

A page that reads fine but offers no tutor hooks is incomplete.

---

## YAML formats

### `07_KnowledgeCheck.yml`

```yaml
module: 03_Tools
questions:
  - id: q1
    prompt: "What turns a Python function into a tool the LLM can see?"
    expected_keywords: [FunctionTool, docstring, type hints]
    accept_paraphrase: true
    difficulty: easy
  - id: q2
    prompt: "Why does the docstring matter for a FunctionTool?"
    expected_keywords: [schema, description, LLM, when to call]
    accept_paraphrase: true
    difficulty: medium
  # 5-7 questions total. All answerable in one sentence.
```

### `08_MiniDrill.yml`

```yaml
module: 03_Tools
exercise:
  id: 03_Tools_mini
  prompt: |
    Write a `calculator` tool with 4 operations (+, -, *, /).
    Wire it into an LlmAgent. Verify the LLM picks the right op
    for each of: "what is 3+4?", "7*5?", "20/4?", "10-5?".
  scaffolding_hint: |
    Start from Work/_template_run.py.
  estimated_minutes: 30
  verification:
    type: script_output   # script_output | code_review | llm_judge
    expect_files: [Work/calc_agent.py]
    expect_run_output_contains: ["7", "35", "5", "5"]
    grading_rubric:
      - "Tool function has correct type hints"
      - "Docstring describes each operation"
      - "Agent successfully invokes the tool for at least 3 of 4 ops"
  solution_pointer: Solutions/03_Tools/calc_agent.py  # only if gate-keeper
  tutor_notes: |
    Common mistake: bare `def calc(a, b, op)` without type hints — LLM can't
    pick the op reliably. Have the student fix it before moving on.
```

### Page frontmatter — repeated here for emphasis

Every concept `.md` (NOT `00_Overview.md` for `_TEMPLATE_MODULE`, NOT YAML files) needs the frontmatter block. `00_Overview.md` also gets frontmatter.

---

## Module-local `AGENTS.md` (~30-60 lines)

Each module folder has its own `AGENTS.md` for the tutor. Template:

```markdown
# AGENTS.md — Module 03 Tools (teaching notes for the AI tutor)

## What the student should walk away knowing
- Bullet, bullet, bullet.

## Pacing
- Easy if: student already writes typed Python. Cruise.
- Hard if: student fuzzy on type hints → drill PY_typing before 02.

## Watch for these mistakes
- Forgetting docstring → LLM can't pick the tool.
- Returning non-serializable objects from a FunctionTool.
- Using `**kwargs` instead of typed params.

## When to suggest a detour
- Student asks "why type hints?" → suggest PY_typing.
- Student asks "what about dataclasses?" → suggest PY_dataclasses.

## Mini-drill grading
- Pass = tool works on ≥3 of 4 operations.
- Edge case to probe: ask the student to handle division by zero. If they
  raise an exception, ask how that surfaces to the LLM (event with error).
```

---

## "In Production" callouts — what to include

Wherever you introduce a tool, API, or pattern that has real-world risk:

```markdown
> **🚀 In Production**
>
> `UnsafeLocalCodeExecutor` runs generated code in your Python process with no
> sandbox. Acceptable in dev for fast iteration; **never** in prod. The standard
> swap is `ContainerCodeExecutor` (Docker isolation) or `VertexAiCodeExecutor`
> (Google-managed sandbox). See also [[16_ProductionSecurity/02_CodeExecSafety]].
```

Each module's `06_InProduction.md` then consolidates these into a checklist for that module's surface area.

---

## Cross-linking conventions

- **Same-module page**: `[link](04_StateScopes.md)` (relative file).
- **Other-module page**: `[link](../05_MultiAgent/03_AgentAsTool.md)`.
- **Detour**: `[[PY_async]]` (the tutor resolves the wiki-style link).
- **Cheat sheet**: `[link](../../Reference/CheatSheets/state_prefixes.md)`.
- **Plan / map**: `[Map](../../MAP.md)`, `[Progress](../../PROGRESS.md)`.
- **Wiki refs must point at a page, not a module.** Use `[[<module>/<page>]]`. To link to a module's overview, use `[[<module>/00_Overview]]`.

---

## Detour pages (`Notes/Detours/*.md`)

Each is a single standalone file (no folder), 60-200 lines. Same frontmatter shape as a concept page, but `module: Detours`. Optional 🧪 mini-exercise at the end. Detours are never gating — phrase them as "if X feels hand-wavy, take 20 min here."

---

## What's authoritative for ADK behavior

In order of preference:
1. **Live docs** at https://adk.dev/ (snapshot dated 2026-05-27).
2. **Real samples** at `/home/carloscabral/study/adk-samples/python/agents/` — if a sample does it, that's the pattern.
3. **Framework source** at `/home/carloscabral/study/adk-python/` — only when 1 and 2 are unclear.

Do **not** invent APIs. If you're not sure whether `runner.run_async()` returns events with `.content.parts` or `.parts`, check a real sample.

---

## Output checklist before you return

For every module folder you author:
- [ ] `00_Overview.md` exists with frontmatter
- [ ] At least one numbered concept page exists
- [ ] `XX_DissectingSample.md` exists (anchored to a real sample)
- [ ] `XX_InProduction.md` exists with consolidated callouts
- [ ] `XX_KnowledgeCheck.yml` exists with 5-7 questions
- [ ] `XX_MiniDrill.yml` exists with verification rubric
- [ ] `AGENTS.md` exists with module-local tutor notes
- [ ] Every concept page has frontmatter + breadcrumbs (top AND bottom)
- [ ] Every concept page has at least one tutor hook (`> ❓` or `> 🛠`)
- [ ] At least one ASCII figure in `_figures/` is referenced from a page
- [ ] In-Production callouts appear inline where appropriate

Return a concise summary (~150 words) listing what you authored and any caveats (e.g., "I left module XX's exercise solution out of `Solutions/` because it's not a gate-keeper per rule 13").
