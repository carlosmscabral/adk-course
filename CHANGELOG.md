# 📜 CHANGELOG

All notable changes to this course will be documented here. Follows a loose [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) shape; one bump per phase + one bump per absorbed ADK release.

---

## [0.3.0] - 2026-05-27

Completeness pass after a docs-and-samples audit. Three new modules, four module expansions, one new detour, and a sample-citation rewiring across the existing modules.

### Added (new modules)
- **`Notes/1A_AppAndRunner/`** — The 2.0 `App` class as container, `on_startup`/`on_shutdown` hooks, `app:` state boundary, and the wiring of `resumability_config` / `context_cache_config` / `context_compaction_config`. Without this, several of the 2.0 features below can't be taught coherently. Slot between modules 01 and 02.
- **`Notes/2A_AgentConfig/`** — Declarative agent definition via `root_agent.yaml`, `adk create`, supported tool/sub-agent reference forms, the Python-vs-YAML tradeoffs, what's currently Python-only. Slot between modules 02 and 03.
- **`Notes/3A_ProjectStructure/`** ⭐ — User-requested. The pragmatic file/folder layout story: single-file → split agent/tools/prompts → directory-per-concept as the project grows. Explicit treatment of what `adk web`/`adk run`/`adk api_server` expect (the `root_agent` discovery rule, `__init__.py` gotchas) and what Cloud Run and Agent Engine deployments expect. Shared utilities pattern, eval/tests layout. Slot between modules 03 and 04. Light-touch callouts wired into 05/14/22 so the convention is reachable from natural pressure points.
- **`Notes/4B_HumanInTheLoop/`** ⭐ — Dedicated HITL module (user-requested). Covers `Context.request_confirmation()`, `EventActions.requested_tool_confirmations`, `Runner.resume()`/`cancel()`, `LongRunningFunctionTool` as a HITL primitive, `RequestInput` pauses in graphs, **Ambient Agents** (Pub/Sub / GCS / Scheduler triggered), driving the approval loop from a frontend or external consumer (Slack, web, mobile), and durable-execution integrations (Temporal, Dapr) for when ADK's built-in resume isn't enough. Slot after 04A.

### Added (module expansions)
- **Module 04 Sessions & State** — +4 pages: `05_ContextCaching`, `06_ContextCompaction`, `07_SessionRewind`, `08_SessionMigrate` (all ADK 2.0 primitives; `09–12` shifted from `05–08`).
- **Module 03 Tools** — +2 pages: `05_ComputerUse` (preview toolset, `BaseComputer`, Playwright/Chromium), `06_ToolLimitations` (single-instance constraints, e.g., Vertex AI RAG Engine tool can only be used alone). Trailing files shifted.
- **Module 16 Production & Security** — +2 pages: `06_AgentIdentityVsUser` (the under-taught distinction between agent identity and controlling-user identity for tool authorization), `07_GeminiAsJudgePlugin` (the safety plugin from `safety-plugins` sample).
- **Module 17 Advanced Models** — +2 pages: `05_PlannersBuiltIn` (`BuiltInPlanner` + `ThinkingConfig`), `06_PlanReActPlanner` (used by ~7 samples but taught nowhere previously).
- **Module 22 Deployment Models** — +1 page: `03A_GKE` (the third path alongside Cloud Run and Agent Engine).

### Added (module deep-dives — user-requested)
- **Module 07 Callbacks** — +3 pages: `05_CallbackContextAnatomy` (what's in `CallbackContext`, what isn't, common gotchas), `06_CallbackRecipeCookbook` (real-life recipes: caching, rate limiting, redaction, source citation, latency budgets, conditional tool execution), `07_CallbacksVsPlugins` (decision rubric).
- **Module 21 ADK API Surface** — +3 pages: `01A_AdkRunUnderTheHood`, `01B_AdkWebUnderTheHood`, `01C_FullCliFamily` (the full `adk` CLI map covering `eval`, `create`, `migrate`, `deploy`). User asked for an under-the-hood treatment of the CLI; the API-surface module is the right home.
- **Module 3A Project Structure** — +1 page: `07A_ConfigAndEnvVars` (user-requested). Centralises env-var coverage that was scattered across `00_Setup`, `Detours/Cloud_Run`, `22/08`, and per-provider 17-pages: full table of ADK-respected env vars, `pydantic-settings` one-class pattern, `.env.dev`/`.env.prod` separation, anti-patterns, and the "validate in `on_startup`, fail loud" rule. Slotted between 07 and 08; trailing files unchanged.

### Added (detour)
- **`Notes/Detours/Grounding.md`** — Google Search Grounding vs Enterprise Search vs Agentic RAG (distinction from module 10A/10B is real and worth a page).

### Changed (sample citations)
- Wove the following samples into existing modules as Dissecting Sample or InProduction citations: `ambient-expense-agent` (4B canonical), `deep-search` (23 frontend, 06 graph reflect-loop), `memory-bank` (11 canonical), `safety-plugins` (13, 16), `agent-observability-bq` (10C, 15), `adk-ae-oauth` (16, 22), `multiformat-hybrid-rag` (10B secondary), `bidi-demo` (18 canonical), `realtime-conversational-agent` (18, 23), `workflows-HITL_concierge` (4B, 06), `camel` (16 prompt-injection).

### Status
- `MAP.md` updated: 1A, 2A, 4B slotted in the Foundation block; module 03/04/16/17/22 lines expanded; `Grounding` added to detour grid.
- `Contents.md` updated: every new page listed with the trailing-files shifted.
- The 0.2.0 additions (`04A_ArtifactsHeavyData`, deployment track 21-24, six deployment detours, REPL→script style flip) remain in flight; this 0.3.0 entry stacks on top.

