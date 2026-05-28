---
module: Detours
page: GeminiPayload
title: The Gemini payload — Content, Part, Role
estimated_minutes: 25
icon: 🧠
prereqs: []
concepts: [Content, Part, Role, multimodal, function_call, function_response]
---

[← Back to Map](../../MAP.md)

Triggered from: `02_FirstAgent` (first `new_message`), `05_MultiAgent` (passing artifacts between agents), `07_Callbacks` (rewriting model output).

> Take this detour the first time you stare at `Content(role='user', parts=[Part(text=...)])` and think "why so many wrappers?" — or when a tool response disappears into the model and nothing comes back. ~25 min.

---

## 🧠 1. The two-level shape

Everything the model sees or emits is a `Content`. A `Content` has exactly two fields:

```
Content
├── role: str        # 'user' | 'model' | 'tool' (and a few more)
└── parts: list[Part]
```

A `Part` is the atom — text, an image, a function call, a function result. One `Content` can hold many `Part`s, all from the same speaker. So "a turn" is a `Content`; "a chunk inside a turn" is a `Part`.

```python
>>> from google.genai import types
>>> msg = types.Content(role='user', parts=[types.Part(text='hello')])
>>> msg.role
'user'
>>> msg.parts[0].text
'hello'
```

That's the minimum viable payload — and it's what `runner.run_async(new_message=...)` wants.

---

## 🧠 2. Roles — who is speaking

| role         | who                          | parts typically contain        |
|--------------|------------------------------|--------------------------------|
| `'user'`     | the human (or upstream agent)| text, images, audio            |
| `'model'`    | the LLM                      | text, function_call            |
| `'tool'`     | the tool runtime's reply     | function_response              |
| `'system'`   | rarely used — ADK puts the system prompt elsewhere | text |

Two rules that bite beginners:

1. **`role='user'` is mandatory on the first turn.** Omit it and the API rejects the payload with a cryptic error.
2. **Tool results must use `role='tool'` and wrap the response in a `function_response` Part.** ADK does this for you when you use `FunctionTool` — but if you ever hand-roll one, you'll see why.

---

## 🧠 3. Part flavors — text is just one

A `Part` is a union; you set exactly one field:

```python
>>> types.Part(text='plain string')
>>> types.Part(inline_data=types.Blob(mime_type='image/png', data=png_bytes))
>>> types.Part(file_data=types.FileData(mime_type='audio/wav', file_uri='gs://bucket/clip.wav'))
>>> types.Part(function_call=types.FunctionCall(name='get_weather', args={'city': 'NYC'}))
>>> types.Part(function_response=types.FunctionResponse(
...     name='get_weather', response={'temp_c': 22}))
```

Multimodal in one user turn — text plus an image:

```python
import base64
img_bytes = open('chart.png', 'rb').read()

multimodal = types.Content(
    role='user',
    parts=[
        types.Part(text='What does this chart show?'),
        types.Part(inline_data=types.Blob(
            mime_type='image/png',
            data=img_bytes,                      # raw bytes — SDK b64-encodes
        )),
    ],
)
```

`inline_data` is fine for small assets (<20MB). For larger, upload to GCS first and use `file_data` with a `gs://` URI.

---

## 🧠 4. The function-call round trip — what "the LLM picks a tool" actually means

When Module 01 says *"the LLM picks `google_search(...)`"*, what literally happens on the wire is this five-step exchange between the **agent** (your program) and the **LLM** (a stateless token-emitter):

1. **Agent → LLM:** a `Content(role='user')` carrying the user's text.
2. **LLM → Agent:** a `Content(role='model')` whose `parts` contain a `function_call` Part — *not* a function invocation. Just a structured request: *"I'd like you to run `google_search` with these args."*
3. **Agent runs the tool** locally. The LLM never touches your function. It can't — it only emits tokens. The agent reads the `function_call` Part, looks up the matching Python function, calls it, captures the return value.
4. **Agent → LLM:** a `Content(role='tool')` whose parts contain a `function_response` Part carrying the return value.
5. **LLM → Agent:** a `Content(role='model')` with the final text reply, now that it can see the tool result.

Inspect the three `Content`s the *agent assembles* across one user turn with one tool call:

```python
from google.genai import types

# Step 1 — what the agent sends first
user_turn = types.Content(
    role='user',
    parts=[types.Part(text='What is the weather in Tokyo?')],
)

# Step 2 — what the model emits (this is the "tool pick")
model_call = types.Content(
    role='model',
    parts=[types.Part(function_call=types.FunctionCall(
        name='get_weather',
        args={'city': 'Tokyo'},
    ))],
)

# Step 3 — agent runs the Python function LOCALLY:
#     result = get_weather(city='Tokyo')
#     → returns {'temp_c': 14, 'condition': 'overcast'}
# The LLM is not involved in this step. At all.

# Step 4 — agent wraps the return value as a function_response Part
tool_turn = types.Content(
    role='tool',
    parts=[types.Part(function_response=types.FunctionResponse(
        name='get_weather',
        response={'temp_c': 14, 'condition': 'overcast'},
    ))],
)

# Step 5 — agent calls LLM again with the full history:
#     llm([user_turn, model_call, tool_turn])
# The LLM now produces:
#     Content(role='model', parts=[Part(text="It's 14°C and overcast in Tokyo.")])
```

