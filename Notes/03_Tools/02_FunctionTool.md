---
module: 03_Tools
page: 02_FunctionTool
title: FunctionTool — typed Python function → tool
estimated_minutes: 20
prereqs: [03_Tools/01]
concepts: [FunctionTool, type-hints, agent-tools-kwarg]
icon: 🛠
in_production: true
detours_suggested: [PY_typing]
---

[← Prev: 03_Tools/01_WhyTools](01_WhyTools.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/03_DocstringAsSchema →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 02 FunctionTool

# 🛠 `FunctionTool`

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


agent = LlmAgent(
    name="calc",
    model="gemini-2.5-flash",
    instruction="Use the `add` tool for any addition the user asks for.",
    tools=[FunctionTool(add)],
)
```

That's a complete agent with one tool. Three things happened invisibly:

1. ADK inspected `add`'s **type hints** to build `parameters`.
2. ADK pulled the **docstring** as `description`.
3. The tool's JSON schema was attached to every Gemini call this agent makes.

## 🛠 Bare function shortcut

You can skip `FunctionTool(...)` and pass the bare function — ADK wraps it for you:

```python
tools=[add]                    # same as
tools=[FunctionTool(add)]
```

Both work. Real samples mix the two styles. We'll use the bare-function form throughout the course because it's shorter; `FunctionTool(...)` is for the times you want to override the name or description explicitly.

## 🧠 The four things ADK needs

| Need | From | If missing |
|---|---|---|
| Tool name | Function name | (required — has to be a real `def`) |
| Description (when to call) | First line of docstring | Model can't tell when to call it → never calls it |
| Parameter names + types | Type hints | Model passes garbage args or refuses to call |
| Return shape | Type hint + actual return | ADK JSON-serializes whatever you return |

**Type hints and a docstring are non-negotiable.** Skip them and the model is flying blind.

## 🛠 Multiple tools

```python
def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Return the product of two integers."""
    return a * b


agent = LlmAgent(
    name="calc",
    model="gemini-2.5-flash",
    instruction="Use the tools to do arithmetic. Show your work.",
    tools=[add, multiply],   # list grows
)
```

The model now sees two tools and picks per call. For "what's 3 + 4 * 2?", it might call `multiply(4, 2)` first, then `add(3, 8)`. Or it might do `add(3, 4)` first if it misreads precedence — that's a prompt-engineering problem, not a tool problem.

## ❓ Type hint check

> ❓ **Ask the student:** which signature is better for an LLM tool, and why?
>
> ```python
> def parse(x): ...
> def parse(x: str) -> dict: ...
> def parse(text: str) -> dict[str, str]: ...
> ```
> *(Expected: the third. Type hints tell the model what to pass and what to expect back; descriptive parameter name `text` is more useful in the schema than `x`.)*

> 🛠 **Have the student run:**
> ```python
> >>> from google.adk.tools import FunctionTool
> >>> def add(a: int, b: int) -> int:
> ...     """Return the sum of two integers."""
> ...     return a + b
> >>> tool = FunctionTool(add)
> >>> tool.name
> 'add'
> >>> tool.description
> 'Return the sum of two integers.'
> ```
> They should see ADK has already extracted the schema-relevant bits.

> **🚀 In Production**
>
> `**kwargs` and `*args` don't translate to a JSON schema. Use explicit, typed parameters always. If you genuinely need a flexible payload, type it as `dict[str, Any]` or a Pydantic model — both work; bare `**kwargs` does not.

---

[← Prev: 03_Tools/01_WhyTools](01_WhyTools.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/03_DocstringAsSchema →]
