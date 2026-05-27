---
module: 05_MultiAgent
page: 09_InProduction
title: Multi-agent gotchas in production
estimated_minutes: 20
prereqs: [05_MultiAgent/08A]
concepts: [description-quality, circular-delegation, name-collisions, instruction-isolation]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 05_MultiAgent/08A_LangGraphAgent](08A_LangGraphAgent.md)  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/10_KnowledgeCheck →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 09 In Production

## 🚀 The four field-failure modes

### 1. Description quality determines routing accuracy

The single highest-leverage knob. Every sub-agent's `description=` is concatenated into the parent's router prompt. Vague descriptions cause wrong delegations; verbose ones blow the parent's context window.

**Mitigation:** treat descriptions like docstrings — write them, test them, version-control them. Build a 20-case routing eval set per parent agent (module 14) and tune until ≥ 90% accuracy.

### 2. Circular delegation

`a → b → a → b ...` happens when both descriptions claim the same territory. The runner will eventually hit a turn cap and error, but you've burnt minutes and tokens.

**Mitigations:**
- Set `max_iterations` on the runner (module 02).
- Replace mutual `sub_agents` with a `SequentialAgent` (the cycle becomes impossible).
- Make descriptions explicitly **mutually exclusive** ("...handles billing; *does not* answer technical questions").

### 3. Name collisions

Two agents (or two tools wrapping agents) named `researcher` — the dispatcher silently picks one. The bug looks like "sometimes it works, sometimes it routes to the wrong place."

**Mitigation:** namespace your agent names: `billing_researcher`, `tech_researcher`. Add a CI check that walks the tree and asserts uniqueness.

### 4. Sub-agents inherit nothing automatically

A common misconception: "the parent's instruction applies to all sub-agents." It does **not**. Each sub-agent runs its own model with its own instruction. The only thing shared is the `Session` and its `state` dict.

If you need a global rule across the tree ("always reply in JSON", "never invent prices"), put it in **each** sub-agent's instruction, or use the [[13_Plugins/05_GlobalInstructionPlugin]] in module 13.

## 🚀 Composition-mode checklist

For every parent-child relationship, ask:

- [ ] Does the user need to talk to the specialist directly (`sub_agents`) or just see the parent's synthesis (`AgentTool`)?
- [ ] Is the path fixed (`SequentialAgent`) or dynamic (`sub_agents` / `AgentTool`)?
- [ ] Have I written a specific, testable `description=` for every node?
- [ ] Do my names collide?
- [ ] Is every state key the children read documented somewhere they write it?
- [ ] What happens if a child fails — does the parent recover, escalate, or just error?

## 🚀 Observability essentials

In your logging plugin (module 13) or directly via callbacks (module 07):

```python
# pseudo:
log_event(author, content)
log_event_action("transfer_to_agent", actions.transfer_to_agent)
log_event_action("escalate", actions.escalate)
log_state_delta(actions.state_delta)
```

Without these three, multi-agent debugging is guesswork. With them, you can replay any session and see exactly which agent owned which turn.

## 🚀 Cost / latency

Composition multiplies model calls. A 4-agent pipeline is ~4x the cost of a single agent. Mitigations:

- Use cheaper models (`gemini-2.5-flash`) for narrow specialists; reserve `gemini-2.5-pro` for the orchestrator or hardest reasoner.
- Cache intermediate results in state — module 17 / context caching.
- For high-traffic systems, consider whether the *whole* split is justified or if two specialists could merge.

> 🤖 **Tutor:** the student should leave this page with a healthy paranoia about descriptions and naming. If they shrug "I'll write that later" — push back. Bad descriptions are 80% of production multi-agent bugs.

---

[← Prev: 05_MultiAgent/08A_LangGraphAgent](08A_LangGraphAgent.md)  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/10_KnowledgeCheck →]