Two things worth burning in:

- **`function_call` is just a structured Part — like text, or an image.** The model "picks" a tool the same way it "picks" a word: by emitting tokens that the SDK decodes into `FunctionCall(name=..., args=...)`. There is no execution on the model side. The "pick" is a request, not an invocation.
- **`role='tool'` exists precisely so the model knows "this `Content` is not the user typing JSON at me — it's a result returned from a tool I requested."** Without that role distinction, the model would treat the response as a weird-looking user message and confuse itself.

**Multi-tool call in one turn:** when the user asks *"weather in Tokyo and Madrid?"* with `[get_weather]`, the sequence is the same shape, just repeated:

```
user_turn  →  model_call(Tokyo)  →  tool_turn(Tokyo)  →
              model_call(Madrid) →  tool_turn(Madrid) →
              model_text("Tokyo is 14°C overcast; Madrid is 22°C clear.")
```

Three LLM calls, two tool round-trips, all orchestrated by the agent. The LLM emits; the agent dispatches.

Cross-ref: this is the wire-level view of [Module 01's agent loop](../01_Foundations/01_WhatIsAnAgent.md). Same loop, just zoomed in to the actual `Content` payloads flowing across the boundary. When you build `Runner` by hand in Module 02, the code that assembles `tool_turn` and re-calls the LLM is what you're writing.

> ⚠️ **This round-trip is for `FunctionTool` (custom Python tools).** Gemini's **built-in** tools — `google_search`, the server-side code executor, URL-context retrieval — don't surface a `function_call` Part for the agent to dispatch. The model invokes them server-side at Google, runs them inside Google's infrastructure, and returns a final text `Content` (with `grounding_metadata` attached when relevant). The agent never sees a `function_response` Part for these; there's nothing for it to wrap. The five-step exchange above is what happens for *your* Python tools. The shorthand "the LLM picks `google_search(...)`" is fine as long as you remember that for built-ins the model and its host do the picking *and* the running — the agent just observes the result come back.

---

## 🧠 5. Cleaning model output — the `llm-auditor` pattern

Real sample (`adk-samples/python/agents/llm-auditor/llm_auditor/sub_agents/reviser/agent.py`):

```python
_END_OF_EDIT_MARK = "---END-OF-EDIT---"

def _remove_end_of_edit_mark(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]      # drop trailing parts
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]   # truncate this one
    return llm_response
```

What's going on:

- The prompt asks the model to emit its revised answer, then `---END-OF-EDIT---`, then optional debug chatter.
- The callback walks `llm_response.content.parts`, finds the marker, truncates that `Part.text` and drops any later `Part`s.
- Notice the in-place mutation — `Part` and `Content` are plain dataclasses, mutate freely.

This is the canonical "model-output scrubber" — same shape works for stripping XML tags, code-fence markers, etc.

---

## 🧠 6. Common bugs

⚠️ **Forgetting `role='user'`.** Default isn't 'user' — it's nothing. You'll see `400 INVALID_ARGUMENT: contents[0].role`.

⚠️ **Mixing roles in one `Content`.** A `Content` is one speaker. If you want user-then-model, that's two `Content`s in the history.

⚠️ **Passing a `Part` where a `Content` is expected.** `runner.run_async(new_message=Part(text='hi'))` looks tidy but errors — wrap it: `Content(role='user', parts=[Part(text='hi')])`.

⚠️ **Tool response without `name`.** `FunctionResponse(response={...})` without `name=` will not associate with the prior `function_call` and the model will re-emit the same call in a loop.

⚠️ **Bytes vs base64.** Pass `inline_data.data` as raw `bytes`. The SDK base64-encodes for transport. Pre-encoding double-encodes and the model sees garbage.

> **🚀 In Production**
>
> Anywhere you mutate `llm_response.content.parts` in a callback, check both `llm_response.content` and `.parts` for `None` first — Gemini sometimes returns an empty `Content` (safety filter, max-tokens cutoff) and `for part in None` will crash the run.

---

## 🛠 Have the student try

Build a multimodal user turn — text plus a small image — and inspect the structure:

```python
from google.genai import types

# A 1x1 transparent PNG (smallest valid image)
PNG_1x1 = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
    '0000000d49444154789c6300010000000500010d0a2db40000000049454e44ae426082'
)

msg = types.Content(
    role='user',
    parts=[
        types.Part(text='Describe this image in one word.'),
        types.Part(inline_data=types.Blob(mime_type='image/png', data=PNG_1x1)),
    ],
)

print(msg.role)                          # 'user'
print(len(msg.parts))                    # 2
print(msg.parts[0].text)                 # 'Describe this image in one word.'
print(msg.parts[1].inline_data.mime_type)  # 'image/png'
print(len(msg.parts[1].inline_data.data))  # 70-ish bytes
```

Then swap the second part for a `Part(file_data=types.FileData(mime_type='image/png', file_uri='gs://my-bucket/x.png'))` and notice the shape — same outer `Content`, different `Part` field.

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — likely `02_FirstAgent/03_FirstRun`, `05_MultiAgent/04_PassingArtifacts`, or `07_Callbacks/03_AfterModel`.
