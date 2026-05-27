---
module: 04_SessionsState
page: 09_OutputKeyShortcut
title: output_key — pipe agent's reply directly into state
estimated_minutes: 15
prereqs: [04_SessionsState/08]
concepts: [output_key, sequential-pipeline, multi-agent-prep]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/08_SessionMigrate](08_SessionMigrate.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/10_PersistentSessions →](10_PersistentSessions.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 09 output_key shortcut

# 🛠 `output_key=` — store the agent's reply directly

A common pattern: agent A produces some text, agent B reads it from state. You could write a tool that captures A's reply and writes it. ADK gives you a one-line shortcut: `output_key=`.

```python
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research the topic and write a 3-paragraph summary.",
    output_key="research_notes",      # ← reply text lands in state["research_notes"]
)
```

After `researcher` produces its final reply, ADK writes `state["research_notes"] = "<the reply text>"`. Same event-with-state_delta machinery as a tool write.

## 🛠 The downstream agent reads it via the prompt template

```python
writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction=(
        "Using the following research notes, write a polished article:\n\n"
        "{research_notes}"
    ),
)
```

When `writer`'s next turn fires, ADK substitutes `{research_notes}` with what `researcher` produced. Two agents, one piece of state, no glue tool.

## 🧠 Used heavily in multi-agent

This pattern is the spine of Module 05's coordinator-worker flows and Module 06's workflow graphs. Real-sample examples:

* [`academic-research/agent.py`](../../../adk-samples/python/agents/academic-research/academic_research/agent.py): `output_key="seminal_paper"` on the coordinator.
* [`academic-research/sub_agents/academic_websearch/agent.py`](../../../adk-samples/python/agents/academic-research/academic_research/sub_agents/academic_websearch/agent.py): `output_key="recent_citing_papers"` on the search sub-agent.
* [`workflows-sequential/agent.py`](../../../adk-samples/python/agents/workflows-sequential/agent.py): `output_key="city"` on the city generator; the next agent reads `{city}`.

Open one of those files now and trace the pipeline.

## 🧠 Prefixing applies here too

```python
output_key="user:last_summary"   # persists across this user's sessions
output_key="temp:scratch"        # gone after this invocation
```

Same prefix rules as page 02. Default (no prefix) = session-scoped.

## ⚠️ Output is the FULL reply text

`output_key` captures `event.content.parts[0].text` of the final response. If the agent produces multi-part replies (rare but possible), only the first text part lands in state. For finer control, use a tool with `tool_context.state[...] = ...` instead.

## ❓ Quiz

> ❓ **Ask the student:** what's the difference between an agent that writes to state via `output_key="x"` vs. an agent that explicitly invokes a `save(x: str)` tool?
> *(Expected: `output_key=` happens automatically on EVERY final reply — no LLM decision involved. The tool requires the LLM to* decide *to call it, which is unreliable. For "always capture this agent's output" use `output_key`; for "capture conditionally" write a tool.)*

> 🛠 **Have the student do this:** modify their calculator agent from Module 03 to add `output_key="last_calc"`. After running, inspect `session.state["last_calc"]` and confirm it's the reply text.

> **🚀 In Production**
>
> `output_key` writes happen even when the reply is "I don't know" or an error message. If you only want to capture *successful* outputs, use a tool with conditional logic instead. Foot-gun: relying on `output_key` to capture structured JSON, and getting prose because the LLM editorialized. Use `output_schema=` (Pydantic model) to constrain reply format — covered in Module 17.

---

[← Prev: 04_SessionsState/08_SessionMigrate](08_SessionMigrate.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/10_PersistentSessions →](10_PersistentSessions.md)
