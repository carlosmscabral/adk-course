---
module: 19_Internals
page: 09_DissectingOneCall
title: Dissecting one runner.run_async call through source
estimated_minutes: 30
prereqs: [19_Internals/08]
concepts: [dissection, tracing, control-flow]
icon: 🔎
in_production: false
---

[← Prev: 19_Internals/08_AutoFlow]  [↑ Map](../../MAP.md)  [Next: 19_Internals/10_TracingOneToolCall →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 09 Dissecting One Call

# 🔎 Dissect one call: from `runner.run_async(...)` to the final Event

We follow a vanilla call:

```python
agent = Agent(model="gemini-2.5-flash", instruction="be terse", tools=[])
runner = InMemoryRunner(agent)
async for event in runner.run_async(
    user_id="u", session_id="s",
    new_message=Content(parts=[Part(text="hi")])
):
    print(event)
```

## The call stack

```
runner.run_async()                        runners.py:914
  └─ _get_or_create_session()             runners.py:807
  └─ build_node(agent)                    workflow/utils/_workflow_graph_utils
  └─ _run_node_async(node=agent)          runners.py:452
        └─ NodeRunner.run(ctx)            workflow/_node_runner.py
              └─ node._run_impl(ctx)      (the LlmAgent-as-node wrapper)
                    └─ run_llm_agent_as_node()  workflow/_llm_agent_wrapper.py
                          └─ agent.run_async(ctx)    agents/base_agent.py:257
                                └─ agent._run_async_impl(ctx)   agents/llm_agent.py:483
                                      └─ self._llm_flow.run_async(ctx)   flows/llm_flows/base_llm_flow.py:818
                                            └─ _run_one_step_async(ctx)    line 833
                                                  ├─ _preprocess_async(ctx)    line 920
                                                  │     └─ for each request_processor: mutate LlmRequest
                                                  │         (instructions, identity, contents, tools, transfer …)
                                                  ├─ _call_llm_async(ctx, llm_request)   line 1192
                                                  │     ├─ _handle_before_model_callback
                                                  │     ├─ llm.generate_content_async(req)   models/google_llm.py
                                                  │     └─ _handle_after_model_callback
                                                  └─ _postprocess_async(ctx, llm_response)  line 952
                                                        ├─ for each response_processor
                                                        ├─ yield content events (partial + final)
                                                        └─ _postprocess_handle_function_calls_async
                                                              └─ (no function calls in this trace → done)
                                — control returns to _run_async_impl
                                — ctx.set_agent_state(end_of_agent=True)
                                — yield end-of-agent event
          (NodeRunner finalizes; emits node-output event with branch + author)
  └─ session_service.append_event(session, event)    sessions/base_session_service.py:114
        └─ apply event.actions.state_delta to session.state
  └─ yield event   ← consumer of run_async receives it
```

## Three checkpoints to memorize

1. **The LLM call is at `base_llm_flow.py:1192` (`_call_llm_async`).** That's the bottleneck. If a request is slow, your profile points here.
2. **State is applied at `base_session_service.py:114` (`append_event`).** Every state mutation happens **after** the event leaves the agent — *not* inside the tool.
3. **The actual `LlmAgent → node` wrapping happens at `runners.py:981` (`build_node(agent_to_run)`).** This is why even single-agent runs go through the workflow scheduler in 2.0.

## What's NOT in the trace

- No callbacks fired (we had none).
- No tools called (empty `tools=[]`).
- No transfer (no `sub_agents`).
- No streaming partials (depends on the model; Gemini does stream by default — page 18).

> 🛠 **Have the student run:** open three terminals/buffers — `runners.py:914`, `base_llm_flow.py:818`, `base_session_service.py:114`. Follow the call by jumping between them on a real session. Use grep/code-nav rather than reading top to bottom.

> ❓ **Ask the student:** "If I want to log every LLM request payload (for debugging), what's the cheapest hook?" *(Answer: `before_model_callback` on the agent, or a `Plugin` with `on_model_request`. Both fire at `base_llm_flow.py` around `_handle_before_model_callback`.)*

[← Prev: 19_Internals/08_AutoFlow]  [↑ Map](../../MAP.md)  [Next: 19_Internals/10_TracingOneToolCall →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 09 Dissecting One Call
