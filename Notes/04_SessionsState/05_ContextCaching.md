---
module: 04_SessionsState
page: 05_ContextCaching
title: Context caching — reuse prefix tokens across turns
estimated_minutes: 20
prereqs: [04_SessionsState/04]
concepts: [ContextCacheConfig, prompt-caching, token-cost, invalidation]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 04_SessionsState/04_WritingStateFromTools](04_WritingStateFromTools.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/06_ContextCompaction →](06_ContextCompaction.md)

You are here: 🗺 Foundation Track ▸ 04 Sessions & State ▸ 05 Context Caching

# 🚀 Context caching (NEW in 2.0)

A long-running agent re-sends the same system instruction, tool schemas, and conversation prefix **on every turn**. That prefix can be 5,000+ tokens — paid for, every turn. ADK 2.0 added first-class prompt caching: tell the runtime "this prefix is stable, cache it" and Gemini will charge the cache rate (typically ~10% of input cost) for repeat hits.

## 🧠 The shape of the config

```python
# Work/05_caching.py — run with: uv run python Work/05_caching.py
from google.adk.agents import LlmAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio


agent = LlmAgent(
    name="cached_helper",
    model="gemini-2.5-flash",
    instruction="You are a careful customer-support assistant. <…long policy…>",
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,        # cache only if prefix exceeds this
        ttl_seconds=300,        # how long the cache lives server-side
        cache_intervals=10,     # re-cache every N turns to absorb history
    ),
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="cache_demo")
    session = await runner.session_service.create_session(
        app_name="cache_demo", user_id="u1",
    )
    for prompt in ("Hi", "What is your return policy?", "And for opened items?"):
        async for event in runner.run_async(
            user_id="u1", session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=prompt)]),
        ):
            if event.is_final_response():
                print(f"> {prompt!r}\n  reply: {event.content.parts[0].text[:60]}…")


asyncio.run(main())
```

```
$ uv run python Work/05_caching.py
> 'Hi'
  reply: Hello! How can I help you today?…
> 'What is your return policy?'
  reply: You can return most items within 30 days…
> 'And for opened items?'
  reply: Opened items are accepted within 14 days…
```

The behavior is identical to the no-cache version. The savings show up on your invoice.

## 🧠 What is actually cached

1. **System instruction** (verbatim).
2. **Tool schemas** (`tools=[…]` declarations).
3. **The growing conversation prefix** — the first `cache_intervals` turns; later turns re-cache.

What is **not** cached: the latest user message and anything after the cache boundary.

## ⚠️ When the cache invalidates

* You change the `instruction=` string (any byte differs).
* You change `tools=[]`.
* You change the model name.
* TTL expires server-side.
* The provider rotates cache infra (rare; treat caching as best-effort).

If `{user:profile}` is templated into the instruction, **every user gets a different prefix** — caching only helps within the same user's session.

## 🛠 Inspecting cache effectiveness

Cache hits surface as `cache_tokens_used` on the event's usage metadata:

```python
if event.usage_metadata and event.usage_metadata.cached_content_token_count:
    print(f"cache hit: {event.usage_metadata.cached_content_token_count} tokens")
```

Plug this into [[15_Observability/00_Overview]] to track your cache hit rate as a production SLI.

## ❓ Quiz

> ❓ **Ask the student:** you template `{user:name}` into your `instruction=`. Two users hit your agent. Do they share a cache entry?
> *(Expected: no. The rendered instruction differs by user, so each user has their own cache entry. Caching helps when the same user sends multiple turns in a window, not across users. To cache across users, keep `{user:*}` OUT of the system instruction and read it from a `before_model_callback` instead.)*

> 🛠 **Have the student run:** the script above with a `print(event.usage_metadata)` line. Note the first turn shows zero cached tokens; turn 2 onward should show non-zero (assuming the prefix exceeds `min_tokens`).

> **🚀 In Production**
>
> Caching is **billed differently per model**. Gemini Flash and Pro publish distinct cache rates; LiteLLM-wrapped models (Module 17) may not support it at all — `ContextCacheConfig` becomes a no-op silently. Always log cache-hit metrics; a silent regression to "no caching" can 10× your bill before you notice.

---

[← Prev: 04_SessionsState/04_WritingStateFromTools](04_WritingStateFromTools.md)  [↑ Map](../../MAP.md)  [Next: 04_SessionsState/06_ContextCompaction →](06_ContextCompaction.md)
