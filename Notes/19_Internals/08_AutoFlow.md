---
module: 19_Internals
page: 08_AutoFlow
title: AutoFlow — the implicit single-agent flow
estimated_minutes: 15
prereqs: [19_Internals/07]
concepts: [AutoFlow, SingleFlow, BaseLlmFlow, agent_transfer]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/07_ModelRegistry]  [↑ Map](../../MAP.md)  [Next: 19_Internals/09_DissectingOneCall →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 08 AutoFlow

# 🧠 AutoFlow — the loop you get for free

When you write `Agent(model=..., instruction=..., tools=[...])` and don't specify a flow, you get **`AutoFlow`**. It's the inner loop that does: "send to LLM → handle tool calls → loop until no more calls → emit final response."

File: `/home/carloscabral/study/adk-python/src/google/adk/flows/llm_flows/auto_flow.py`

## The whole file (44 lines):

```python
class AutoFlow(SingleFlow):
    """AutoFlow is SingleFlow with agent transfer capability."""

    def __init__(self):
        super().__init__()
        self.request_processors += [agent_transfer.request_processor]
```

That's it. `AutoFlow = SingleFlow + transfer`.

## The hierarchy

```
BaseLlmFlow              (flows/llm_flows/base_llm_flow.py)
   └── SingleFlow        (flows/llm_flows/single_flow.py)
          └── AutoFlow   (flows/llm_flows/auto_flow.py)
```

- **`BaseLlmFlow`** (1432 lines, line 462) — the actual loop: `run_async`, `_run_one_step_async`, `_preprocess_async`, `_postprocess_async`, `_postprocess_handle_function_calls_async`.
- **`SingleFlow`** (~150 lines) — adds the **default processor stack**: instructions, identity, contents-from-events, NL planning, tool registration, output schema enforcement.
- **`AutoFlow`** (44 lines) — adds `agent_transfer.request_processor`, which is the magic that turns `sub_agents` into LLM-visible "transfer to X" tools.

## Which agent uses which flow?

In `LlmAgent.__init__` (you'll see in `llm_agent.py` around the field defaults), the flow is chosen at construction time:

- `disallow_transfer_to_parent=False` AND has `sub_agents` → `AutoFlow`
- Otherwise → `SingleFlow`

The actual selection logic uses the `_llm_flow` private attribute and the imports at the top of `llm_agent.py` (lines 46-48):

```python
from ..flows.llm_flows.auto_flow import AutoFlow
from ..flows.llm_flows.base_llm_flow import BaseLlmFlow
from ..flows.llm_flows.single_flow import SingleFlow
```

## The processor stack

`SingleFlow.__init__` builds two lists:

- `self.request_processors` — mutate the outgoing `LlmRequest` before send.
- `self.response_processors` — mutate the incoming response / events.

`AutoFlow` appends `agent_transfer.request_processor` to the request side. That processor:

1. Inspects the agent's `sub_agents`.
2. For each (allowed) target, registers a synthetic `transfer_to_agent` function.
3. The LLM sees them as tools. Calling one emits a `FunctionResponse` whose `actions.transfer_to_agent` field is set.
4. The runner sees the transfer action → routes the next turn to the target.

That's the entire mechanism for "the LLM decides to delegate to a sub-agent."

> 🛠 **Have the student run:** create a tiny `Agent` with two `sub_agents`, then in a REPL inspect `agent._llm_flow.__class__.__name__` → expect `'AutoFlow'`. Remove the sub_agents → expect `'SingleFlow'`.

> ❓ **Ask the student:** "If I want to disable LLM-driven transfer but keep sub_agents available for programmatic dispatch, what field do I set?" *(Answer: `disallow_transfer_to_peers=True` and/or `disallow_transfer_to_parent=True`. See `llm_agent.py` fields.)*

[← Prev: 19_Internals/07_ModelRegistry]  [↑ Map](../../MAP.md)  [Next: 19_Internals/09_DissectingOneCall →]
