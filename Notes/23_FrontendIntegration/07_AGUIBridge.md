---
module: 23_FrontendIntegration
page: 07_AGUIBridge
title: AG-UI — when your frontend already speaks an agent protocol
estimated_minutes: 15
prereqs: [23_FrontendIntegration/06]
concepts: [AG-UI, protocol_bridge, framework_agnostic_ui]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 06_A2UIClient](06_A2UIClient.md)  [↑ Map](../../MAP.md)  [Next: 08_StreamingPartialResults →](08_StreamingPartialResults.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 07 AG-UI Bridge

# 🧠 AG-UI — frontend protocol, framework-agnostic

**AG-UI** (Agent-User Interaction protocol) is an open spec for how frontends and backends exchange agent events: streaming text, tool calls, state changes, generative UI. Think of it as "AG-UI is to frontends what A2A is to agent-agent" — a wire contract that lets you swap *either side* without rewriting the other.

You'll meet AG-UI when:

- Your frontend was built with [CopilotKit](https://copilotkit.ai) or a similar AG-UI-aware UI framework.
- Your frontend team standardized on AG-UI to keep the option of swapping backends.
- You want a streaming chat UI **without** writing event-stream parsers.

## ADK + AG-UI

ADK doesn't ship a built-in AG-UI server (as of 2.0 GA). The bridge is a thin shim: parse the AG-UI event spec into ADK's `Runner` calls, translate ADK events back into AG-UI frames.

### Shape of the shim

```python
# Work/23_frontend/agui_shim.py — pseudo-code shape; a real shim is ~150 LOC
import json, asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent
from google.genai import types

agent = Agent(name="demo", model="gemini-2.5-flash", instruction="be helpful")
runner = InMemoryRunner(app_name="demo", agent=agent)

app = FastAPI()

@app.post("/agui")
async def agui(req: Request):
    """Speak the AG-UI event protocol (SSE-style) against ADK underneath."""
    body = await req.json()
    user_id = body["userId"]
    thread_id = body["threadId"]              # AG-UI's term for session_id
    text = body["messages"][-1]["content"]

    session = await runner.session_service.get_session(
        app_name="demo", user_id=user_id, session_id=thread_id
    ) or await runner.session_service.create_session(
        app_name="demo", user_id=user_id, session_id=thread_id
    )

    async def emit():
        # AG-UI: start of run
        yield f"data: {json.dumps({'type': 'RUN_STARTED', 'threadId': thread_id})}\n\n"
        msg = types.Content(role="user", parts=[types.Part(text=text)])
        async for ev in runner.run_async(user_id=user_id, session_id=thread_id, new_message=msg):
            if ev.content and ev.content.parts:
                for p in ev.content.parts:
                    if p.text:
                        yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CHUNK', 'delta': p.text})}\n\n"
                    if p.function_call:
                        yield f"data: {json.dumps({'type': 'TOOL_CALL_START', 'name': p.function_call.name})}\n\n"
        yield f"data: {json.dumps({'type': 'RUN_FINISHED'})}\n\n"

    return StreamingResponse(emit(), media_type="text/event-stream")
```

That's the whole bridge concept. Your AG-UI-aware frontend then "just works" — it doesn't know it's talking to ADK.

## Why bother (vs. building your own SPA)

Pick AG-UI when:

- **Frontend team is upstream.** They already shipped a CopilotKit/AG-UI UI for another backend. You're slotting ADK underneath.
- **You want to swap backends later.** AG-UI is provider-agnostic — moving from LangChain to ADK is "change the shim", not "rewrite the frontend".
- **Generative UI is a goal.** AG-UI defines patterns for the agent to *emit* UI components ("show this user a confirmation button"), not just text.

Skip AG-UI when:

- You control both ends and your needs are simple — vanilla SSE / WebSocket (pages 03–05) is less indirection.
- You're using `adk web` for dev and shipping a custom branded SPA for prod.

## Cross-reference

- [21 ADK API Surface](../21_ApiSurface/) — what AG-UI sits *above*. The shim translates AG-UI ↔ that surface.
- [10 A2A](../10_A2A/) — same shape, different audience: A2A is agent↔agent, AG-UI is agent↔frontend.

> 🚀 **In Production**
>
> If you build an AG-UI shim, version it. AG-UI is a moving spec; your frontend will pin a version, and your shim's translation tables must match. Mismatch = the frontend silently drops events it doesn't recognize.

> ❓ **Ask the student:** "If both A2A and AG-UI are 'agent protocols', what's the difference in audience?"
>
> (Answer: A2A is server↔server, agent-to-agent. AG-UI is server↔browser, agent-to-user. A2A speaks task lifecycle; AG-UI speaks UI events.)

> 🤖 **Tutor:** if the student isn't using a CopilotKit-style frontend, this page is informational — don't dwell. The custom SPA path (page 05) is the default.

[← Prev: 06_A2UIClient](06_A2UIClient.md)  [↑ Map](../../MAP.md)  [Next: 08_StreamingPartialResults →](08_StreamingPartialResults.md)
