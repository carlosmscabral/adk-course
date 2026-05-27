# 📜 CHANGELOG

All notable changes to this course will be documented here. Follows a loose [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) shape; one bump per phase + one bump per absorbed ADK release.

---

## [0.3.4] - 2026-05-27

Dogfood Wave 3. Six parallel verification agents (read-only, `git status` clean post-run) covered the modules and detours 0.3.2/0.3.3 did not sample: 10A Embeddings, 10B RAG, 15 Observability, 19 Internals, 20 Framework Comparison, 22 Deployment, 24 Channel Integrations, 99 Capstone, and detours Grounding / OpenTelemetry / WebSockets / gRPC. Same severity rubric as prior waves. Five parallel fix agents then corrected 23 files surgically against `/home/carloscabral/study/adk-python/src/`. Both 🔴 and 🟡 landed in this bump (no split — the residue is small enough).

### Fixed
- **Pub/Sub trigger route** — real path is `/apps/{app_name}/trigger/pubsub`, not `/trigger/pubsub` (`cli/trigger_routes.py:401`). `user_id` is derived from the subscription resource name: `subscription.replace("/", "--")` (`trigger_routes.py:414-415`). Nine mentions updated across `Notes/24_ChannelIntegrations/07_AmbientAgentsAsChannels.md` (5) and `10_DissectingSample.md` (4); user_id note added once per file.
- **`BigQueryAgentAnalyticsPlugin` import path** — corrected from fabricated `google.adk.plugins.analytics.bigquery` to real `google.adk.plugins.bigquery_agent_analytics_plugin` (`plugins/bigquery_agent_analytics_plugin.py:1967`). Affected `Notes/22_DeploymentModels/07_ObservabilityWiring.md`.
- **19 Internals line-citation drift** — `base_session_service.py:141` → `:114` (four occurrences across `09_DissectingOneCall.md`, `11_TracingOneStateMutation.md`: `async def append_event` is at line 114, not 141). `llm_agent.py:340` → `:294` for the `tools` field declaration in `02_LlmAgentSource.md`. Other Internals citations spot-verified and confirmed accurate.
- **Capstone API name drift** — `FinalResponseMatchV1` → `FinalResponseMatchV2Evaluator` (metric key `final_response_match_v2`; class at `evaluation/final_response_match_v2.py:130`; registered at `metric_evaluator_registry.py:148-149`). `WorkflowAgent` → `Workflow` (real export at `workflow/_workflow.py:148`, re-exported in `google/adk/__init__.py`). Brief incorrectly identified the class as `RougeEvaluator` — that's the legacy v1 evaluator; agent flagged and used the correct v2 class. Affected `Notes/99_Capstone/01_TrackA_ResearchAssistant.md`, `04_SharedRequirements.md`.
- **Vertex AI RAG Engine GA migration** — preview surface (`vertexai.preview.rag`, flat `embedding_model_config=` / `chunk_size=` kwargs) replaced with GA surface (`vertexai.rag` with `backend_config=RagVectorDbConfig(rag_embedding_model_config=RagEmbeddingModelConfig(vertex_prediction_endpoint=VertexPredictionEndpoint(...)))` and `transformation_config=TransformationConfig(chunking_config=ChunkingConfig(chunk_size=, chunk_overlap=))`). Default embedding model now `gemini-embedding-001`. ⚠️ Preview-era callout added to `06_DissectingRAGSample.md` since the `adk-samples/python/agents/RAG/` sample still pins the preview namespace (verified at `agent.py:26`, `prepare_corpus_and_data.py:23,64`). Affected `Notes/10B_RAGPipeline/04_VertexAIRAGEngine.md`, `06_DissectingRAGSample.md`.
- **Embedding model deprecation** — `text-embedding-004` deprecated 2026-01-14; `text-embedding-005` is legacy. Recommended default is `gemini-embedding-001` (3072 dims, supports `task_type`). Switching model families requires re-embedding the entire corpus. Callouts added in `Notes/10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings.md` (model table reordered) and `06_DissectingSample.md` (flag without rewriting quoted sample); model swapped in `04_BuildingAnIndex.md` and `Notes/10B_RAGPipeline/03_HandRolledRAG.md`. Default index dimensions bumped 768 → 3072.
- **IndexDatapoint proto note** — added one-line clarification in `Notes/10A_EmbeddingsVectorSearch/04_BuildingAnIndex.md` that Vector Search `upsert_datapoints` takes `IndexDatapoint` proto objects (`from google.cloud.aiplatform_v1 import IndexDatapoint`), not dicts.
- **`LoggingPlugin` output format** — corrected from implied structured JSON to actual ANSI-colored stdout via `print(f"\033[90m...\033[0m")` (`plugins/logging_plugin.py:284-288`). Course now points students at `structlog` / `logging.dictConfig` for production. Affected `Notes/15_Observability/02_StructuredLogging.md`.
- **OpenTelemetry span attribute names** — replaced generic placeholders with the actual GenAI-semconv-compliant attribute names ADK emits: `gen_ai.request.model`, `gen_ai.usage.input_tokens`/`output_tokens`, `gen_ai.agent.name`, `gen_ai.tool.name`, plus GCP-specific `gcp.vertex.agent.session_id` and `gcp.vertex.agent.invocation_id` (`telemetry/tracing.py:44-58, 331-334`). Affected `Notes/15_Observability/04_TracingAnAgentRun.md`, `05_Metrics.md`.
- **Grounding multi-tool restriction inverted** — `google_search` cannot be combined with other tools on **Gemini 1.x** only (`tools/google_search_tool.py:74-78`); on 2.x the check is bypassed, and `bypass_multi_tools_limit` flag exists (`:42`). Course previously stated the inverse. Fixed prose at L69 and the flowchart at L175 in `Notes/Detours/Grounding.md`.
- **OpenAI Agents SDK idiom** — `handoffs=[handoff(researcher)]` → `handoffs=[researcher]` with inline note that `sub_agents=` is ADK terminology and `handoff(...)` wrapping is only for customization. Affected `Notes/20_FrameworkComparison/05_OpenAIAgentsSDK.md`.
- **Pydantic AI idiom** — `system_prompt="..."` → `instructions="..."` (newer preferred form in pydantic-ai 0.0.40+; both kwargs still exist). Affected `Notes/20_FrameworkComparison/06_PydanticAI.md`.
- **OpenTelemetry exporter install note** — `opentelemetry-sdk` only ships the SDK + console exporter; OTLP needs separate `pip install opentelemetry-exporter-otlp`. Install callout added to `Notes/Detours/OpenTelemetry.md`.
- **WebSockets 64KB claim** — RFC 6455 allows payloads up to 2^63 bytes; "64 KB" was a library-default fragment size, not a protocol limit. Python `websockets` library defaults to `max_size=2**20` (1 MiB), tunable via `max_size`/`write_limit`. Affected `Notes/Detours/WebSockets.md`.
- **gRPC HTTP/2 frame diagram** — replaced conflated HEADERS/DATA frame depiction with correct sequence: opening HEADERS (`:path`), interleaved bidirectional DATA frames, trailing HEADERS with `grpc-status`. Caption clarifies single bidi RPC = one stream id with bidirectional frames. Affected `Notes/Detours/gRPC.md`.

