# AGENTS.md — Module 08 MCP (teaching notes for the AI tutor)

## What the student should walk away knowing
- MCP is a protocol, not a framework. ADK consumes it; FastMCP serves it.
- The three transports and when each one is right.
- `MCPToolset` plugs into `tools=[...]` exactly like a `FunctionTool`.
- The lifecycle bug — resources need cleanup; `async with` is the canonical fix.
- Production MCP needs: retries, version pinning, per-request auth, separate latency observability.

## Pacing
- Easy if: student has used FastAPI or any decorator-based web framework — FastMCP feels familiar instantly.
- Easy if: student already understands `asyncio` and async context managers.
- Hard if: student is fuzzy on `async`/`await` — drill [[PY_async]] before tackling the lifecycle page.
- Hard if: student has never seen JSON-RPC. Stay at the "it's a function call over the wire" level; don't get into RPC framing unless asked.

## Watch for these mistakes
- Confusing transport choice — students reach for `StdioConnectionParams` for everything because the antom sample uses it. Push them toward `StreamableHTTPConnectionParams` as the default.
- Forgetting URL path — FastMCP `http` transport defaults to `/mcp`, NOT `/`. The mismatch silently hangs the connection.
- Calling tools before the server is up. Lazy connection bites them.
- Skipping `__aexit__`. Don't move past page 04 without seeing them actually leak (and fix) a stdio process.
- Putting secrets in the agent's prompt instead of MCP server's env / per-request headers.

## When to suggest a detour
- "Tell me more about FastMCP" → [[FastMCP]] (full detour).
- "What's an `async with`?" → [[PY_async]].
- "How do I run this in production?" → preview [[15_Observability/00_Overview]] for the latency split, then [[16_ProductionSecurity/00_Overview]] for auth.

## Mini-drill grading
- Pass = the agent's final reply mentions Tokyo weather and the word "sunny" (proving the MCP tool was called, not hallucinated).
- Bonus = student adds a print statement inside `fetch_weather` and observes it firing only on tool-needing prompts, not greetings.

## Common follow-up questions
- "What if I want to expose Python tools without writing a FastMCP server?" — Just use `FunctionTool` directly (Module 03). MCP is for cross-process / cross-framework reuse.
- "Can one MCPToolset talk to multiple servers?" — No. One toolset per server. Add multiple to `tools=[...]`.
- "What about authentication?" — HTTP transports take a `headers={}` dict. For dynamic per-call auth, use a `before_tool_callback` (Module 07).
- "Does MCPToolset support streaming responses?" — The transports do; the toolset surfaces results as completed values to the LLM today.
