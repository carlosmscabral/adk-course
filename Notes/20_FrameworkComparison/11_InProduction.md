---
module: 20_FrameworkComparison
page: 11_InProduction
title: Framework choice as a long-term commitment
estimated_minutes: 15
prereqs: [20_FrameworkComparison/10]
concepts: [migration, abstraction-leak, framework-risk]
icon: 🚀
in_production: true
---

[← Prev: 20_FrameworkComparison/10_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/12_KnowledgeCheck →]

You are here: 🗺 Production Track ▸ 20 Framework Comparison ▸ 11 In Production

# 🚀 Framework choice as a long-term commitment

## What makes framework choice hard

A framework is **structural debt**. Once your app is built on it:

- The framework's vocabulary leaks into your team's docs ("the supervisor will hand off…").
- The framework's release cadence drives your release cadence.
- The framework's bugs become your bugs.
- The framework's abandonment becomes your migration project.

You will live with the choice for **years**.

## The 4 risks to underwrite

### 1. Churn risk

How often does the framework break APIs?

- **High churn**: LangChain (the package split + LCEL transition was painful). Pin everything.
- **Medium churn**: AutoGen (the AG2 vs autogen-core split).
- **Low churn**: ADK 2.0 GA (frozen surface), OpenAI Agents, Pydantic AI.

Action: read the last 6 months of release notes before committing.

### 2. Vendor risk

What if the company / lead maintainer stops investing?

- **Low risk**: ADK (Google), OAI Agents (OpenAI), LangChain (commercial company), Pydantic AI (Pydantic team).
- **Medium**: CrewAI (small commercial company), Letta (commercial + open core).
- **Higher**: AutoGen (after the fork, the future of each half is uncertain).

Action: prefer frameworks with a paid product behind them OR with an active enough community to outlive any one company.

### 3. Abstraction-leak risk

Every framework's abstractions leak somewhere. You cannot avoid this — you can only choose **whose leaks you can tolerate**.

- ADK's leaks: GCP integration assumes Vertex / BigQuery exist; if you want fully cloud-agnostic, you'll fight the framework occasionally.
- LangGraph's leaks: LangChain's package boundaries are confusing; pinning is fragile.
- CrewAI's leaks: prompts are stitched together opaquely; debugging a "why did the agent say X" sometimes requires reading framework source.
- AutoGen's leaks: termination conditions on text patterns; brittle in production.
- OAI Agents' leaks: OpenAI-shaped; non-OAI providers have rough edges.
- Pydantic AI's leaks: schema-violation retries can chew through tokens.
- Letta's leaks: memory layout is opinionated; deviating is painful.

Action: build a 1-week spike that **exercises the leak** (the GCP feature you don't need, the agent that doesn't fit the metaphor, etc.). See if you can route around it.

### 4. Hire-ability risk

Can you find engineers who know it?

- **Easiest hire**: LangChain (largest community).
- **Hard but trainable**: ADK, LangGraph, CrewAI, OAI Agents.
- **Niche hire**: Pydantic AI, Letta (small but high-quality candidate pools).

For ADK specifically: hire Python engineers who can read pydantic; they'll ramp in a week.

## The migration playbook (when you must)

1. **Build a shim.** Wrap framework calls behind your own functions / classes so the framework isn't sprinkled across your codebase.
2. **Port one feature at a time.** Strangler-fig pattern. Run both frameworks side-by-side for a release or two.
3. **Move tests first.** Your evals are the contract. If they pass against the new framework, you're done.
4. **Accept some loss.** Some features won't survive verbatim. Decide which to drop, which to re-build, which to defer.

## The "framework-agnostic" myth

Some teams say "we'll abstract the framework so we can swap it." This rarely survives contact with reality. You can shim the call-site, but the framework's **mental model** is baked into your design (your "agents" might not be entities in another framework; your "events" might not exist). True swap-ability requires keeping the design at the lowest-common-denominator — which means losing what made the framework worth using.

> 🚀 **In Production**
>
> Don't optimize for hypothetical migration. Optimize for **picking right the first time**, with a **clear escape hatch** (shimmed call-sites, framework-agnostic tests, observability that doesn't care which framework emitted the event).

> 🛠 **Have the student run:** for their current project's framework choice, write a 1-page "framework decision record" (FDR): (a) the 5 questions answered, (b) the 3 risks and mitigations, (c) the date and version pinned, (d) a "revisit in 6 months" tickle.

[← Prev: 20_FrameworkComparison/10_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 20_FrameworkComparison/12_KnowledgeCheck →]
