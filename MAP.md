# 🗺 MAP — ADK Python Practical Course Master Map

**How to read this:** boxes are modules grouped by track (left→right reading order), `━━━ Mn ━━━` bars are cross-concept milestone drills you tackle after the modules above them, and 🐍 / ☁️ / 📡 detours at the bottom are optional sidebars you pull in only when a page suggests one or you hit a gap. **Checkboxes here are presentational** — your actual progress lives in [PROGRESS.md](PROGRESS.md). Hover any module name in [Contents.md](Contents.md) for the page-by-page TOC.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  ADK Python — Practical Course :: Master Map                  ║
║                       (ADK 2.0 GA · snapshot 2026-05-27)                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝


  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🗺  FOUNDATION TRACK                                                       │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 00  Setup ............... install ADK 2.0, key, repo tour            │
  │   [ ] 01  Foundations ......... mental model: agent · runner · session     │
  │   [ ] 1A  App & Runner Arch ... App container · on_startup/shutdown ·      │
  │                                  app:* state · cache/compaction/resume wires│
  │   [ ] 02  First Agent ......... LlmAgent + Runner + InMemorySession by hand│
  │   [ ] 2A  Agent Config (YAML) . declarative agents · adk create · YAML ↔ Py│
  │   [ ] 03  Tools ............... FunctionTool · AgentTool · built-ins ·     │
  │                                  Computer Use · tool limitations           │
  │   [ ] 3A  Project Structure ... file layout · adk web/run expectations ·   │
  │                                  deploy expectations · shared/ · eval/     │
  │   [ ] 04  Sessions & State .... state prefixes · events · deltas ·         │
  │                                  context caching · compaction · rewind     │
  │   [ ] 04A Artifacts & Heavy Data ☁️  ArtifactService · multimodal Parts ·  │
  │                                  GCS · signed URLs · video understanding   │
  │   [ ] 4B  HITL & Resume/Cancel  request_confirmation · Runner.resume() ·   │
  │                                  Ambient Agents · client-driven approvals  │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
            ━━━━━━━━━━━━━ 🏁  M1: Conversation Server  ━━━━━━━━━━━━━
                          (CLI loop + 2 FunctionTools + state)
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🧩  COMPOSITION TRACK                                                      │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 05  Multi-Agent ......... sub_agents, transfer, AgentTool            │
  │   [ ] 06  Graph Workflows ..... ADK 2.0 graph (+ legacy Seq/Par/Loop)      │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
            ━━━━━━━━━━━━━━ 🏁  M2: Workflow Editor  ━━━━━━━━━━━━━━━
                       (research pipeline, legacy vs graph)
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🔌  INTEGRATION TRACK                                                      │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 07  Callbacks ........... before/after_model · tool · agent · error  │
  │   [ ] 08  MCP ................. MCPToolset · FastMCP · serve MCP           │
  │   [ ] 09  Skills .............. Skill · Script · Frontmatter · Toolset     │
  │   [ ] 10  A2A ................. AgentCard · to_a2a() · RemoteA2aAgent      │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
            ━━━━━━━━━━━━ 🏁  M3: Federated Travel Planner  ━━━━━━━━━
                  (sub_agents + MCP-out + A2A-in + Skills)
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  ☁️  DATA & GCP TRACK    (GCP-first; substrate for Memory)                  │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 10A  Embeddings & Vector Search .. Vertex AI text-embedding · VS     │
  │   [ ] 10B  RAG Pipeline ................ ingest→chunk→embed→retrieve →     │
  │                                           augment, Vertex AI RAG Engine    │
  │   [ ] 10C  BigQuery for Agents ......... BQ as data source, BQ VECTOR_SEARCH│
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  ⚙️  RUNTIME TRACK                                                          │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 11  Memory .............. Session vs State vs Memory; Memory Bank    │
  │   [ ] 12  Code Execution ...... UnsafeLocal · BuiltIn · Container · Sandbox│
  │   [ ] 13  Plugins ............. logging · reflect-and-retry · ctx filter   │
  │   [ ] 14  Evaluation .......... EvalSet · LlmAsJudge · Trajectory · Rubric │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
            ━━━━━━━━━━━━━━ 🏁  M4: Auditor With Evals  ━━━━━━━━━━━━━━
                 (multi-agent + plugin + callback + 5 evals)
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🚀  PRODUCTION TRACK                                                       │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 15  Observability ....... structured logging · OTel traces & metrics │
  │   [ ] 16  Production & Security  guardrails · auth · secrets · injection · │
  │                                  agent-identity dichotomy · Gemini-as-judge│
  │   [ ] 17  Advanced Models ..... Gemini · Claude · Gemma · LiteLlm ·        │
  │                                  Planners (BuiltIn · PlanReAct)            │
  │   [ ] 18  Streaming & Live 🎙 .. bidi voice/video · SSE · LongRunning tools │
  │   [ ] 19  Internals ........... a guided source-read of adk-python/        │
  │   [ ] 20  Framework Comparison  ADK vs LangGraph · CrewAI · AutoGen · OAI  │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🌐  DEPLOYMENT & INTEGRATION TRACK                                         │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   [ ] 21  ADK API Surface ......... adk api_server · HTTP/SSE/WS endpoints │
  │                                     · session & event REST shapes          │
  │   [ ] 22  Deployment Models ☁️ .... Cloud Run · Agent Engine (Runtime) ·   │
  │                                     GKE · scaling · sessions · cold start  │
  │   [ ] 23  Frontend Integration .... custom SPA · A2UI client · user_id &   │
  │                                     session lifecycle · SSE/WS from client │
  │   [ ] 24  Channel Integrations .... Slack · Google Chat · Discord ·        │
  │                                     webhook → Runner adapter pattern       │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼

  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🏆  CAPSTONE                                                               │
  ├────────────────────────────────────────────────────────────────────────────┤
  │   [ ] 99  ━━━ 🏁 M5: Production-Grade Agent ━━━                            │
  │            Track A: Research Assistant  ·  Track B: Code Reviewer          │
  │            Track C: Personal Knowledge Hub                                 │
  │            (≥3 agents · ≥2 tools · persistent state · memory · 5 evals     │
  │             · plugin · callbacks · A2A · OTel · README)                    │
  └────────────────────────────────────────────────────────────────────────────┘


  ┌────────────────────────────────────────────────────────────────────────────┐
  │  🧭  DETOURS (any-time, optional)                                           │
  ├────────────────────────────────────────────────────────────────────────────┤
  │                                                                            │
  │   🐍 Python          ☁️ GCP / 📡 Protocol     📦 Framework     🌐 Deploy    │
  │   ─────────          ─────────────────       ────────────     ─────────    │
  │   PY_dataclasses     GeminiPayload           FastMCP          Cloud_Run    │
  │   PY_pydantic        WebSockets              a2UI             AgentEngine  │
  │   PY_async           AudioEncoding           VisualBuilder    FastAPI_for_ADK│
  │   PY_typing          AudioQuantization                        SignedUrls_GCS│
  │   PY_contextvars     ProtocolBuffers                          Slack_Bots   │
  │   PY_generators      gRPC                                     GoogleChat_Apps│
  │   PY_testing 🧪      OpenTelemetry                                          │
  │   PY_logging         PromptInjection ⚠️                                     │
  │   PY_packaging       Grounding                                              │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘
```

---

## Legend

| Marker | Meaning |
|---|---|
| `[ ]` / `[x]` | Module checkbox (presentational; real progress in [PROGRESS.md](PROGRESS.md)) |
| `🏁 Mn` | Milestone drill — cross-concept, gates the next track |
| 🗺 | Navigation / structural |
| 🧩 | Composition |
| 🔌 | Integration / protocol |
| ☁️ | GCP-specific |
| ⚙️ | Runtime / operational |
| 🚀 | Production / in-production |
| 🌐 | Deployment & integration (API, frontend, channels) |
| 🎙 | Live / streaming |
| 🧭 | Detour — optional sidebar |
| 🐍 | Python deep-dive detour |
| 🧪 | Testing / evaluation |
| ⚠️ | Gotcha / security |

## Where to start

If this is your first session, your cursor is at `00_Setup/00_Overview`. Open Claude Code, point it at this repo, and say: *"Read AGENTS.md and pick up where I left off."* See [README.md](README.md#how-to-use-this-course-the-ai-tutor-model) for the runtime contract.
