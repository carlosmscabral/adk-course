---
module: 23_FrontendIntegration
page: 08_StreamingPartialResults
title: Rendering partial tokens vs final results
estimated_minutes: 20
prereqs: [23_FrontendIntegration/03]
concepts: [event_partial, turn_complete, idempotent_render, replace_vs_append]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 07_AGUIBridge](07_AGUIBridge.md)  [↑ Map](../../MAP.md)  [Next: 09_FileUploadFlow →](09_FileUploadFlow.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 08 Streaming Partial Results

# 🛠 Partial vs final — two flags, two render paths

Every ADK event your frontend receives has two booleans your render code cares about:

| Flag | Meaning |
|------|---------|
| `event.partial` | Is this a token-by-token chunk? If `true`, more chunks follow. |
| `event.turn_complete` | Is this the last event of the agent's turn? After this, you accept new user input. |

**Concretely** — Gemini sends a stream of partials (`partial=true`) and then one *consolidated* final event (`partial=false`) containing the full text. If you naively append every event's text, you'll double-print the final.

## The naive bug

```javascript
// BUG — produces "hello world helloworld" or worse
es.onmessage = (e) => {
  const ev = JSON.parse(e.data);
  out.textContent += ev.content?.parts?.[0]?.text ?? "";
};
```

## The fix — append partials, replace on final

```javascript
// Work/frontend/render_partial.js
let buffer = "";
es.onmessage = (e) => {
  const ev = JSON.parse(e.data);
  const text = ev.content?.parts?.[0]?.text ?? "";
  if (!text) return;
  if (ev.partial) {
    buffer += text;
    document.getElementById("current").textContent = buffer;
  } else {
    // final event — REPLACE the buffer; the final text is the consolidated form
    document.getElementById("current").textContent = text;
    buffer = "";
  }
};
```

Or the inverse pattern: **ignore the final consolidated event entirely** if you've been accumulating partials.

```javascript
es.onmessage = (e) => {
  const ev = JSON.parse(e.data);
  if (!ev.partial) return;                       // skip final consolidation
  const text = ev.content?.parts?.[0]?.text ?? "";
  document.getElementById("current").textContent += text;
};
```

Either works. Pick one and stay consistent.

## Server-side check — what's actually on the wire

```python
# Work/23_frontend/peek_partials.py — run with: uv run python Work/23_frontend/peek_partials.py
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = Agent(name="poet", model="gemini-2.5-flash", instruction="write a 4-line haiku about rain")

async def main():
    r = InMemoryRunner(app_name="demo", agent=agent)
    s = await r.session_service.create_session(app_name="demo", user_id="u")
    msg = types.Content(role="user", parts=[types.Part(text="haiku please")])
    async for ev in r.run_async(user_id="u", session_id=s.id, new_message=msg):
        text = ""
        if ev.content and ev.content.parts:
            text = "".join(p.text or "" for p in ev.content.parts)
        print(f"partial={ev.partial} turn_complete={ev.turn_complete} text={text[:40]!r}")

asyncio.run(main())
```

Run that. You'll see a flurry of `partial=True` events with growing chunks, then one `partial=False, turn_complete=True` event with the consolidated text.

## Tool calls in the stream

When the agent calls a tool, you get events with `function_call` in `content.parts` (request) and `function_response` (result). These are **not** partial text — they're discrete UI affordances. Render them as separate visual elements (chips, expandable cards) rather than appending to the text buffer.

```javascript
function render(ev) {
  for (const part of ev.content?.parts ?? []) {
    if (part.text) appendText(part.text, ev.partial);
    if (part.function_call) renderToolChip(part.function_call.name, "pending");
    if (part.function_response) updateToolChip(part.function_response.name, "done", part.function_response.response);
  }
}
```

Page 10 covers the optimistic pattern in detail.

## Final state — when do you accept new user input?

The rule: wait for an event with `turn_complete=true`. Until then, the agent might still emit more text, tool calls, or sub-agent transfers. If you accept input mid-turn, you'll race the agent.

```javascript
es.onmessage = (e) => {
  const ev = JSON.parse(e.data);
  render(ev);
  if (ev.turn_complete) {
    inputBox.disabled = false;   // re-enable
    inputBox.focus();
  }
};
```

Optimistic variant: re-enable on `turn_complete`, *but* if the user types before that, queue locally and send on `turn_complete`. Don't send mid-turn.

> 🚀 **In Production**
>
> Partial events arrive ~50-200ms apart at full speed. If your render path triggers a React reconcile per event, you'll burn CPU and the UI will jank. Throttle: requestAnimationFrame'd flush of an in-memory buffer, or batch every N events.

> ❓ **Ask the student:** "If you accumulate partials AND render the final event, what does the user see?"
>
> (Answer: doubled text. The final event is the full consolidated text; partials already gave you the same content piecewise. Pick one path.)

> 🛠 **Have the student run:** `peek_partials.py`. Count the partials vs the finals. Then write a tiny SPA that renders partials only, and confirm no duplication.

[← Prev: 07_AGUIBridge](07_AGUIBridge.md)  [↑ Map](../../MAP.md)  [Next: 09_FileUploadFlow →](09_FileUploadFlow.md)
