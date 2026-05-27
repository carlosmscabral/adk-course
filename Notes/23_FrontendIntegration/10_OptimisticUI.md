---
module: 23_FrontendIntegration
page: 10_OptimisticUI
title: Optimistic UI — render the tool call while it pends
estimated_minutes: 20
prereqs: [23_FrontendIntegration/08]
concepts: [optimistic_ui, pending_tool_call, HITL, approval_chips]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 09_FileUploadFlow](09_FileUploadFlow.md)  [↑ Map](../../MAP.md)  [Next: 11_DissectingSample →](11_DissectingSample.md)

You are here: 🗺 Integration Track ▸ 23 Frontend Integration ▸ 10 Optimistic UI

# 🛠 Show the tool call before the result lands

A user asks "what's the weather in Paris?". The agent emits `function_call: get_weather(city="Paris")`, the tool runs (3 seconds), then `function_response`. If your UI waits silently for those 3 seconds, the user thinks it hung.

Optimistic UI = render the *call* immediately (a chip, a spinner, a card), then update it in place when the result lands.

## The render contract

```
event with function_call    ─► insert a chip:  "🔧 get_weather(Paris)  ⏳"
event with function_response─► update same chip: "🔧 get_weather(Paris)  ✅ 22°C"
```

You key chips by `function_call_id` (ADK assigns this automatically) so the response lands on the right chip even when multiple tools run in parallel.

```javascript
// Work/frontend/tool_chips.js
const chips = new Map();  // function_call_id → DOM node

function renderEvent(ev) {
  for (const part of ev.content?.parts ?? []) {
    if (part.function_call) {
      const id = part.function_call.id;
      const node = document.createElement("div");
      node.className = "chip pending";
      node.textContent = `🔧 ${part.function_call.name} ⏳`;
      document.getElementById("chat").appendChild(node);
      chips.set(id, node);
    }
    if (part.function_response) {
      const id = part.function_response.id;
      const node = chips.get(id);
      if (node) {
        node.className = "chip done";
        node.textContent = `🔧 ${part.function_response.name} ✅`;
      }
    }
    if (part.text && !ev.partial) {
      // final text — render below the chips
    }
  }
}
```

## HITL — when the tool needs human approval

Some tools shouldn't auto-execute. The agent emits a `function_call`, but the *tool* is a `LongRunningFunctionTool` that pauses until human approval lands.

Module 4B (Human-in-the-Loop, forthcoming) covers the backend mechanics — pause, persist, resume. The frontend's job is:

1. Render the pending tool call as an **approval card** with Approve / Reject buttons.
2. On click, POST to a `/approve` endpoint with the function call id + verdict.
3. The backend resumes the Runner with the verdict written into state or returned from the tool.
4. The stream resumes; chip flips to ✅ (or ❌).

```javascript
// Work/frontend/hitl_chip.js — sketch
function renderApprovalCard(call) {
  const card = document.createElement("div");
  card.className = "card approval";
  card.innerHTML = `
    <p>Run <strong>${call.name}</strong> with args: <code>${JSON.stringify(call.args)}</code>?</p>
    <button data-verdict="approve">Approve</button>
    <button data-verdict="reject">Reject</button>
  `;
  card.querySelectorAll("button").forEach(b => {
    b.onclick = async () => {
      await fetch("/approve", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({call_id: call.id, verdict: b.dataset.verdict}),
      });
      card.classList.add(b.dataset.verdict);
    };
  });
  return card;
}
```

Cross-reference: [4B Human-in-the-Loop & Resume/Cancel](../4B_HumanInTheLoop/) — the backend half. The frontend half lives here.

## Optimistic *messages* — risky, sometimes worth it

You can also render the user's typed message before the network round-trip completes:

```javascript
function send(text) {
  appendUserBubble(text, {pending: true});   // optimistic
  fetch("/run_sse", {...}).then(stream => {
    markUserBubble(text, {pending: false});  // confirmed
  }).catch(() => {
    markUserBubble(text, {failed: true});    // restore + show error
  });
}
```

This feels fast — but on failure you have to **unwind** the optimistic bubble. Add a retry affordance. For chat this trade is usually worth it; for actions (send-email, run-query) it usually isn't.

## Streaming partials inside a chip

If your tool yields progress (e.g., a `LongRunningFunctionTool` that emits intermediate updates), each update arrives as a `function_response` event with progress data. Update the chip's body with progress text or a percentage bar.

```javascript
if (part.function_response) {
  const node = chips.get(part.function_response.id);
  const r = part.function_response.response;
  if (r.status === "in_progress") {
    node.textContent = `🔧 ${part.function_response.name} ${r.progress}%`;
  } else {
    node.textContent = `🔧 ${part.function_response.name} ✅`;
  }
}
```

> 🚀 **In Production**
>
> Optimistic UI hides latency, but it also hides *failures*. Every optimistic action needs a confirmed/failed terminal state visible to the user. Otherwise the user assumes success and you support-ticket the discrepancy. Rule: if it can fail silently, don't be optimistic about it.

> ❓ **Ask the student:** "What's the right chip update if a tool errors? (function_response with an error payload)"
>
> (Answer: flip class to `error`, surface the error text in a tooltip or expandable, let the user click to retry — don't just leave the spinner spinning.)

> 🛠 **Have the student run:** build a tool with `time.sleep(3)` in it, wire it into an agent, watch the chip stay yellow then flip green. Then make the tool raise — watch the chip go red.

[← Prev: 09_FileUploadFlow](09_FileUploadFlow.md)  [↑ Map](../../MAP.md)  [Next: 11_DissectingSample →](11_DissectingSample.md)
