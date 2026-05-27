---
module: 04_SessionsState
page: 10_PersistentSessions
title: Persistent sessions — DatabaseSessionService
estimated_minutes: 15
prereqs: [04_SessionsState/09]
concepts: [DatabaseSessionService, sqlite, postgres, VertexAiSessionService]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/09_OutputKeyShortcut](09_OutputKeyShortcut.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/11_DissectingSample →](11_DissectingSample.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 10 Persistent sessions

# 🚀 Persistent sessions

`InMemorySessionService` is convenient for dev. Real apps need persistence.

## 🚀 The drop-in: `DatabaseSessionService`

```python
from google.adk.sessions import DatabaseSessionService

session_service = DatabaseSessionService(
    db_url="sqlite:///sessions.db",          # SQLite file
    # db_url="postgresql://user:pw@host/db", # Postgres
)
```

That's the entire change. Everything else — `Runner`, `Agent`, `run_async` — is identical. Sessions and their events persist across process restarts.

> 🛠 **Have the student do this:** modify their `hello_agent.py` (Module 02 mini-drill) to use `DatabaseSessionService(db_url="sqlite:///Work/sessions.db")`. Run it twice with the same `session_id` (hard-code one). Note: the second run continues the conversation because state and events were persisted.

## 🚀 Install the SQL driver

`DatabaseSessionService` needs the `[db]` extra:

```bash
$ pip install "google-adk[db]"
```

That pulls in `sqlalchemy` (and `sqlite3` is in the stdlib). For Postgres you'll also want `psycopg[binary]`:

```bash
$ pip install "google-adk[db]" "psycopg[binary]"
```

## 🚀 The four-option matrix

| Backend | Url / class | When |
|---|---|---|
| In-memory | `InMemorySessionService()` | unit tests, throwaway demos |
| SQLite | `DatabaseSessionService(db_url="sqlite:///x.db")` | single instance, file persistence |
| Postgres / MySQL | `DatabaseSessionService(db_url="postgresql://...")` | multi-instance, shared backend |
| Vertex AI | `VertexAiSessionService(project=, location=, ...)` | running on Agent Engine; managed by Google |

The agent code is identical across all four. **You change one line to migrate.**

## 🧠 Migration discipline

Going from `InMemorySessionService` to `DatabaseSessionService` at launch loses zero data (in-memory was always going to vanish on restart). Going the other way is fine for tests too.

Going from SQLite to Postgres mid-flight: you have data to migrate. Plan for it — Module 16 covers session-data export/import patterns.

## 🚀 Vertex AI Session Service (preview)

If you deploy on Agent Engine (`adk deploy agent_engine ...`), use:

```python
from google.adk.sessions import VertexAiSessionService

session_service = VertexAiSessionService(
    project="my-gcp-project",
    location="us-central1",
)
```

Google manages the storage. Multi-region replication, retention, encryption — handled. The tradeoff: GCP-only and tied to your Vertex project. Module 10A introduces it properly.

## ❓ Quick check

> ❓ **Ask the student:** you swap `InMemorySessionService()` for `DatabaseSessionService(db_url="sqlite:///x.db")` in a service that's been running for a week with 1000 active conversations. What happens?
> *(Expected: those 1000 conversations were in memory; they're gone on restart. The new backend starts empty. Lesson: pick persistent from day one if persistence matters.)*

> **🚀 In Production**
>
> If you use `DatabaseSessionService` against SQLite, remember SQLite **does not support concurrent writers well**. Fine for single-process services; bad for multi-process. The moment you horizontally scale, switch to Postgres. Same one-line change.

---

[← Prev: 04_SessionsState/09_OutputKeyShortcut](09_OutputKeyShortcut.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/11_DissectingSample →](11_DissectingSample.md)
