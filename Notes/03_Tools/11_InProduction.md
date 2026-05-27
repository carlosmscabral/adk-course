---
module: 03_Tools
page: 11_InProduction
title: Tools — production checklist
estimated_minutes: 10
prereqs: [03_Tools/10]
concepts: [type-hints, json-serializable, error-events, rate-limit]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 03_Tools/10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/12_KnowledgeCheck →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 11 In Production

# 🚀 Tools — production checklist

Six rules. Each one comes from a real outage somewhere.

## 🚀 1. Type hints are non-negotiable

```python
def fetch(id, user=None):       # ← no
def fetch(id: int, user: str | None = None) -> dict:   # ← yes
```

Without hints, ADK can't generate a meaningful JSON schema. Gemini will either skip the tool or pass garbage. **Every tool argument and the return value gets a type hint.**

## 🚀 2. Return JSON-serializable objects

ADK serializes your return value to JSON before feeding it back to the LLM. Dicts of `str | int | float | bool | None | list | dict` work. Plain Python classes don't (unless you give them a JSON encoder).

```python
return {"temp_c": 19, "city": "Paris"}              # good
return Weather(temp_c=19, city="Paris")             # may fail unless dataclass/pydantic
return datetime.now()                                # bad — datetime isn't JSON-native
return datetime.now().isoformat()                   # good
```

When in doubt, use a `dict` literal or a Pydantic model.

## 🚀 3. Tool exceptions surface as events

If your tool raises, ADK wraps the exception as a tool-error event and feeds it to the LLM (with the exception message). The LLM may retry, may give up, may apologize to the user. **Catch your own foreseeable errors and return informative dicts** rather than letting exceptions leak:

```python
def get_weather(city: str) -> dict:
    """..."""
    try:
        return _api.fetch(city)
    except CityNotFound:
        return {"error": "city_not_found", "city": city}
    except RateLimited as e:
        return {"error": "rate_limited", "retry_after_s": e.retry_after}
```

The LLM is much better at handling structured errors than at handling raw stack traces.

## 🚀 4. Rate-limit YOUR tools, don't trust the LLM

The LLM may helpfully call your tool 50 times in a row trying to refine an answer. If your tool calls a paid API, that's expensive. **Server-side rate-limiting on every tool that touches external systems.** Don't rely on prompt-engineering to make the model polite.

## 🚀 5. Idempotency for state-changing tools

If `create_order(items)` runs twice (model retried, plugin replayed, etc.), you want one order, not two. Pass an idempotency key:

```python
def create_order(items: list[dict], idempotency_key: str) -> dict:
    """Create an order. Pass a unique key per logical order to dedupe retries."""
    ...
```

The LLM happily generates a fresh UUID if you tell it to in the docstring.

## 🚀 6. Validate inputs before side effects

```python
def send_email(to: str, body: str) -> dict:
    """..."""
    if "@" not in to:
        return {"error": "invalid_email", "to": to}
    if len(body) > 100_000:
        return {"error": "body_too_large", "length": len(body)}
    # ...send...
```

The LLM may pass nonsense (especially under prompt-injection). Treat tool inputs the way you'd treat HTTP request bodies — never trusted.

> ❓ **Ask the student:** which rule would have caught the bug *"a customer was charged for the same purchase 4 times because the agent retried after a timeout"*?
> *(Expected: rule 5 — idempotency. Without an idempotency key, retries duplicate the side effect.)*

> 🤖 **Tutor:** these rules are most easily internalized AFTER the student has written one tool. Walk them in detail when grading the mini-drill on the next page.

---

[← Prev: 03_Tools/10_DissectingSample](10_DissectingSample.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/12_KnowledgeCheck →]
