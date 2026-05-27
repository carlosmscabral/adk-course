---
module: Detours
page: PY_dataclasses
title: Dataclasses — boilerplate-free record types
estimated_minutes: 25
icon: 🐍
prereqs: []
concepts: [dataclass, field, default_factory, frozen, __post_init__]
---

[← Back to Map](../../MAP.md)

Triggered from: `03_Tools` (typed args / structured returns), `09_Skills` (frontmatter records), `11_Memory` (memory records).

> Take this detour if you keep writing `class Foo: def __init__(self, x, y): self.x = x; self.y = y` and feel silly. Dataclasses generate the dunder soup for you. ~25 min.

---

## 🐍 1. The boilerplate it replaces

Before:

```python
>>> class Stock:
...     def __init__(self, name, shares, price):
...         self.name = name
...         self.shares = shares
...         self.price = price
...     def __repr__(self):
...         return f"Stock(name={self.name!r}, shares={self.shares}, price={self.price})"
...     def __eq__(self, other):
...         return (self.name, self.shares, self.price) == (other.name, other.shares, other.price)
```

After:

```python
>>> from dataclasses import dataclass
>>> @dataclass
... class Stock:
...     name: str
...     shares: int
...     price: float
...
>>> Stock("GOOG", 100, 490.1)
Stock(name='GOOG', shares=100, price=490.1)
>>> Stock("GOOG", 100, 490.1) == Stock("GOOG", 100, 490.1)
True
```

`@dataclass` reads the type-annotated class attributes and synthesizes `__init__`, `__repr__`, and `__eq__`. Type hints are **mandatory** — without them the field isn't seen.

---

## 🐍 2. Mutable defaults — `field(default_factory=...)`

The classic Python trap. Don't do this:

```python
>>> @dataclass
... class Cart:
...     items: list = []  # ValueError on class creation
```

Python (and dataclasses) refuse the shared-mutable-default footgun. Use a factory:

```python
>>> from dataclasses import field
>>> @dataclass
... class Cart:
...     items: list[str] = field(default_factory=list)
...
>>> a, b = Cart(), Cart()
>>> a.items.append("apple")
>>> b.items
[]
```

`field()` is also the way to exclude a field from `__init__` or `__repr__` (`field(init=False)`, `field(repr=False)`).

---

## 🐍 3. `frozen=True` — instances are hashable & immutable

```python
>>> @dataclass(frozen=True)
... class Coord:
...     x: int
...     y: int
...
>>> c = Coord(1, 2)
>>> c.x = 99
dataclasses.FrozenInstanceError: cannot assign to field 'x'
>>> {Coord(1,2): "origin-ish"}     # frozen → hashable → dict key OK
{Coord(x=1, y=2): 'origin-ish'}
```

Use frozen for value objects, cache keys, and anything that crosses async boundaries (immutability dodges whole classes of bugs).

---

## 🐍 4. `__post_init__` for validation

`__init__` is auto-generated, so where do you put `if shares < 0: raise ...`? In `__post_init__`, called at the end of `__init__`:

```python
>>> @dataclass
... class Stock:
...     name: str
...     shares: int
...     price: float
...     def __post_init__(self):
...         if self.shares < 0:
...             raise ValueError("shares must be >= 0")
...
>>> Stock("GOOG", -1, 1.0)
ValueError: shares must be >= 0
```

> ⚠️ **Gotcha**: type hints in dataclasses are **not enforced at runtime**. `Stock("GOOG", "one hundred", 1.0)` happily constructs. If you want enforcement, that's Pydantic's job (next detour).

---

## 🐍 5. Dataclass vs Pydantic (preview)

| | `@dataclass` | `pydantic.BaseModel` |
|---|---|---|
| In stdlib | ✅ | ❌ (3rd party) |
| Validates types at runtime | ❌ | ✅ |
| Coerces (`"5"` → `5`) | ❌ | ✅ (lax mode) |
| Generates JSON schema | ❌ | ✅ (ADK uses this) |
| Serialization | manual (`asdict`) | `.model_dump()` / `.model_dump_json()` |
| Overhead | ~0 | small but real |

Rule of thumb in ADK: internal records → dataclass. **Anything the LLM or external system sees → Pydantic** (because ADK wants a JSON schema). See [[PY_pydantic]].

---

## 🛠 Have the student try

Model an `AdRequest` for an ad-generation agent:

```python
from dataclasses import dataclass, field

@dataclass
class AdRequest:
    prompt: str
    score: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be in [0,1]")
```

Then:
1. Construct one with no tags. Confirm `tags == []`.
2. Construct a second one. Append to `tags` on the first. Confirm the second's `tags` is still `[]` (proves `default_factory` is working).
3. Try `AdRequest("hi", score=1.5)` and watch it raise.

---

Back to: whichever page triggered this — likely `03_Tools/02_FunctionTool` (typed args) or `09_Skills/02_Frontmatter`.

[← Back to Map](../../MAP.md)
