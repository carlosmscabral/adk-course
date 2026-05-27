---
module: Detours
page: PY_generators
title: Generators — sync, async, and the streaming pattern
estimated_minutes: 25
icon: 🐍
prereqs: [PY_async]
concepts: [yield, generator, async_generator, async_for, yield_from, StopIteration]
---

[← Back to Map](../../MAP.md)

Triggered from: `18_StreamingLive` (`03_TextStreaming`, `05_StreamingTools`).

> Take this detour if `async for event in runner.run_async(...)` works but you can't explain *what produces* each event. The answer is "an async generator". ~25 min. Assumes [[PY_async]].

---

## 🐍 1. Sync generators — `yield` as pause

A function with `yield` is a **generator function**. Calling it doesn't run the body — it returns a generator object you iterate:

```python
>>> def count(n):
...     for i in range(n):
...         yield i
...
>>> g = count(3)
>>> g
<generator object count at 0x...>
>>> next(g)
0
>>> next(g)
1
>>> next(g)
2
>>> next(g)
StopIteration
```

`yield` pauses the function, hands the value back, and saves all local state. The next `next()` resumes where it stopped.

---

## 🐍 2. Memory-friendly streaming

The win: you can produce a billion items without materializing a list.

```python
>>> def lines(path):
...     with open(path) as f:
...         for line in f:
...             yield line.rstrip()
...
>>> sum(1 for _ in lines("huge.log"))   # constant memory
```

Compare to `open(...).readlines()` which loads the whole file. Generators are the Pythonic answer to "stream of values, computed on demand".

---

## 🐍 3. Async generators — `yield` inside `async def`

Combine them and you get the producer side of `async for`:

```python
>>> import asyncio
>>> async def ticks(n, delay=0.1):
...     for i in range(n):
...         await asyncio.sleep(delay)
...         yield i
...
>>> async def main():
...     async for t in ticks(3):
...         print("tick", t)
...
>>> asyncio.run(main())
tick 0
tick 1
tick 2
```

This is exactly the shape of `runner.run_async(...)` — it `awaits` an LLM chunk, `yields` an `Event`, awaits the next chunk, yields again. Each `await` lets the loop run other work.

> ⚠️ Can't use plain `for` on an async generator, and can't use `next()` either. It's `async for` or `await agen.__anext__()`.

---

## 🐍 4. `yield from` — sync delegation

Sync-only sugar for "yield every value from another iterable":

```python
>>> def chain(*iters):
...     for it in iters:
...         yield from it       # equivalent to: for x in it: yield x
...
>>> list(chain([1,2], [3,4], [5]))
[1, 2, 3, 4, 5]
```

`yield from` is also how generator-based coroutines worked before `async def` existed. You'll see it in older code; for new async code, use `async for ... yield ...` or just `await`.

---

## 🐍 5. `return` inside a generator = StopIteration value

A generator's `return value` attaches `value` to the `StopIteration` it raises:

```python
>>> def gen():
...     yield 1
...     yield 2
...     return "done"
...
>>> g = gen()
>>> next(g); next(g)
1
2
>>> try: next(g)
... except StopIteration as e: print("returned:", e.value)
returned: done
```

Rarely useful day-to-day, but ADK sometimes wraps generator-style helpers that return a final summary alongside streamed chunks — knowing this dunder lets you stop being surprised by `StopIteration(value=...)`.

---

## 🛠 Have the student try

An async generator that yields 5 numbers, ~100ms apart, consumed with `async for`:

```python
import asyncio

async def slow_count(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for x in slow_count(5):
        print("got", x)

asyncio.run(main())
```

Then a small twist: collect the values into a list with an async comprehension —

```python
async def main():
    xs = [x async for x in slow_count(5)]
    print(xs)
```

This is how you'd "drain" `runner.run_async` into a list of events when you don't need streaming behavior.

---

Back to: whichever page triggered this — likely `18_StreamingLive/03_TextStreaming` or `18_StreamingLive/05_StreamingTools`.

[← Back to Map](../../MAP.md)
