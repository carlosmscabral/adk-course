---
module: 19_Internals
page: 01_RepoMap
title: Repo map — one sentence per subdir
estimated_minutes: 20
prereqs: [19_Internals/00]
concepts: [repo-layout, subpackages]
icon: 🗺
in_production: false
---

[← Prev: 19_Internals/00_Overview]  [↑ Map](../../MAP.md)  [Next: 19_Internals/02_LlmAgentSource →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 01 Repo Map

# 🗺 Repo map

Look at `_figures/source_map.txt` next to this page. It's the canonical tree. Below is the one-sentence summary you'll memorize for navigation:

```
agents/        — agent classes (BaseAgent, LlmAgent, Sequential/Parallel/Loop, RemoteA2a)
runners.py     — top-level entry; pumps the event generator and persists events
sessions/      — Session pydantic model + service backends (InMemory/Sqlite/DB/VertexAi)
events/        — Event (= LlmResponse + actions + node_info) and EventActions
tools/         — BaseTool + FunctionTool/AgentTool/McpToolset; FunctionDeclaration build
flows/llm_flows/ — the inner LLM loop (preprocess → call → postprocess → handle fn calls)
workflow/      — graph runtime: Workflow node, scheduler, parallel worker
models/        — BaseLlm + per-provider impls (Gemini/Claude/LiteLlm/Apigee) + LLMRegistry
memory/        — InMemory/VertexAiMemoryBank/VertexAiRagMemory services
plugins/       — Plugin base + built-ins (LoggingPlugin, GlobalInstructionPlugin, …)
skills/        — Skills feature (frontmatter, Script, SkillRegistry, SkillToolset)
a2a/           — AgentCard, to_a2a(), server bindings, RemoteA2aAgent
code_executors/— BuiltIn/Container/VertexAi/GKE/AgentEngineSandbox
evaluation/    — AgentEvaluator + EvalSet/Case + judges (LlmAsJudge, RubricBased, …)
telemetry/     — OpenTelemetry tracer shim
cli/           — `adk run/eval/web/create/deploy`
platform/      — time/uuid/thread shims (so tests can inject deterministic behavior)
```

## Reading rules

1. **Underscore-prefixed files are private.** `_base_node.py`, `_workflow.py`. Treat as implementation. Don't import from outside the package.
2. **`__init__.py` files re-export the public API.** `from google.adk.agents import LlmAgent` resolves through `agents/__init__.py`. When in doubt, that file lists what is supported.
3. **`base_*.py`** = the abstract contract. `*_*.py` = a concrete impl.
4. **Tests live in a parallel tree** (not shipped with the wheel). Real-world tests of behavior are at `adk-samples/` and your own evals.

## Where the "magic" lives

- The **agent loop**: `flows/llm_flows/base_llm_flow.py::BaseLlmFlow._run_one_step_async`.
- The **graph loop**: `workflow/_node_runner.py` + `workflow/_dynamic_node_scheduler.py`.
- The **event sink**: `sessions/base_session_service.py::append_event` (it's where `state_delta` is applied).
- The **model dispatch**: `models/registry.py::LLMRegistry.resolve`.

> ❓ **Ask the student:** "If I want to know whether `runner.run_async` is sync or async, where do I look first — the docs or the source?" *(Answer: the source. Type signatures don't lie. Docs can lag.)*

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-python/src/google/adk/agents/` and identify which file is `BaseAgent` and which is `LlmAgent`.

[← Prev: 19_Internals/00_Overview]  [↑ Map](../../MAP.md)  [Next: 19_Internals/02_LlmAgentSource →]