### Verified-only (no edits required)
- **Skills knowledge check Q2** — brief said Q2 cited 3 invocation patterns; actual Q2 is about the 3 SkillToolset auto-exposed tools (`list_skills`, `load_skill`, `load_skill_resource`), which is correct per source (`skill_toolset.py:93,186,262`). Q4 already correctly says 4 invocation patterns matching `00_Overview.md`. No fix needed.
- **`Notes/11_Memory/03_VertexAIMemoryBank.md` model pin** — already uses `gemini-2.5-flash`, the dominant in-course model (256 occurrences vs 32 for 2.5-pro). No change.

### Method
- **Wave 3 dogfood** (read-only): 6 parallel agents covered 10A/B, 15, 19, 20, 22/24, 99, and 4 detours. `git status` clean post-run.
- **🔴 + 🟡 combined fix wave**: 5 parallel fix agents with non-overlapping file scopes:
  - **A** — 24 Channel Integrations Pub/Sub + 22 BQ import
  - **B** — 19 Internals citations + 99 Capstone class names
  - **C** — 10B Vertex AI RAG Engine GA migration
  - **D** — 10A embeddings deprecation + 15 OTel/Logging plumbing
  - **E** — Grounding inversion + framework idioms + detour 🟡s
- **Brief deviations followed source**:
  1. Capstone v2 evaluator class is `FinalResponseMatchV2Evaluator` (not `RougeEvaluator`, which is the legacy v1).
  2. Pub/Sub mentions were 9 across two files, not "~5" as estimated in the brief.
  3. Skills Q2 was already correct; the inverted-count claim was a Wave-3 dogfood misread.

