---
module: 04_SessionsState
page: 08_SessionMigrate
title: Session migrate — move sessions across services and schemas
estimated_minutes: 20
prereqs: [04_SessionsState/07]
concepts: [adk migrate session, SessionService, schema-version, cross-backend]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/07_SessionRewind](07_SessionRewind.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/09_OutputKeyShortcut →](09_OutputKeyShortcut.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 08 Session Migrate

# 🚀 Session migrate (NEW in 2.0)

You ran dev on `InMemorySessionService`, staging on `DatabaseSessionService(sqlite)`, and prod is moving to `VertexAiSessionService`. Or your session schema bumped from v0 → v1 with the 2.0 GA cut. Either way you need to move sessions across backends and across schema versions without losing state or events. ADK 2.0 ships `adk migrate session` and a programmatic API.

## 🧠 The CLI shape

```bash
$ adk migrate session \
    --source-url sqlite:///./dev_sessions.db \
    --dest-url postgresql://prod_user:pw@prod-host/sessions \
    --app-name research_assistant \
    --schema-version v1 \
    --dry-run
```

`--dry-run` prints the migration plan: how many sessions, how many events, any schema warnings. Remove the flag to commit.

## 🧠 Programmatic migration

```python
# Work/08_migrate.py — run with: uv run python Work/08_migrate.py
from google.adk.sessions import DatabaseSessionService, VertexAiSessionService
from google.adk.sessions.migration import migrate_sessions
import asyncio


async def main():
    src = DatabaseSessionService(db_url="sqlite:///./dev_sessions.db")
    dst = VertexAiSessionService(project="my-gcp-project", location="us-central1")

    report = await migrate_sessions(
        source=src,
        dest=dst,
        app_name="research_assistant",
        schema_version="v1",       # target schema
        batch_size=50,
        on_conflict="skip",        # skip | overwrite | error
    )
    print(f"migrated: {report.migrated}  skipped: {report.skipped}  "
          f"failed: {report.failed}")


asyncio.run(main())
```

```
$ uv run python Work/08_migrate.py
migrated: 1247  skipped: 3  failed: 0
```

The `migrate_sessions` helper streams sessions in batches so you can move millions without blowing memory.

## 🧠 What gets carried over

| Carries | Notes |
|---|---|
| All events (active + inactive) | Rewind history survives the move |
| Session-scoped state | Replayed identically |
| `user:` state | Per-user; keyed by `user_id` (must be stable across backends) |
| `app:` state | Per-app; keyed by `app_name` (must match) |
| `temp:` state | Dropped — `temp:` is by-definition invocation-local |
| Artifact references | Carried, but **the artifact bytes do not move** — handle artifact storage separately (Module 04A) |

## ⚠️ Schema versions

ADK 2.0 introduced `schema_version` on the persisted session. v0 (pre-2.0) sessions do not carry `cache_metadata` or the compaction `inactive_event_ids` field; migration synthesizes empty values. The reverse (v1 → v0) is **rejected** — you cannot downgrade.

If you maintain an older agent fleet alongside 2.0, run them against a v0 backend until you cut everything over.

## 🧠 The three real migration scenarios

| From → To | Why | Tooling |
|---|---|---|
| `InMemory` → `Database(sqlite)` | First production deploy | impossible — in-memory is by definition non-persistent. Start fresh. |
| `Database(sqlite)` → `Database(postgres)` | Horizontal scale | `adk migrate session` |
| `Database(postgres)` → `VertexAiSessionService` | Move to Agent Engine | `adk migrate session` (handles `user:` per-user fan-out) |

## 🧠 Migration + rewind

Migration preserves event IDs. A session you rewound on the source still presents the same active/inactive view on the destination — and you can continue rewinding after the move. The two features are designed to compose.

## ❓ Quiz

> ❓ **Ask the student:** you migrate from `DatabaseSessionService(sqlite)` to `VertexAiSessionService`. Your sessions reference artifacts stored in `InMemoryArtifactService`. What breaks?
> *(Expected: the artifact bytes were in process memory on the dev box; they are not on Vertex. The artifact REFERENCES move but the bytes don't exist on the destination. You must also migrate your artifact backend — see Module 04A. The fix is to move artifacts to `GcsArtifactService` before migrating sessions.)*

> 🛠 **Have the student run:** `adk migrate session --source-url sqlite:///./dev.db --dest-url sqlite:///./staging.db --app-name your_app --dry-run` against any throwaway DB. Read the plan output.

> **🚀 In Production**
>
> Always `--dry-run` first. Always migrate during a maintenance window (or run dual-write for a transition period — write to both backends and read from the new one). On Vertex, the destination is regional — pick `location=` to match your agent's region or every read takes a cross-region hop. Plan rollback: keep the source backend writable until you have verified 24h of clean reads on the destination.

---

[← Prev: 04_SessionsState/07_SessionRewind](07_SessionRewind.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/09_OutputKeyShortcut →](09_OutputKeyShortcut.md)
