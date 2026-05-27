---
module: Detours
page: PY_contextvars
title: contextvars — async-safe per-task locals
estimated_minutes: 20
icon: 🐍
prereqs: [PY_async]
concepts: [ContextVar, set, get, async_locals, create_task_snapshot]
---

[← Back to Map](../../MAP.md)

Triggered from: `03_Tools` (`ToolContext` injection), `19_Internals` (how ADK threads per-call state).

> Take this detour if you've wondered "how does each async tool call see *its own* `ToolContext` even though they share an event loop?". The answer is `contextvars`. ~20 min. Assumes [[PY_async]].

---

## 🐍 1. The problem `ContextVar` solves

Threads have `threading.local()` — each thread sees its own value. Async doesn't have threads; it has many coroutines on one thread. So thread-local is useless. `ContextVar` is the async-safe replacement.

```python
>>> from contextvars import ContextVar
>>> request_id: ContextVar[str] = ContextVar("request_id", default="-")
>>> request_id.get()
'-'
>>> request_id.set("req-42")
<Token at 0x...>
>>> request_id.get()
'req-42'
```

`.set()` returns a `Token` you can use to restore the previous value. Most of the time you don't — the runtime resets it for you (see §3).

---

## 🐍 2. Why ADK uses it for `ToolContext`

When a `FunctionTool` runs, ADK needs to give it access to "the current session, the current event stream, the current state — but only mine, not some other concurrent tool call's". A `ContextVar` is set right before the tool runs and read inside it:

```
runner ──┬─→ tool_call_A: ctx.set(ToolContext_A) → tool_A() reads it
         └─→ tool_call_B: ctx.set(ToolContext_B) → tool_B() reads it
              (both happening concurrently on one loop, no collision)
```

Each `await` boundary preserves the calling coroutine's context. You never see this plumbing — but knowing it exists explains why `ToolContext` "just works" inside async tools.

---

## 🐍 3. Setting across an `await`

```python
>>> import asyncio
>>> from contextvars import ContextVar
>>> user: ContextVar[str] = ContextVar("user", default="anon")
>>>
>>> async def inner():
...     print("inside :", user.get())
...
>>> async def outer():
...     user.set("ada")
...     print("before :", user.get())
...     await asyncio.sleep(0)        # yield to loop
...     print("after  :", user.get())
...     await inner()
...
>>> asyncio.run(outer())
before : ada
after  : ada
inside : ada
```

The value survives `await` and propagates into called coroutines. Exactly what you want.

---

## 🐍 4. The `asyncio.create_task` gotcha

When you spawn a task with `asyncio.create_task`, it **snapshots the context at creation time**. Mutating the var afterwards in the parent doesn't reach the child:

```python
>>> async def child():
...     await asyncio.sleep(0.1)
...     print("child sees:", user.get())
...
>>> async def parent():
...     user.set("ada")
...     t = asyncio.create_task(child())   # snapshot taken NOW
...     user.set("bob")                     # too late for child
...     await t
...
>>> asyncio.run(parent())
child sees: ada
```

This is usually what you want (each task gets a frozen view), but it bites when you assume the var is a shared mutable. If you need a child to see updates, pass the value as an argument.

---

## 🐍 5. `Context.run` — explicit isolation

For a one-off "run this callable in a snapshot of the current context", use `copy_context()`:

```python
>>> from contextvars import copy_context
>>> def show(): print("ctx user:", user.get())
>>> user.set("ada")
>>> ctx = copy_context()      # snapshot
>>> user.set("bob")
>>> ctx.run(show)
ctx user: ada                  # snapshot, not "bob"
>>> show()
ctx user: bob
```

ADK uses this pattern internally when fanning out parallel agent calls — each branch gets an isolated context so they can `.set()` independently without stomping each other.

> ⚠️ **In ADK**: don't try to "reach across" tool calls via `ContextVar` to share state. That's what `session.state` is for. `ContextVar` is per-call plumbing; session state is the durable, addressable channel.

---

## 🛠 Have the student try

Ten lines that prove the value survives an `await`:

```python
import asyncio
from contextvars import ContextVar

mode: ContextVar[str] = ContextVar("mode", default="prod")

async def main():
    mode.set("debug")
    print("before sleep:", mode.get())
    await asyncio.sleep(0.1)
    print("after sleep :", mode.get())   # still "debug"

asyncio.run(main())
print("outside run :", mode.get())       # "prod" — the run had its own context
```

Then add `asyncio.create_task(...)` after a `set()` and confirm the §4 gotcha for yourself.

---

Back to: whichever page triggered this — likely `03_Tools/05_ToolContext` or `19_Internals/03_AsyncPlumbing`.

[← Back to Map](../../MAP.md)