### Why
- User: "let's dispatch" — fire all Wave 3 fixes (🔴 and 🟡 together, residue small enough not to split).

---

## [0.3.3] - 2026-05-27

🟡 second pass after dogfood Wave 2. Four parallel fix agents corrected the imprecise-but-not-broken drift items deferred from 0.3.2. Same source-grounded methodology against `/home/carloscabral/study/adk-python/src/` plus the `a2a-sdk` source for the A2A path/scheme fixes.

### Fixed
- **A2A well-known path** — modern canonical path is `/.well-known/agent-card.json` (`AGENT_CARD_WELL_KNOWN_PATH` in `a2a/utils/constants.py:3`); `/.well-known/agent.json` is the legacy fallback (`PREV_AGENT_CARD_WELL_KNOWN_PATH`). `RemoteA2aAgent` imports the new path from the a2a-sdk (`remote_a2a_agent.py:51-54`). One 🪧 callout in `02_AgentCard.md` documents the fallback. Note: the on-disk filename `agent.json` for `adk api_server --a2a` directory mode (`fast_api.py:669-694`) is a separate concept and stays as-is. Affected `Notes/10_A2A/01_WhatIsA2A.md`, `02_AgentCard.md`, `03_ServeWithToA2a.md`, `04_ConsumeWithRemoteA2aAgent.md`, `05_A2A_vs_MCP.md`, `06_DissectingSample.md`, `07_InProduction.md`, `08_KnowledgeCheck.yml`, `09_MiniDrill.yml`, `AGENTS.md`.
- **A2A `SecurityScheme` is a union, not a constructor** — concrete classes: `HTTPAuthSecurityScheme`, `APIKeySecurityScheme`, `OAuth2SecurityScheme`, `OpenIdConnectSecurityScheme`, `MutualTLSSecurityScheme` (`a2a/types.py:1524-1538`). Fields are snake_case (`bearer_format`, not `bearerFormat`); `HTTPAuthSecurityScheme(scheme=, bearer_format=, type='http')` (`a2a/types.py:447-470`). Affected `Notes/10_A2A/02_AgentCard.md`, `07_InProduction.md`.
- **`SkillRegistry` ABC signatures are keyword-only** — `async def get_skill(self, *, name: str) -> Skill` and `async def search_skills(self, *, query: str) -> list[Frontmatter]` (`skills/skill_registry.py:29-54`). `get_skill` **raises** on missing name, doesn't return `None`. Concrete GCS impl confirms return types (`integrations/skill_registry/gcp_skill_registry.py:51,73`). Call sites updated to keyword form (`registry.search_skills(query=...)`). Affected `Notes/09_Skills/04_SkillRegistry.md`, `02_SkillAnatomy.md`, `07_KnowledgeCheck.yml`.
- **Skills frontmatter accepts `allowed-tools` alias** — `Frontmatter` Pydantic model uses `ConfigDict(populate_by_name=True)` and `alias="allowed-tools"` / `serialization_alias="allowed-tools"` on the `allowed_tools` field (`skills/models.py:56-69`). Added one-line note in `02_SkillAnatomy.md`.
- **`VertexAiMemoryBankService.agent_engine_id` expects bare ID** — source `vertex_ai_memory_bank_service.py:220-226` **warns** (not rejects) when the value contains `/`, then concatenates it into `'reasoningEngines/' + agent_engine_id`, producing a double-prefixed malformed path that fails at API call time. Page now shows `agent_engine_id="456"` with an inline `api_resource.name.split('/')[-1]` extraction comment. Affected `Notes/11_Memory/03_VertexAIMemoryBank.md`.
- **`app_engine_id` typo** → `agent_engine_id` in `Notes/11_Memory/06_DissectingMemoryBank.md` L77.
- **`--staging_bucket` is deprecated** — `cli_tools_click.py:1559-1569` emits `WARNING: --staging_bucket is deprecated and will be removed`; `:2256-2260` flag help text is `"Deprecated. This argument is no longer required or used."` Modern shape is `client.agent_engines.create(config=...)`. Added ⚠️ deprecation callout adjacent to the use. Affected `Notes/22_DeploymentModels/03_AgentEnginePath.md`.
- **Google Chat JWT issuer link** — verified `chat@system.gserviceaccount.com` is current via [verify-requests-from-chat docs](https://developers.google.com/workspace/chat/verify-requests-from-chat); no code change, added 🪧 link callout pointing at the official source. Affected `Notes/Detours/GoogleChat_Apps.md`.

### Verified-only (no edits required)
- `Notes/Detours/a2UI.md` CLI flags were already fixed in 0.3.2 (`--session_service_uri`, `--reload_agents`).

### Method
- **🟡 fix wave**: 4 parallel agents with non-overlapping file scopes (module 09 / module 10 / module 11 / cross-cutting 22+Detours). Brief was wrong on two items where source contradicted it; agents flagged and followed source:
  1. `get_skill` raises on missing name (brief implied `-> Skill | None`).
  2. The `agent_engine_id` validator only **warns** with `/` in the value — does not reject; failure surfaces downstream at the API call.
- **Out-of-original-scope catch**: Wave 2E agent flagged `Notes/10_A2A/07_InProduction.md` had the same `SecurityScheme` + path drift outside the brief's explicit file list. Picked up post-agent in this bump.

### Why
- User: "let's go" — dispatch the 🟡 wave deferred at end of 0.3.2. This closes the dogfood Wave 2 cycle (0.3.1 → 0.3.2 → 0.3.3).

---

## [0.3.2] - 2026-05-27

Dogfood Wave 2. Six parallel verification agents (read-only, `git status` clean post-run) covered the modules 0.3.1 did not sample: 06 Graph Workflows, 07 Callbacks, 08 MCP, 2A Agent Config, 10C BigQuery, 12 Code Execution, 13 Plugins, 14 Evaluation, 16 Production & Security, 17 Advanced Models, 18 Streaming & Live, and the VisualBuilder / a2UI / FastMCP detours. Same severity rubric as 0.3.1 (🔴 wrong shape, won't run / 🟡 drifted / 🟢 verified). Five parallel fix agents then corrected ~51 files surgically against `/home/carloscabral/study/adk-python/src/`. Only the 🔴 wave landed in this bump; 🟡 stays pending for the next pass.

### Fixed
- **Graph workflow API path** — real import is `from google.adk.workflow import Workflow, START` (not `google.adk.agents.workflow.WorkflowAgent`). `FunctionNode` + `@node` decorator are the public surface; `_ParallelWorker` is private. `Event` lives at `google.adk.events`. Real resume API is `runner.run_async(invocation_id=..., new_message=...)`. Worst offender because `AGENTS.md` doubled down on the wrong path; reversed. Affected all of `Notes/06_GraphWorkflows/` plus `Detours/VisualBuilder.md`.
- **`FunctionNode.rerun_on_resume` does exist** (brief was wrong) — `_function_node.py:174` shows `rerun_on_resume: bool = False`; workflow-level default is `True`, per-node default is `False`. Kept kwarg in examples with the scope note.
- **Sample-version skew** — `workflow-*`, `agent-skills-tutorial`, `financial-advisor` samples pin `google-adk<2.0.0`; flagged in 06's sample-anchor table so students don't read 1.x APIs as canonical.
- **`adk create` flags** — real flags are `--api_key`, `--project`, `--region` (no `google-` prefix). Source: `cli_tools_click.py:436-498`. Affected `Notes/2A_AgentConfig/03_AdkCreateCli.md`.
- **`LlmAgentConfig` is `extra='forbid'`** — unknown YAML keys (e.g., `global_instruction:`) raise validation errors at load; `_ADK_AGENT_CLASSES = {"LlmAgent", "LoopAgent", "ParallelAgent", "SequentialAgent"}` (no `WorkflowAgent`; graphs are Python-only). `ToolConfig` accepts only `name:` + `args:` — no `toolset:`/`class:` discriminator. Affected `Notes/2A_AgentConfig/02_RootAgentYaml.md`, `04_ToolReferences.md`, `07_PythonOnlyFeatures.md`, `01_WhyDeclarative.md`.
- **Callbacks DO stack per agent** — `BeforeModelCallback: TypeAlias = Union[_SingleBeforeModelCallback, list[_SingleBeforeModelCallback]]` (llm_agent.py:75-87). Pages and `AGENTS.md` previously claimed otherwise. Affected `Notes/07_Callbacks/05_CallbackContextAnatomy.md`, `06_CallbackRecipeCookbook.md`, `07_CallbacksVsPlugins.md`, `AGENTS.md`.
- **`ToolContext` and `CallbackContext` are aliases of the same class** — `ToolContext = Context` (tool_context.py:29), `CallbackContext = Context` (callback_context.py:22). Not subclasses. `ctx.session_id` is not real; use `ctx.session.id`.
- **Plugin imports + signatures** — `ContextFilterPlugin` and `GlobalInstructionPlugin` are not in `plugins/__init__.py __all__`; deep imports required. `GlobalInstructionPlugin(global_instruction=...)` kwarg, not `instruction=`. Real plugin hook names are `_callback`-suffixed. Affected `Notes/13_Plugins/01_WhatIsAPlugin.md`, `04_ContextFilterPlugin.md`, `05_GlobalInstructionPlugin.md`.
- **MCP lifecycle — Runner auto-closes toolsets** — `runners.py:2094-2144` (`_cleanup_toolsets`). Use `await runner.close()` with try/finally; `MCPToolset` is NOT an async context manager (no `__aenter__`/`__aexit__`). Affected `Notes/08_MCP/04_LifecycleManagement.md`, `07_InProduction.md`, `08_KnowledgeCheck.yml`, `09_MiniDrill.yml`, `AGENTS.md`, `Notes/10_A2A/03_ServeWithToA2a.md`.
- **MCP auth headers** — fabricated `tool_context.headers["Authorization"]` replaced with real `MCPToolset(header_provider=...)` recipe (`mcp_toolset.py:112-114`, `mcp_tool.py:386-398`).
- **`FastMCP` detour imports** — `MCPToolset, StdioConnectionParams` from `google.adk.tools.mcp_tool`; `StdioServerParameters` from `mcp` itself; example wraps params in `StdioConnectionParams(server_params=..., timeout=10.0)`.
- **`adk web` flags** — `--session_service_uri` (not `--session-service`), `--reload_agents` (not `--reload` for agent-code reload; `--reload` toggles the server). Affected `Detours/a2UI.md`.
- **Evaluation API shapes** — `LlmAsJudge` is an abstract base, config-driven via `judge_model_options.judge_model` (NOT `LlmAsJudge(model=...)`); real `__init__(self, eval_metric, criterion_type, expected_invocations_required=False)`. `RubricBasedEvaluator` constructor takes config, not `rubric=[...]`. Affected `Notes/14_Evaluation/04_LlmAsJudge.md`, `05_RubricBasedEvaluator.md`.
- **`adk eval` flags** — first positional is a DIRECTORY; real flags are `--config_file_path`, `--print_detailed_results`, `--eval_storage_uri`, `--log_level`. `--num_runs`, `--output_dir`, `--config_path` were fabricated. Affected `Notes/14_Evaluation/08_AdkEvalCli.md`.
- **Five evaluator types, not four** — `00_Overview.md` count fixed. `RougeEvaluator` (real class) has metric name `response_match_score`; surfaced as a 🪧 Naming callout.
- **`ContainerCodeExecutor` real kwargs** — only `base_url`, `image`, `docker_path`; dropped fictional `network`, `timeout_seconds`, `mem_limit`. **`GkeCodeExecutor` real fields** — `kubeconfig_path`, `kubeconfig_context`, `image`, `namespace`, `executor_type`, `cpu_limit`; no `service_account` (use Workload Identity binding via gcloud + kubectl annotate). Affected `Notes/12_CodeExecution/05_ContainerAndGke.md`.
- **Auth API real shape** — `BaseAuthenticatedTool` subclass + `tool_context.request_credential(auth_config)` / `get_auth_response(auth_config)` two-turn flow (`context.py:679, 696`). `@requires_auth` decorator and `tool_context.auth_state` do NOT exist. `BaseAuthenticatedTool` subclass overrides `_run_async_impl(args, tool_context, credential)`. Affected `Notes/16_ProductionSecurity/03_Authentication.md`, `10_InProduction.md`.
- **Streaming requires opt-in** — `runner.run_async()` default is `StreamingMode.NONE` (run_config.py); text streaming needs `run_config=RunConfig(streaming_mode=StreamingMode.SSE)`. Affected `Notes/18_StreamingLive/01_StreamingFundamentals.md`, `03_TextStreaming.md`, `11_MiniDrill_TextStream.yml`.
- **`LongRunningFunctionTool` is deferred-result, not async-generator** — `function_call_id` round-trip; tool returns `{"status": "pending", "job_id": ...}`; worker replays `function_response` with matching id (`function_tool.py:213-274`, `auth_tool.py:141-148`). Yield-progress pattern is the common fabrication. `_call_live(input_stream=...)` is the LIVE-only streaming-INPUT path, separate concern. Affected `Notes/18_StreamingLive/05_StreamingTools.md`.
- **`LLMRegistry.register(llm_cls)` is single-arg** — class implements `supported_models() -> list[str]` regex patterns classmethod (`registry.py:99-107`, `base_llm.py:45`). Two-arg `register("name", cls)` and `LLMRegistry.list_models()` were fabricated; real lookup is `LLMRegistry.resolve(model)`. Class is `Claude` (NOT `ClaudeLlm`), subclass of `AnthropicLlm` (anthropic_llm.py:716). Affected `Notes/17_AdvancedModels/01_LLMRegistry.md`, `14_MiniDrill.yml`.
- **BigQuery WriteMode default** — `BLOCKED` (config.py:56); `maximum_bytes_billed` IS first-class on `BigQueryToolConfig` (config.py:63-69, `>=10_485_760` validator). Page previously claimed unsafe default. Affected `Notes/10C_BigQueryAgents/03_BigQueryAsTool.md`, `07_InProduction.md`, `AGENTS.md`.
- **`adk web --builder` flag does not exist** — removed phantom flag from VisualBuilder detour.

### Method
- **Dogfood**: 6 read-only verification agents with non-overlapping module scopes, grounded against `/home/carloscabral/study/adk-python/src/` and ADK docs at <https://adk.dev/>. Reports written to the 🔴/🟡/🟢 severity rubric established in 0.3.1. `git status --short` verified empty after each agent returned.
- **Fix wave (🔴 only)**: 5 parallel agents with non-overlapping file scopes. Each fix verified against framework source with file:line citations; grep confirmations of bad strings returning 0 hits.
- **New pattern surfaced**: sample-version skew. Several samples still pin `google-adk<2.0.0`; pages anchored to them inherit 1.x APIs as if canonical. Flagged in 06's sample-anchor table; full sweep deferred to the 🟡 pass.
- **Reaffirmed lesson from 0.3.1**: brief-only authoring → confident hallucination; source-grounded authoring → correct content. The 0.3.0 modules touched by this wave were brief-authored; the bill is this entry.

### Pending (🟡 next pass, per user "later the imprecise as well")
- A2A well-known path (`/.well-known/agent-card.json` vs legacy `/.well-known/agent.json`)
- Skills signatures sweep
- GCP drift remainder (10A/10B)
- Memory module typos
- CLI flag drift remainder (`staging_bucket` deprecation note, Chat issuer)

### Why
- User: "let's expand our dogfood/review for the rest of our course, and then later, fix them." then "let's dispatch it all. first the wrong ones and later the imprecise as well." This entry is the 🔴 dispatch; 🟡 follows.

---

## [0.3.1] - 2026-05-27

Dogfood-and-fix cycle. Four parallel verification agents read the new 2.0-surface modules against `/home/carloscabral/study/adk-python/src/` (the real framework source) instead of against the brief. Five parallel fix agents then corrected ~25 surgically. The pattern that the verification surfaced: pages authored from the brief were confidently wrong on real API shapes; pages anchored to source were correct. This entry is the corrections, not new scope.

### Fixed
- **App container, not LlmAgent** — `ContextCacheConfig`, `EventsCompactionConfig` (not `ContextCompactionConfig`), and `ResumabilityConfig` attach to `App`, not `LlmAgent`. Imports from `google.adk.apps`. Affected `Notes/04_SessionsState/05_ContextCaching.md`, `06_ContextCompaction.md`, `Notes/1A_AppAndRunner/00_Overview.md`.
- **`LlmEventSummarizer` signature** — takes `llm=` and `prompt_template=`, not `model=`/`instruction=`. Affected `Notes/04_SessionsState/06_ContextCompaction.md`.
- **`Runner.rewind_async` real shape** — takes `rewind_before_invocation_id=`, no `to_event_id=` or `state_overrides=` (auto-computed from session events, skipping `app:`/`user:` prefixes). Affected `Notes/04_SessionsState/07_SessionRewind.md`.
- **Session migrate is a schema upgrade tool, not a cross-backend mover** — `migration_runner.upgrade(source_db_url, dest_db_url)` (pickle→JSON). Added "What this does NOT do." Affected `Notes/04_SessionsState/08_SessionMigrate.md`.
- **`Runner.cancel` does not exist** — replaced with the real abandon pattern (timeout / don't resume / append terminal `Event` via `session_service.append_event(...)`). Affected `Notes/4B_HumanInTheLoop/04_RunnerResumeAndCancel.md`, retitled to "Resume and abandon", and `12_InProduction.md`.
- **Ambient trigger endpoints — partial reversal** — `POST /apps/{app_name}/trigger/pubsub` and `/trigger/eventarc` DO exist in 2.0 (opt-in via `--with-triggers pubsub,eventarc`; source: `trigger_routes.py:391-467`, `cli_tools_click.py:1687`). GCS routes through Eventarc. Only `/triggers/gcs` and `/triggers/scheduler` were fabricated. Affected `Notes/4B_HumanInTheLoop/07_AmbientAgents.md`.
- **`rerun_on_resume` has two scopes** — workflow-level (default `True`, `_workflow.py:157`) AND node-level (default `False`, `_base_node.py:56`); node-level opt-out wins. Affected `Notes/4B_HumanInTheLoop/06_RequestInputInGraphs.md`.
- **`adk` CLI flag names** — real flags are `--session_service_uri` and `--artifact_service_uri` (not `--session_db_url`/`--artifact_storage_uri`). `--credential_service_uri` does not exist. Affected `Notes/21_AdkApiSurface/01_AdkRunCli.md`, `01A_AdkRunUnderTheHood.md`, `01B_AdkWebUnderTheHood.md`, `01C_FullCliFamily.md`.
- **`adk web` defaults** — default port is `8000` (not `8501`); dev UI is Angular (not Vite/React). Affected `Notes/21_AdkApiSurface/01B_AdkWebUnderTheHood.md`, `Notes/23_FrontendIntegration/06_A2UIClient.md`.
- **`/run_live` wire protocol** — real `LiveRequest` Pydantic model in (`content`/`blob`/`activityStart`/`activityEnd`/`close`); ADK Event JSON out (camelCase, `partial`/`turnComplete`/`interrupted`). Not Gemini Live native protocol. Documented query-string params and 1002 close-code gotcha. Affected `Notes/21_AdkApiSurface/05_WebSocketsForLive.md` (full rewrite).
- **REST shapes** — only `user_id` and `session_id` required; `app_name` falls back to `ADK_DEFAULT_APP_NAME`; `new_message` is `Optional`. Affected `Notes/21_AdkApiSurface/03_RestShapes.md`.
- **Session/event/artifact endpoints** — `list-sessions` returns `list[Session]` directly; DELETE takes no body; `PATCH /sessions/{s}` exists. Affected `Notes/21_AdkApiSurface/07_SessionAndEventResources.md`.
- **No `/debug/*` routes** — replaced with the real route list (`/health`, `/version`, `/list-apps`, `/apps/{app}/app-info`, session/event/artifact/memory CRUD, `/run`, `/run_sse`, `/run_live`, `/dev-ui`). Affected `Notes/Detours/FastAPI_for_ADK.md`.
- **`ComputerUseToolset` is an empty `__init__.py`** — must import from `base_computer` and `computer_use_toolset` submodules; 16 abstract methods (added missing `hover_at`, `scroll_at`). Affected `Notes/03_Tools/06_ComputerUse.md`.
- **`VertexAiRagRetrieval`** — requires `description=` kwarg; single-tool is a recommended pattern, not runtime-enforced. Affected `Notes/03_Tools/07_ToolLimitations.md`.
- **`SqliteSessionService` is fictional** — real class is `DatabaseSessionService(db_url="sqlite:///...")`. Affected `Notes/01_Foundations/07_KnowledgeCheck.yml`.
- **Agent Engine deploy** — `--staging_bucket` deprecated with active warning; newer SDK shape is `client.agent_engines.create(config=...)` (`cli_deploy.py:1169`); `VertexAiSessionService.rewind()` is fabricated — use `runner.rewind_async()`. Affected `Notes/Detours/AgentEngine.md`.
- **`Runner.resume` shape** — `runner.run_async(invocation_id=paused_invocation_id, new_message=function_response)` with `adk_request_confirmation` function-response part. Affected `Notes/1A_AppAndRunner/04_WiringResumability.md`.
- **PROGRESS.md reconciled** — Module 00 and 01 page lists corrected against actual files on disk.

### Method
- **Dogfood**: 4 read-only verification agents with non-overlapping scopes (tutor contract on 00+01 / Foundation core 02-04 / 2.0-surface 1A+4B+04 expansions / deployment 21-24), each grounded against `/home/carloscabral/study/adk-python/src/` and ADK docs at <https://adk.dev/>. Reports written to a 🔴/🟡/🟢 severity rubric.
- **Fix wave**: 5 parallel agents with non-overlapping file scopes to enable parallelism without git conflicts. Each fix verified against framework source with file:line citations.
- **Lesson**: agents working from a brief produce confident hallucinations correlated with how thin the brief is. Agents grounded against source produce correct content. The 0.3.0 modules were authored from brief — most of the fixes here are that bill coming due. Subsequent authoring should ground against source by default.

### Why
- User asked: "let's dogfood using sub-agents and find/review our learnings." The verification pass found ~15 🔴 (wrong API shape, will not run) and ~10 🟡 (correct intent, drifting names) defects across the 2.0-surface modules. Shipping a course where the 2.0 examples don't import is worse than shipping nothing 2.0-shaped, so the fix pass took precedence over new scope.

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
