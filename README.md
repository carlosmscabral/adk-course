# ADK Python — The Practical Course

A Practical-Python-style, MD-based course that takes a working Python developer from zero to deep fluency in **Google ADK Python 2.0 GA** (verified 2026-05-27 against [adk.dev](https://adk.dev/)). Engine-first: you wire up `LlmAgent`, `Runner`, and `InMemorySessionService` by hand before you trust any abstraction. Anchored to real samples in the official [adk-samples](https://github.com/google/adk-samples) repo (clone it alongside this one) so the patterns you learn are the ones you will meet in production.

The course is the artifact. It is written for a student-of-one but structured so any AI coding assistant can teach it adaptively — see [AGENTS.md](AGENTS.md), the operating manual.

---

## 🎯 Audience

A working Python developer (intermediate or better) who wants to deeply own a single agent framework rather than collect surface-level demos. Not a beginner's intro to Python. Not a generic LLM survey. The student already writes typed Python, knows `async`/`await` well enough to read it, and has shipped at least one Python app.

If you have never written a `FunctionTool` or do not know what a `Session` is in ADK — that is fine. That is the floor. The course starts at the engine and walks up.

## 🔧 Prerequisites

- **Python 3.11+** (3.12 or 3.13 fine; 3.10 will hit ADK 2.0 type-system features).
- **Google AI Studio API key** (free tier, for Gemini direct) for the Foundation, Composition, and Integration tracks.
- **A billable Google Cloud project** with Vertex AI + BigQuery APIs enabled for the Data & GCP track (10A, 10B, 10C). The public datasets used (`bigquery-public-data.london_bicycles`) keep cost near zero, but you need billing turned on.
- **A working microphone** for the Live/streaming module (18). If no mic, that module's voice mini-drill is skipped — the SSE drill stands in.
- **`uv` or `poetry`** for env management (the course uses `uv` in examples; either is fine).
- **`gcloud` CLI** authenticated against your project (`gcloud auth application-default login`) for the GCP track.

You will install `google-adk` (the ADK Python package — 2.0 GA) in Module 00.

## 🚀 Getting started (5 minutes)

```bash
# 1. Clone this course
git clone https://github.com/carlosmscabral/adk-course.git
cd adk-course

# 2. (Recommended) Clone the official ADK samples alongside it
#    Several modules dissect real samples line-by-line.
cd ..
git clone https://github.com/google/adk-samples.git
cd adk-course
```

**Pick an AI coding assistant.** Any tool that can read your filesystem and run shell commands works. Recommended, in order:

| Tool | Why | Install |
|---|---|---|
| **Claude Code** | What the course was authored against; richest support for the `AGENTS.md` operating contract. | [claude.com/claude-code](https://claude.com/claude-code) |
| **Cursor** | IDE-integrated; same Claude/GPT models under the hood. | [cursor.com](https://cursor.com) |
| **Antigravity** | Google's AI coding tool; native fit for Gemini-heavy work. | [antigravity.google](https://antigravity.google) |
| **GitHub Copilot Chat (Agent mode)** | If you already use Copilot. | [github.com/features/copilot](https://github.com/features/copilot) |

**Open the cloned `adk-course/` directory** in your assistant of choice, then send this prompt verbatim:

> **Read AGENTS.md and pick up where I left off.**

That is the entire interface. The assistant will:

1. Load [`AGENTS.md`](AGENTS.md) (the operating manual), [`MAP.md`](MAP.md), [`PROGRESS.md`](PROGRESS.md), and [`student_profile.md`](student_profile.md).
2. See your cursor is at `00_Setup/00_Overview` (first session) or wherever you left off.
3. Open that page, perform the lesson one concept at a time, pause for your input, run the embedded knowledge checks and mini-drill, and update `PROGRESS.md` + `student_profile.md` at session end.

**Subsequent sessions:** the same prompt. The assistant reads `PROGRESS.md`, sees what you completed last time, and resumes.

**If you fork the repo** (recommended for solo students — your progress and notes live in your own copy), update the clone URL above accordingly and commit your `PROGRESS.md` + `student_profile.md` writebacks as you go. They are the durable record of your journey through the course.

> 💡 **First-session tip.** Don't pre-read pages. The tutor experience is designed around discovery — you'll get more out of "the tutor asks me, then I find out" than "I read ahead and confirm." Open the assistant cold and let it drive.

## 🤖 How to use this course (the AI-tutor model)

This is not a book you read alone. Every page is **a script for an AI coding assistant to perform**, not an essay to skim. You open a session with Claude Code (or Antigravity, or any AI assistant that can read your filesystem), and the assistant:

1. Reads [AGENTS.md](AGENTS.md), [MAP.md](MAP.md), [PROGRESS.md](PROGRESS.md), and [student_profile.md](student_profile.md).
2. Identifies your cursor (the next page you have not completed).
3. Performs the lesson — one concept at a time, with REPL pauses.
4. Asks the knowledge-check questions one at a time from `07_KnowledgeCheck.yml`.
5. Watches your code in [`Work/`](Work/), grades against the `08_MiniDrill.yml` rubric.
6. Updates [`PROGRESS.md`](PROGRESS.md) and [`student_profile.md`](student_profile.md) at session end.

**Start every session with**: "Read AGENTS.md and pick up where I left off." The assistant takes it from there.

If you want to read the pages directly without a tutor, you can — the prose is self-contained — but you will miss the adaptive pacing, the inline grading, and the detour suggestions calibrated to your gaps. The tutor contract is what makes the course adapt.

## 🗺 Repo tour

```
adk-course/
├── README.md                  ← you are here
├── AGENTS.md                  ← 🤖 the operating manual for the tutor
├── MAP.md                     ← the visual master map
├── Contents.md                ← detailed TOC
├── PROGRESS.md                ← your cursor (which page next)
├── student_profile.md         ← your adaptive memory (the tutor updates this)
├── CHANGELOG.md               ← course-version log
├── Notes/                     ← the modules (numbered)
│   ├── 00_Setup/ … 99_Capstone/
│   ├── Detours/               ← optional sidebars (PY_*, GeminiPayload, FastMCP …)
│   ├── Updates/               ← release-note absorptions, dated
│   ├── _AUTHORING.md          ← how to add a module or detour
│   └── _TEMPLATE_MODULE/      ← copyable module skeleton
├── Drills/                    ← cross-concept milestones (M1–M5)
├── Solutions/                 ← SPARSE — only gate-keeper solutions
├── Work/                      ← your sandbox (gitignored except _template_run.py)
└── Reference/
    ├── CheatSheets/           ← one-pagers per API surface
    └── docs_snapshot.md       ← what version of docs we track
```

Read [MAP.md](MAP.md) to see how the modules connect. Read [Contents.md](Contents.md) for the flat page-by-page TOC.

## 🏁 What you will be able to do

After completing the course, you can:

1. **Build a multi-agent ADK app from a blank file** — `LlmAgent`, sub-agents, tools, sessions, memory, callbacks, evals — without referencing samples.
2. **Read and explain any sample** in [`adk-samples/python/agents/`](https://github.com/google/adk-samples/tree/main/python/agents), including the deep ones (`travel-concierge`, `data-science`, `deep-search`, `llm-auditor`).
3. **Pick the right composition primitive** — `LlmAgent`-with-tools vs `sub_agents` vs `AgentTool` vs `WorkflowAgent` (graph) — and justify it.
4. **Federate agents** — expose an ADK agent via A2A (`to_a2a()`), consume external A2A agents (`RemoteA2aAgent`), reach OUT for tools via MCP (`MCPToolset`), and serve your own MCP server with FastMCP.
5. **Stand up GCP-native retrieval** — Vertex AI embeddings, Vector Search, RAG Engine, BigQuery analytical agents, BigQuery vector search.
6. **Ship to production** — callbacks-as-policy, plugins for cross-cutting concerns, evals as CI, OpenTelemetry tracing, secrets handling, sandboxed code execution, prompt-injection defense, ADK vs LangGraph/CrewAI/AutoGen/OpenAI-SDK framework choice.

## 📅 The five phases

The course ships in five phases, each end-to-end usable. Earlier phases prove the format works before later ones get authored.

| Phase | Tracks | Modules | Outcome |
|---|---|---|---|
| **Phase 0** | Scaffolding | 00 Setup, 01 Foundations | Format & AI-tutor contract validated |
| **Phase 1** | Foundation | 02 First Agent, 03 Tools, 04 Sessions & State → **M1** | Build a tool-using stateful single agent |
| **Phase 2** | Composition | 05 Multi-Agent, 06 Graph Workflows → **M2** | Fluent in multi-agent + graph workflows |
| **Phase 3** | Integration | 07 Callbacks, 08 MCP, 09 Skills, 10 A2A → **M3** | Federate agents across MCP and A2A |
| **Phase 3.5** | Data & GCP | 10A Embeddings, 10B RAG, 10C BigQuery | GCP-native retrieval substrate |
| **Phase 4** | Runtime | 11 Memory, 12 Code Exec, 13 Plugins, 14 Eval → **M4** | Run, observe, evaluate agents |
| **Phase 5** | Production | 15–20 + **M5 Capstone** | Production-grade end-to-end agent |

See [MAP.md](MAP.md) for the visual.

---

## License & lineage

Licensed under the [Apache License 2.0](LICENSE) — aligns with [`adk-python`](https://github.com/google/adk-python) and [`adk-samples`](https://github.com/google/adk-samples). Pedagogical shape (engine-first, breadcrumb navigation, sparse solutions, spiral curriculum) is inspired by [Practical Python Programming](https://github.com/dabeaz-course/practical-python) by David Beazley. This course covers Google ADK Python 2.0 GA against the docs snapshot at [`Reference/docs_snapshot.md`](Reference/docs_snapshot.md).
