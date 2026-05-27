---
module: 20_FrameworkComparison
page: 07_LettaMemGPT
title: Letta / MemGPT — memory-first agents
estimated_minutes: 15
prereqs: [20_FrameworkComparison/06]
concepts: [Letta, MemGPT, hierarchical-memory, persistence]
icon: 🧠
in_production: false
---

[← Prev: 20_FrameworkComparison/06_PydanticAI]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/08_FeatureMatrix →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 07 Letta / MemGPT

# 🧠 Letta / MemGPT

**MemGPT** was a 2023 research paper from Berkeley on **hierarchical memory for LLM agents**: a main context (the LLM's prompt) plus an "OS-like" external memory (recall, archival) the agent can read/write with self-issued tool calls. **Letta** is the productionized open-source runtime (`pip install letta`) plus a hosted SaaS.

The pitch: most agents are stateless or have weak memory. Letta's agents remember **months of conversation** and treat memory as the primary substrate.

## Hello-world (sketch)

```python
from letta_client import Letta

client = Letta(token=...)

# Create a persistent agent — survives across processes.
agent = client.agents.create(
    name="my_assistant",
    system="You are a helpful long-running assistant.",
    memory_blocks=[
        {"label": "human", "value": "The user is Carlos, a Python dev."},
        {"label": "persona", "value": "Friendly, concise."},
    ],
    model="openai/gpt-4o",
)

# Talk to it.
resp = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "What language am I using?"}],
)
```

## How memory works

- **Core memory blocks** (`human`, `persona`, more) — always in the prompt; the agent can edit them with `core_memory_replace` tool calls.
- **Recall memory** — full conversation log; searchable.
- **Archival memory** — vector-indexed long-term store; the agent can write to it with `archival_memory_insert` and read with `archival_memory_search`.

The agent **uses tool calls to manage its own memory**. The framework's job is to make those tool calls cheap, reliable, and version-tracked.

## Multi-agent

Letta supports multi-agent (agents calling other agents), but the **primary axis** is "one agent, long lifetime." If you want to express "research crew with 4 roles," CrewAI or ADK is more natural.

## Where Letta shines vs ADK

- **Long-horizon memory.** Letta's memory model is its whole reason for being. ADK has `VertexAiMemoryBankService` / `VertexAiRagMemoryService`, which give you most of the same capability, but Letta's "the LLM curates its own memory" is more sophisticated by default.
- **Hosted persistence.** Their SaaS handles the storage; ADK requires you to wire your own backend.

## Where ADK beats Letta

- **Multi-agent orchestration.** ADK has workflows, sub_agents, A2A — Letta is single-agent-first.
- **Tooling depth.** ADK has MCP, code execution sandboxes, plugins, callbacks, evals, observability — Letta is leaner.
- **Vendor neutrality.** ADK is GCP-native but multi-provider for models. Letta is provider-neutral but ties you to its persistence layer (open-source backend exists, but the SaaS is the smooth path).

## When to pick Letta

- The defining feature of your app is **the agent remembers you across months**.
- You're building a "personal companion" / "lifelong assistant."
- You want hierarchical memory without writing it yourself.

## When NOT to

- Your workflow is multi-agent / orchestrated.
- You need cloud-vendor neutrality without depending on Letta's services.
- You want low-level control of memory layout (Letta's choices are good but opinionated).

> 💡 **You can combine them.** Use ADK as the orchestrator and embed a Letta agent as a tool (or behind an A2A boundary) when you need the deep memory layer specifically.

> ❓ **Ask the student:** "Track C of the Capstone (module 99) is a Personal Knowledge Hub. Why does it use `VertexAiMemoryBankService` instead of Letta?" *(Answer: cohesion — we stay inside the GCP/ADK story. But Letta would be defensible if memory quality were the dominant requirement.)*

[← Prev: 20_FrameworkComparison/06_PydanticAI]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/08_FeatureMatrix →]
