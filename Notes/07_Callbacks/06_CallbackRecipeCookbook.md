---
module: 07_Callbacks
page: 06_CallbackRecipeCookbook
title: Real-life callback recipes — caching, rate limiting, PII redaction, citations, budgets, gating
estimated_minutes: 35
prereqs: [07_Callbacks/05]
concepts: [recipes, caching, rate-limit, redaction, citation, budget, conditional-tool-exec]
icon: 🛠
in_production: true
detours_suggested: [PY_logging]
---

[← Prev: 07_Callbacks/05_CallbackContextAnatomy](05_CallbackContextAnatomy.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/07_CallbacksVsPlugins →](07_CallbacksVsPlugins.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 06 Callback recipe cookbook

# 🛠 Seven production recipes

You've seen the hooks. Now see them solving real problems. Each recipe is a runnable snippet — drop in, adapt, ship.

> **All recipes assume these imports** (paste once at the top of your file):
>
> ```python
> from google.adk.models import LlmResponse, LlmRequest
> from google.genai import types
> ```

## Recipe 1 — Response cache (deterministic prompts)

If the same exact prompt is asked twice, skip the LLM call.

```python
# Work/06r1_response_cache.py
import hashlib

def _key(req): return hashlib.sha256(
    (req.contents[-1].parts[0].text or "").encode()).hexdigest()[:16]

def cache_lookup(ctx, llm_request):
    cache = ctx.state.setdefault("app:resp_cache", {})
    hit = cache.get(_key(llm_request))
    if hit:
        return LlmResponse(content=types.Content(
            role="model", parts=[types.Part(text=hit)]))
    return None

def cache_store(ctx, llm_response):
    if llm_response.content and llm_response.content.parts:
        cache = ctx.state.setdefault("app:resp_cache", {})
        cache[ctx.state.get("temp:_last_key", "")] = llm_response.content.parts[0].text
    return llm_response
```

Wire `cache_lookup` to `before_model_callback`, `cache_store` to `after_model_callback`. Same-prompt repeats are free.

## Recipe 2 — Rate limiter (per user)

Cap a noisy user at N calls per minute.

```python
# Work/06r2_rate_limit.py
import time

def per_user_limit(ctx, llm_request):
    window = ctx.state.get("user:rl_window", time.time())
    count = ctx.state.get("user:rl_count", 0)
    if time.time() - window > 60:
        window, count = time.time(), 0
    if count >= 30:
        return LlmResponse(content=types.Content(
            role="model",
            parts=[types.Part(text="Rate limit — try again in a minute.")]))
    ctx.state["user:rl_window"] = window
    ctx.state["user:rl_count"] = count + 1
    return None
```

Wire to `before_model_callback`. The `user:` prefix means the counter is per user across sessions.

## Recipe 3 — PII redaction (output filter)

Strip emails and phones before the user sees the reply.

```python
# Work/06r3_pii_redact.py
import re

_PII = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"\b(\+?\d[\d -]{8,}\d)\b"), "[PHONE]"),
]

def redact_pii(ctx, llm_response):
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for part in llm_response.content.parts:
        if part.text:
            for pat, rep in _PII:
                part.text = pat.sub(rep, part.text)
    return llm_response
```

Wire to `after_model_callback`. Cheap, deterministic, doesn't depend on the LLM cooperating.

## Recipe 4 — Source citation injection

Append a Sources block when the model used `google_search` grounding.

```python
# Work/06r4_citations.py
def inject_citations(ctx, llm_response):
    gm = llm_response.grounding_metadata
    if not (llm_response.content and gm and gm.grounding_chunks):
        return llm_response
    bullets = [
        f"* [{c.web.title}]({c.web.uri})" for c in gm.grounding_chunks if c.web
    ]
    if bullets:
        llm_response.content.parts.append(
            types.Part(text="\n\nSources:\n" + "\n".join(bullets)))
    return llm_response
```

This is the `llm-auditor` `_render_reference` pattern (page 09). Wire to `after_model_callback`.

## Recipe 5 — Latency budget enforcement

Refuse to start another tool round once the wall clock is exhausted.

```python
# Work/06r5_latency_budget.py
import time

def start_budget(ctx):
    ctx.state["temp:budget_start"] = time.time()
    return None

def enforce_budget(tool, args, tool_context):
    start = tool_context.state.get("temp:budget_start", time.time())
    if time.time() - start > 8.0:                # 8s wall clock
        return {"error": "latency_budget_exceeded"}
    return None
```

Wire `start_budget` to `before_agent_callback`, `enforce_budget` to `before_tool_callback`. The agent sees a tool error and can wrap up.

## Recipe 6 — Conditional tool execution (feature flag)

Disable a tool for users without a paid plan.

```python
# Work/06r6_feature_flag.py
PAID_ONLY = {"web_search", "code_exec"}

def feature_gate(tool, args, tool_context):
    if tool.name in PAID_ONLY and not tool_context.state.get("user:is_paid"):
        return {"error": "feature_requires_upgrade", "tool": tool.name}
    return None
```

Wire to `before_tool_callback`. The LLM gets the error dict and can apologize / offer the upgrade path.

## Recipe 7 — Audit log (decorate after_tool)

Emit a structured log for every tool call. Feeds [[15_Observability/00_Overview]].

```python
# Work/06r7_audit.py
import json, time, hashlib

def audit_tool(tool, args, tool_context, tool_response):
    record = {
        "ts": time.time(),
        "invocation_id": tool_context.invocation_id,
        "agent": tool_context.agent_name,
        "tool": tool.name,
        "args_sha": hashlib.sha256(json.dumps(args, sort_keys=True).encode()
            ).hexdigest()[:12],
        "ok": "error" not in (tool_response or {}),
    }
    print(json.dumps(record))   # in prod: ship to your logger
    return tool_response
```

Wire to `after_tool_callback`. Don't print args directly — they may contain PII; hash them.

## 🧠 Stacking recipes

A single agent often wants several of these. Each callback hook on an `LlmAgent` accepts **either a single callable OR a list of callables**. When you pass a list, ADK runs them in order until one returns a non-`None` value — that return short-circuits the chain (and, for `before_model_callback`, replaces the LLM call). See `llm_agent.py:75-87` and the field docstring at lines 391-405 ("Callback or list of callbacks…called in the order they are listed until a callback does not return None").

So you have two equally valid styles:

**Style A — pass a list, let ADK iterate:**

```python
agent = Agent(
    name="cookbook_demo", model="gemini-2.5-flash",
    instruction="Help the user.",
    tools=[google_search],
    before_agent_callback=start_budget,
    before_model_callback=[cache_lookup, per_user_limit],   # run in order
    after_model_callback=[redact_pii, inject_citations],    # run in order
    before_tool_callback=[feature_gate, enforce_budget],
    after_tool_callback=audit_tool,
)
```

**Style B — compose by hand** (still fine; preferred when you need conditional plumbing between steps):

```python
def composed_before_model(ctx, llm_request):
    out = cache_lookup(ctx, llm_request)
    if out is not None:
        return out
    return per_user_limit(ctx, llm_request)

agent = Agent(
    name="cookbook_demo", model="gemini-2.5-flash",
    instruction="Help the user.",
    tools=[google_search],
    before_agent_callback=start_budget,
    before_model_callback=composed_before_model,
    after_model_callback=lambda c, r: inject_citations(c, redact_pii(c, r)),
    before_tool_callback=lambda t, a, c: feature_gate(t, a, c) or enforce_budget(t, a, c),
    after_tool_callback=audit_tool,
)
```

Either way: PII redaction + citations + cache + rate-limit + budget + feature flag + audit, on one agent. Style A is shorter when each step is independent; Style B wins when one step's behavior depends on another's output.

> 🛠 **Have the student do this:** pick TWO recipes (cache + redact is a great pair), wire them onto their Module 02 agent, and confirm both fire by adding `print(...)` markers.

> ⚠️ **Gotcha** — lambda composition of `after_model_callback` reads pretty but errors are hard to trace. In real code, write a named `composed_after_model` function and `logging.exception` around each step.

> **🚀 In Production**
>
> Recipe 1 (cache) is **only safe for deterministic prompts**. The moment your instruction includes `{user:*}` or the current time, the same surface prompt produces different ideal answers — caching becomes wrong. Always include user_id and a version tag in the cache key, or use [[13_Plugins/00_Overview]]'s shared infrastructure.

[← Prev: 07_Callbacks/05_CallbackContextAnatomy](05_CallbackContextAnatomy.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/07_CallbacksVsPlugins →](07_CallbacksVsPlugins.md)
