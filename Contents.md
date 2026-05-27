# 📚 Contents — ADK Python Practical Course

Full flat table of contents. Every module page, every detour, every cheat sheet, every drill, in reading order. Pages marked 🚧 are stubs — the directory exists so navigation does not break, but content has not landed yet.

[Home](README.md) · [🗺 Map](MAP.md) · [🤖 Tutor manual](AGENTS.md) · [📍 Progress](PROGRESS.md) · [📜 Changelog](CHANGELOG.md)

---

## How this is organised

Each module is a folder under `Notes/NN_Topic/` with the canonical skeleton:

```
00_Overview.md            Goals, prereqs, time, sample anchor
01_…NN_…                  Numbered concept pages, one idea each
05_DissectingSample.md    Real-sample read-through (anchor in adk-samples/)
06_InProduction.md        Consolidated real-world callouts for this module
07_KnowledgeCheck.yml     5–7 questions, tutor asks one at a time
08_MiniDrill.yml          Exercise + verification rubric
AGENTS.md                 Module-local teaching notes for the tutor
_figures/                 ASCII diagrams used by this module
```

The four trailing files (`DissectingSample`, `InProduction`, `KnowledgeCheck`, `MiniDrill`) always sit at the end in that order — their numeric prefix shifts up if a module has more concept pages.

---

## Foundation Track

### 0. [Setup](Notes/00_Setup/) 🚧
- [00 Overview](Notes/00_Setup/00_Overview.md) 🚧
- [01 Install & API Key](Notes/00_Setup/01_InstallAndKey.md) 🚧
- [02 Repo Tour](Notes/00_Setup/02_RepoTour.md) 🚧
- [03 First `adk run`](Notes/00_Setup/03_FirstAdkRun.md) 🚧
- [05 Dissecting Sample — `fun-facts`](Notes/00_Setup/05_DissectingSample.md) 🚧
- [06 In Production](Notes/00_Setup/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/00_Setup/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/00_Setup/08_MiniDrill.yml) 🚧

### 1. [Foundations](Notes/01_Foundations/) 🚧
- [00 Overview](Notes/01_Foundations/00_Overview.md) 🚧
- [01 Mental Model](Notes/01_Foundations/01_MentalModel.md) 🚧
- [02 The Agent Loop](Notes/01_Foundations/02_AgentLoop.md) 🚧
- [03 Session & Events](Notes/01_Foundations/03_SessionAndEvents.md) 🚧
- [04 Tools in the Loop](Notes/01_Foundations/04_ToolsInTheLoop.md) 🚧
- [05 Dissecting Sample — `fun-facts` (read)](Notes/01_Foundations/05_DissectingSample.md) 🚧
- [06 In Production](Notes/01_Foundations/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/01_Foundations/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/01_Foundations/08_MiniDrill.yml) 🚧

### 1A. [App &amp; Runner Architecture](Notes/1A_AppAndRunner/) 🚧
- [00 Overview](Notes/1A_AppAndRunner/00_Overview.md) 🚧
- [01 The `App` class — the 2.0 container](Notes/1A_AppAndRunner/01_TheAppClass.md) 🚧
- [02 `on_startup` / `on_shutdown` hooks](Notes/1A_AppAndRunner/02_StartupShutdownHooks.md) 🚧
- [03 `app:` state — the cross-session boundary](Notes/1A_AppAndRunner/03_AppStateBoundary.md) 🚧
- [04 Wiring resumability, caching, compaction](Notes/1A_AppAndRunner/04_ConfigWiring.md) 🚧
- [05 Runner vs App vs Agent — who owns what](Notes/1A_AppAndRunner/05_WhoOwnsWhat.md) 🚧
- [06 Dissecting Sample — App pattern in canonical samples](Notes/1A_AppAndRunner/06_DissectingSample.md) 🚧
- [07 In Production](Notes/1A_AppAndRunner/07_InProduction.md) 🚧
- [08 Knowledge Check](Notes/1A_AppAndRunner/08_KnowledgeCheck.yml) 🚧
- [09 Mini-Drill](Notes/1A_AppAndRunner/09_MiniDrill.yml) 🚧

### 2. [First Agent](Notes/02_FirstAgent/) 🚧
- [00 Overview](Notes/02_FirstAgent/00_Overview.md) 🚧
- [01 `LlmAgent` by hand](Notes/02_FirstAgent/01_LlmAgentByHand.md) 🚧
- [02 `Runner` + `InMemorySessionService`](Notes/02_FirstAgent/02_RunnerAndSession.md) 🚧
- [03 `run_async` & Events](Notes/02_FirstAgent/03_RunAsyncAndEvents.md) 🚧
- [04 Extracting final text](Notes/02_FirstAgent/04_ExtractingText.md) 🚧
- [05 Dissecting Sample — `currency-agent`](Notes/02_FirstAgent/05_DissectingSample.md) 🚧
- [06 In Production](Notes/02_FirstAgent/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/02_FirstAgent/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/02_FirstAgent/08_MiniDrill.yml) 🚧

