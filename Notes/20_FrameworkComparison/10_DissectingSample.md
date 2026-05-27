---
module: 20_FrameworkComparison
page: 10_DissectingSample
title: How each competitor would build `llm-auditor`
estimated_minutes: 25
prereqs: [20_FrameworkComparison/09]
concepts: [llm-auditor, cross-framework-translation]
icon: 🛠
in_production: false
---

[← Prev: 20_FrameworkComparison/09_ChoosingAFramework]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/11_InProduction →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 10 Dissecting Sample

# 🛠 What each framework would do with `llm-auditor`

Re-read the ADK sample at `/home/carloscabral/study/adk-samples/python/agents/llm-auditor/`.

In ADK, `llm-auditor`:

- A root `LlmAgent` that delegates.
- A `critic` sub_agent (judges factuality with search-grounded reasoning).
- A `reviser` sub_agent (rewrites to fix the issues the critic raised).
- Sub-agents are wired with `sub_agents=[critic, reviser]`, so the root can `transfer_to_agent`.
- Uses Gemini, `google_search` tool in the critic, callbacks for output cleanup.

Now: what would each competitor do?

## LangGraph

```python
# StateGraph with three nodes: root_router → critic → reviser → END
class S(TypedDict):
    text: str; critique: str; revised: str

graph = StateGraph(S)
graph.add_node("critic", lambda s: {"critique": critic_llm.invoke(s["text"])})
graph.add_node("reviser", lambda s: {"revised": rev_llm.invoke(s["text"]+s["critique"])})
graph.set_entry_point("critic")
graph.add_edge("critic", "reviser")
graph.add_edge("reviser", END)
```

- Critic and reviser become **nodes** in a `StateGraph`. Shared state is a typed dict.
- `google_search` becomes a `TavilySearchResults` (or similar LangChain retriever).
- Callbacks become LangChain `RunnableLambda` middleware.

**Difference**: explicit, typed state object. No "agent transfer" — the graph IS the orchestration.

## CrewAI

```python
critic = Agent(role="Auditor", goal="Find factual errors in {text}",
               tools=[SerperDevTool()])
reviser = Agent(role="Editor", goal="Rewrite {text} addressing the critique")
crew = Crew(agents=[critic, reviser],
            tasks=[Task(agent=critic, description="Audit {text}",
                        expected_output="A critique list."),
                   Task(agent=reviser, description="Revise based on the critique.",
                        expected_output="Final clean text.")],
            process=Process.sequential)
```

- Two `Agent`s with role/goal/backstory; two `Task`s; `sequential` Crew.
- `google_search` → a CrewAI search tool (Serper, Tavily).

**Difference**: role prompts replace explicit transfer logic. Easier to read, less expressive.

## AutoGen / AG2

```python
critic = AssistantAgent("critic", model_client=mc,
    system_message="Critique the text. End your message with CRITIQUE_DONE.")
reviser = AssistantAgent("reviser", model_client=mc,
    system_message="Rewrite given the critique. End with FINAL.")
team = RoundRobinGroupChat([critic, reviser],
    termination_condition=TextMentionTermination("FINAL"))
```

- A `RoundRobinGroupChat` with termination on `"FINAL"`.

**Difference**: termination is text-driven, not code-driven. Brittle but flexible.

## OpenAI Agents SDK

```python
reviser = Agent(name="Reviser", instructions="Rewrite given a critique.")
critic = Agent(name="Critic", instructions="Critique, then hand off to Reviser.",
               handoffs=[handoff(reviser)],
               tools=[function_tool(web_search)])
```

- `critic` has a `handoff` to `reviser`. Same as ADK's `transfer_to_agent`.

**Difference**: smaller surface, OAI-first. No native graph or Workflow.

## Pydantic AI

```python
class Critique(BaseModel):
    issues: list[str]
class Revised(BaseModel):
    text: str

critic = Agent("openai:gpt-4o", output_type=Critique)
reviser = Agent("openai:gpt-4o", output_type=Revised)

def audit(text):
    c = critic.run_sync(text).output
    r = reviser.run_sync(f"{text}\n\nIssues: {c.issues}").output
    return r.text
```

- Two single-purpose typed agents; orchestration is plain Python.

**Difference**: no agent framework's worth of orchestration. Just typed LLM functions composed by hand.

## Letta / MemGPT

Would be **awkward**. Letta is single-agent-first. You'd model the auditor as one persistent agent with two "personas" it switches between — but the value Letta brings (long-term memory) is orthogonal to what `llm-auditor` does. **Verdict**: wrong fit.

## What this exercise teaches

The same task can be solved in every framework — but each one **shapes the solution**. ADK's solution centers on `sub_agents` + transfer; LangGraph's centers on state-graph nodes; CrewAI's centers on personas; AutoGen's on conversation termination. The shape becomes the constraint as your app grows.

> ❓ **Ask the student:** "After this exercise, which framework's `llm-auditor` rewrite do you find easiest to read? Which would be easiest to extend with a 4th 'fact-checker' agent? Are they the same answer?" *(Often not — readability and extensibility diverge.)*

> 🛠 **Have the student run:** open `adk-samples/python/agents/llm-auditor/agent.py` and `adk-samples/python/agents/llm-auditor/sub_agents/critic/agent.py`. Re-read with fresh eyes after this comparison.

[← Prev: 20_FrameworkComparison/09_ChoosingAFramework]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/11_InProduction →]
