---
module: 19_Internals
page: 02_LlmAgentSource
title: LlmAgent — fields and the run loop
estimated_minutes: 30
prereqs: [19_Internals/01]
concepts: [LlmAgent, _run_async_impl, pydantic-model]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/01_RepoMap]  [↑ Map](../../MAP.md)  [Next: 19_Internals/03_RunnerSource →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 02 LlmAgent Source

# 🧠 LlmAgent — the class you've been using

File: `/home/carloscabral/study/adk-python/src/google/adk/agents/llm_agent.py`
Class: `LlmAgent(BaseAgent)` — declared around **line 193**.

## Class-level fields you've already used

Skim lines 193-480. `LlmAgent` is a **pydantic model**, so every "field" you set in `Agent(...)` lands on a `pydantic.Field`. The important ones:

| Field | Line ≈ | What it does |
|---|---|---|
| `model: Union[str, BaseLlm]` | 208 | name (`"gemini-2.5-flash"`) OR a `BaseLlm` instance |
| `instruction: Union[str, InstructionProvider]` | 216 | dynamic, supports `{state_key}` substitution |
| `global_instruction` | 230 | deprecated — moved to `GlobalInstructionPlugin` |
| `static_instruction` | 243 | sent once for caching |
| `tools: list[BaseTool \| Callable \| BaseToolset]` | 294 | tools / toolsets |
| `sub_agents: list[BaseAgent]` | inherited from BaseAgent | child agents |
| `before/after_model_callback` and similar | ≈400 | callback hooks |

The **two class-vars** `DEFAULT_MODEL` (line 196) and `DEFAULT_LIVE_MODEL` (line 199) — set with `LlmAgent.set_default_model(...)` (line 591). This is the seam for "switch the whole app to a different default model in one line."

## `_run_async_impl` — the actual loop (lines 483-520)

This is the method that yields `Event`s back to the runner. The shape:

```python
async def _run_async_impl(self, ctx):
    agent_state = self._load_agent_state(ctx, BaseAgentState)

    # 1. RESUMING a sub-agent transfer? Run it, then end.
    if agent_state is not None and (sub := self._get_subagent_to_resume(ctx)):
        async for event in sub.run_async(ctx):
            yield event
        ctx.set_agent_state(self.name, end_of_agent=True)
        yield self._create_agent_state_event(ctx)
        return

    # 2. NORMAL path: drive the LLM flow until done or pause.
    should_pause = False
    async for event in self._llm_flow.run_async(ctx):
        self.__maybe_save_output_to_state(event)
        yield event
        if ctx.should_pause_invocation(event):
            should_pause = True
    if should_pause:
        return

    # 3. If resumable and not paused, emit end-of-agent.
    if ctx.is_resumable:
        ...
        ctx.set_agent_state(self.name, end_of_agent=True)
        yield self._create_agent_state_event(ctx)
```

Three things to internalize:

1. **The agent itself doesn't talk to the LLM.** `self._llm_flow` does. The agent is a config + control wrapper.
2. **It's a generator.** `async for event` is the only way data leaves an agent. Everything (tool calls, deltas, final response) flows through `yield event`.
3. **Pause is a first-class state.** Long-running tools, request-for-confirmation, and resumable apps share the same pause path.

## `canonical_model` — model resolution (line 554)

```python
@property
def canonical_model(self) -> BaseLlm:
    if isinstance(self.model, BaseLlm):    return self.model
    elif self.model:                       return LLMRegistry.new_llm(self.model)
    else:
        # walk up the parent chain
        ancestor = self.parent_agent
        while ancestor:
            if isinstance(ancestor, LlmAgent):
                return ancestor.canonical_model
            ancestor = ancestor.parent_agent
        return self._resolve_default_model()
```

This is why **child agents inherit `model` from the parent** if not specified. The walk happens on every invocation.

> ⚠️ **Gotcha:** because `model` resolution walks ancestors, the **last** `LlmAgent` in the chain wins. If your root explicitly sets `gemini-2.5-pro` and a deeply nested agent sets `gemini-2.5-flash`, the deep one wins for itself but not for its parent.

> 🛠 **Have the student run:** open `llm_agent.py` and find `_run_async_impl`. Count how many times `yield event` appears. *(Answer: 3 — one in the resume path, one in the main loop, one in the end-of-agent emit.)*

> ❓ **Ask the student:** "Where is the actual LLM call made — in `LlmAgent` or somewhere it delegates to?" *(Answer: `self._llm_flow.run_async`, which lives in `flows/llm_flows/base_llm_flow.py`. We'll go there in page 09.)*

[← Prev: 19_Internals/01_RepoMap]  [↑ Map](../../MAP.md)  [Next: 19_Internals/03_RunnerSource →]