### 2A. [Agent Config (YAML)](Notes/2A_AgentConfig/) 🚧
- [00 Overview](Notes/2A_AgentConfig/00_Overview.md) 🚧
- [01 Why declarative — Python vs YAML tradeoffs](Notes/2A_AgentConfig/01_WhyDeclarative.md) 🚧
- [02 `adk create` & the `root_agent.yaml` shape](Notes/2A_AgentConfig/02_AdkCreateAndShape.md) 🚧
- [03 Referencing tools & sub-agents from YAML](Notes/2A_AgentConfig/03_ReferencingToolsAndSubAgents.md) 🚧
- [04 What's Python-only (limitations)](Notes/2A_AgentConfig/04_LimitationsToday.md) 🚧
- [05 Round-tripping — Python ↔ YAML](Notes/2A_AgentConfig/05_RoundTripping.md) 🚧
- [06 Dissecting Sample — config-driven agent](Notes/2A_AgentConfig/06_DissectingSample.md) 🚧
- [07 In Production](Notes/2A_AgentConfig/07_InProduction.md) 🚧
- [08 Knowledge Check](Notes/2A_AgentConfig/08_KnowledgeCheck.yml) 🚧
- [09 Mini-Drill](Notes/2A_AgentConfig/09_MiniDrill.yml) 🚧

### 3. [Tools](Notes/03_Tools/) 🚧
- [00 Overview](Notes/03_Tools/00_Overview.md) 🚧
- [01 Why tools](Notes/03_Tools/01_WhyTools.md) 🚧
- [02 `FunctionTool`](Notes/03_Tools/02_FunctionTool.md) 🚧
- [03 `AgentTool` (intro)](Notes/03_Tools/03_AgentAsTool.md) 🚧
- [04 Built-in tools](Notes/03_Tools/04_BuiltInTools.md) 🚧
- [05 Computer Use toolset (preview)](Notes/03_Tools/05_ComputerUse.md) 🚧
- [06 Tool limitations & single-instance constraints](Notes/03_Tools/06_ToolLimitations.md) 🚧
- [07 Dissecting Sample — `currency-agent` / `academic-research`](Notes/03_Tools/07_DissectingSample.md) 🚧
- [08 In Production](Notes/03_Tools/08_InProduction.md) 🚧
- [09 Knowledge Check](Notes/03_Tools/09_KnowledgeCheck.yml) 🚧
- [10 Mini-Drill](Notes/03_Tools/10_MiniDrill.yml) 🚧

### 3A. [Project Structure](Notes/3A_ProjectStructure/) 🚧
- [00 Overview](Notes/3A_ProjectStructure/00_Overview.md) 🚧
- [01 Why structure matters](Notes/3A_ProjectStructure/01_WhyStructureMatters.md) 🚧
- [02 The minimal layout — one `agent.py`](Notes/3A_ProjectStructure/02_MinimalLayout.md) 🚧
- [03 The small layout — agent + tools + prompts split](Notes/3A_ProjectStructure/03_SmallLayout.md) 🚧
- [04 The growing layout — `tools/`, `prompts/`, `sub_agents/` directories](Notes/3A_ProjectStructure/04_GrowingLayout.md) 🚧
- [05 What `adk web` / `adk run` / `adk api_server` expect (discovery rules)](Notes/3A_ProjectStructure/05_AdkCliExpectations.md) 🚧
- [06 What deployment expects (Cloud Run Dockerfile, Agent Engine packing)](Notes/3A_ProjectStructure/06_DeploymentExpectations.md) 🚧
- [07 Shared utilities — `shared/` across multiple agents](Notes/3A_ProjectStructure/07_SharedUtilities.md) 🚧
- [07A Config & env vars — settings class, multi-env, validation](Notes/3A_ProjectStructure/07A_ConfigAndEnvVars.md)
- [08 Eval + tests layout](Notes/3A_ProjectStructure/08_EvalAndTestsLayout.md) 🚧
- [09 Dissecting Sample — a sample with a non-trivial layout](Notes/3A_ProjectStructure/09_DissectingSample.md) 🚧
- [10 In Production](Notes/3A_ProjectStructure/10_InProduction.md) 🚧
- [11 Knowledge Check](Notes/3A_ProjectStructure/11_KnowledgeCheck.yml) 🚧
- [12 Mini-Drill](Notes/3A_ProjectStructure/12_MiniDrill.yml) 🚧

### 4. [Sessions & State](Notes/04_SessionsState/) 🚧
- [00 Overview](Notes/04_SessionsState/00_Overview.md) 🚧
- [01 Session lifecycle](Notes/04_SessionsState/01_SessionLifecycle.md) 🚧
- [02 State scopes (no-prefix · `user:` · `app:` · `temp:`)](Notes/04_SessionsState/02_StateScopes.md) 🚧
- [03 Event deltas](Notes/04_SessionsState/03_EventDeltas.md) 🚧
- [04 Instruction templating (`{var}`, `{var?}`, `output_key=`)](Notes/04_SessionsState/04_InstructionTemplating.md) 🚧
- [05 Context caching (`ContextCacheConfig`)](Notes/04_SessionsState/05_ContextCaching.md) 🚧
- [06 Context compaction (`compaction_interval`, `LlmEventSummarizer`)](Notes/04_SessionsState/06_ContextCompaction.md) 🚧
- [07 Session rewind (`Runner.rewind`)](Notes/04_SessionsState/07_SessionRewind.md) 🚧
- [08 Session migrate (`adk migrate session`, v0→v1)](Notes/04_SessionsState/08_SessionMigrate.md) 🚧
- [09 Dissecting Sample — `llm-auditor/sub_agents/critic`](Notes/04_SessionsState/09_DissectingSample.md) 🚧
- [10 In Production](Notes/04_SessionsState/10_InProduction.md) 🚧
- [11 Knowledge Check](Notes/04_SessionsState/11_KnowledgeCheck.yml) 🚧
- [12 Mini-Drill](Notes/04_SessionsState/12_MiniDrill.yml) 🚧

### 4A. [Artifacts & Heavy Data](Notes/04A_ArtifactsHeavyData/) ☁️ 🚧
- [00 Overview](Notes/04A_ArtifactsHeavyData/00_Overview.md) 🚧
- [01 Why artifacts (vs state, vs context)](Notes/04A_ArtifactsHeavyData/01_WhyArtifacts.md) 🚧
- [02 `ArtifactService` & `InMemoryArtifactService`](Notes/04A_ArtifactsHeavyData/02_ArtifactService.md) 🚧
- [03 `GcsArtifactService` (☁️ GCP-first)](Notes/04A_ArtifactsHeavyData/03_GcsArtifactService.md) 🚧
- [04 Save/load from a tool (`tool_context.save_artifact` / `load_artifact`)](Notes/04A_ArtifactsHeavyData/04_SaveLoadFromTool.md) 🚧
- [05 Multimodal Parts — images, PDFs, audio, video](Notes/04A_ArtifactsHeavyData/05_MultimodalParts.md) 🚧
- [06 Heavy-file handoff between sub-agents](Notes/04A_ArtifactsHeavyData/06_HandoffBetweenAgents.md) 🚧
- [07 Signed URLs & client uploads](Notes/04A_ArtifactsHeavyData/07_SignedUrlsAndUploads.md) 🚧
- [08 Dissecting Sample — multimodal agent](Notes/04A_ArtifactsHeavyData/08_DissectingSample.md) 🚧
- [09 In Production](Notes/04A_ArtifactsHeavyData/09_InProduction.md) 🚧
- [10 Knowledge Check](Notes/04A_ArtifactsHeavyData/10_KnowledgeCheck.yml) 🚧
- [11 Mini-Drill](Notes/04A_ArtifactsHeavyData/11_MiniDrill.yml) 🚧

### 4B. [Human-in-the-Loop &amp; Resume/Cancel](Notes/4B_HumanInTheLoop/) 🛠
- [00 Overview](Notes/4B_HumanInTheLoop/00_Overview.md)
- [01 Why HITL — the three canonical reasons](Notes/4B_HumanInTheLoop/01_WhyHITL.md)
- [02 `ctx.request_confirmation()` — pausing inside a tool](Notes/4B_HumanInTheLoop/02_RequestConfirmation.md)
- [03 `EventActions.requested_tool_confirmations` — the pause event on the wire](Notes/4B_HumanInTheLoop/03_RequestedToolConfirmations.md)
- [04 Resume & Cancel — `runner.run_async(invocation_id=...)` and the dual](Notes/4B_HumanInTheLoop/04_RunnerResumeAndCancel.md)
- [05 `LongRunningFunctionTool` as a HITL primitive](Notes/4B_HumanInTheLoop/05_LongRunningFunctionTool.md)
- [06 `RequestInput` — pause the whole graph for a human](Notes/4B_HumanInTheLoop/06_RequestInputInGraphs.md)
- [07 Ambient Agents — event-triggered runs (Pub/Sub, GCS, Scheduler)](Notes/4B_HumanInTheLoop/07_AmbientAgents.md)
- [08 Frontend-driven approvals — the client owns the approval UI](Notes/4B_HumanInTheLoop/08_FrontendDrivenApprovals.md)
- [09 Chat-platform approvals — Slack & Google Chat as approval surfaces](Notes/4B_HumanInTheLoop/09_ChatPlatformApprovals.md)
- [10 Durable execution integrations — Temporal, Dapr](Notes/4B_HumanInTheLoop/10_DurableExecutionIntegrations.md)
- [11 Dissecting Sample — `ambient-expense-agent`](Notes/4B_HumanInTheLoop/11_DissectingSample.md)
- [12 In Production](Notes/4B_HumanInTheLoop/12_InProduction.md)
- [13 Knowledge Check](Notes/4B_HumanInTheLoop/13_KnowledgeCheck.yml)
- [14 Mini-Drill](Notes/4B_HumanInTheLoop/14_MiniDrill.yml)

### 🏁 [M1 — Conversation Server](Drills/M1_ConversationServer.md) 🚧

---

## Composition Track

### 5. [Multi-Agent](Notes/05_MultiAgent/) 🚧
- [00 Overview](Notes/05_MultiAgent/00_Overview.md) 🚧
- [01 `sub_agents`](Notes/05_MultiAgent/01_SubAgents.md) 🚧
- [02 `transfer_to_agent`](Notes/05_MultiAgent/02_Transfer.md) 🚧
- [03 `AgentTool`](Notes/05_MultiAgent/03_AgentAsTool.md) 🚧
- [04 Sharing state across agents](Notes/05_MultiAgent/04_SharingState.md) 🚧
- [05 Dissecting Sample — `llm-auditor`](Notes/05_MultiAgent/05_DissectingSample.md) 🚧
- [06 In Production](Notes/05_MultiAgent/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/05_MultiAgent/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/05_MultiAgent/08_MiniDrill.yml) 🚧
- [08A LangGraphAgent — wrap a LangGraph workflow](Notes/05_MultiAgent/08A_LangGraphAgent.md)

### 6. [Graph Workflows](Notes/06_GraphWorkflows/) 🚧
- [00 Overview](Notes/06_GraphWorkflows/00_Overview.md) 🚧
- [01 Legacy templates (Seq/Par/Loop)](Notes/06_GraphWorkflows/01_LegacyTemplates.md) 🚧
- [02 Graph intro (nodes & edges)](Notes/06_GraphWorkflows/02_GraphIntro.md) 🚧
- [03 Graph routes & dynamic routing](Notes/06_GraphWorkflows/03_GraphRoutes.md) 🚧
- [04 Human-in-the-loop pauses](Notes/06_GraphWorkflows/04_HumanInTheLoop.md) 🚧
- [05 Dissecting Sample — `workflow-concurrent_research_writer`](Notes/06_GraphWorkflows/05_DissectingSample.md) 🚧
- [06 In Production](Notes/06_GraphWorkflows/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/06_GraphWorkflows/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/06_GraphWorkflows/08_MiniDrill.yml) 🚧

### 🏁 [M2 — Workflow Editor](Drills/M2_WorkflowEditor.md) 🚧

---

## Integration Track

### 7. [Callbacks](Notes/07_Callbacks/) 🚧
- [00 Overview](Notes/07_Callbacks/00_Overview.md) 🚧
- [01 `before/after_model_callback`](Notes/07_Callbacks/01_BeforeAfterModel.md) 🚧
- [02 `before/after_tool_callback`](Notes/07_Callbacks/02_BeforeAfterTool.md) 🚧
- [03 `before/after_agent_callback`](Notes/07_Callbacks/03_BeforeAfterAgent.md) 🚧
- [04 `on_model_error_callback` / `on_tool_error_callback`](Notes/07_Callbacks/04_OnErrorCallbacks.md) 🚧
- [05 `CallbackContext` anatomy — what's accessible, what isn't, common gotchas](Notes/07_Callbacks/05_CallbackContextAnatomy.md) 🚧
- [06 Real-life callback recipe cookbook (caching · rate limiting · redaction · citations · latency budgets · conditional tool exec)](Notes/07_Callbacks/06_CallbackRecipeCookbook.md) 🚧
- [07 Callbacks vs Plugins — when to reach for which](Notes/07_Callbacks/07_CallbacksVsPlugins.md) 🚧
- [08 Dissecting Sample — `llm-auditor/sub_agents/critic`](Notes/07_Callbacks/08_DissectingSample.md) 🚧
- [09 In Production](Notes/07_Callbacks/09_InProduction.md) 🚧
- [10 Knowledge Check](Notes/07_Callbacks/10_KnowledgeCheck.yml) 🚧
- [11 Mini-Drill](Notes/07_Callbacks/11_MiniDrill.yml) 🚧

### 8. [MCP](Notes/08_MCP/) 🚧
- [00 Overview](Notes/08_MCP/00_Overview.md) 🚧
- [01 The MCP protocol](Notes/08_MCP/01_MCPProtocol.md) 🚧
- [02 `MCPToolset`](Notes/08_MCP/02_MCPToolset.md) 🚧
- [03 Transports — stdio / SSE / streamable-HTTP](Notes/08_MCP/03_TransportOptions.md) 🚧
- [04 Serving MCP (with FastMCP)](Notes/08_MCP/04_ServingMCP.md) 🚧
- [05 Dissecting Sample — `travel-planner-google-maps-mcp`](Notes/08_MCP/05_DissectingSample.md) 🚧
- [06 In Production](Notes/08_MCP/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/08_MCP/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/08_MCP/08_MiniDrill.yml) 🚧

### 9. [Skills](Notes/09_Skills/) 🚧
- [00 Overview](Notes/09_Skills/00_Overview.md) 🚧
- [01 Skill anatomy](Notes/09_Skills/01_SkillAnatomy.md) 🚧
- [02 Frontmatter + Script](Notes/09_Skills/02_FrontmatterAndScript.md) 🚧
- [03 `SkillToolset` + `SkillRegistry`](Notes/09_Skills/03_SkillToolset.md) 🚧
- [04 The four invocation patterns](Notes/09_Skills/04_FourPatterns.md) 🚧
- [05 Dissecting Sample — `agent-skills-tutorial`](Notes/09_Skills/05_DissectingSample.md) 🚧
- [06 In Production](Notes/09_Skills/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/09_Skills/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/09_Skills/08_MiniDrill.yml) 🚧

### 10. [A2A](Notes/10_A2A/) 🚧
- [00 Overview](Notes/10_A2A/00_Overview.md) 🚧
- [01 `AgentCard`](Notes/10_A2A/01_AgentCard.md) 🚧
- [02 Exposing via `to_a2a()`](Notes/10_A2A/02_ExposingViaA2A.md) 🚧
- [03 `RemoteA2aAgent`](Notes/10_A2A/03_RemoteA2aAgent.md) 🚧
- [04 A2A vs MCP](Notes/10_A2A/04_A2A_vs_MCP.md) 🚧
- [05 Dissecting Sample — `currency-agent` (A2A side)](Notes/10_A2A/05_DissectingSample.md) 🚧
- [06 In Production](Notes/10_A2A/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/10_A2A/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/10_A2A/08_MiniDrill.yml) 🚧

### 🏁 [M3 — Federated Travel Planner](Drills/M3_FederatedPlanner.md) 🚧

---

## Data & GCP Track

### 10A. [Embeddings & Vector Search](Notes/10A_EmbeddingsVectorSearch/) ☁️ 🚧
- [00 Overview](Notes/10A_EmbeddingsVectorSearch/00_Overview.md) 🚧
- [01 Embedding basics](Notes/10A_EmbeddingsVectorSearch/01_EmbeddingBasics.md) 🚧
- [02 Vertex AI text-embedding models](Notes/10A_EmbeddingsVectorSearch/02_VertexEmbeddingModels.md) 🚧
- [03 Vertex AI Vector Search — index](Notes/10A_EmbeddingsVectorSearch/03_VectorSearchIndex.md) 🚧
- [04 Querying & ANN tradeoffs](Notes/10A_EmbeddingsVectorSearch/04_QueryingANN.md) 🚧
- [05 Dissecting Sample — `RAG`](Notes/10A_EmbeddingsVectorSearch/05_DissectingSample.md) 🚧
- [06 In Production](Notes/10A_EmbeddingsVectorSearch/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/10A_EmbeddingsVectorSearch/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/10A_EmbeddingsVectorSearch/08_MiniDrill.yml) 🚧

### 10B. [RAG Pipeline](Notes/10B_RAGPipeline/) ☁️ 🚧
- [00 Overview](Notes/10B_RAGPipeline/00_Overview.md) 🚧
- [01 RAG concepts](Notes/10B_RAGPipeline/01_RAGConcepts.md) 🚧
- [02 Chunking](Notes/10B_RAGPipeline/02_Chunking.md) 🚧
- [03 Hand-rolled RAG](Notes/10B_RAGPipeline/03_HandRolledRAG.md) 🚧
- [04 Vertex AI RAG Engine](Notes/10B_RAGPipeline/04_VertexAIRAGEngine.md) 🚧
- [05 RAG into ADK](Notes/10B_RAGPipeline/05_RAGintoADK.md) 🚧
- [06 Dissecting RAG Sample](Notes/10B_RAGPipeline/06_DissectingRAGSample.md) 🚧
- [07 In Production](Notes/10B_RAGPipeline/07_InProduction.md) 🚧
- [08 Knowledge Check](Notes/10B_RAGPipeline/08_KnowledgeCheck.yml) 🚧
- [09 Mini-Drill](Notes/10B_RAGPipeline/09_MiniDrill.yml) 🚧

### 10C. [BigQuery for Agents](Notes/10C_BigQueryAgents/) ☁️ 🚧
- [00 Overview](Notes/10C_BigQueryAgents/00_Overview.md) 🚧
- [01 BQ as data source](Notes/10C_BigQueryAgents/01_BQAsDataSource.md) 🚧
- [02 NL2SQL](Notes/10C_BigQueryAgents/02_NL2SQL.md) 🚧
- [03 BQ `VECTOR_SEARCH`](Notes/10C_BigQueryAgents/03_BQVectorSearch.md) 🚧
- [04 `BigQueryAgentAnalyticsPlugin`](Notes/10C_BigQueryAgents/04_AnalyticsPlugin.md) 🚧
- [05 Dissecting Sample — `data-science`](Notes/10C_BigQueryAgents/05_DissectingSample.md) 🚧
- [06 In Production](Notes/10C_BigQueryAgents/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/10C_BigQueryAgents/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/10C_BigQueryAgents/08_MiniDrill.yml) 🚧

---

## Runtime Track

### 11. [Memory](Notes/11_Memory/) 🚧
- [00 Overview](Notes/11_Memory/00_Overview.md) 🚧
- [01 Session vs State vs Memory](Notes/11_Memory/01_SessionVsStateVsMemory.md) 🚧
- [02 `InMemoryMemoryService`](Notes/11_Memory/02_InMemoryMemoryService.md) 🚧
- [03 `VertexAiMemoryBankService`](Notes/11_Memory/03_VertexAiMemoryBank.md) 🚧
- [04 `VertexAiRagMemoryService`](Notes/11_Memory/04_VertexAiRagMemory.md) 🚧
- [05 Dissecting Sample — `load_memory` use](Notes/11_Memory/05_DissectingSample.md) 🚧
- [06 In Production](Notes/11_Memory/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/11_Memory/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/11_Memory/08_MiniDrill.yml) 🚧

### 12. [Code Execution](Notes/12_CodeExecution/) 🚧
- [00 Overview](Notes/12_CodeExecution/00_Overview.md) 🚧
- [01 `UnsafeLocalCodeExecutor` (dev only) ⚠️](Notes/12_CodeExecution/01_UnsafeLocalForDev.md) 🚧
- [02 `BuiltInCodeExecutor`](Notes/12_CodeExecution/02_BuiltInCodeExecutor.md) 🚧
- [03 `ContainerCodeExecutor` / sandbox executors](Notes/12_CodeExecution/03_ContainerAndSandbox.md) 🚧
- [04 Picking the right executor](Notes/12_CodeExecution/04_PickingTheRightOne.md) 🚧
- [05 Dissecting Sample — `data-science`](Notes/12_CodeExecution/05_DissectingSample.md) 🚧
- [06 In Production](Notes/12_CodeExecution/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/12_CodeExecution/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/12_CodeExecution/08_MiniDrill.yml) 🚧

### 13. [Plugins](Notes/13_Plugins/) 🚧
- [00 Overview](Notes/13_Plugins/00_Overview.md) 🚧
- [01 `LoggingPlugin`](Notes/13_Plugins/01_LoggingPlugin.md) 🚧
- [02 `ReflectAndRetryToolPlugin`](Notes/13_Plugins/02_ReflectAndRetry.md) 🚧
- [03 `ContextFilterPlugin`](Notes/13_Plugins/03_ContextFilter.md) 🚧
- [04 Writing a custom plugin](Notes/13_Plugins/04_WritingACustomPlugin.md) 🚧
- [05 Dissecting Sample](Notes/13_Plugins/05_DissectingSample.md) 🚧
- [06 In Production](Notes/13_Plugins/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/13_Plugins/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/13_Plugins/08_MiniDrill.yml) 🚧

### 14. [Evaluation](Notes/14_Evaluation/) 🧪 🚧
- [00 Overview](Notes/14_Evaluation/00_Overview.md) 🚧
- [01 `EvalCase` & `EvalSet`](Notes/14_Evaluation/01_EvalCaseEvalSet.md) 🚧
- [02 `LlmAsJudge`](Notes/14_Evaluation/02_LlmAsJudge.md) 🚧
- [03 `TrajectoryEvaluator`](Notes/14_Evaluation/03_TrajectoryEvaluator.md) 🚧
- [04 `RubricBasedEvaluator` + `HallucinationsV1` + `FinalResponseMatchV1/V2`](Notes/14_Evaluation/04_RubricBasedEvaluator.md) 🚧
- [05 Dissecting Sample — `academic-research/eval/`](Notes/14_Evaluation/05_DissectingSample.md) 🚧
- [06 In Production](Notes/14_Evaluation/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/14_Evaluation/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/14_Evaluation/08_MiniDrill.yml) 🚧

### 🏁 [M4 — Auditor With Evals](Drills/M4_AuditorWithEvals.md) 🚧

---

## Production Track

### 15. [Observability](Notes/15_Observability/) 🚧
- [00 Overview](Notes/15_Observability/00_Overview.md) 🚧
- [01 Structured logging](Notes/15_Observability/01_StructuredLogging.md) 🚧
- [02 ADK built-in telemetry](Notes/15_Observability/02_BuiltInTelemetry.md) 🚧
- [03 OpenTelemetry tracing](Notes/15_Observability/03_OTelTracing.md) 🚧
- [04 Metrics & dashboards](Notes/15_Observability/04_MetricsAndDashboards.md) 🚧
- [05 Dissecting Sample](Notes/15_Observability/05_DissectingSample.md) 🚧
- [06 In Production](Notes/15_Observability/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/15_Observability/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/15_Observability/08_MiniDrill.yml) 🚧

### 16. [Production & Security](Notes/16_ProductionSecurity/) 🚀 🚧
- [00 Overview](Notes/16_ProductionSecurity/00_Overview.md) 🚧
- [01 Auth & `CredentialManager`](Notes/16_ProductionSecurity/01_AuthAndCredentials.md) 🚧
- [02 Secrets handling (Secret Manager + ADC)](Notes/16_ProductionSecurity/02_SecretsHandling.md) 🚧
- [03 Callbacks as policy](Notes/16_ProductionSecurity/03_CallbacksAsPolicy.md) 🚧
- [04 Guardrails cookbook](Notes/16_ProductionSecurity/04_GuardrailsCookbook.md) 🚧
- [05 Prompt-injection defense ⚠️](Notes/16_ProductionSecurity/05_PromptInjectionDefense.md) 🚧
- [06 Agent identity vs controlling-user identity ⚠️](Notes/16_ProductionSecurity/06_AgentIdentityVsUser.md) 🚧
- [07 Gemini-as-Judge safety plugin](Notes/16_ProductionSecurity/07_GeminiAsJudgePlugin.md) 🚧
- [08 Dissecting Sample — `ai-security-agent` / `safety-plugins` / `camel`](Notes/16_ProductionSecurity/08_DissectingSample.md) 🚧
- [09 In Production](Notes/16_ProductionSecurity/09_InProduction.md) 🚧
- [10 Knowledge Check](Notes/16_ProductionSecurity/10_KnowledgeCheck.yml) 🚧
- [11 Mini-Drill](Notes/16_ProductionSecurity/11_MiniDrill.yml) 🚧

### 17. [Advanced Models](Notes/17_AdvancedModels/) 🚧
- [00 Overview](Notes/17_AdvancedModels/00_Overview.md) 🚧
- [01 `LLMRegistry`](Notes/17_AdvancedModels/01_LLMRegistry.md) 🚧
- [02 Gemini, Claude, Gemma](Notes/17_AdvancedModels/02_GeminiClaudeGemma.md) 🚧
- [03 `LiteLlm` & `OpenAILlm`](Notes/17_AdvancedModels/03_LiteLlmAndOpenAI.md) 🚧
- [04 Routing per-agent / per-task](Notes/17_AdvancedModels/04_RoutingPerAgent.md) 🚧
- [05 Planners — `BuiltInPlanner` + `ThinkingConfig`](Notes/17_AdvancedModels/05_PlannersBuiltIn.md) 🚧
- [06 `PlanReActPlanner` & writing a `BasePlanner` subclass](Notes/17_AdvancedModels/06_PlanReActPlanner.md) 🚧
- [07 Dissecting Sample — `gemma-food-tour-guide` / planner samples](Notes/17_AdvancedModels/07_DissectingSample.md) 🚧
- [08 In Production](Notes/17_AdvancedModels/08_InProduction.md) 🚧
- [09 Knowledge Check](Notes/17_AdvancedModels/09_KnowledgeCheck.yml) 🚧
- [10 Mini-Drill](Notes/17_AdvancedModels/10_MiniDrill.yml) 🚧

### 18. [Streaming & Live](Notes/18_StreamingLive/) 🎙 🚧
- [00 Overview](Notes/18_StreamingLive/00_Overview.md) 🚧
- [01 Streaming fundamentals](Notes/18_StreamingLive/01_StreamingFundamentals.md) 🚧
- [02 Gemini Live intro](Notes/18_StreamingLive/02_GeminiLiveIntro.md) 🚧
- [03 Text streaming](Notes/18_StreamingLive/03_TextStreaming.md) 🚧
- [04 Audio I/O](Notes/18_StreamingLive/04_AudioIO.md) 🚧
- [05 Streaming tools (`LongRunningFunctionTool`)](Notes/18_StreamingLive/05_StreamingTools.md) 🚧
- [06 Video input](Notes/18_StreamingLive/06_VideoInput.md) 🚧
- [07 Live production patterns](Notes/18_StreamingLive/07_LiveProductionPatterns.md) 🚧
- [08 Dissecting Live Sample](Notes/18_StreamingLive/08_DissectingLiveSample.md) 🚧
- [09 In Production](Notes/18_StreamingLive/09_InProduction.md) 🚧
- [10 Knowledge Check](Notes/18_StreamingLive/10_KnowledgeCheck.yml) 🚧
- [11 Mini-Drill](Notes/18_StreamingLive/11_MiniDrill.yml) 🚧

### 19. [Internals](Notes/19_Internals/) 🚧
- [00 Overview](Notes/19_Internals/00_Overview.md) 🚧
- [01 Repo Map](Notes/19_Internals/01_RepoMap.md) 🚧
- [02 LlmAgent Source](Notes/19_Internals/02_LlmAgentSource.md) 🚧
- [03 Runner Source](Notes/19_Internals/03_RunnerSource.md) 🚧
- [04 Session & Event Source](Notes/19_Internals/04_SessionEventSource.md) 🚧
- [05 Tool Dispatch](Notes/19_Internals/05_ToolDispatch.md) 🚧
- [06 Workflow Source](Notes/19_Internals/06_WorkflowSource.md) 🚧
- [07 Model Registry](Notes/19_Internals/07_ModelRegistry.md) 🚧
- [08 AutoFlow](Notes/19_Internals/08_AutoFlow.md) 🚧
- [09 Dissecting One Call](Notes/19_Internals/09_DissectingOneCall.md) 🚧
- [10 Tracing One Tool Call](Notes/19_Internals/10_TracingOneToolCall.md) 🚧
- [11 Tracing One State Mutation](Notes/19_Internals/11_TracingOneStateMutation.md) 🚧
- [12 In Production](Notes/19_Internals/12_InProduction.md) 🚧
- [13 Knowledge Check](Notes/19_Internals/13_KnowledgeCheck.yml) 🚧
- [14 Mini-Drill](Notes/19_Internals/14_MiniDrill.yml) 🚧

### 20. [Framework Comparison](Notes/20_FrameworkComparison/) 🚧
- [00 Overview](Notes/20_FrameworkComparison/00_Overview.md) 🚧
- [01 LangChain / LangGraph](Notes/20_FrameworkComparison/01_LangChainLangGraph.md) 🚧
- [02 CrewAI](Notes/20_FrameworkComparison/02_CrewAI.md) 🚧
- [03 AutoGen](Notes/20_FrameworkComparison/03_AutoGen.md) 🚧
- [04 OpenAI Agents SDK](Notes/20_FrameworkComparison/04_OpenAIAgentsSDK.md) 🚧
- [05 PydanticAI & Letta (brief)](Notes/20_FrameworkComparison/05_PydanticAILettaBrief.md) 🚧
- [06 In Production](Notes/20_FrameworkComparison/06_InProduction.md) 🚧
- [07 Knowledge Check](Notes/20_FrameworkComparison/07_KnowledgeCheck.yml) 🚧
- [08 Mini-Drill](Notes/20_FrameworkComparison/08_MiniDrill.yml) 🚧
- [99 Choosing a framework — decision flowchart](Notes/20_FrameworkComparison/99_ChoosingAFramework.md) 🚧

---

## Deployment & Integration Track 🌐

### 21. [ADK API Surface](Notes/21_AdkApiSurface/) 🌐 🚧
- [00 Overview](Notes/21_AdkApiSurface/00_Overview.md) 🚧
- [01 `adk run` — the CLI command](Notes/21_AdkApiSurface/01_AdkRunCli.md) 🚧
- [01A `adk run` under the hood — what it does internally](Notes/21_AdkApiSurface/01A_AdkRunUnderTheHood.md) 🚧
- [01B `adk web` under the hood — dev UI + ASGI mount](Notes/21_AdkApiSurface/01B_AdkWebUnderTheHood.md) 🚧
- [01C The full `adk` CLI family — `run` / `web` / `api_server` / `eval` / `create` / `migrate` / `deploy`](Notes/21_AdkApiSurface/01C_FullCliFamily.md) 🚧
- [02 `adk api_server` — serving the agent as an ASGI/HTTP service](Notes/21_AdkApiSurface/02_AdkApiServer.md) 🚧
- [03 REST shapes — `POST /run`, `GET /sessions`, event JSON shape](Notes/21_AdkApiSurface/03_RestShapes.md) 🚧
- [04 SSE endpoints — streaming events via Server-Sent Events](Notes/21_AdkApiSurface/04_SseEndpoints.md) 🚧
- [05 WebSockets for Live — endpoints for the Live API](Notes/21_AdkApiSurface/05_WebSocketsForLive.md) 🚧
- [06 Wrapping in FastAPI — extending the API with custom routes](Notes/21_AdkApiSurface/06_WrappingInFastAPI.md) 🚧
- [07 Session & Event resources — REST shape](Notes/21_AdkApiSurface/07_SessionAndEventResources.md) 🚧
- [08 Authenticating the API — auth at the API boundary](Notes/21_AdkApiSurface/08_AuthenticatingTheApi.md) 🚧
- [09 Dissecting Sample — a sample served via `adk api_server`](Notes/21_AdkApiSurface/09_DissectingSample.md) 🚧
- [10 In Production](Notes/21_AdkApiSurface/10_InProduction.md) 🚧
- [11 Knowledge Check](Notes/21_AdkApiSurface/11_KnowledgeCheck.yml) 🚧
- [12 Mini-Drill](Notes/21_AdkApiSurface/12_MiniDrill.yml) 🚧

### 22. [Deployment Models](Notes/22_DeploymentModels/) ☁️ 🌐 🚧
- [00 Overview](Notes/22_DeploymentModels/00_Overview.md) 🚧
- [01 Deployment landscape — Cloud Run vs Agent Engine vs GKE summary](Notes/22_DeploymentModels/01_DeploymentLandscape.md) 🚧
- [02 Cloud Run path ☁️ — Dockerfile, `adk deploy cloud_run`, env vars](Notes/22_DeploymentModels/02_CloudRunPath.md) 🚧
- [03 Agent Engine path ☁️ — managed Runtime, `agent_engine_app.py`](Notes/22_DeploymentModels/03_AgentEnginePath.md) 🚧
- [03A GKE ☁️ — workload identity, Helm shape, when GKE wins](Notes/22_DeploymentModels/03A_GKE.md) 🚧
- [04 Session persistence comparison — per-platform persistence](Notes/22_DeploymentModels/04_SessionPersistenceComparison.md) 🚧
- [05 Scaling & cold start — concurrency, cold start](Notes/22_DeploymentModels/05_ScalingAndColdStart.md) 🚧
- [06 Auth & IAM — auth + IAM per platform](Notes/22_DeploymentModels/06_AuthAndIAM.md) 🚧
- [07 Observability wiring — OTel wiring per platform](Notes/22_DeploymentModels/07_ObservabilityWiring.md) 🚧
- [08 Secrets across platforms — secrets per platform](Notes/22_DeploymentModels/08_SecretsAcrossPlatforms.md) 🚧
- [09 Cost model comparison — cost model side-by-side](Notes/22_DeploymentModels/09_CostModelComparison.md) 🚧
- [10 Dissecting Sample — anchored to `adk-ae-oauth`](Notes/22_DeploymentModels/10_DissectingSample.md) 🚧
- [11 In Production](Notes/22_DeploymentModels/11_InProduction.md) 🚧
- [12 Knowledge Check](Notes/22_DeploymentModels/12_KnowledgeCheck.yml) 🚧
- [13 Mini-Drill](Notes/22_DeploymentModels/13_MiniDrill.yml) 🚧

### 23. [Frontend Integration](Notes/23_FrontendIntegration/) 🌐 🚧
- [00 Overview](Notes/23_FrontendIntegration/00_Overview.md) 🚧
- [01 Who owns `user_id` & `session_id`?](Notes/23_FrontendIntegration/01_WhoOwnsIds.md) 🚧
- [02 Session lifecycle from the client](Notes/23_FrontendIntegration/02_SessionLifecycle.md) 🚧
- [03 Calling `/run` from a SPA (REST)](Notes/23_FrontendIntegration/03_CallingRunFromSpa.md) 🚧
- [04 Consuming SSE for streaming responses](Notes/23_FrontendIntegration/04_ConsumingSse.md) 🚧
- [05 WebSockets from the browser (Live)](Notes/23_FrontendIntegration/05_WebSocketsFromBrowser.md) 🚧
- [06 A2UI from the client side](Notes/23_FrontendIntegration/06_A2UIFromClient.md) 🚧
- [07 Auth context propagation (Firebase, OIDC, IAP)](Notes/23_FrontendIntegration/07_AuthContextPropagation.md) 🚧
- [08 When is A2A the right client-side answer?](Notes/23_FrontendIntegration/08_WhenA2AForClients.md) 🚧
- [09 Dissecting Sample — `adk web` UI as reference client](Notes/23_FrontendIntegration/09_DissectingSample.md) 🚧
- [10 In Production](Notes/23_FrontendIntegration/10_InProduction.md) 🚧
- [11 Knowledge Check](Notes/23_FrontendIntegration/11_KnowledgeCheck.yml) 🚧
- [12 Mini-Drill](Notes/23_FrontendIntegration/12_MiniDrill.yml) 🚧

### 24. [Channel Integrations](Notes/24_ChannelIntegrations/) 🌐 🚧
- [00 Overview](Notes/24_ChannelIntegrations/00_Overview.md) 🚧
- [01 The webhook → Runner adapter pattern](Notes/24_ChannelIntegrations/01_WebhookAdapter.md) 🚧
- [02 Mapping channel users → ADK `user_id`](Notes/24_ChannelIntegrations/02_MappingChannelUsers.md) 🚧
- [03 Slack bot integration](Notes/24_ChannelIntegrations/03_SlackBot.md) 🚧
- [04 Google Chat app integration](Notes/24_ChannelIntegrations/04_GoogleChatApp.md) 🚧
- [05 Discord (briefly) + general pattern](Notes/24_ChannelIntegrations/05_DiscordAndGeneral.md) 🚧
- [06 Long-running responses on chat platforms](Notes/24_ChannelIntegrations/06_LongRunningOnChat.md) 🚧
- [07 Dissecting Sample — chat adapter](Notes/24_ChannelIntegrations/07_DissectingSample.md) 🚧
- [08 In Production](Notes/24_ChannelIntegrations/08_InProduction.md) 🚧
- [09 Knowledge Check](Notes/24_ChannelIntegrations/09_KnowledgeCheck.yml) 🚧
- [10 Mini-Drill](Notes/24_ChannelIntegrations/10_MiniDrill.yml) 🚧

---

## Capstone

### 99. [Capstone — M5 Production-Grade Agent](Notes/99_Capstone/) 🏆 🚧
- [00 Overview & track selection (A / B / C)](Notes/99_Capstone/00_Overview.md) 🚧
- [01 Track A — Research Assistant](Notes/99_Capstone/01_TrackA_ResearchAssistant.md) 🚧
- [02 Track B — Code Reviewer](Notes/99_Capstone/02_TrackB_CodeReviewer.md) 🚧
- [03 Track C — Personal Knowledge Hub](Notes/99_Capstone/03_TrackC_PersonalKnowledgeHub.md) 🚧
- [04 Shared Requirements](Notes/99_Capstone/04_SharedRequirements.md) 🚧
- [04A Dissecting a capstone (travel-concierge)](Notes/99_Capstone/04A_DissectingACapstone.md) 🚧
- [05 Building Plan](Notes/99_Capstone/05_BuildingPlan.md) 🚧
- [06 Self-Review Checklist](Notes/99_Capstone/06_SelfReviewChecklist.md) 🚧
- [07 In Production](Notes/99_Capstone/07_InProduction.md) 🚧
- [08 Knowledge Check](Notes/99_Capstone/08_KnowledgeCheck.yml) 🚧
- [09 Mini-Drill — the capstone itself](Notes/99_Capstone/09_MiniDrill.yml) 🚧

---

## Milestone Drills (cross-concept)

- 🏁 [M1 — Conversation Server](Drills/M1_ConversationServer.md) 🚧 — after Foundation Track
- 🏁 [M2 — Workflow Editor](Drills/M2_WorkflowEditor.md) 🚧 — after Composition Track
- 🏁 [M3 — Federated Travel Planner](Drills/M3_FederatedPlanner.md) 🚧 — after Integration Track
- 🏁 [M4 — Auditor With Evals](Drills/M4_AuditorWithEvals.md) 🚧 — after Runtime Track
- 🏁 [M5 — Capstone](Drills/M5_Capstone.md) 🚧 — see [Notes/99_Capstone/](Notes/99_Capstone/)

---

## Detours (optional, any-time) 🧭

### 🐍 Python deep-dives ([Notes/Detours/](Notes/Detours/))

- [PY_dataclasses](Notes/Detours/PY_dataclasses.md) 🚧
- [PY_pydantic](Notes/Detours/PY_pydantic.md) 🚧
- [PY_async](Notes/Detours/PY_async.md) 🚧
- [PY_typing](Notes/Detours/PY_typing.md) 🚧
- [PY_contextvars](Notes/Detours/PY_contextvars.md) 🚧
- [PY_generators](Notes/Detours/PY_generators.md) 🚧
- [PY_testing](Notes/Detours/PY_testing.md) 🚧 🧪
- [PY_logging](Notes/Detours/PY_logging.md) 🚧
- [PY_packaging](Notes/Detours/PY_packaging.md) 🚧

### ☁️ GCP / 📡 protocol / 📦 framework detours

- [GeminiPayload](Notes/Detours/GeminiPayload.md) 🚧
- [FastMCP](Notes/Detours/FastMCP.md) 🚧
- [a2UI](Notes/Detours/a2UI.md) 🚧
- [VisualBuilder](Notes/Detours/VisualBuilder.md) 🚧
- [WebSockets](Notes/Detours/WebSockets.md) 🚧 🌐
- [AudioEncoding](Notes/Detours/AudioEncoding.md) 🚧 🔊
- [AudioQuantization](Notes/Detours/AudioQuantization.md) 🚧 🔉
- [ProtocolBuffers](Notes/Detours/ProtocolBuffers.md) 🚧 📦
- [gRPC](Notes/Detours/gRPC.md) 🚧 📡
- [OpenTelemetry](Notes/Detours/OpenTelemetry.md) 🚧 📊
- [PromptInjection](Notes/Detours/PromptInjection.md) 🚧 ⚠️

### 🌐 Deployment & integration detours

- [Cloud_Run](Notes/Detours/Cloud_Run.md) 🚧 ☁️
- [AgentEngine](Notes/Detours/AgentEngine.md) 🚧 ☁️
- [FastAPI_for_ADK](Notes/Detours/FastAPI_for_ADK.md) 🚧 🌐
- [SignedUrls_GCS](Notes/Detours/SignedUrls_GCS.md) 🚧 ☁️
- [Slack_Bots](Notes/Detours/Slack_Bots.md) 🚧 🌐
- [GoogleChat_Apps](Notes/Detours/GoogleChat_Apps.md) 🚧 🌐
- [Grounding](Notes/Detours/Grounding.md) 🚧 ☁️

---

## Reference

### Cheat sheets ([Reference/CheatSheets/](Reference/CheatSheets/))

- [`LlmAgent` signature](Reference/CheatSheets/llmagent_signature.md)
- [Runner & session lifecycle](Reference/CheatSheets/runner_session_lifecycle.md)
- [State prefixes](Reference/CheatSheets/state_prefixes.md)
- [`EventActions` fields](Reference/CheatSheets/event_actions.md)
- [Tool authoring](Reference/CheatSheets/tool_authoring.md)
- [Callback signatures](Reference/CheatSheets/callback_signatures.md)
- [A2A vs MCP quickref](Reference/CheatSheets/a2a_mcp_quickref.md)

### Updates ([Notes/Updates/](Notes/Updates/))

- [2026-05 — ADK 2.0 GA absorption](Notes/Updates/2026-05_adk-2.0.md)

### Meta

- [Docs snapshot — what version of docs we track](Reference/docs_snapshot.md)
- [Authoring recipe — how to add modules/detours/updates](Notes/_AUTHORING.md)
- [Template module — the copyable skeleton](Notes/_TEMPLATE_MODULE/)

---

[Home](README.md) · [🗺 Map](MAP.md) · [🤖 Tutor manual](AGENTS.md) · [📍 Progress](PROGRESS.md)
