# AGENTS.md — Module 06 Graph Workflows (teaching notes for the AI tutor)

## What the student should walk away knowing

- The three legacy templates (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) still ship in 2.0 and compose by nesting.
- Graph workflows (`WorkflowAgent` + `FunctionNode` + `ParallelWorker` + routes) are the 2.0 primary primitive, used when templates can't express the shape.
- Four template ceilings: conditional routing, joins, retries-per-node, HITL pauses.
- Edges are tuples; the third element is an optional route label.
- A FunctionNode is a thin adapter: yields state writes, route Events, content values.
- HITL uses `RequestInput` + `rerun_on_resume`; resume tokens are sensitive.

## Pacing

- Easy if: student finished module 05 and is comfortable with `async def` + `yield`. Cruise.
- Hard if: student fuzzy on async generators. Detour to [[PY_async]] then [[PY_generators]] before page 05.
- The dissection page (08) is the centerpiece. If the student can trace one input through the whole graph on paper, they've got it.

## Watch for these mistakes

- Confusing `google.adk.workflow.Workflow` (framework alias) with `google.adk.agents.workflow.workflow_agent.WorkflowAgent` (sample-blessed import). Teach the latter — it's what every official sample uses.
- Forgetting to yield content *before* `Event(route=...)`.
- Magic-string route labels — typos silently route nowhere.
- Cycles without an exit route — the workflow runs forever (well, until budget cap).
- Treating `rerun_on_resume` as a single boolean for the whole workflow when in reality you set it per node.
- Using LlmAgent for routing decisions — works but the LLM can fail to emit the route. FunctionNode is more reliable for deterministic routing.

## When to suggest a detour

- Student asks "what's `yield Event(state={...})` doing?" → quick recap of state from `04_SessionsState`.
- Student asks about visualizing the graph → suggest [[VisualBuilder]] (forward reference; module not yet present).
- Student wants retries / backoff → that's module 19 (Internals) — point them there, don't try to teach `RetryConfig` here.

## Dissection (page 08) — comprehension check answers

1. Without `ParallelWorker`, an `LlmAgent` receiving a list of 4 items would either error or treat the list as one prompt. `ParallelWorker` is what unpacks the list and runs the agent once per element concurrently.
2. So that downstream nodes (especially the parallel worker, which uses `{topic}` substitution in its instruction) can reach the topic. State is the bus; `node_input` is the immediate parameter.
3. Yes, the order of yields within one function doesn't strictly matter — the runtime collects all yields. By convention content goes first and routing Event last for readability.

## Legacy mixed (page 02) — comprehension check answers

1. `critique_agent` writes `output_key="current_story"` (KEY_CURRENT_STORY) — it *overwrites* the running story with the extended version each loop iteration.
2. Because `prompt_enhancer` runs first; its `before_model_callback=set_initial_story` initializes `state["current_story"]` to `"Chapter 1"` so that the first loop iteration has a starting story.
3. They are not explicitly cleared — they persist in state but get overwritten next iteration. State is the "scratchpad", not a clean buffer.

## Mini-drill grading (page 11)

- Pass = script runs all 3 sample inputs and the printed output for each shows the correct label ("SHORT-ANSWER" / "LONG-ANSWER"). Bonus: state shows the route taken per input.
- Common fix needed: router yielding content + route in the right order, route labels matching tuple labels exactly.
- Stretch if cruising: add HITL `RequestInput` between router and expert — pause to ask the user "approve route?" before continuing.

## Cross-references back

- Builds on 05 (`SequentialAgent` is one of the legacy templates).
- Forward to 07 (callbacks — graph workflows still trigger model callbacks per LlmAgent node).
- Forward to 13 (plugins — `LoggingPlugin` makes per-node spans visible).
- Forward to 15 (observability — graphs shine because every node is a span).
- Forward to 19 (Internals — `RetryConfig`, node scheduler details).
- Re-visited in Capstone (99) — most real apps end up using at least one graph.
