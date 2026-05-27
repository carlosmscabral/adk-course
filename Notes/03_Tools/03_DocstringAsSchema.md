---
module: 03_Tools
page: 03_DocstringAsSchema
title: The docstring IS the schema description
estimated_minutes: 15
prereqs: [03_Tools/02]
concepts: [docstring, schema-description, when-to-call]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 03_Tools/02_FunctionTool](02_FunctionTool.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/04_ToolContext →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 03 Docstring as schema

# 🧠 The docstring is the schema

The LLM reads your docstring to decide **whether** to call the tool. A vague docstring → the LLM never picks the tool. A precise docstring → the LLM picks it confidently.

## 🧠 The translation

```
{{INCLUDE _figures/tool_schema.txt}}
```

The Args: block is best-practice but optional. The first paragraph of the docstring becomes `description`, which is the single highest-leverage string in the whole agent.

## ⚠️ Anti-example: the never-called tool

```python
def helper(x: str) -> str:
    """Do the thing."""    # ← useless
    return _munge(x)
```

The LLM sees a tool called `helper` whose description says "Do the thing." It has no idea **when** to call it. Result: the tool is never invoked. The agent ignores the user's request or hallucinates an answer.

## ✅ Same function, useful docstring

```python
def helper(x: str) -> str:
    """Normalize a user-supplied product code.

    Strips whitespace, uppercases, and removes hyphens. Use this before
    looking up a product by code so user input matches our DB format.

    Args:
        x: Raw product code as typed by the user.

    Returns:
        Canonical product code (uppercase, no whitespace, no hyphens).
    """
    return _munge(x)
```

Now the LLM knows:
* **What** the function does (normalize a product code).
* **When** to call it (before any product-code lookup).
* **What to pass** (raw user input).
* **What to expect back** (canonical form).

## 🧠 Three examples — inductive

| Docstring | When LLM picks it |
|---|---|
| `"""Get the weather."""` | Maybe, if user mentions weather. Often guesses args. |
| `"""Get the current weather for a city. Returns temp_c and conditions."""` | Reliably picks it for weather questions. |
| `"""Get the current weather for a city. Returns temp_c and conditions. Use this when the user asks about temperature, conditions, or whether to bring an umbrella."""` | Picks it for adjacent questions too ("should I wear a jacket?"). |

The rule: **the docstring is a prompt-within-a-prompt.** Treat it that way.

## ❓ Self-check

> ❓ **Ask the student:** here's a docstring — what's wrong with it for LLM purposes?
> ```python
> def fetch(id: int) -> dict:
>     """Fetches a record."""
> ```
> *(Expected: too vague — "Fetches a record" doesn't say what kind of record, when to use it, what's in the returned dict. The LLM may call it for any "lookup" request, including ones it shouldn't.)*

> 🛠 **Have the student do this:** rewrite the above docstring to be useful for an LLM. They should add: what KIND of record, WHEN to use it, what's in the return value, and (if relevant) what happens on not-found.

> **🚀 In Production**
>
> Docstrings get reviewed as code — but for tools, they need a *prompt-engineering* eye too. Many teams establish a checklist for tool docstrings: (1) one-line summary, (2) when to call, (3) parameter semantics, (4) return shape, (5) failure modes. If a tool keeps getting called wrong, the bug is usually in the docstring, not the model.

---

[← Prev: 03_Tools/02_FunctionTool](02_FunctionTool.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/04_ToolContext →]
