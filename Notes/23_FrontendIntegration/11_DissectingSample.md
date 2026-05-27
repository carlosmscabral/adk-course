---
module: 23_FrontendIntegration
page: 11_DissectingSample
title: Dissecting deep-search — a real SPA + ADK backend
estimated_minutes: 45
prereqs: [23_FrontendIntegration/10]
concepts: [deep_search, vite_react, run_sse_parser, agent_research_loop]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 10_OptimisticUI](10_OptimisticUI.md)  [↑ Map](../../MAP.md)  [Next: 12_InProduction →](12_InProduction.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 11 Dissecting Sample

# 🔬 Dissecting `deep-search`

> 🤖 **Tutor:** this page is a **guided read of real code**. Open the sample in the student's editor and walk them through. Don't paste — point at file paths.

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/deep-search/`

## Why this sample

`deep-search` is the canonical "ADK + custom SPA" sample. The backend is a research-loop agent (sequential plan → search → critique → revise → report) emitting rich events with grounding chunks; the frontend is a Vite/React app that consumes the event stream and renders a live activity timeline next to the chat. Every pattern in this module shows up — `user_id`/`session_id` ownership (pattern A — frontend mints UUID), `/run_sse` consumption with a custom SSE parser, partial-vs-final rendering, tool-call timeline chips.

## What we'll trace

By the end the student should be able to:

- Point at the file/line where the frontend mints `session_id`.
- Point at the file/line where the SSE response body is parsed.
- Point at the file/line where the backend agent's research loop is constructed.
- Explain the proxy convention (`/api/...`) the frontend uses to talk to the backend.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/deep-search/` and confirm the `app/` (backend) + `frontend/` (Vite SPA) layout.

## File-by-file walkthrough

### `frontend/vite.config.ts` — the proxy convention

Open it. Note the Vite dev-server proxy: `/api` → `http://localhost:8000`. **This is how the SPA talks to ADK in dev** without CORS issues. The frontend always fetches `/api/whatever`; Vite forwards it. In prod, your reverse proxy (Cloud Run, Nginx) does the same job.

> ❓ **Ask the student:** "Why does the frontend use `/api/...` instead of `http://localhost:8000/...` directly?"
>
> (Answer: avoids CORS preflights in dev; lets the same code work in prod where the API is served from the same origin.)

### `frontend/src/App.tsx` — session creation (line ~83)

```ts
const createSession = async () => {
  const generatedSessionId = uuidv4();   // pattern A: frontend mints
  const response = await fetch(`/api/apps/app/users/u_999/sessions/${generatedSessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  return await response.json();
};
```

Two things to flag:

- `uuidv4()` — **pattern A** from page 01 (frontend mints `session_id`).
- `u_999` — hard-coded user_id. This is a sample; in your prod app this comes from your auth (page 02). The sample doesn't have auth wired.

### `frontend/src/App.tsx` — the SSE fetch (line ~326)

```ts
const response = await fetch("/api/run_sse", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    appName: currentAppName,
    userId: currentUserId,
    sessionId: currentSessionId,
    newMessage: { parts: [{ text: query }], role: "user" },
    streaming: false   // surprising — see note below
  }),
});
```

> ❓ **Ask the student:** "Why `streaming: false` if this is SSE?"
>
> (Answer: in ADK's `/run_sse` semantics, `streaming` controls whether the *model* streams token-by-token. Even with `streaming: false`, ADK still sends each *event* — tool call, tool response, final message — as a separate SSE frame. The sample wants distinct event-level chunks for the activity timeline, not token-level chunks for the text bubble.)

### `frontend/src/App.tsx` — the SSE parser (line ~358+)

The sample writes its own SSE parser instead of using `EventSource`. Walk the reader-loop with the student. Notice:

- `reader.read()` + `TextDecoder` — same shape as page 05 vanilla SPA.
- Line-buffered accumulation — handles partial reads where `\n\n` lands across chunks.
- Each event is parsed JSON and dispatched into either the chat text or the activity timeline.

### `frontend/src/components/ActivityTimeline.tsx`

This is the **right column** of the UI. Each agent event becomes a timeline item:

- "Planning research..." (sub-agent transfer)
- "Searching for X" (tool call chip — page 10 optimistic pattern)
- "Found 8 sources" (tool response with grounding count)
- "Critiquing..." → "Revising..." (the loop iterations)

This is what makes deep-search feel alive. The user sees the agent *thinking*. That timeline maps 1:1 to the event stream from `run_sse` — nothing magic.

### `app/agent.py` — the backend

Open `/home/carloscabral/study/adk-samples/python/agents/deep-search/app/agent.py`. Note the imports:

```python
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
```

The shape is: `SequentialAgent(plan → LoopAgent(search → critique) → report)`. The loop iterates until the critic says `grade: "pass"`. Every event from these sub-agents flows through the SSE stream to the timeline.

The `collect_research_sources_callback` writes grounding metadata into state — the frontend reads these from the event's `actions.stateDelta` to render the citation chips.

### How the backend is served

The sample's `Makefile` runs `adk api_server` for the backend and `vite dev` for the frontend. In prod (`adk deploy`), the SPA is built (`npm run build`) and served as static files alongside the ADK API.

## Trace one turn

```
user types "what's new in cold-fusion research?"
  → frontend mints session_id (uuidv4)
  → POST /api/apps/app/users/u_999/sessions/{sid}
  → frontend POSTs /api/run_sse with the prompt
  → backend constructs Runner, calls runner.run_async(...)
  → events stream back, one per:
      - plan agent emits a SearchQuery list (state delta)
      - search loop iteration 1: function_call google_search → response with chunks
      - critic agent emits Feedback (grade=fail, follow-up queries)
      - loop iteration 2: more searches
      - critic: grade=pass
      - report agent emits final text (partials + final)
  → frontend dispatches each event:
      - text → chat bubble (accumulate partials)
      - tool_call → timeline chip ⏳
      - tool_response → timeline chip ✅ + source count
      - state_delta with citations → citation chips below text
```

## Module concepts present in this sample

| Module concept | Where in the sample |
|---|---|
| Pattern A — frontend mints `session_id` (page 01) | `frontend/src/App.tsx:84` (`uuidv4()`) |
| Custom SSE parser (page 03, page 05) | `frontend/src/App.tsx:~360` (reader loop) |
| Proxy convention `/api` (page 05) | `frontend/vite.config.ts` |
| Partial vs final text (page 08) | `accumulatedTextRef` handling in `App.tsx` |
| Tool-call timeline (page 10) | `ActivityTimeline.tsx` |
| State-delta consumption (page 08 cross-ref) | `actions.stateDelta` parsing in `App.tsx` |

## What it doesn't have (yet)

- **Auth** — `u_999` is hard-coded. You'd add Firebase or OIDC per page 02 before shipping.
- **File upload** — not relevant to this agent. See `realtime-conversational-agent` for a sample with file/audio input.
- **HITL approval** — none of the loops gate on human approval. Add per page 10 + module 4B.

> 🛠 **Have the student run:** `cd ~/study/adk-samples/python/agents/deep-search && make dev` (or follow its README). Hit the UI with a query, watch the timeline populate.

[← Prev: 10_OptimisticUI](10_OptimisticUI.md)  [↑ Map](../../MAP.md)  [Next: 12_InProduction →](12_InProduction.md)
