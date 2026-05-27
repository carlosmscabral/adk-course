---
module: 02_FirstAgent
page: 04_TheGeminiPayload
title: types.Content — the Gemini message shape
estimated_minutes: 15
prereqs: [02_FirstAgent/03]
concepts: [types.Content, types.Part, role, multipart]
icon: 🧠
in_production: false
detours_suggested: [GeminiPayload]
---

[← Prev: 02_FirstAgent/03_RunAsyncIsAGenerator](03_RunAsyncIsAGenerator.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/05_DissectingSample →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 04 The Gemini payload

# 🧠 `types.Content` — the Gemini message shape

You've already used it: `types.Content(role="user", parts=[types.Part(text="say hi")])`. Let's look at it on purpose.

```python
# Work/04_gemini_payload.py — run with: uv run python Work/04_gemini_payload.py
from google.genai import types

msg = types.Content(role="user", parts=[types.Part(text="hello")])
print(msg)
```

```text
Content(role='user', parts=[Part(text='hello')])
```

## 🧠 Why `parts`?

Because a single message can carry **multiple kinds of payload**: text, an inline image, an inline audio clip, a tool call, a tool result, a function-response. Each is a `Part`. Most user messages have one text Part. Multimodal messages might have a text Part + an image Part.

```python
# multimodal example (Module 18 deepens this)
msg = types.Content(
    role="user",
    parts=[
        types.Part(text="describe this photo"),
        types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=b"...")),
    ],
)
```

## 🧠 Roles you'll see

| `role` | Author |
|---|---|
| `"user"` | The human (or upstream caller). |
| `"model"` | The LLM. |
| `"function"` | A tool result, on its way back to the LLM. |

The Runner sets the right role automatically when wrapping tool results. You set `role="user"` on the messages you create from your application code. If you forget `role=`, the Runner sets it to `"user"` for you (see `run_async`'s code), but be explicit anyway.

## 🛠 Pull text from events the same way

Going **out** of the agent, events still wrap their payload as `Content` + `Part`:

```python
async for event in runner.run_async(...):
    if event.is_final_response() and event.content:
        for part in event.content.parts or []:
            if part.text:
                print(part.text)
```

A reply can be multi-part (rare in chat, common in multimodal output) — iterate `parts` if you care about all of them. For Foundation Track, `parts[0].text` is fine.

## ❓ Why does ADK reuse Gemini's types?

> ❓ **Ask the student:** ADK could define its own `Message` class. Why does it use `google.genai.types.Content` directly?
> *(Expected: zero translation between agent code and the Gemini API. The `Content` you pass to ADK is the same shape Gemini's SDK accepts. Reduces bugs, makes streaming straightforward.)*

## 🧭 Detour pointer

If you want a tour of every `Part` variant (inline_data, file_data, function_call, function_response, executable_code, code_execution_result), take detour [[GeminiPayload]] (~20 min). For Foundation Track, text is enough.

> 🛠 **Have the student run:** a tiny script that inspects a `Part`:
> ```python
> # Work/04b_part_probe.py — run with: uv run python Work/04b_part_probe.py
> from google.genai import types
>
> p = types.Part(text="hi")
> print(p.text)              # 'hi'
> print(p.inline_data is None)  # True
> ```
> Then ask: what would `types.Part(text="a", inline_data=...)` mean? *(Answer: it's a single part trying to be two things at once — invalid. One payload per Part.)*

---

[← Prev: 02_FirstAgent/03_RunAsyncIsAGenerator](03_RunAsyncIsAGenerator.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/05_DissectingSample →]
