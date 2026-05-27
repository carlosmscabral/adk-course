---
module: 07_Callbacks
page: 02_BeforeAfterModel
title: before/after_model_callback — wrap the LLM call
estimated_minutes: 25
prereqs: [07_Callbacks/01]
concepts: [before_model_callback, after_model_callback, LlmRequest, LlmResponse, CallbackContext]
icon: 🛠
in_production: true
detours_suggested: [PY_async]
---

[← Prev: 07_Callbacks/01_WhyCallbacks](01_WhyCallbacks.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/03_BeforeAfterTool →](03_BeforeAfterTool.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 02 Before/After Model

# 🛠 Wrapping the LLM call

Two hooks bracket every LLM call:

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None: ...

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None: ...
```

Returning `None` lets the pipeline continue. Returning an `LlmResponse` **replaces** what would have happened:

- From `before_model`: skip the LLM call entirely. Useful for caching, refusal, or mocking in tests.
- From `after_model`: rewrite the model's response. Useful for citations, redaction, formatting.

## Example — refuse before calling the model

```python
from google.genai import types

def refuse_offtopic(callback_context, llm_request):
    last_user = llm_request.contents[-1].parts[0].text or ""
    if "stock tip" in last_user.lower():
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="I don't give financial advice.")],
            )
        )
    return None
```

You just saved one LLM call (and an audit incident). The `LlmResponse` you return is emitted as the model's reply; the agent loop continues from there.

## Example — decorate after the model

This is the canonical `llm-auditor` pattern. The `critic_agent` uses `google_search` and the response carries `grounding_metadata`. The callback appends each source URL as a Markdown bullet:

```python
def _render_reference(callback_context, llm_response):
    if not llm_response.content or not llm_response.grounding_metadata:
        return llm_response  # nothing to enrich
    refs = []
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        if chunk.web:
            refs.append(f"* [{chunk.web.title}]({chunk.web.uri})\n")
    if refs:
        llm_response.content.parts.append(
            types.Part(text="\n\nReference:\n\n" + "".join(refs))
        )
    return llm_response
```

(That's a paraphrase. We dissect the real version in `06_DissectingSample.md`.)

## Wiring it up

```python
from google.adk import Agent

agent = Agent(
    model="gemini-2.5-flash",
    name="critic",
    instruction="Verify each claim with the search tool.",
    tools=[google_search],
    before_model_callback=refuse_offtopic,
    after_model_callback=_render_reference,
)
```

Both can be `async def`. Both receive a `CallbackContext` — same one you saw in 04 for state.

> 🛠 **Have the student run:** add a `before_model_callback` that prints `len(llm_request.contents)` and confirm it grows on each tool-loop turn. (This is your cheapest possible tracer.)

> ⚠️ **Gotcha** — mutating `llm_request.contents` in `before_model_callback` is allowed, but it changes the conversation the model sees, not the session history. If you want the session to forget something, you also need to manage events (covered in 04).

> 🚀 **In Production**
>
> `after_model_callback` is the right place for **deterministic post-processing** — citations, watermarks, JSON repair, output schema validation. If your post-processing is itself an LLM call (e.g., "rewrite politely"), reconsider: that's a job for a second `LlmAgent` or a `WorkflowAgent` step so it shows up in traces.

[← Prev: 07_Callbacks/01_WhyCallbacks](01_WhyCallbacks.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/03_BeforeAfterTool →](03_BeforeAfterTool.md)
