# 📚 Contents — ADK Python Practical Course

Full flat table of contents. Every module page, every detour, every cheat sheet, every drill, in reading order. Module folders use the canonical skeleton (Overview → concept pages → DissectingSample → InProduction → KnowledgeCheck → MiniDrill); the exact numbering shifts per module to fit how many concept pages it carries.

Modules whose ID has a letter suffix (`1A`, `2A`, `3A`, `4B`, `04A`, `10A`, `10B`, `10C`) are **side modules** — companion / spillover material attached to a numbered main-line module. They sit in the same track as their parent and are taught in reading order, but you can detour around them on a first pass if you are sprinting toward a milestone.

[Home](README.md) · [🗺 Map](MAP.md) · [🤖 Tutor manual](AGENTS.md) · [📍 Progress](PROGRESS.md) · [📜 Changelog](CHANGELOG.md)

---

## How this is organised

Each module is a folder under `Notes/NN_Topic/` with the canonical skeleton:

```
00_Overview.md            Goals, prereqs, time, sample anchor
01_…NN_…                  Numbered concept pages, one idea each
NN_DissectingSample.md    Real-sample read-through (anchor in adk-samples/)
NN_InProduction.md        Consolidated real-world callouts for this module
NN_KnowledgeCheck.yml     5–7 questions, tutor asks one at a time
NN_MiniDrill.yml          Exercise + verification rubric
AGENTS.md                 Module-local teaching notes for the tutor
_figures/                 ASCII diagrams used by this module
```

The four trailing files (`DissectingSample`, `InProduction`, `KnowledgeCheck`, `MiniDrill`) always sit at the end in that order — their numeric prefix shifts up if a module has more concept pages.

Tracks below follow [MAP.md](MAP.md) exactly.

---

## Foundation Track 🗺

### 0. [Setup](Notes/00_Setup/)
- [Setup — install ADK, run your first agent](Notes/00_Setup/00_Overview.md)
- [Installing google-adk and configuring your API key](Notes/00_Setup/01_InstallingADK.md)
- [Hello, fun-facts — your first agent conversation](Notes/00_Setup/02_HelloFunFacts.md)
- [Three repos you will live in](Notes/00_Setup/03_RepoTour.md)
- [Reading fun-facts/agent.py line by line](Notes/00_Setup/04_DissectingSample.md)
- [Setup hygiene for real projects](Notes/00_Setup/05_InProduction.md)
- [Knowledge Check](Notes/00_Setup/06_KnowledgeCheck.yml)
- [Mini-Drill](Notes/00_Setup/07_MiniDrill.yml)

### 1. [Foundations](Notes/01_Foundations/)
- [Foundations — the mental model](Notes/01_Foundations/00_Overview.md)
- [What is an agent? The loop, drawn.](Notes/01_Foundations/01_WhatIsAnAgent.md)
- [Runner, Session, Event — the three runtime primitives](Notes/01_Foundations/02_RunnerSessionEvent.md)
- [Tools are just Python functions](Notes/01_Foundations/03_ToolsArePythonFunctions.md)
- [State lives on the session](Notes/01_Foundations/04_StateLivesOnSession.md)
- [Re-reading fun-facts/agent.py with arrows](Notes/01_Foundations/05_DissectingSample.md)
- [Foundations — production checklist](Notes/01_Foundations/06_InProduction.md)
- [Knowledge Check](Notes/01_Foundations/07_KnowledgeCheck.yml)
- [Mini-Drill](Notes/01_Foundations/08_MiniDrill.yml)

### 1A. [App & Runner Architecture](Notes/1A_AppAndRunner/) — *side module*
- [App & Runner Architecture — the 2.0 container that owns everything cross-cutting](Notes/1A_AppAndRunner/00_Overview.md)
- [App vs Runner vs Agent — who owns what](Notes/1A_AppAndRunner/01_AppVsRunnerVsAgent.md)
- [App lifecycle — on_startup and on_shutdown hooks](Notes/1A_AppAndRunner/02_OnStartupShutdown.md)
- [The `app:` state boundary — lifetime semantics](Notes/1A_AppAndRunner/03_AppStateBoundary.md)
- [Wiring `resumability_config` on the App](Notes/1A_AppAndRunner/04_WiringResumability.md)
- [Wiring `context_cache_config` on the App](Notes/1A_AppAndRunner/05_WiringContextCache.md)
- [Wiring `events_compaction_config` on the App](Notes/1A_AppAndRunner/06_WiringContextCompaction.md)
- [Runner is constructed from the App](Notes/1A_AppAndRunner/07_RunnerInsideTheApp.md)
- [Dissecting `memory-bank` — App in a real sample](Notes/1A_AppAndRunner/08_DissectingSample.md)
- [In Production — App & Runner hardening checklist](Notes/1A_AppAndRunner/09_InProduction.md)
- [Knowledge Check](Notes/1A_AppAndRunner/10_KnowledgeCheck.yml)
- [Mini-Drill](Notes/1A_AppAndRunner/11_MiniDrill.yml)

### 2. [First Agent](Notes/02_FirstAgent/)
- [First Agent — instantiate the runtime by hand](Notes/02_FirstAgent/00_Overview.md)
- [LlmAgent by hand](Notes/02_FirstAgent/01_LlmAgentByHand.md)
- [Runner and InMemorySessionService](Notes/02_FirstAgent/02_RunnerAndSession.md)
- [run_async returns an async generator](Notes/02_FirstAgent/03_RunAsyncIsAGenerator.md)
- [types.Content — the Gemini message shape](Notes/02_FirstAgent/04_TheGeminiPayload.md)
- [Dissecting currency-agent](Notes/02_FirstAgent/05_DissectingSample.md)
- [First-Agent production checklist](Notes/02_FirstAgent/06_InProduction.md)
- [Knowledge Check](Notes/02_FirstAgent/07_KnowledgeCheck.yml)
- [Mini-Drill](Notes/02_FirstAgent/08_MiniDrill.yml)

