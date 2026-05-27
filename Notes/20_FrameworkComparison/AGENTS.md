# AGENTS.md — Module 20 Framework Comparison (teaching notes for the AI tutor)

## What the student should walk away knowing
- The 7 axes for scoring agent frameworks (multi-agent style, tool model, memory, observability, code-exec, vendor neutrality, maturity).
- A one-sentence summary of each: LangChain/LangGraph, CrewAI, AutoGen/AG2, OpenAI Agents SDK, Pydantic AI, Letta/MemGPT.
- The decision flowchart's 5 questions, in order.
- ADK's specific moats (A2A, MCP first-class, GCP integration, evals, Live, Skills) and where the alternatives still win.
- The 4 risks to underwrite before committing (churn, vendor, abstraction-leak, hire-ability).

## Pacing
- Easy if: student has used at least one other framework (LangChain or OpenAI Agents). They'll fly through 02-07 because they're confirming what they know.
- Hard if: student has only ever used ADK. They will need to actually skim each framework's hello-world snippet rather than skip past it. Encourage opening each framework's docs/README in a tab while reading.

## Watch for these mistakes
- Treating the matrix as a leaderboard. It's a snapshot per-axis, not an overall ranking.
- Dismissing a framework on a single weakness ("LangChain churns, so it's bad"). The student should weigh strengths AND weaknesses.
- Recommending ADK reflexively because we've spent 20 modules on it. Probe with "what if your team won't deploy on GCP?" — they should reach for LangGraph.

## When to suggest a detour
- Student fuzzy on what "state-graph" means → 06 GraphWorkflows recap.
- Student asks "what's A2A actually do for me?" → suggest re-reading `10_A2A/`.

## Mini-drill grading
- The 200-word essay rubric is in the YAML. Use LLM judging.
- If the student writes too much, ask them to cut. If too short, ask them to expand on the LangGraph trade-off they conceded.
- Bonus probe: "Now write the *opposite* essay — justify LangGraph over ADK for the same spec." (Forces real understanding; reveals whether their first essay was fair or one-sided.)

## Things to say verbatim
- "Framework choice is structural debt — pick once, live with it for years. The decision deserves an FDR (framework decision record), not a gut call."
- "Every framework's abstractions leak. You're choosing whose leaks you can tolerate."
- "The most expensive choice isn't the wrong one — it's the late one. Pick within a sprint."