### Why
- User asked for completeness against ADK 2.0 docs + samples. A two-agent audit (docs at <https://adk.dev/> and the 73 samples under `adk-samples/python/agents/`) surfaced the gaps above. HITL was explicitly requested as a dedicated session; the rest are the audit's must-add column. Lower-priority items (Express Mode, Apigee, more telemetry sinks) were deferred to a future minor.

---

## [0.2.0] - 2026-05-27

Scope expansion after Phase B authoring. Three structural changes:

### Changed
- **Style: REPL → runnable scripts on ADK pages.** Rule #2 in `_AUTHORING_AGENT_BRIEF.md` flipped. ADK is async-only and session-bound — `>>>` blocks don't actually run. Switched to `# Work/NN_name.py — run with: uv run python Work/NN_name.py` script style on the ~14 ADK runtime pages. Pure-Python detours (`PY_async`, `PY_typing`, etc.) and pure-data manipulation pages keep REPL — that's how Python is actually taught.

### Added
- **New module `04A_ArtifactsHeavyData/`** ☁️ — `ArtifactService`, `GcsArtifactService`, multimodal Parts, video understanding, signed URLs, heavy-file handoff between sub-agents. Slot after Sessions/State because artifacts ride the same Event substrate. GCP-first.
- **New track: Deployment & Integration** 🌐 — four modules between Framework Comparison (20) and the Capstone (99):
  - `21_AdkApiSurface/` — `adk api_server`, HTTP/SSE/WS endpoints, REST shapes, wrapping in FastAPI.
  - `22_DeploymentModels/` — Cloud Run vs Agent Engine (Runtime); session persistence, scaling, cold start, auth, observability differences.
  - `23_FrontendIntegration/` — custom SPA, A2UI client, user_id/session lifecycle from the client, SSE/WS from the browser, auth context propagation.
  - `24_ChannelIntegrations/` — webhook → Runner adapter pattern, Slack bot, Google Chat app, Discord, long-running responses on chat platforms.
- **6 new detours**: `Cloud_Run`, `AgentEngine`, `FastAPI_for_ADK`, `SignedUrls_GCS`, `Slack_Bots`, `GoogleChat_Apps`.
- `MAP.md` updated: new track added, detour grid extended with a 🌐 Deploy column, legend gained 🌐.
- `Contents.md` updated: 04A inserted after 04; new track + detours listed.

### Why
- The user asked whether artifacts/multimedia/heavy-data were covered (they weren't) and whether the ADK API/frontend/Cloud-Run-vs-Agent-Engine/Slack/Google-Chat story had a home (it didn't). Both gaps were real and structural — patching them with extra `InProduction` blurbs would have buried them. New module + new track is the honest fix.

---

## [0.1.0] - 2026-05-27

Initial course scaffold. ADK Python 2.0 GA targeted. Docs snapshot at 2026-05-27.

### Added
- Repo-root files: [README.md](README.md), [AGENTS.md](AGENTS.md) (the AI-tutor operating manual), [MAP.md](MAP.md), [Contents.md](Contents.md), [PROGRESS.md](PROGRESS.md) (cursor at `00_Setup/00_Overview`), [student_profile.md](student_profile.md) (empty template).
- Top-level directories: `Notes/` (with empty module folders 00–20, 99, `Detours/`, `Updates/`, `_TEMPLATE_MODULE/`), `Drills/`, `Solutions/`, `Work/`, `Reference/CheatSheets/`.
- Docs snapshot: [Reference/docs_snapshot.md](Reference/docs_snapshot.md) — pins ADK 2.0 GA, fetch date 2026-05-27, source <https://adk.dev/>, refresh cadence 4 weeks.
- ADK 2.0 release-note absorption: [Notes/Updates/2026-05_adk-2.0.md](Notes/Updates/2026-05_adk-2.0.md) — graph workflows, collaborative agents, Visual Builder, Ambient Agents, Resume/Cancel, Agent Config, Skills, Context caching/compression, Session rewind/migrate. Legacy Sequential/Parallel/Loop templates still supported.
- Authoring recipe: [Notes/_AUTHORING.md](Notes/_AUTHORING.md) — how to add a module, detour, and release-update entry.
- Module template: [Notes/_TEMPLATE_MODULE/](Notes/_TEMPLATE_MODULE/) — copyable skeleton (`00_Overview`, `01_FirstConcept`, `05_DissectingSample`, `06_InProduction`, `07_KnowledgeCheck.yml`, `08_MiniDrill.yml`, `AGENTS.md`, `_figures/`).
- Cheat sheets in [Reference/CheatSheets/](Reference/CheatSheets/): `llmagent_signature.md`, `runner_session_lifecycle.md`, `state_prefixes.md`, `event_actions.md`, `tool_authoring.md`, `callback_signatures.md`, `a2a_mcp_quickref.md`.
- Student sandbox starter: [Work/_template_run.py](Work/_template_run.py) — runnable `InMemorySessionService` + `LlmAgent` + `runner.run_async(...)` loop against Gemini 2.5 Flash.

### Status
- **Phase 0 — Scaffolding & format MVP**: in progress. Repo-root + cheat sheets + template + Updates entry shipped. Modules `00_Setup/` and `01_Foundations/` still to author before the Phase 0 dogfood gate.
- All module folders exist as empty directories so the navigation links from [Contents.md](Contents.md) and [MAP.md](MAP.md) do not 404; content lands in subsequent phases.