### 2A. [Agent Config (YAML)](Notes/2A_AgentConfig/) — *side module*
- [Agent Config (YAML) — declarative agent definitions](Notes/2A_AgentConfig/00_Overview.md)
- [Why declarative — when YAML beats Python](Notes/2A_AgentConfig/01_WhyDeclarative.md)
- [Anatomy of `root_agent.yaml`](Notes/2A_AgentConfig/02_RootAgentYaml.md)
- [Generating an agent with `adk create`](Notes/2A_AgentConfig/03_AdkCreateCli.md)
- [Referencing tools from YAML](Notes/2A_AgentConfig/04_ToolReferences.md)
- [Composing sub-agents in YAML](Notes/2A_AgentConfig/05_SubAgentReferences.md)
- [YAML vs Python — an honest comparison](Notes/2A_AgentConfig/06_YamlVsPythonTradeoffs.md)
- [What YAML can't express](Notes/2A_AgentConfig/07_PythonOnlyFeatures.md)
- [Dissecting `multi_agent_basic_config`](Notes/2A_AgentConfig/08_DissectingSample.md)
- [In Production — YAML agent checklist](Notes/2A_AgentConfig/09_InProduction.md)
- [Knowledge Check](Notes/2A_AgentConfig/10_KnowledgeCheck.yml)
- [Mini-Drill](Notes/2A_AgentConfig/11_MiniDrill.yml)

### 3. [Tools](Notes/03_Tools/)
- [Tools — give the agent a body](Notes/03_Tools/00_Overview.md)
- [Why tools? Agents without them are chatbots](Notes/03_Tools/01_WhyTools.md)
- [FunctionTool — typed Python function → tool](Notes/03_Tools/02_FunctionTool.md)
- [The docstring IS the schema description](Notes/03_Tools/03_DocstringAsSchema.md)
- [ToolContext — tools can see (and change) state](Notes/03_Tools/04_ToolContext.md)
- [Built-in tools — google_search, load_memory, exit_loop, transfer_to_agent](Notes/03_Tools/05_BuiltInTools.md)
- [Computer Use toolset — letting the agent drive a browser (preview)](Notes/03_Tools/06_ComputerUse.md)
- [Tool limitations — single-instance & mutually-exclusive constraints](Notes/03_Tools/07_ToolLimitations.md)
- [AgentTool — call an agent like a tool (preview)](Notes/03_Tools/08_AgentToolPreview.md)
- [LongRunningFunctionTool — for slow tools (mention)](Notes/03_Tools/09_LongRunningTool.md)
- [Dissecting currency-agent and academic-research tool use](Notes/03_Tools/10_DissectingSample.md)
- [Tools — production checklist](Notes/03_Tools/11_InProduction.md)
- [Knowledge Check](Notes/03_Tools/12_KnowledgeCheck.yml)
- [Mini-Drill](Notes/03_Tools/13_MiniDrill.yml)

### 3A. [Project Structure](Notes/3A_ProjectStructure/) — *side module*
- [Project Structure — the smallest layout that still works](Notes/3A_ProjectStructure/00_Overview.md)
- [What breaks first when you don't split](Notes/3A_ProjectStructure/01_WhyStructureMatters.md)
- [The minimal layout — one agent.py](Notes/3A_ProjectStructure/02_MinimalLayout.md)
- [The small layout — agent + tools + prompts split](Notes/3A_ProjectStructure/03_SmallLayout.md)
- [The growing layout — directories per concept](Notes/3A_ProjectStructure/04_GrowingLayout.md)
- [What adk web / adk run / adk api_server expect on disk](Notes/3A_ProjectStructure/05_AdkCliExpectations.md)
- [What deployment expects — Cloud Run, Agent Engine, pyproject](Notes/3A_ProjectStructure/06_DeploymentExpectations.md)
- [Shared utilities — when one agent isn't enough](Notes/3A_ProjectStructure/07_SharedUtilities.md)
- [Config & env vars — one settings class, env-driven defaults](Notes/3A_ProjectStructure/07A_ConfigAndEnvVars.md)
- [Eval + tests layout — where adk eval and pytest look](Notes/3A_ProjectStructure/08_EvalAndTestsLayout.md)
- [Dissecting fun-facts vs travel-concierge side-by-side](Notes/3A_ProjectStructure/09_DissectingSample.md)
- [In Production — Project Structure hardening checklist](Notes/3A_ProjectStructure/10_InProduction.md)
- [Knowledge Check](Notes/3A_ProjectStructure/11_KnowledgeCheck.yml)
- [Mini-Drill](Notes/3A_ProjectStructure/12_MiniDrill.yml)

### 4. [Sessions & State](Notes/04_SessionsState/)
- [Sessions and State — persisting context across turns](Notes/04_SessionsState/00_Overview.md)
- [Session vs. State](Notes/04_SessionsState/01_SessionVsState.md)
- [State scopes — the four prefixes](Notes/04_SessionsState/02_StateScopes.md)
- [Reading state in the instruction prompt](Notes/04_SessionsState/03_ReadingStateInPrompts.md)
- [Writing state from a tool](Notes/04_SessionsState/04_WritingStateFromTools.md)
- [Context caching — reuse prefix tokens across turns](Notes/04_SessionsState/05_ContextCaching.md)
- [Context compaction — summarize old turns to fit the window](Notes/04_SessionsState/06_ContextCompaction.md)
- [Session rewind — reverse to before a prior invocation](Notes/04_SessionsState/07_SessionRewind.md)
- [Session migrate — upgrade a DB-backed session store's schema](Notes/04_SessionsState/08_SessionMigrate.md)
- [output_key — pipe agent's reply directly into state](Notes/04_SessionsState/09_OutputKeyShortcut.md)
- [Persistent sessions — DatabaseSessionService](Notes/04_SessionsState/10_PersistentSessions.md)
- [Dissecting llm-auditor — critic → reviser state flow](Notes/04_SessionsState/11_DissectingSample.md)
- [Sessions & State — production checklist](Notes/04_SessionsState/12_InProduction.md)
- [Knowledge Check](Notes/04_SessionsState/13_KnowledgeCheck.yml)
- [Mini-Drill](Notes/04_SessionsState/14_MiniDrill.yml)

### 04A. [Artifacts & Heavy Data](Notes/04A_ArtifactsHeavyData/) ☁️ — *side module*
- [Artifacts & Heavy Data — getting bytes out of state](Notes/04A_ArtifactsHeavyData/00_Overview.md)
- [Why artifacts — when state is the wrong store](Notes/04A_ArtifactsHeavyData/01_WhyArtifacts.md)
- [ArtifactService shape — the interface and the dev implementation](Notes/04A_ArtifactsHeavyData/02_ArtifactServiceShape.md)
- [GcsArtifactService — bucket, IAM, lifecycle ☁️](Notes/04A_ArtifactsHeavyData/03_GcsArtifactService.md)
- [Save and load artifacts from a tool](Notes/04A_ArtifactsHeavyData/04_SaveAndLoadFromTools.md)
- [Multimodal Parts — inline_data vs file_data](Notes/04A_ArtifactsHeavyData/05_MultimodalParts.md)
- [Video understanding — Gemini video Parts ☁️](Notes/04A_ArtifactsHeavyData/06_VideoUnderstanding.md)
- [Signed URLs & cross-agent handoff ☁️](Notes/04A_ArtifactsHeavyData/07_SignedUrlsHandoff.md)
- [artifact_delta on Events — how the Runner persists](Notes/04A_ArtifactsHeavyData/08_ArtifactDeltaInEvents.md)
- [Heavy-file handoff between sub-agents](Notes/04A_ArtifactsHeavyData/09_HeavyFileBetweenSubAgents.md)
- [Dissecting brand-aligned-presentations — artifacts end-to-end](Notes/04A_ArtifactsHeavyData/10_DissectingSample.md)
- [Artifacts in production — checklist](Notes/04A_ArtifactsHeavyData/11_InProduction.md)
- [Knowledge Check](Notes/04A_ArtifactsHeavyData/12_KnowledgeCheck.yml)
- [Mini-Drill](Notes/04A_ArtifactsHeavyData/13_MiniDrill.yml)

### 4B. [Human-in-the-Loop & Resume/Cancel](Notes/4B_HumanInTheLoop/) 🛠 — *side module*
- [Human-in-the-Loop & Resume/Cancel — pause an agent for a human, then resume](Notes/4B_HumanInTheLoop/00_Overview.md)
- [Why HITL — the three canonical cases](Notes/4B_HumanInTheLoop/01_WhyHITL.md)
- [ctx.request_confirmation() — pausing inside a tool](Notes/4B_HumanInTheLoop/02_RequestConfirmation.md)
- [EventActions.requested_tool_confirmations — the pause event on the wire](Notes/4B_HumanInTheLoop/03_RequestedToolConfirmations.md)
- [Resume and abandon — runner.run_async(invocation_id=...) and how to drop a paused invocation](Notes/4B_HumanInTheLoop/04_RunnerResumeAndCancel.md)
- [LongRunningFunctionTool — pause for an external system (which may be a human)](Notes/4B_HumanInTheLoop/05_LongRunningFunctionTool.md)
- [RequestInput — pause the whole graph for a human](Notes/4B_HumanInTheLoop/06_RequestInputInGraphs.md)
- [Ambient Agents — event-triggered runs that occasionally pause for a human](Notes/4B_HumanInTheLoop/07_AmbientAgents.md)
- [Frontend-driven approvals — the client owns the approval UI](Notes/4B_HumanInTheLoop/08_FrontendDrivenApprovals.md)
- [Slack & Google Chat as approval surfaces — interactive messages, cards, callbacks](Notes/4B_HumanInTheLoop/09_ChatPlatformApprovals.md)
- [Durable execution — Temporal, Dapr for when ADK's built-in resume isn't enough](Notes/4B_HumanInTheLoop/10_DurableExecutionIntegrations.md)
- [Dissecting ambient-expense-agent — ambient + HITL composed end to end](Notes/4B_HumanInTheLoop/11_DissectingSample.md)
- [In Production — HITL hardening checklist](Notes/4B_HumanInTheLoop/12_InProduction.md)
- [Knowledge Check](Notes/4B_HumanInTheLoop/13_KnowledgeCheck.yml)
- [Mini-Drill](Notes/4B_HumanInTheLoop/14_MiniDrill.yml)

### 🏁 [M1 — Conversation Server (CLI loop, two tools, persistent todos)](Drills/M1_ConversationServer.md)

---

## Composition Track 🧩

### 5. [Multi-Agent](Notes/05_MultiAgent/)
- [Composing agents — sub_agents, AgentTool, transfer_to_agent](Notes/05_MultiAgent/00_Overview.md)
- [Why compose agents at all?](Notes/05_MultiAgent/01_WhyComposeAgents.md)
- [sub_agents — implicit LLM delegation](Notes/05_MultiAgent/02_SubAgents.md)
- [transfer_to_agent — the routing mechanism](Notes/05_MultiAgent/03_TransferToAgent.md)
- [AgentTool — wrap an agent as a tool](Notes/05_MultiAgent/04_AgentAsTool.md)
- [Sharing state across agents — output_key is the bus](Notes/05_MultiAgent/05_SharingStateAcrossAgents.md)
- [SequentialAgent — when order is fixed](Notes/05_MultiAgent/06_SequentialAgent.md)
- [Dissecting the llm-auditor sample](Notes/05_MultiAgent/07_DissectingLlmAuditor.md)
- [Quick read — financial-advisor's AgentTool stack](Notes/05_MultiAgent/08_DissectingAgentTool.md)
- [LangGraphAgent — wrap a LangGraph workflow as an ADK agent](Notes/05_MultiAgent/08A_LangGraphAgent.md)
- [Multi-agent gotchas in production](Notes/05_MultiAgent/09_InProduction.md)
- [Knowledge Check](Notes/05_MultiAgent/10_KnowledgeCheck.yml)
- [Mini-Drill](Notes/05_MultiAgent/11_MiniDrill.yml)

### 6. [Graph Workflows](Notes/06_GraphWorkflows/)
- [Graph workflows — beyond Sequential / Parallel / Loop](Notes/06_GraphWorkflows/00_Overview.md)
- [Legacy workflow templates — Sequential, Parallel, Loop](Notes/06_GraphWorkflows/01_LegacyTemplates.md)
- [Templates mix — reading story_teller](Notes/06_GraphWorkflows/02_LegacyMixed.md)
- [Why graphs — what templates can't express](Notes/06_GraphWorkflows/03_WhyGraphWorkflows.md)
- [Workflow, nodes, edges](Notes/06_GraphWorkflows/04_GraphIntro.md)
- [Defining nodes — agents, functions, list-yielding fan-out](Notes/06_GraphWorkflows/05_DefiningNodes.md)
- [Routing edges — static vs dynamic](Notes/06_GraphWorkflows/06_RoutingEdges.md)
- [Human-in-the-loop — pause, resume, cancel](Notes/06_GraphWorkflows/07_HumanInTheLoop.md)
- [Dissecting workflow-concurrent_research_writer](Notes/06_GraphWorkflows/08_DissectingWorkflowSample.md)
- [Graph workflows in production](Notes/06_GraphWorkflows/09_InProduction.md)
- [Knowledge Check](Notes/06_GraphWorkflows/10_KnowledgeCheck.yml)
- [Mini-Drill](Notes/06_GraphWorkflows/11_MiniDrill.yml)

### 🏁 [M2 — Workflow Editor (legacy vs graph, side by side)](Drills/M2_WorkflowEditor.md)

---

## Integration Track 🔌

### 7. [Callbacks](Notes/07_Callbacks/)
- [Module 07 — Callbacks (lifecycle hooks for shaping, guardrails, observability)](Notes/07_Callbacks/00_Overview.md)
- [Why callbacks (the prompt is not your guardrail)](Notes/07_Callbacks/01_WhyCallbacks.md)
- [before/after_model_callback — wrap the LLM call](Notes/07_Callbacks/02_BeforeAfterModel.md)
- [before/after_tool_callback — guard and reshape tool calls](Notes/07_Callbacks/03_BeforeAfterTool.md)
- [before/after_agent_callback — per-invocation setup and teardown](Notes/07_Callbacks/04_BeforeAfterAgent.md)
- [CallbackContext anatomy — what's there, what isn't, common gotchas](Notes/07_Callbacks/05_CallbackContextAnatomy.md)
- [Real-life callback recipes — caching, rate limiting, PII redaction, citations, budgets, gating](Notes/07_Callbacks/06_CallbackRecipeCookbook.md)
- [Callbacks vs Plugins — when to reach for which](Notes/07_Callbacks/07_CallbacksVsPlugins.md)
- [on_model_error / on_tool_error — recover from exceptions](Notes/07_Callbacks/08_ErrorCallbacks.md)
- [Dissecting llm-auditor — _render_reference and _remove_end_of_edit_mark](Notes/07_Callbacks/09_DissectingSample.md)
- [Callbacks in production — guardrail checklist](Notes/07_Callbacks/10_InProduction.md)
- [Knowledge Check](Notes/07_Callbacks/11_KnowledgeCheck.yml)
- [Mini-Drill](Notes/07_Callbacks/12_MiniDrill.yml)

### 8. [MCP](Notes/08_MCP/)
- [Module 08 — MCP (consume external servers, expose your own tools)](Notes/08_MCP/00_Overview.md)
- [What is MCP (and why ADK speaks it natively)](Notes/08_MCP/01_WhatIsMCP.md)
- [MCPToolset — the consumer side](Notes/08_MCP/02_MCPToolset.md)
- [MCP transports — stdio, HTTP-SSE, Streamable-HTTP](Notes/08_MCP/03_Transports.md)
- [Lifecycle management — when MCP sessions open and close](Notes/08_MCP/04_LifecycleManagement.md)
- [Serving your tools via FastMCP](Notes/08_MCP/05_ServingViaFastMCP.md)
- [Dissecting antom-payment, currency-agent, travel-planner](Notes/08_MCP/06_DissectingSample.md)
- [MCP in production — auth, retries, version pinning, observability](Notes/08_MCP/07_InProduction.md)
- [Knowledge Check](Notes/08_MCP/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/08_MCP/09_MiniDrill.yml)

### 9. [Skills](Notes/09_Skills/)
- [Module 09 — Skills (reusable capability bundles, NEW in 2.0)](Notes/09_Skills/00_Overview.md)
- [What is a Skill (and why we needed a new primitive)](Notes/09_Skills/01_WhatIsASkill.md)
- [Skill anatomy — Frontmatter, instructions, Resources, Scripts](Notes/09_Skills/02_SkillAnatomy.md)
- [SkillToolset — wiring skills into an agent](Notes/09_Skills/03_SkillToolset.md)
- [SkillRegistry — sharing skills across agents](Notes/09_Skills/04_SkillRegistry.md)
- [Dissecting agent-skills-tutorial — the four patterns end-to-end](Notes/09_Skills/05_DissectingSample.md)
- [Skills in production — versioning, governance, description hygiene](Notes/09_Skills/06_InProduction.md)
- [Knowledge Check](Notes/09_Skills/07_KnowledgeCheck.yml)
- [Mini-Drill](Notes/09_Skills/08_MiniDrill.yml)

### 10. [A2A](Notes/10_A2A/)
- [Module 10 — A2A (expose agents as services, consume remote agents)](Notes/10_A2A/00_Overview.md)
- [What is A2A (the protocol, in one page)](Notes/10_A2A/01_WhatIsA2A.md)
- [AgentCard — the manifest your agent publishes](Notes/10_A2A/02_AgentCard.md)
- [Serving an ADK agent with to_a2a()](Notes/10_A2A/03_ServeWithToA2a.md)
- [Consuming a remote agent with RemoteA2aAgent](Notes/10_A2A/04_ConsumeWithRemoteA2aAgent.md)
- [A2A vs MCP (the comparison that confuses everyone)](Notes/10_A2A/05_A2A_vs_MCP.md)
- [Dissecting currency-agent — A2A serve + MCP consume + A2A client](Notes/10_A2A/06_DissectingSample.md)
- [A2A in production — versioning, auth, rate-limit, observability, sticky sessions](Notes/10_A2A/07_InProduction.md)
- [Knowledge Check](Notes/10_A2A/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/10_A2A/09_MiniDrill.yml)

### 🏁 [M3 — Federated Travel Planner (Callbacks + MCP + Skills + A2A)](Drills/M3_FederatedPlanner.md)

---

## Data & GCP Track ☁️

### 10A. [Embeddings & Vector Search](Notes/10A_EmbeddingsVectorSearch/) ☁️ — *side module*
- [Embeddings & Vector Search — Overview](Notes/10A_EmbeddingsVectorSearch/00_Overview.md)
- [What is an embedding?](Notes/10A_EmbeddingsVectorSearch/01_WhatIsAnEmbedding.md)
- [☁️ Vertex AI text embeddings — the SDK](Notes/10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings.md)
- [☁️ Vertex AI Vector Search — concepts](Notes/10A_EmbeddingsVectorSearch/03_VectorSearchIntro.md)
- [☁️ Building & deploying an index](Notes/10A_EmbeddingsVectorSearch/04_BuildingAnIndex.md)
- [☁️ Querying — find_neighbors](Notes/10A_EmbeddingsVectorSearch/05_QueryingTheIndex.md)
- [🔎 Dissecting the RAG sample](Notes/10A_EmbeddingsVectorSearch/06_DissectingSample.md)
- [🚀 In Production — embeddings & vector search](Notes/10A_EmbeddingsVectorSearch/07_InProduction.md)
- [Knowledge Check](Notes/10A_EmbeddingsVectorSearch/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/10A_EmbeddingsVectorSearch/09_MiniDrill.yml)

### 10B. [RAG Pipeline](Notes/10B_RAGPipeline/) ☁️ — *side module*
- [RAG Pipeline — Overview](Notes/10B_RAGPipeline/00_Overview.md)
- [The RAG loop in 7 stages](Notes/10B_RAGPipeline/01_RAGConcepts.md)
- [Chunking — three strategies](Notes/10B_RAGPipeline/02_Chunking.md)
- [🛠 Hand-rolled RAG end-to-end](Notes/10B_RAGPipeline/03_HandRolledRAG.md)
- [☁️ Vertex AI RAG Engine — the managed shortcut](Notes/10B_RAGPipeline/04_VertexAIRAGEngine.md)
- [🛠 Wiring RAG into an ADK agent](Notes/10B_RAGPipeline/05_RAGIntoADK.md)
- [🔎 Dissecting the RAG sample — line by line](Notes/10B_RAGPipeline/06_DissectingRAGSample.md)
- [🚀 In Production — RAG pipelines](Notes/10B_RAGPipeline/07_InProduction.md)
- [Knowledge Check](Notes/10B_RAGPipeline/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/10B_RAGPipeline/09_MiniDrill.yml)

### 10C. [BigQuery for Agents](Notes/10C_BigQueryAgents/) ☁️ — *side module*
- [BigQuery for Agents — Overview](Notes/10C_BigQueryAgents/00_Overview.md)
- [☁️ When BigQuery makes sense for an agent](Notes/10C_BigQueryAgents/01_BigQueryForAgents.md)
- [🧠 NL2SQL — schema-grounding & prompt structure](Notes/10C_BigQueryAgents/02_NL2SQLPattern.md)
- [🛠 ☁️ BigQuery as a tool — with cost cap](Notes/10C_BigQueryAgents/03_BigQueryAsTool.md)
- [☁️ BigQuery vector search — SQL-native](Notes/10C_BigQueryAgents/04_BigQueryVectorSearch.md)
- [🚀 BQ as a telemetry sink — `BigQueryAgentAnalyticsPlugin` (teaser)](Notes/10C_BigQueryAgents/05_BigQueryAgentAnalyticsPlugin.md)
- [🔎 Dissecting the data-science sample](Notes/10C_BigQueryAgents/06_DissectingDataScience.md)
- [🚀 In Production — BigQuery for agents](Notes/10C_BigQueryAgents/07_InProduction.md)
- [Knowledge Check](Notes/10C_BigQueryAgents/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/10C_BigQueryAgents/09_MiniDrill.yml)

---

## Runtime Track ⚙️

### 11. [Memory](Notes/11_Memory/)
- [Memory — beyond one session](Notes/11_Memory/00_Overview.md)
- [Session vs State vs Memory — three lifetimes](Notes/11_Memory/01_SessionVsStateVsMemory.md)
- [InMemoryMemoryService — the dev-only backend](Notes/11_Memory/02_InMemoryMemoryService.md)
- [VertexAiMemoryBankService — managed, auto-summarized](Notes/11_Memory/03_VertexAIMemoryBank.md)
- [VertexAiRagMemoryService — bring your own index](Notes/11_Memory/04_VertexAIRagMemoryService.md)
- [load_memory and PreloadMemoryTool](Notes/11_Memory/05_LoadMemoryTool.md)
- [Dissecting the memory-bank sample](Notes/11_Memory/06_DissectingMemoryBank.md)
- [Memory in production](Notes/11_Memory/07_InProduction.md)
- [Knowledge Check](Notes/11_Memory/08_KnowledgeCheck.yml)
- [Mini-Drill](Notes/11_Memory/09_MiniDrill.yml)

### 12. [Code Execution](Notes/12_CodeExecution/)
- [Code execution — letting agents run Python](Notes/12_CodeExecution/00_Overview.md)
- [Why code execution](Notes/12_CodeExecution/01_WhyCodeExecution.md)
- [UnsafeLocalCodeExecutor — the dev footgun](Notes/12_CodeExecution/02_UnsafeLocalCodeExecutor.md)
- [BuiltInCodeExecutor — Gemini's own sandbox](Notes/12_CodeExecution/03_BuiltInCodeExecutor.md)
- [VertexAiCodeExecutor — the managed default](Notes/12_CodeExecution/04_VertexAiCodeExecutor.md)
- [ContainerCodeExecutor and GkeCodeExecutor](Notes/12_CodeExecution/05_ContainerAndGke.md)
- [AgentEngineSandboxCodeExecutor](Notes/12_CodeExecution/06_AgentEngineSandbox.md)
- [Dissecting the data-science analytics sub-agent](Notes/12_CodeExecution/07_DissectingSample.md)
- [Code execution in production](Notes/12_CodeExecution/08_InProduction.md)
- [Knowledge Check](Notes/12_CodeExecution/09_KnowledgeCheck.yml)
- [Mini-Drill](Notes/12_CodeExecution/10_MiniDrill.yml)

### 13. [Plugins](Notes/13_Plugins/)
- [Plugins — cross-cutting concerns at runner scope](Notes/13_Plugins/00_Overview.md)
- [What is a Plugin (vs a Callback)](Notes/13_Plugins/01_WhatIsAPlugin.md)
- [LoggingPlugin](Notes/13_Plugins/02_LoggingPlugin.md)
- [ReflectAndRetryToolPlugin](Notes/13_Plugins/03_ReflectAndRetryToolPlugin.md)
- [ContextFilterPlugin](Notes/13_Plugins/04_ContextFilterPlugin.md)
- [GlobalInstructionPlugin](Notes/13_Plugins/05_GlobalInstructionPlugin.md)
- [BigQueryAgentAnalyticsPlugin](Notes/13_Plugins/06_BigQueryAgentAnalyticsPlugin.md)
- [Writing a custom plugin](Notes/13_Plugins/07_WritingACustomPlugin.md)
- [Dissecting the safety-plugins sample](Notes/13_Plugins/08_DissectingSample.md)
- [Plugins in production](Notes/13_Plugins/09_InProduction.md)
- [Knowledge Check](Notes/13_Plugins/10_KnowledgeCheck.yml)
- [Mini-Drill](Notes/13_Plugins/11_MiniDrill.yml)

### 14. [Evaluation](Notes/14_Evaluation/) 🧪
- [Evaluation — testing agent behavior](Notes/14_Evaluation/00_Overview.md)
- [Evals are not tests](Notes/14_Evaluation/01_EvalsAreNotTests.md)
- [EvalCase and EvalSet](Notes/14_Evaluation/02_EvalCaseEvalSet.md)
- [AgentEvaluator — running an eval set](Notes/14_Evaluation/03_AgentEvaluator.md)
- [LlmAsJudge — an LLM rates the answer](Notes/14_Evaluation/04_LlmAsJudge.md)
- [RubricBasedEvaluator](Notes/14_Evaluation/05_RubricBasedEvaluator.md)
- [TrajectoryEvaluator — score the path, not just the answer](Notes/14_Evaluation/06_TrajectoryEvaluator.md)
- [HallucinationsV1 and FinalResponseMatchV1/V2](Notes/14_Evaluation/07_BuiltInMetrics.md)
- [adk eval — the CLI entry point](Notes/14_Evaluation/08_AdkEvalCli.md)
- [Dissecting the academic-research eval](Notes/14_Evaluation/09_DissectingSample.md)
- [Evaluation in production](Notes/14_Evaluation/10_InProduction.md)
- [Knowledge Check](Notes/14_Evaluation/11_KnowledgeCheck.yml)
- [Mini-Drill](Notes/14_Evaluation/12_MiniDrill.yml)

### 🏁 [M4 — Auditor with plugins, callbacks, and evals](Drills/M4_AuditorWithEvals.md)

---

## Production Track 🚀

### 15. [Observability](Notes/15_Observability/)
- [Observability — seeing what your agent is doing in production](Notes/15_Observability/00_Overview.md)
- [Why agents need observability more than ordinary services](Notes/15_Observability/01_WhyObservability.md)
- [Structured logging with LoggingPlugin](Notes/15_Observability/02_StructuredLogging.md)
- [OpenTelemetry — traces, spans, attributes](Notes/15_Observability/03_OpenTelemetryBasics.md)
- [One Runner.run_async() = one trace](Notes/15_Observability/04_TracingAnAgentRun.md)
- [The four metrics every agent needs](Notes/15_Observability/05_Metrics.md)
- [BigQuery as the long-term observability sink](Notes/15_Observability/06_BigQueryAsSink.md)
- [Dissecting agent-observability-bq end-to-end](Notes/15_Observability/07_DissectingSample.md)
- [Observability in production — the hardening checklist](Notes/15_Observability/08_InProduction.md)
- [Knowledge Check](Notes/15_Observability/09_KnowledgeCheck.yml)
- [Mini-Drill](Notes/15_Observability/10_MiniDrill.yml)

### 16. [Production & Security](Notes/16_ProductionSecurity/) 🚀
- [Production & Security — defense in depth for agents](Notes/16_ProductionSecurity/00_Overview.md)
- [A threat model for agents](Notes/16_ProductionSecurity/01_ThreatModelForAgents.md)
- [Prompt injection — taxonomy and defenses](Notes/16_ProductionSecurity/02_PromptInjectionDefense.md)
- [Auth context for tools — AuthHandler and CredentialManager](Notes/16_ProductionSecurity/03_Authentication.md)
- [Secrets — Secret Manager, ADC, .env is dev-only](Notes/16_ProductionSecurity/04_SecretsHandling.md)
- [Guardrails cookbook — seven recipes you copy-paste](Notes/16_ProductionSecurity/05_GuardrailsCookbook.md)
- [Agent identity vs controlling-user identity](Notes/16_ProductionSecurity/06_AgentIdentityVsUser.md)
- [Gemini-as-Judge — the runtime safety classifier plugin](Notes/16_ProductionSecurity/07_GeminiAsJudgePlugin.md)
- [Dissecting safety-plugins](Notes/16_ProductionSecurity/08_DissectingSafetyPlugins.md)
- [Dissecting policy-as-code](Notes/16_ProductionSecurity/09_DissectingPolicyAsCode.md)
- [Security in production — defense-in-depth checklist](Notes/16_ProductionSecurity/10_InProduction.md)
- [Knowledge Check](Notes/16_ProductionSecurity/11_KnowledgeCheck.yml)
- [Mini-Drill](Notes/16_ProductionSecurity/12_MiniDrill.yml)

### 17. [Advanced Models](Notes/17_AdvancedModels/)
- [Advanced Models — beyond Gemini](Notes/17_AdvancedModels/00_Overview.md)
- [LLMRegistry — how ADK resolves a model](Notes/17_AdvancedModels/01_LLMRegistry.md)
- [Gemini variants — Flash-Lite, Flash, Pro](Notes/17_AdvancedModels/02_GeminiVariants.md)
- [Claude via Vertex AI](Notes/17_AdvancedModels/03_ClaudeViaVertex.md)
- [Gemma — open-weights, local](Notes/17_AdvancedModels/04_GemmaLocal.md)
- [Planners — BuiltInPlanner + ThinkingConfig](Notes/17_AdvancedModels/05_PlannersBuiltIn.md)
- [PlanReActPlanner — plan, reason, act on any model](Notes/17_AdvancedModels/06_PlanReActPlanner.md)
- [LiteLlm — the universal adapter](Notes/17_AdvancedModels/07_LiteLlm.md)
- [OpenAI models in ADK](Notes/17_AdvancedModels/08_OpenAIModels.md)
- [ApigeeLlm — enterprise gateway routing](Notes/17_AdvancedModels/09_ApigeeLlm.md)
- [Different models for different sub_agents](Notes/17_AdvancedModels/10_PerAgentModel.md)
- [Model selection patterns — tiering, config, fallback, cost-aware swap](Notes/17_AdvancedModels/10A_ModelSelectionPatterns.md)
- [Dissecting gemma-food-tour-guide](Notes/17_AdvancedModels/11_DissectingSample.md)
- [Models in production — routing, lock-in, rate limits](Notes/17_AdvancedModels/12_InProduction.md)
- [Knowledge Check](Notes/17_AdvancedModels/13_KnowledgeCheck.yml)
- [Mini-Drill](Notes/17_AdvancedModels/14_MiniDrill.yml)

### 18. [Streaming & Live](Notes/18_StreamingLive/) 🎙
- [Streaming and Live — text tokens, bidi voice, the whole wire](Notes/18_StreamingLive/00_Overview.md)
- [Streaming fundamentals — async generators, partials, backpressure](Notes/18_StreamingLive/01_StreamingFundamentals.md)
- [The Gemini Live API — what it is, what ADK wraps](Notes/18_StreamingLive/02_GeminiLiveIntro.md)
- [Text streaming — tokens to stdout, then SSE to a browser](Notes/18_StreamingLive/03_TextStreaming.md)
- [Audio I/O — mic in (16 kHz PCM), speaker out (24 kHz PCM)](Notes/18_StreamingLive/04_AudioIO.md)
- [Streaming tools — LongRunningFunctionTool (deferred result) and live input streams](Notes/18_StreamingLive/05_StreamingTools.md)
- [Video input — webcam / screen capture into Live](Notes/18_StreamingLive/06_VideoInput.md)
- [Live production patterns — barge-in, VAD, latency, reconnection](Notes/18_StreamingLive/07_LiveProductionPatterns.md)
- [Dissecting bidi-demo — every line, end to end](Notes/18_StreamingLive/08_DissectingLiveSample.md)
- [Streaming in production — costs, safety, session caps, telemetry](Notes/18_StreamingLive/09_InProduction.md)
- [Knowledge Check](Notes/18_StreamingLive/10_KnowledgeCheck.yml)
- [Mini-Drill — Text streaming](Notes/18_StreamingLive/11_MiniDrill_TextStream.yml)
- [Mini-Drill — Voice Live](Notes/18_StreamingLive/12_MiniDrill_VoiceLive.yml)
- [Mini-Drill — SSE on the web](Notes/18_StreamingLive/13_MiniDrill_SSEWeb.yml)

### 19. [Internals](Notes/19_Internals/)
- [Reading the ADK source — what, why, when](Notes/19_Internals/00_Overview.md)
- [Repo map — one sentence per subdir](Notes/19_Internals/01_RepoMap.md)
- [LlmAgent — fields and the run loop](Notes/19_Internals/02_LlmAgentSource.md)
- [Runner.run_async — top-level plumbing](Notes/19_Internals/03_RunnerSource.md)
- [Session and Event — the data model](Notes/19_Internals/04_SessionEventSource.md)
- [Tool dispatch — schema, args, errors](Notes/19_Internals/05_ToolDispatch.md)
- [Workflow runtime — nodes, edges, scheduler](Notes/19_Internals/06_WorkflowSource.md)
- [LLMRegistry — model resolution](Notes/19_Internals/07_ModelRegistry.md)
- [AutoFlow — the implicit single-agent flow](Notes/19_Internals/08_AutoFlow.md)
- [Dissecting one runner.run_async call through source](Notes/19_Internals/09_DissectingOneCall.md)
- [Tracing one tool invocation end-to-end](Notes/19_Internals/10_TracingOneToolCall.md)
- [Tracing one tool_context.state mutation](Notes/19_Internals/11_TracingOneStateMutation.md)
- [When to read the source, when not to](Notes/19_Internals/12_InProduction.md)
- [Knowledge Check](Notes/19_Internals/13_KnowledgeCheck.yml)
- [Mini-Drill](Notes/19_Internals/14_MiniDrill.yml)

### 20. [Framework Comparison](Notes/20_FrameworkComparison/)
- [Placing ADK in the agent-framework landscape](Notes/20_FrameworkComparison/00_Overview.md)
- [The landscape — one-page overview](Notes/20_FrameworkComparison/01_TheLandscape.md)
- [LangChain & LangGraph](Notes/20_FrameworkComparison/02_LangChainAndLangGraph.md)
- [CrewAI — role-based "teams of agents"](Notes/20_FrameworkComparison/03_CrewAI.md)
- [AutoGen / AG2 — conversational multi-agent](Notes/20_FrameworkComparison/04_AutoGen.md)
- [OpenAI Agents SDK — slim, OAI-shaped](Notes/20_FrameworkComparison/05_OpenAIAgentsSDK.md)
- [Pydantic AI — type-driven agents](Notes/20_FrameworkComparison/06_PydanticAI.md)
- [Letta / MemGPT — memory-first agents](Notes/20_FrameworkComparison/07_LettaMemGPT.md)
- [The big feature matrix](Notes/20_FrameworkComparison/08_FeatureMatrix.md)
- [Choosing a framework — decision flowchart](Notes/20_FrameworkComparison/09_ChoosingAFramework.md)
- [How each competitor would build `llm-auditor`](Notes/20_FrameworkComparison/10_DissectingSample.md)
- [Framework choice as a long-term commitment](Notes/20_FrameworkComparison/11_InProduction.md)
- [Knowledge Check](Notes/20_FrameworkComparison/12_KnowledgeCheck.yml)
- [Mini-Drill](Notes/20_FrameworkComparison/13_MiniDrill.yml)

---

## Deployment & Integration Track 🌐

### 21. [ADK API Surface](Notes/21_AdkApiSurface/) 🌐
- [Overview — what ADK exposes over the wire](Notes/21_AdkApiSurface/00_Overview.md)
- [adk run — the shortest path from code to live agent](Notes/21_AdkApiSurface/01_AdkRunCli.md)
- [adk run under the hood — argv to first event](Notes/21_AdkApiSurface/01A_AdkRunUnderTheHood.md)
- [adk web under the hood — the dev UI and its ASGI mount](Notes/21_AdkApiSurface/01B_AdkWebUnderTheHood.md)
- [The full adk CLI family](Notes/21_AdkApiSurface/01C_FullCliFamily.md)
- [adk api_server — the headless HTTP surface](Notes/21_AdkApiSurface/02_AdkApiServer.md)
- [REST shapes — /run, sessions, and the Event JSON](Notes/21_AdkApiSurface/03_RestShapes.md)
- [SSE — streaming events with /run_sse](Notes/21_AdkApiSurface/04_SseEndpoints.md)
- [WebSockets — /run_live for bidi voice/video](Notes/21_AdkApiSurface/05_WebSocketsForLive.md)
- [Wrapping ADK in your own FastAPI process](Notes/21_AdkApiSurface/06_WrappingInFastAPI.md)
- [Session and event resources — the REST CRUD surface](Notes/21_AdkApiSurface/07_SessionAndEventResources.md)
- [Authenticating the API — IAP, OIDC, custom middleware](Notes/21_AdkApiSurface/08_AuthenticatingTheApi.md)
- [Dissecting currency-agent served three ways](Notes/21_AdkApiSurface/09_DissectingSample.md)
- [In Production — API surface hardening checklist](Notes/21_AdkApiSurface/10_InProduction.md)
- [Knowledge Check](Notes/21_AdkApiSurface/11_KnowledgeCheck.yml)
- [Mini-Drill](Notes/21_AdkApiSurface/12_MiniDrill.yml)

### 22. [Deployment Models](Notes/22_DeploymentModels/) ☁️ 🌐
- [Overview — where ADK agents actually run in production](Notes/22_DeploymentModels/00_Overview.md)
- [The deployment landscape — Cloud Run vs Agent Engine vs GKE](Notes/22_DeploymentModels/01_DeploymentLandscape.md)
- [Cloud Run path — Dockerfile, adk deploy, env vars](Notes/22_DeploymentModels/02_CloudRunPath.md)
- [Agent Engine path — managed Runtime, AgentEngineApp, session persistence](Notes/22_DeploymentModels/03_AgentEnginePath.md)
- [GKE — the third path](Notes/22_DeploymentModels/03A_GKE.md)
- [Session persistence — what each platform gives you](Notes/22_DeploymentModels/04_SessionPersistenceComparison.md)
- [Scaling, cold start, concurrency](Notes/22_DeploymentModels/05_ScalingAndColdStart.md)
- [Auth and IAM across platforms](Notes/22_DeploymentModels/06_AuthAndIAM.md)
- [Observability wiring per platform](Notes/22_DeploymentModels/07_ObservabilityWiring.md)
- [Secrets across platforms](Notes/22_DeploymentModels/08_SecretsAcrossPlatforms.md)
- [Cost model — what actually moves the bill](Notes/22_DeploymentModels/09_CostModelComparison.md)
- [Dissecting adk-ae-oauth — the same agent, two deployments](Notes/22_DeploymentModels/10_DissectingSample.md)
- [In Production — deployment hardening checklist](Notes/22_DeploymentModels/11_InProduction.md)
- [Knowledge Check](Notes/22_DeploymentModels/12_KnowledgeCheck.yml)
- [Mini-Drill](Notes/22_DeploymentModels/13_MiniDrill.yml)

### 23. [Frontend Integration](Notes/23_FrontendIntegration/) 🌐
- [Frontend Integration — browsers and SPAs as ADK clients](Notes/23_FrontendIntegration/00_Overview.md)
- [Who owns user_id and session_id?](Notes/23_FrontendIntegration/01_WhoOwnsTheSession.md)
- [Auth context propagation — token → backend → ToolContext](Notes/23_FrontendIntegration/02_AuthContextPropagation.md)
- [SSE from the browser — EventSource, reconnection, errors](Notes/23_FrontendIntegration/03_SseFromTheBrowser.md)
- [WebSockets from the browser — bidi for Live](Notes/23_FrontendIntegration/04_WebSocketsFromBrowser.md)
- [A minimal SPA hitting adk api_server](Notes/23_FrontendIntegration/05_CustomSPApattern.md)
- [A2UI / adk web — the dev frontend, and customizing it](Notes/23_FrontendIntegration/06_A2UIClient.md)
- [AG-UI — when your frontend already speaks an agent protocol](Notes/23_FrontendIntegration/07_AGUIBridge.md)
- [Rendering partial tokens vs final results](Notes/23_FrontendIntegration/08_StreamingPartialResults.md)
- [File upload — multipart from browser to ArtifactService](Notes/23_FrontendIntegration/09_FileUploadFlow.md)
- [Optimistic UI — render the tool call while it pends](Notes/23_FrontendIntegration/10_OptimisticUI.md)
- [Dissecting deep-search — a real SPA + ADK backend](Notes/23_FrontendIntegration/11_DissectingSample.md)
- [In Production — frontend integration hardening checklist](Notes/23_FrontendIntegration/12_InProduction.md)
- [Knowledge Check](Notes/23_FrontendIntegration/13_KnowledgeCheck.yml)
- [Mini-Drill](Notes/23_FrontendIntegration/14_MiniDrill.yml)

### 24. [Channel Integrations](Notes/24_ChannelIntegrations/) 🌐
- [Channel Integrations — Slack, Chat, Discord, ambient triggers](Notes/24_ChannelIntegrations/00_Overview.md)
- [The universal webhook → Runner adapter](Notes/24_ChannelIntegrations/01_WebhookToRunnerPattern.md)
- [Long-running responses on chat platforms — ACK + background](Notes/24_ChannelIntegrations/02_LongRunningOnChat.md)
- [Slack bot — Events API, slash commands, threading](Notes/24_ChannelIntegrations/03_SlackBot.md)
- [Google Chat app — Apps Script-free, IAM-secured](Notes/24_ChannelIntegrations/04_GoogleChatApp.md)
- [Discord — Interactions API, Ed25519, deferred responses](Notes/24_ChannelIntegrations/05_DiscordBot.md)
- [WhatsApp and Email — sketches, same pattern](Notes/24_ChannelIntegrations/06_WhatsAppEmail.md)
- [Ambient agents — Pub/Sub-triggered ADK, posting back to a channel](Notes/24_ChannelIntegrations/07_AmbientAgentsAsChannels.md)
- [Auth and per-user session — mapping channel users to ADK user_id](Notes/24_ChannelIntegrations/08_AuthAndPerUserSession.md)
- [Handling multimedia — voice notes, images, files from chat](Notes/24_ChannelIntegrations/09_HandlingMultimedia.md)
- [Dissecting ambient-expense-agent — Pub/Sub channel + HITL](Notes/24_ChannelIntegrations/10_DissectingSample.md)
- [In Production — channel integration hardening checklist](Notes/24_ChannelIntegrations/11_InProduction.md)
- [Knowledge Check](Notes/24_ChannelIntegrations/12_KnowledgeCheck.yml)
- [Mini-Drill](Notes/24_ChannelIntegrations/13_MiniDrill.yml)

---

## Capstone 🏆

### 99. [Capstone — one production-grade agent](Notes/99_Capstone/)
- [Capstone — one production-grade agent](Notes/99_Capstone/00_Overview.md)
- [Track A — Research Assistant](Notes/99_Capstone/01_TrackA_ResearchAssistant.md)
- [Track B — Code Reviewer](Notes/99_Capstone/02_TrackB_CodeReviewer.md)
- [Track C — Personal Knowledge Hub](Notes/99_Capstone/03_TrackC_PersonalKnowledgeHub.md)
- [Shared requirements (all tracks)](Notes/99_Capstone/04_SharedRequirements.md)
- [Dissecting a capstone-shaped sample (travel-concierge)](Notes/99_Capstone/04A_DissectingACapstone.md)
- [Suggested 5-day build plan](Notes/99_Capstone/05_BuildingPlan.md)
- [Self-review checklist — module by module](Notes/99_Capstone/06_SelfReviewChecklist.md)
- [What to do with the capstone after the course](Notes/99_Capstone/07_InProduction.md)
- [Knowledge Check](Notes/99_Capstone/08_KnowledgeCheck.yml)
- [Mini-Drill — the capstone itself](Notes/99_Capstone/09_MiniDrill.yml)

---

## Milestone Drills (cross-concept) 🏁

- 🏁 [M1 — Conversation Server (CLI loop, two tools, persistent todos)](Drills/M1_ConversationServer.md) — after Foundation Track
- 🏁 [M2 — Workflow Editor (legacy vs graph, side by side)](Drills/M2_WorkflowEditor.md) — after Composition Track
- 🏁 [M3 — Federated Travel Planner (Callbacks + MCP + Skills + A2A)](Drills/M3_FederatedPlanner.md) — after Integration Track
- 🏁 [M4 — Auditor with plugins, callbacks, and evals](Drills/M4_AuditorWithEvals.md) — after Runtime Track
- 🏁 [M5 — Capstone (final integration)](Drills/M5_Capstone.md) — see [Notes/99_Capstone/](Notes/99_Capstone/)

---

## Detours (optional, any-time) 🧭

### 🐍 Python deep-dives ([Notes/Detours/](Notes/Detours/))

- [Dataclasses — boilerplate-free record types](Notes/Detours/PY_dataclasses.md)
- [Pydantic v2 — the schema layer ADK speaks](Notes/Detours/PY_pydantic.md)
- [asyncio — async/await, the loop, and run_async](Notes/Detours/PY_async.md)
- [Type hints — what ADK reads to build tool schemas](Notes/Detours/PY_typing.md)
- [contextvars — async-safe per-task locals](Notes/Detours/PY_contextvars.md)
- [Generators — sync, async, and the streaming pattern](Notes/Detours/PY_generators.md)
- [pytest — fixtures, mocks, and what tests do not test](Notes/Detours/PY_testing.md) 🧪
- [logging — stdlib basics and the structlog upgrade](Notes/Detours/PY_logging.md)
- [Packaging — pyproject.toml, uv, and shipping an agent](Notes/Detours/PY_packaging.md)

### ☁️ GCP / 📡 protocol / 📦 framework detours

- [The Gemini payload — Content, Part, Role](Notes/Detours/GeminiPayload.md)
- [FastMCP — the decorator framework for MCP servers](Notes/Detours/FastMCP.md)
- [adk web — the ADK dev UI](Notes/Detours/a2UI.md)
- [ADK 2.0 Visual Builder — drag-and-drop graph authoring](Notes/Detours/VisualBuilder.md)
- [WebSockets — the bidirectional cousin of HTTP](Notes/Detours/WebSockets.md) 🌐
- [Audio encoding — PCM, μ-law, Opus, MP3 and why Live picks PCM](Notes/Detours/AudioEncoding.md) 🔊
- [Audio quantization — bit depth, sample rate, and what breaks ASR](Notes/Detours/AudioQuantization.md) 🔉
- [Protocol Buffers — the schema and the wire format](Notes/Detours/ProtocolBuffers.md) 📦
- [gRPC — HTTP/2 + protobuf + generated stubs](Notes/Detours/gRPC.md) 📡
- [OpenTelemetry — traces, spans, metrics for agents](Notes/Detours/OpenTelemetry.md) 📊
- [Prompt injection — taxonomy and defense patterns](Notes/Detours/PromptInjection.md) ⚠️

### 🌐 Deployment & integration detours

- [Cloud Run — the container target for ADK deployments](Notes/Detours/Cloud_Run.md) ☁️
- [Vertex AI Agent Engine — the managed runtime for ADK](Notes/Detours/AgentEngine.md) ☁️
- [FastAPI for ADK — wrapping and extending adk api_server](Notes/Detours/FastAPI_for_ADK.md) 🌐
- [GCS Signed URLs — direct upload without proxying through your agent](Notes/Detours/SignedUrls_GCS.md) ☁️
- [Slack bots — Events API, scopes, and the response_url pattern](Notes/Detours/Slack_Bots.md) 🌐
- [Google Chat Apps — config, message vs card responses, threading](Notes/Detours/GoogleChat_Apps.md) 🌐
- [Grounding — Search, Enterprise Search, and Agentic RAG](Notes/Detours/Grounding.md) ☁️

---

## Reference

### Cheat sheets ([Reference/CheatSheets/](Reference/CheatSheets/))

- [`LlmAgent(...)` signature](Reference/CheatSheets/llmagent_signature.md)
- [Runner & Session lifecycle](Reference/CheatSheets/runner_session_lifecycle.md)
- [State prefixes](Reference/CheatSheets/state_prefixes.md)
- [`EventActions` fields](Reference/CheatSheets/event_actions.md)
- [Tool authoring](Reference/CheatSheets/tool_authoring.md)
- [Callback signatures](Reference/CheatSheets/callback_signatures.md)
- [A2A vs MCP quickref](Reference/CheatSheets/a2a_mcp_quickref.md)

### Updates ([Notes/Updates/](Notes/Updates/))

- [2026-05 — ADK Python 2.0 GA release-note absorption](Notes/Updates/2026-05_adk-2.0.md)

### Meta

- [Docs snapshot — what version of docs we track](Reference/docs_snapshot.md)
- [Authoring recipe — how to add modules/detours/updates](Notes/_AUTHORING.md)

---

[Home](README.md) · [🗺 Map](MAP.md) · [🤖 Tutor manual](AGENTS.md) · [📍 Progress](PROGRESS.md)
