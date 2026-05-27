---
module: 04_SessionsState
page: 08_SessionMigrate
title: Session migrate — upgrade a DB-backed session store's schema
estimated_minutes: 15
prereqs: [04_SessionsState/07]
concepts: [adk migrate session, migration_runner.upgrade, schema-version, DatabaseSessionService]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/07_SessionRewind](07_SessionRewind.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/09_OutputKeyShortcut →](09_OutputKeyShortcut.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 08 Session Migrate

# 🚀 Session migrate (NEW in 2.0)

`DatabaseSessionService` writes sessions and events into a SQL DB you control (sqlite, Postgres, MySQL, anything SQLAlchemy speaks). When ADK bumps the **on-disk schema** between versions, your old DB still has the old shape — the service can read it for a release or two, but the supported path is to migrate. ADK 2.0 ships `adk migrate session` (a CLI) and `migration_runner.upgrade(...)` (a function) to do that.

This is a **DB schema upgrade tool**, not a cross-backend session mover. It walks the migration graph in `google/adk/sessions/migration/migration_runner.py` (currently `0` pickle → `1` JSON) and writes the destination DB at `LATEST_SCHEMA_VERSION`. There is no built-in helper for moving sessions from `InMemorySessionService` to `DatabaseSessionService`, or from `DatabaseSessionService` to `VertexAiSessionService` — those are different stores entirely.

## 🧠 The CLI

```bash
$ adk migrate session \
    --source_db_url sqlite:///./old_sessions.db \
    --dest_db_url   sqlite:///./new_sessions.db
```

That's it — two required flags, plus optional `--log_level`. Note the **underscores** in the flag names. Source and destination must be different URLs; in-place migration is rejected.

If the source is already at `LATEST_SCHEMA_VERSION`, the runner logs "no migration needed" and exits. Otherwise it walks the version chain, writing intermediate steps into temporary SQLite files and the final result into `--dest_db_url`.

## 🧠 Programmatic call

```python
# Work/08_migrate.py — run with: uv run python Work/08_migrate.py
from google.adk.sessions.migration import migration_runner


def main():
    migration_runner.upgrade(
        source_db_url="sqlite:///./old_sessions.db",
        dest_db_url="sqlite:///./new_sessions.db",
    )
    print("done")


main()
```

```
$ uv run python Work/08_migrate.py
INFO ... Migrating from sqlite:///./old_sessions.db to sqlite:///./new_sessions.db (schema v1)...
INFO ... Finished migration step to schema 1.
done
```

`upgrade(...)` is a plain (sync) function. It raises `RuntimeError` if you pass the same URL for source and destination, or if no migration path is registered for the source's detected schema version.

## ⚠️ What this does NOT do

* **Does NOT move sessions across services.** `InMemory` → `Database` → `VertexAi` are different backends with different storage; there is no built-in tool that copies sessions between them. If you need that, you write it yourself: `list_sessions` + `get_session` + `create_session` + `append_event`, in a loop, against the two services.
* **Does NOT carry data the new schema doesn't model.** Pickled fields that no longer exist on the JSON schema are dropped.
* **Does NOT support downgrades.** Once you're on the newer schema, the migration graph only walks forward.
* **Does NOT support in-place migration.** Source and destination URLs must differ — the runner reads the source and writes a fresh destination.

## 🧠 How the runner works

Reading `migration_runner.py`:

1. Detects the source DB's `schema_version` from the `adk_internal_metadata` table (falls back to `SCHEMA_VERSION_0_PICKLE` if no metadata table exists).
2. Walks the `MIGRATIONS` dict, building a chain from the source version to `LATEST_VERSION`.
3. For each step except the last, writes into a temporary `sqlite:///<tmp>.db` file; the last step writes into `dest_db_url`.
4. Each step's `migrate(source_db_url, dest_db_url)` function reads rows with raw `SELECT * FROM <table>` (via `sqlalchemy.text`), transforms them to the next schema, and merges them into the destination tables created from that version's SQLAlchemy models.
5. Stamps the destination's `adk_internal_metadata` row with the new schema version.
6. Cleans up the temporary files in a `finally` block.

The "multi-hop via temp sqlite" design means a Postgres→Postgres migration that needs two hops uses sqlite as an intermediate format. That is fine for correctness but does mean disk I/O on the box running the migration.

## ❓ Quiz

> ❓ **Ask the student:** you ran dev on `DatabaseSessionService("sqlite:///dev.db")` against ADK 1.x. You upgrade to ADK 2.x and the service starts logging a deprecation warning about schema v0. What do you run?
> *(Expected: `adk migrate session --source_db_url sqlite:///dev.db --dest_db_url sqlite:///dev_v1.db`, then point the service at the new file. Note the underscores in the flag names; this is one of the few ADK CLIs that uses snake_case.)*

> ❓ **Ask the student:** you want to "migrate" sessions from `InMemorySessionService` (dev) into `DatabaseSessionService` (staging). Does `adk migrate session` do this?
> *(Expected: no. `adk migrate session` is a DB schema upgrade tool — both source and destination must be SQLAlchemy URLs. Moving between session backends is not a built-in operation. In-memory sessions are by definition non-persistent; you start fresh in staging or you write your own copy script using the two services' public APIs.)*

> 🛠 **Have the student run:** the programmatic script above twice in a row against the same source DB. The second run should log "already at latest version. No migration needed." and exit cleanly.

> **🚀 In Production**
>
> Always do a full DB **snapshot** before running `upgrade`. The runner writes the destination from scratch, so the source DB is read-only during the run — but the destination is yours, and if anything goes wrong you want to point the service back at the snapshotted source. Keep the source DB around until you've verified at least 24h of clean reads on the destination. Multi-hop migrations write intermediate SQLite files to your system temp dir; make sure `/tmp` has space proportional to your session DB.

---

[← Prev: 04_SessionsState/07_SessionRewind](07_SessionRewind.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/09_OutputKeyShortcut →](09_OutputKeyShortcut.md)
