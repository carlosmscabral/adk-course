---
module: 21_AdkApiSurface
page: 07_SessionAndEventResources
title: Session and event resources — the REST CRUD surface
estimated_minutes: 20
prereqs: [21_AdkApiSurface/06, 04_SessionsState/05]
concepts: [session CRUD, list sessions, event history, artifact endpoints]
icon: 📡
in_production: true
detours_suggested: []
---

[← Prev: 06_WrappingInFastAPI](06_WrappingInFastAPI.md)  [↑ Map](../../MAP.md)  [Next: 08_AuthenticatingTheApi →](08_AuthenticatingTheApi.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 07 Session & event resources

---

## 📡 The shape of a session over HTTP

A session is a real REST resource. Its URL contains the three identifiers ADK builds every API around:

```
/apps/{app_name}/users/{user_id}/sessions/{session_id}
```

The full CRUD:

| Method | Path                                                    | Body              | Returns                            |
|--------|---------------------------------------------------------|-------------------|------------------------------------|
| POST   | `/apps/{a}/users/{u}/sessions/{s}`                      | `{"state": {...}}`| Created session (with `id=s`).     |
| POST   | `/apps/{a}/users/{u}/sessions`                          | `{"state": {...}}`| Created session (auto-assigned id).|
| GET    | `/apps/{a}/users/{u}/sessions/{s}`                      | —                 | Full session + event list.         |
| GET    | `/apps/{a}/users/{u}/sessions`                          | —                 | `{"sessions": [...]}` for that user.|
| DELETE | `/apps/{a}/users/{u}/sessions/{s}`                      | —                 | `{"deleted": true}`.               |

The backend is whatever `--session_service_uri` resolved to. Same URL, different storage.

## 📡 Reading a session

```python
# Work/21_AdkApiSurface/07_read_session.py — run with: uv run python Work/21_AdkApiSurface/07_read_session.py
import httpx, json

BASE = "http://localhost:8000"
sess = httpx.get(f"{BASE}/apps/research_assistant/users/alice/sessions/sess-001").json()

print("session id:", sess["id"])
print("state keys:", list(sess.get("state", {}).keys()))
print("event count:", len(sess.get("events", [])))
for ev in sess.get("events", [])[-3:]:
    print(f"  {ev['author']}: {ev.get('content', {}).get('role', '?')}")
```

```
$ uv run python Work/21_AdkApiSurface/07_read_session.py
session id: sess-001
state keys: ['user:preferred_units']
event count: 7
  user: user
  research_assistant: model
  research_assistant: model
```

Notice **the full event history** is in the response. That can be large (KBs to MBs for long conversations). If you're building a frontend, consider client-side pagination or fetching event ranges (a future-ADK feature).

## 📡 Creating a session with seed state

```bash
curl -sS -X POST "http://localhost:8000/apps/research_assistant/users/alice/sessions/sess-onboard" \
  -H "content-type: application/json" \
  -d '{
    "state": {
      "user:preferred_units": "metric",
      "user:locale": "en-CA",
      "app:tier": "pro"
    }
  }'
```

Prefixes (`user:`, `app:`, `temp:`, no-prefix) follow the rules from **04 SessionsState page 04**. The HTTP layer is a pass-through — the state machine lives in the session service.

## 📡 Listing a user's sessions

```python
# Work/21_AdkApiSurface/07_list_sessions.py
import httpx
sessions = httpx.get(
    "http://localhost:8000/apps/research_assistant/users/alice/sessions"
).json()
for s in sessions["sessions"]:
    print(s["id"], s.get("last_update_time"))
```

Useful for a "your conversations" UI panel. The list does **not** include event history — that requires a per-session GET.

## 📡 Deleting

```bash
curl -X DELETE "http://localhost:8000/apps/research_assistant/users/alice/sessions/sess-001"
```

DELETE is **terminal** for most backends. `DatabaseSessionService` may soft-delete; `InMemorySessionService` hard-deletes; `VertexAiSessionService` retains audit metadata even after delete. Cross-link to **22 Deployment Models page 04** for what each backend actually does.

## 📡 Artifacts as nested resources

If your agent attaches artifacts (files, images, BigQuery URIs), they get their own routes under the session:

```
GET    /apps/{a}/users/{u}/sessions/{s}/artifacts
GET    /apps/{a}/users/{u}/sessions/{s}/artifacts/{artifact_name}
GET    /apps/{a}/users/{u}/sessions/{s}/artifacts/{artifact_name}/versions/metadata
GET    /apps/{a}/users/{u}/sessions/{s}/artifacts/{artifact_name}/versions/{version_id}
POST   /apps/{a}/users/{u}/sessions/{s}/artifacts/{artifact_name}     ← upload
DELETE /apps/{a}/users/{u}/sessions/{s}/artifacts/{artifact_name}
```

Full coverage in **04A Artifacts & Heavy Data**. The HTTP surface mirrors the in-process `ArtifactService` API one-to-one.

## ⚠️ Gotcha — `user_id` is opaque to ADK

`user_id` is a string the server takes at face value. If your auth layer doesn't validate that the calling user matches the `user_id` in the URL, **any logged-in user can read any other user's sessions** by guessing IDs. Page 08 covers the middleware that gates this.

## 🚀 In Production

> **🚀 In Production**
>
> The session GET returns the **full event history**. For a 100-turn conversation that's hundreds of KB. Three mitigations: (1) cache the response in your frontend; (2) request only event slices (custom route — ADK doesn't ship one); (3) summarize old events with a background job that rewrites the session to keep the recent N turns plus a digest. The third option is most production-realistic for long-lived conversations.

> ❓ **Ask the student:** "What happens if you POST a session with an ID that already exists?" *(Returns the existing session — idempotent. Useful for "ensure session" patterns.)*

---

[← Prev: 06_WrappingInFastAPI](06_WrappingInFastAPI.md)  [↑ Map](../../MAP.md)  [Next: 08_AuthenticatingTheApi →](08_AuthenticatingTheApi.md)
