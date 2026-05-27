---
module: 21_AdkApiSurface
page: 03_RestShapes
title: REST shapes — /run, sessions, and the Event JSON
estimated_minutes: 25
prereqs: [21_AdkApiSurface/02, 04_SessionsState/02]
concepts: [POST /run, Event JSON, content.parts, actions, function_call]
icon: 📡
in_production: true
detours_suggested: [GeminiPayload]
---

[← Prev: 02_AdkApiServer](02_AdkApiServer.md)  [↑ Map](../../MAP.md)  [Next: 04_SseEndpoints →](04_SseEndpoints.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 03 REST shapes

---

## 📡 The request

`POST /run` takes one JSON body:

```json
{
  "app_name":   "research_assistant",
  "user_id":    "alice",
  "session_id": "sess-001",
  "new_message": {
    "role": "user",
    "parts": [{"text": "What is the speed of light in m/s?"}]
  },
  "streaming": false
}
```

Four required fields and one optional `streaming`. The `new_message` shape is the same `google.genai.types.Content` you build by hand in module 04. Cross-link: [[GeminiPayload]] for the full Content/Part schema.

## 📡 The response — `List[Event]`

`/run` returns **the complete list of events** the runner produced for that turn — in order. One turn typically yields 2-6 events.

```json
[
  {
    "id": "ev-001",
    "author": "research_assistant",
    "invocation_id": "inv-abc",
    "timestamp": 1716827521.412,
    "content": {
      "role": "model",
      "parts": [{"text": "The speed of light in a vacuum is approximately 299,792,458 m/s."}]
    },
    "actions": {"state_delta": {}, "artifact_delta": {}}
  }
]
```

A turn that involved one tool call looks like this:

```json
[
  {"author": "research_assistant", "content": {"role": "model",
     "parts": [{"functionCall": {"name": "google_search", "args": {"q": "ADK release date"}}}]}},
  {"author": "research_assistant", "content": {"role": "user",
     "parts": [{"functionResponse": {"name": "google_search", "response": {"results": ["..."]}}}]}},
  {"author": "research_assistant", "content": {"role": "model",
     "parts": [{"text": "ADK 2.0 GA shipped in May 2026."}]}}
]
```

Three events for one turn: the function call, the function response, and the final text. Notice the `functionResponse` event's `role` is `"user"` — that is how Gemini frames tool results back to the model.

## 📡 Sessions in the URL

The session resource lives at:

```
/apps/{app_name}/users/{user_id}/sessions/{session_id}
```

CRUD verbs:

| Method | Path                                                    | What it does                                        |
|--------|---------------------------------------------------------|-----------------------------------------------------|
| POST   | `/apps/{a}/users/{u}/sessions/{s}`                      | Create session with explicit ID. Body: `{"state": {...}}`. |
| POST   | `/apps/{a}/users/{u}/sessions`                          | Create session with auto-generated ID.              |
| GET    | `/apps/{a}/users/{u}/sessions/{s}`                      | Fetch full session + events.                        |
| GET    | `/apps/{a}/users/{u}/sessions`                          | List sessions for that user.                        |
| DELETE | `/apps/{a}/users/{u}/sessions/{s}`                      | Delete (irreversible in most backends).             |

Sessions are **eagerly created**. A `/run` call against a non-existent `session_id` returns 404 unless you POST the session first.

## 📡 Sketch — a tiny client by hand

```python
# Work/21_AdkApiSurface/03_run_client.py — run with: uv run python Work/21_AdkApiSurface/03_run_client.py
# Pre-req: adk api_server Work/21_AdkApiSurface --port 8000
import httpx, json

BASE = "http://localhost:8000"
APP = "research_assistant"
USER = "alice"
SESSION = "sess-001"

# 1. Create session (idempotent: 200 if exists, 200 on first create)
httpx.post(f"{BASE}/apps/{APP}/users/{USER}/sessions/{SESSION}", json={})

# 2. Send one turn
resp = httpx.post(
    f"{BASE}/run",
    json={
        "app_name": APP,
        "user_id": USER,
        "session_id": SESSION,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Speed of light in m/s, integer only."}],
        },
    },
    timeout=60.0,
)
events = resp.json()
print(f"got {len(events)} events")
for ev in events:
    text_parts = [p.get("text", "") for p in (ev.get("content", {}).get("parts") or [])]
    if any(text_parts):
        print(f"  {ev['author']}: {' '.join(text_parts)}")
```

```
$ uv run python Work/21_AdkApiSurface/03_run_client.py
got 1 events
  research_assistant: 299792458
```

> 🛠 **Have the student run:** the script above. Then have them re-run it without re-creating the session — see that history accumulates across calls (the second turn will see the first turn's user message).

## 📡 `actions` — the side-channel

Every event carries an `actions` block beside `content`. The fields you'll meet most:

- `state_delta` — keys to apply to session state (state machine, page 04 of this module).
- `artifact_delta` — artifact IDs newly attached.
- `transfer_to_agent` — `sub_agent` to route to next (multi-agent).
- `escalate` — request the parent agent take over.
- `skip_summarization` — bypass auto-summarization on long histories.

When you read events client-side, **always** check `actions` if you care about state or routing; the text in `content.parts` is the user-visible slice but not the full story.

## ⚠️ Gotcha — streaming vs `/run`

`/run` waits for the **entire** turn before returning. Long tool calls can hold the connection for tens of seconds. For interactive UIs, use `/run_sse` (page 04). For voice, use `/run_live` (page 05).

## 🚀 In Production

> **🚀 In Production**
>
> The full `Event` JSON exposes **internal state** — `actions.state_delta`, function-call args, tool names. Treat the raw events as **internal** and post-process before sending to a browser. Standard recipe: strip `actions` and any `functionCall`/`functionResponse` parts unless the UI specifically needs them. See module **16 Production & Security** for the redactor pattern.

---

[← Prev: 02_AdkApiServer](02_AdkApiServer.md)  [↑ Map](../../MAP.md)  [Next: 04_SseEndpoints →](04_SseEndpoints.md)
