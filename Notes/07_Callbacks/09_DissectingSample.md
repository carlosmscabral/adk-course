---
module: 07_Callbacks
page: 09_DissectingSample
title: Dissecting llm-auditor — _render_reference and _remove_end_of_edit_mark
estimated_minutes: 30
prereqs: [07_Callbacks/08]
concepts: [after_model_callback, grounding_metadata, LlmResponse, sample dissection]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 07_Callbacks/08_ErrorCallbacks](08_ErrorCallbacks.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/10_InProduction →](10_InProduction.md)

You are here: 🗺 Integration Track ▸ 07 Callbacks ▸ 09 Dissecting Sample

# 🧠 Reading the canonical sample

We're going to read two files line by line. They live at:

- `/home/carloscabral/study/adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/critic/agent.py`
- `/home/carloscabral/study/adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/reviser/agent.py`

> 🛠 **Have the student run:** open both files in a split. Don't paraphrase. Read the bytes.

## Part 1 — `critic/agent.py`

```python
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types

from . import prompt
```

Three imports map to three concepts you already know: the `Agent`, the `CallbackContext`, the `LlmResponse`. Plus `google_search` (the built-in tool) and `types` (the `genai` Part/Content schema).

```python
def _render_reference(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """Appends grounding references to the response."""
    del callback_context
```

`del callback_context` is the polite "I don't use this arg" — keeps linters quiet without `_callback_context: ...`.

```python
    if (
        not llm_response.content
        or not llm_response.content.parts
        or not llm_response.grounding_metadata
    ):
        return llm_response
```

Three guard clauses. If the model returned no content, no parts, or no grounding (no `google_search` was actually invoked), return the response unchanged. **This is the passthrough idiom returning the response itself rather than `None` — both work for `after_model_callback`; returning the response makes the type explicit.**

```python
    references = []
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title, uri, text = "", "", ""
        if chunk.retrieved_context:
            title = chunk.retrieved_context.title
            uri = chunk.retrieved_context.uri
            text = chunk.retrieved_context.text
        elif chunk.web:
            title = chunk.web.title
            uri = chunk.web.uri
        parts = [s for s in (title, text) if s]
        if uri and parts:
            parts[0] = f"[{parts[0]}]({uri})"
        if parts:
            references.append("* " + ": ".join(parts) + "\n")
```

The grounding metadata distinguishes `retrieved_context` (a stored doc) from `web` (a live URL). The callback handles both. The final `parts[0] = f"[{parts[0]}]({uri})"` is the Markdown link.

```python
    if references:
        reference_text = "".join(["\n\nReference:\n\n", *references])
        llm_response.content.parts.append(types.Part(text=reference_text))
    if all(part.text is not None for part in llm_response.content.parts):
        all_text = "\n".join(part.text for part in llm_response.content.parts)
        llm_response.content.parts[0].text = all_text
        del llm_response.content.parts[1:]
    return llm_response
```

Two final moves: (1) append a new `Part` with the references list; (2) **collapse** all text parts into the first part — keeps the downstream rendering simple (one part = one rendered block).

```python
critic_agent = Agent(
    model="gemini-2.5-flash",
    name="critic_agent",
    instruction=prompt.CRITIC_PROMPT,
    tools=[google_search],
    after_model_callback=_render_reference,
)
```

Wiring. Notice how minimal the agent definition is — the policy lives in the callback, the prompt is just the prose.

## Part 2 — `reviser/agent.py` (the sentinel-stripping idiom)

```python
_END_OF_EDIT_MARK = "---END-OF-EDIT---"

def _remove_end_of_edit_mark(callback_context, llm_response):
    del callback_context
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
    return llm_response
```

Different problem, same idiom. The reviser's instruction tells the LLM to emit a sentinel after its final edit. The callback truncates everything after that sentinel. **This is the prompt-engineering escape hatch:** when you can't trust the LLM to stop, you tell it to mark a stop and you enforce it in code.

> ❓ **Ask the student:** why is this `after_model_callback` rather than a tool? (Answer: there's no external action, just response shaping; tools are for side effects.)

[← Prev: 07_Callbacks/08_ErrorCallbacks](08_ErrorCallbacks.md)  [↑ Map](../../MAP.md)  [Next: 07_Callbacks/10_InProduction →](10_InProduction.md)
