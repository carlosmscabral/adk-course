---
module: Detours
page: PY_pydantic
title: Pydantic v2 — the schema layer ADK speaks
estimated_minutes: 30
icon: 🐍
prereqs: [PY_dataclasses]
concepts: [BaseModel, Field, validation, coercion, model_dump, model_validate]
---

[← Back to Map](../../MAP.md)

Triggered from: `03_Tools` (structured tool returns / configs), `07_Callbacks` (typed payloads), `14_Evaluation` (eval case schemas).

> Take this detour if you've seen `BaseModel` in an ADK sample and wondered why it's there instead of a plain class. ~30 min. Assumes you've read [[PY_dataclasses]].

---

## 🐍 1. Why ADK reaches for Pydantic, not dataclasses

ADK needs to hand the LLM a **JSON schema** for tool args, tool returns, agent configs, and eval cases. Dataclasses don't generate one. Pydantic does, for free:

```python
>>> from pydantic import BaseModel, Field
>>> class WeatherQuery(BaseModel):
...     city: str = Field(..., description="City name, e.g. 'Paris'")
...     units: str = Field("celsius", description="'celsius' or 'fahrenheit'")
...
>>> WeatherQuery.model_json_schema()
{'properties': {'city': {'description': "City name, e.g. 'Paris'", 'title': 'City', 'type': 'string'},
                'units': {'default': 'celsius', 'description': "'celsius' or 'fahrenheit'", ...}},
 'required': ['city'], 'title': 'WeatherQuery', 'type': 'object'}
```

That schema is exactly what `FunctionTool` / `BaseTool` advertises to the model.

---

## 🐍 2. Validation on construction

Unlike dataclasses, types are **enforced**:

```python
>>> class User(BaseModel):
...     name: str
...     age: int
...
>>> User(name="Ada", age=37)
User(name='Ada', age=37)
>>> User(name="Ada", age="thirty-seven")
ValidationError: 1 validation error for User
age
  Input should be a valid integer, ...
```

But notice the **coercion** wrinkle — `"37"` (a numeric string) is accepted by default:

```python
>>> User(name="Ada", age="37")
User(name='Ada', age=37)
```

Pydantic v2 has "lax" (default) and "strict" modes. Lax coerces. If you want `"37"` to fail:

```python
>>> User.model_validate({"name": "Ada", "age": "37"}, strict=True)
ValidationError: ... Input should be a valid integer [type=int_type, input_value='37', ...]
```

> ⚠️ **In ADK**: tool args usually come from the LLM as JSON — lax coercion is your friend (model returns `"5"` for `int`, Pydantic salvages it). For internal contracts, prefer strict.

---

## 🐍 3. `Field(...)` carries metadata

`Field` is to Pydantic what `field` is to dataclasses — but it also holds **description** and **constraints** that surface in the JSON schema:

```python
>>> from pydantic import BaseModel, Field
>>> class CalcArgs(BaseModel):
...     a: float = Field(..., description="left operand")
...     b: float = Field(..., description="right operand")
...     op: str = Field(..., pattern="^[+\\-*/]$", description="one of + - * /")
```

`...` (literally Ellipsis) means "required, no default". The `description` is what the LLM reads when deciding whether to call the tool — write it like a tooltip for a smart-but-impatient user.

---

## 🐍 4. Serialization round-trip

```python
>>> u = User(name="Ada", age=37)
>>> u.model_dump()
{'name': 'Ada', 'age': 37}
>>> u.model_dump_json()
'{"name":"Ada","age":37}'
>>> User.model_validate_json('{"name":"Ada","age":37}')
User(name='Ada', age=37)
```

`model_dump()` → dict. `model_dump_json()` → JSON string. `model_validate()` / `model_validate_json()` are the inverse. ADK uses these constantly when round-tripping tool calls through the model.

> ⚠️ **v1 → v2 rename gotcha**: if you read older blog posts you'll see `.dict()` and `.json()` and `parse_obj()`. Those are deprecated. v2 names: `model_dump`, `model_dump_json`, `model_validate`.

---

## 🐍 5. Dataclass vs BaseModel — when to use which

```
       dataclass                  BaseModel
       ─────────                  ─────────
       internal record            crosses a boundary
       no validation needed       validate untrusted input
       zero deps                  schema for LLM / API / CLI
       speed-critical hot path    LLM-facing tool args
```

Inside ADK: `LlmAgent`, `BaseTool.run_async`'s return types, callback signatures, `EvalCase` — **all** Pydantic models. Your own internal helpers can stay dataclasses.

---

## 🛠 Have the student try

Promote the `AdRequest` from [[PY_dataclasses]] to a Pydantic model and round-trip it:

```python
from pydantic import BaseModel, Field

class AdRequest(BaseModel):
    prompt: str = Field(..., description="user-facing ad copy prompt")
    score: float = Field(0.0, ge=0.0, le=1.0, description="quality score 0-1")
    tags: list[str] = Field(default_factory=list)

req = AdRequest(prompt="summer sale", score="0.7", tags=["urgent"])  # note "0.7"
print(req)                   # coerced to 0.7
print(req.model_dump_json()) # serialize
print(AdRequest.model_validate_json(req.model_dump_json()))  # deserialize
```

Then deliberately break it: `AdRequest(prompt="x", score=2.0)` → ValidationError (constraint `le=1.0`). Notice the error message is structured and self-documenting — that's what makes Pydantic worth the dependency.

---

Back to: whichever page triggered this — likely `03_Tools/03_StructuredIO` or `14_Evaluation/02_EvalCases`.

[← Back to Map](../../MAP.md)
