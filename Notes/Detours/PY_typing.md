---
module: Detours
page: PY_typing
title: Type hints — what ADK reads to build tool schemas
estimated_minutes: 25
icon: 🐍
prereqs: []
concepts: [type_hints, Annotated, Optional, Union, TypedDict, Literal]
---

[← Back to Map](../../MAP.md)

Triggered from: `03_Tools` (FunctionTool schema generation), `14_Evaluation` (eval rubric types).

> Take this detour if "the LLM picked the wrong tool" or "my arg came through as a string" feels random. The fix is almost always a type hint the model can see. ~25 min.

---

## 🐍 1. The primitives

```python
def greet(name: str, times: int = 1) -> str:
    return f"hi {name} " * times
```

Annotations are **stored**, not enforced. Python won't complain if you pass an int to `name`. The point isn't runtime safety — it's so **other tools** (mypy, IDEs, FunctionTool) can introspect:

```python
>>> greet.__annotations__
{'name': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
```

ADK's `FunctionTool` reads exactly this dict (plus the docstring) to build the JSON schema the LLM sees.

---

## 🐍 2. Containers and unions

Modern (3.9+) syntax — use this, not `typing.List`:

```python
def tally(rows: list[dict[str, int]]) -> dict[str, int]: ...
```

Optional / union:

```python
from typing import Optional, Union

def lookup(key: str) -> Optional[str]: ...       # str | None
def parse(x: Union[int, str]) -> int: ...        # old form

# 3.10+ shorthand:
def lookup(key: str) -> str | None: ...
def parse(x: int | str) -> int: ...
```

`X | None` is the same as `Optional[X]`. Use the pipe form in new code.

---

## 🐍 3. `Annotated` — the ADK power move

`Annotated[T, ...metadata...]` attaches arbitrary metadata to a type without changing the type itself. ADK uses the metadata as the **description** the LLM sees:

```python
>>> from typing import Annotated
>>> def search(
...     query: Annotated[str, "the user's search query, verbatim"],
...     top_k: Annotated[int, "max results to return, 1-20"] = 5,
... ) -> list[str]:
...     ...
```

When wrapped as a `FunctionTool`, that string becomes the `description` field in the JSON schema. The model is dramatically better at picking args when each param has a one-sentence description.

> Without `Annotated`, ADK falls back to the docstring's param section. `Annotated` is more precise — and survives docstring rewording.

---

## 🐍 4. `Literal` — enums-as-strings

When a param must be one of a few known strings, `Literal` tells the model exactly what to pick:

```python
>>> from typing import Literal
>>> def convert(value: float, to: Literal["celsius", "fahrenheit", "kelvin"]) -> float:
...     ...
```

The generated JSON schema becomes `"enum": ["celsius", "fahrenheit", "kelvin"]`. The LLM almost never hallucinates outside that set. Much better than `to: str` + a docstring sentence saying "must be one of...".

---

## 🐍 5. `TypedDict` — dict-shaped returns the model understands

If a tool returns a dict, the model doesn't know what keys to expect unless you tell it:

```python
>>> from typing import TypedDict
>>> class Weather(TypedDict):
...     city: str
...     temp_c: float
...     condition: str
...
>>> def get_weather(city: str) -> Weather:
...     return {"city": city, "temp_c": 22.0, "condition": "sunny"}
```

The schema generator picks up `Weather` and tells the LLM "the result has keys `city: str, temp_c: float, condition: str`". The LLM can then reason about each field.

> ⚠️ **Or use Pydantic.** `TypedDict` is the lightweight option; a `BaseModel` gives validation too. See [[PY_pydantic]].

---

## 🛠 Have the student try

Take this untyped function and add hints so a `FunctionTool` wrapper would generate something useful:

```python
def book_flight(origin, destination, date, seats=1, cabin="economy"):
    """Book a flight."""
    ...
```

Aim for something like:

```python
from typing import Annotated, Literal, TypedDict

class Booking(TypedDict):
    confirmation: str
    total_usd: float

def book_flight(
    origin: Annotated[str, "IATA code, e.g. 'JFK'"],
    destination: Annotated[str, "IATA code, e.g. 'CDG'"],
    date: Annotated[str, "ISO date, YYYY-MM-DD"],
    seats: Annotated[int, "number of seats, 1-9"] = 1,
    cabin: Literal["economy", "business", "first"] = "economy",
) -> Booking:
    """Book a flight on the specified date."""
    ...
```

Inspect `book_flight.__annotations__`. Notice every field carries enough info that the LLM can fill it correctly without trial-and-error.

---

Back to: whichever page triggered this — likely `03_Tools/02_FunctionTool`.

[← Back to Map](../../MAP.md)
