# 📦 Docs snapshot

**This course is built against a pinned snapshot of the ADK docs so the curriculum does not silently drift from upstream reality.**

| Field | Value |
|---|---|
| Framework | Google ADK Python |
| Version targeted | **2.0 GA** |
| Snapshot date | **2026-05-27** |
| Source of truth | <https://adk.dev/> |
| Companion release note | [Notes/Updates/2026-05_adk-2.0.md](../Notes/Updates/2026-05_adk-2.0.md) |
| Refresh cadence | **every 4 weeks** |

---

## Section index (the major doc sections we anchor to)

The course's modules map to these doc sections. Page references in `05_DissectingSample.md` files and `> 🚀 In Production` callouts cite live samples; behavioral claims cite this snapshot.

| Doc section | Course module(s) |
|---|---|
| Get Started / Quickstart | [00 Setup](../Notes/00_Setup/) |
| Foundations / Mental Model | [01 Foundations](../Notes/01_Foundations/) |
| Agents — `LlmAgent` | [02 First Agent](../Notes/02_FirstAgent/) |
| Agents — Workflow agents (Sequential/Parallel/Loop) | [06 Graph Workflows](../Notes/06_GraphWorkflows/) (legacy section) |
| Agents — Graph workflows (2.0) | [06 Graph Workflows](../Notes/06_GraphWorkflows/) |
| Agents — Collaborative agents (2.0) | [05 Multi-Agent](../Notes/05_MultiAgent/) |
| Agents — Multi-agent (`sub_agents`, transfer) | [05 Multi-Agent](../Notes/05_MultiAgent/) |
| Agents — `BaseAgent`, custom subclasses | [19 Internals](../Notes/19_Internals/) |
| Tools — `FunctionTool`, docstring schema | [03 Tools](../Notes/03_Tools/) |
| Tools — `AgentTool`, built-in tools | [03 Tools](../Notes/03_Tools/), [05 Multi-Agent](../Notes/05_MultiAgent/) |
| Tools — `LongRunningFunctionTool` | [03 Tools](../Notes/03_Tools/), [18 Streaming & Live](../Notes/18_StreamingLive/) |
| Tools — `McpToolset` | [08 MCP](../Notes/08_MCP/) |
| Tools — `SkillToolset` | [09 Skills](../Notes/09_Skills/) |
| Runtime — `Runner`, `InMemoryRunner` | [02 First Agent](../Notes/02_FirstAgent/) |
| Runtime — Resume / Cancel (2.0) | [02 First Agent](../Notes/02_FirstAgent/), [06 Graph Workflows](../Notes/06_GraphWorkflows/) |
| Sessions — `SessionService` implementations | [04 Sessions & State](../Notes/04_SessionsState/) |
| Sessions — rewind / migrate (2.0) | [04 Sessions & State](../Notes/04_SessionsState/) |
| State — prefixes, deltas, templating | [04 Sessions & State](../Notes/04_SessionsState/) |
| Events — `actions`, `state_delta`, `artifact_delta` | [04 Sessions & State](../Notes/04_SessionsState/) |
| Memory — Memory Bank, RAG memory | [11 Memory](../Notes/11_Memory/) |
| Callbacks — model / tool / agent / error | [07 Callbacks](../Notes/07_Callbacks/) |
| Plugins — logging, retry, context filter, BQ analytics | [13 Plugins](../Notes/13_Plugins/) |
| Skills — `Skill`, `Script`, `Frontmatter`, registry | [09 Skills](../Notes/09_Skills/) |
| Agent Config (2.0) | [02 First Agent](../Notes/02_FirstAgent/) |
| A2A — `AgentCard`, `to_a2a`, `RemoteA2aAgent` | [10 A2A](../Notes/10_A2A/) |
| Models — Gemini, Claude, Gemma, LiteLlm, registry | [17 Advanced Models](../Notes/17_AdvancedModels/) |
| Live API — bidi voice/video | [18 Streaming & Live](../Notes/18_StreamingLive/) |
| Code execution — sandboxed executors | [12 Code Execution](../Notes/12_CodeExecution/) |
| Evaluation — `EvalCase`, `EvalSet`, judges, trajectory | [14 Evaluation](../Notes/14_Evaluation/) |
| Vertex AI integration (embeddings, RAG Engine, Memory Bank) | [10A](../Notes/10A_EmbeddingsVectorSearch/) · [10B](../Notes/10B_RAGPipeline/) · [11](../Notes/11_Memory/) |
| BigQuery integration (data source, vector search, analytics plugin) | [10C BigQuery for Agents](../Notes/10C_BigQueryAgents/) |
| CLI — `adk run`, `adk eval`, `adk web`, `adk create`, `adk deploy` | [00 Setup](../Notes/00_Setup/), [14 Evaluation](../Notes/14_Evaluation/) |
| Observability — built-in telemetry, OTel | [15 Observability](../Notes/15_Observability/) |
| Auth & credentials — `AuthHandler`, `CredentialManager` | [16 Production & Security](../Notes/16_ProductionSecurity/) |
| Visual Builder (2.0) | [Detours/VisualBuilder.md](../Notes/Detours/VisualBuilder.md) |
| Ambient Agents (2.0) | [06 Graph Workflows](../Notes/06_GraphWorkflows/) |

---

## Refresh cadence

Every 4 weeks, an assistant-driven task:

1. Fetches `https://adk.dev/` landing page + release-notes feed.
2. Diffs the section index above against current docs.
3. Adds a dated entry under [Notes/Updates/YYYY-MM_release.md](../Notes/Updates/).
4. Bumps this file's snapshot date and adds new section rows if applicable.
5. Banners affected module overviews with `> ⚠ Updated YYYY-MM`.
6. Adds a `### Updated` entry to [../CHANGELOG.md](../CHANGELOG.md).

See [../Notes/_AUTHORING.md](../Notes/_AUTHORING.md) § 3 for the full release-absorption recipe.

---

## Reference repos

Read-only context the course points at:

| Repo | Purpose |
|---|---|
| `/home/carloscabral/study/adk-python/` | Framework source — for Module 19 (Internals) and surgical detours only. |
| `/home/carloscabral/study/adk-samples/python/agents/` | 60+ canonical samples — every module dissects 1–2 of these. |
| `/home/carloscabral/study/practical-python/Notes/` | Pedagogical-style reference (the file shape this course mimics). |

If a behavioral claim in the course disagrees with one of these repos, the repo wins — file an issue to update the page.

---

[← Reference index](../Reference/) · [📍 Progress](../PROGRESS.md) · [📜 Changelog](../CHANGELOG.md)
