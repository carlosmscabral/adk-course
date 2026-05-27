---
module: Detours
page: PY_async
title: asyncio — async/await, the loop, and run_async
estimated_minutes: 30
icon: 🐍
prereqs: []
concepts: [async, await, event_loop, asyncio.run, gather, async_for]
---

[← Back to Map](../../MAP.md)

Triggered from: `02_FirstAgent` (`runner.run_async`), `18_StreamingLive` (bidi streams).

> Take this detour if `await` and `async for` feel like magic syntax you copy-paste from samples. ~30 min. We won't cover everything — just enough to read ADK code without flinching.

---

## 🐍 1. The mental model — one thread, many waitings

A normal function runs from top to bottom, blocking the thread. An `async def` function returns a **coroutine** — a paused computation. You hand coroutines to an **event loop**, which interleaves them whenever one hits an `await` on something I/O-bound (network, disk, sleep):

```
sync:    [---compute---][---wait HTTP---][---compute---]
async:   [---compute---][await]                          ← loop runs another coro here
         (other coro)              [---compute---]
                        [HTTP done][---compute---]
```

Async wins when you have many concurrent I/O-bound tasks. It does **not** speed up CPU work — for that you want threads or processes.

---

## 🐍 2. `async def`, `await`, and the smallest possible program

```python
>>> import asyncio
>>> async def hello():
...     await asyncio.sleep(0.1)
...     return "hi"
...
>>> hello()
<coroutine object hello at 0x...>          # NOT "hi" — just the coroutine
>>> asyncio.run(hello())
'hi'
```

Three rules:

1. Calling `hello()` does **nothing useful** — you get a coroutine object back. You must `await` it (inside another `async def`) or hand it to a runner.
2. `asyncio.run(coro)` is the top-level entry point. It creates a loop, runs `coro` to completion, closes the loop.
3. `await` is only legal inside `async def`.

---

## 🐍 3. Concurrency with `asyncio.gather`

The whole point of async is running many things at once:

```python
>>> import asyncio, time
>>> async def slow(name, sec):
...     await asyncio.sleep(sec)
...     return f"{name} done"
...
>>> async def main():
...     t = time.time()
...     results = await asyncio.gather(slow("a", 1), slow("b", 1), slow("c", 1))
...     print(results, f"in {time.time()-t:.2f}s")
...
>>> asyncio.run(main())
['a done', 'b done', 'c done'] in 1.00s
```

Three 1-second sleeps in 1 second — they ran concurrently. Sequential `await` (no `gather`) would take 3s.

---

## 🐍 4. `async for` and async iterators

`runner.run_async()` returns an **async iterator** of `Event`s. That means:

```python
async def go():
    async for event in runner.run_async(user_id=..., session_id=..., new_message=...):
        print(event.author, event.content)
```

`async for` is the iteration protocol's async cousin — each `__anext__` is awaitable, so the loop can yield to others between events. We cover the *producer* side in [[PY_generators]].

---

## 🐍 5. Pitfalls (the bugs you will hit)

**A. Forgetting `await`.** Function returns a coroutine, you treat it as the result:

```python
>>> async def get_value(): return 42
>>> async def bad():
...     x = get_value()       # ❌ x is a coroutine, not 42
...     print(x + 1)          # TypeError
```

Python 3.11+ warns: `RuntimeWarning: coroutine 'get_value' was never awaited`. Heed it.

**B. Mixing blocking I/O into async.** `time.sleep(5)` inside an `async def` blocks the **entire** event loop — every other coroutine freezes for 5s. Use `await asyncio.sleep(5)`. Same for `requests.get` → use `httpx.AsyncClient` or `aiohttp`.

**C. `asyncio.run` inside `asyncio.run`.** Once a loop is running you can't start another. From a notebook or a running app, use `await coro` directly (Jupyter has a top-level loop already).

**D. CPU-heavy work blocks too.** `await asyncio.to_thread(heavy_fn, ...)` punts it to a thread pool.

> ⚠️ **In ADK**: an LLM call is I/O-bound (HTTP round-trip to Gemini), which is exactly why `runner.run_async` is async. If you `time.sleep(1)` inside a `FunctionTool`, you'll stall the runner. Use `asyncio.sleep` or make the tool itself `async def`.

---

## 🛠 Have the student try

Two coroutines, concurrent, in two lines that matter:

```python
import asyncio

async def fetch(name, sec):
    await asyncio.sleep(sec)
    return name.upper()

async def main():
    results = await asyncio.gather(fetch("alpha", 0.5), fetch("beta", 0.5))
    print(results)

asyncio.run(main())   # ['ALPHA', 'BETA'] — in ~0.5s, not 1.0s
```

Then break it: replace `await asyncio.sleep(0.5)` with `time.sleep(0.5)` (after `import time`). Notice it now takes ~1.0s — you serialized the work by blocking the loop.

---

Back to: whichever page triggered this — likely `02_FirstAgent/04_RunAsync` or `18_StreamingLive/01_LiveBasics`.

[← Back to Map](../../MAP.md)
