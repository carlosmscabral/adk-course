# AGENTS.md — Module 10 A2A (teaching notes for the AI tutor)

## What the student should walk away knowing
- A2A is the network contract that turns an ADK agent into a callable service.
- `AgentCard` is the manifest; ADK auto-builds it from the agent definition.
- `to_a2a(root_agent)` returns a Starlette ASGI app — run it with uvicorn.
- `RemoteA2aAgent` consumes a remote agent as if it were local — usable as a sub_agent.
- A2A and MCP are NOT alternatives; they compose at different granularities (whole agent vs single function).
- Production A2A needs auth, versioning, rate limits, and persistent stores OR sticky sessions.

## Pacing
- Easy if: student has built any HTTP service before — the mental model maps cleanly.
- Easy if: student is already comfortable with multi-agent (Module 05).
- Hard if: student is fuzzy on async / ASGI — give them the uvicorn command verbatim and don't dwell.
- Hard if: student tries to debug two-process bugs without separate terminals. Insist on the two-terminal setup.

## Watch for these mistakes
- Conflating A2A and MCP. Reach for the A2A-vs-MCP figure as soon as it comes up.
- Forgetting `uvicorn` — they import `a2a_app` and run `python` and see nothing happen.
- Writing agent_card="http://...:10001/" instead of full `.well-known/agent-card.json` path.
- Designing for one replica then surprised when sticky sessions don't exist.
- Skipping AgentCard versioning ("it's just a Python field"). Push back: it's a public contract.

## When to suggest a detour
- "How do I lay this out visually?" → [[a2UI]] (visual builder for A2A flows).
- "How do I auth across orgs?" → [[16_ProductionSecurity/00_Overview]].
- "What's a Starlette / ASGI?" → quick aside, link to Starlette docs; don't go deep.

## Mini-drill grading
- Pass = student can demonstrate the AgentCard via curl AND a successful end-to-end call through `RemoteA2aAgent`.
- Pass requires actually running two processes. If they smush it into one, fail and make them split.

## Common follow-up questions
- "Can I expose just one method instead of the whole agent?" — No; A2A is agent-level. Use MCP for function-level.
- "Can RemoteA2aAgent stream?" — Yes, via the underlying A2A streaming. ADK adapts the events into the parent's event stream.
- "Can I have multiple agents on one port?" — Use `adk api_server --a2a path/to/agents_dir` to serve each at `/<name>/.well-known/agent-card.json`.
- "What's the relationship between A2A and `AgentTool`?" — AgentTool wraps a local Agent as a function; RemoteA2aAgent wraps a remote Agent as a sub_agent. Compose freely.
