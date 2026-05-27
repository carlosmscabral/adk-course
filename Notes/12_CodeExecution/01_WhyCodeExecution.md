---
module: 12_CodeExecution
page: 01_WhyCodeExecution
title: Why code execution
estimated_minutes: 15
prereqs: [03_Tools/01]
concepts: [code execution, LLM weakness at arithmetic, generated code]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 12_CodeExecution/00_Overview]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/02_UnsafeLocalCodeExecutor →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 01 Why

# 🧠 The LLM is bad at arithmetic and great at writing Python

Three failures you can elicit at any LLM with no special prep:

```
>>> "What is 437,521 × 928,371?"
406,205,007,491   ← wrong (real answer 406,205,007,491… maybe? hard to tell at a glance)

>>> "Sort these tuples by the second element descending: [...]"
…close, but with a swap or two…

>>> "Plot the first 100 prime numbers."
…makes up a description; no plot.
```

A **tool** would solve the first one if you exposed `multiply(a, b)`. But:

- You can't pre-write a tool for every transformation the user might want.
- The LLM is *better* at *writing* Python that does it than at simulating Python in its head.

That's the value proposition of code execution: **let the model write code, give it a sandbox, let the answer come back as a tool result.**

## Where you use it

- **Arithmetic & math** that exceeds LLM precision (currency conversion, statistical aggregates, geometry).
- **Data wrangling** — "sort this", "dedupe this", "join this CSV with that JSON".
- **Plotting** — generate a chart as a returned image artifact.
- **Quick what-ifs** — the agent writes a 5-line Monte Carlo to answer "what's the chance of X?"

## What it is, mechanically

The LLM emits a special "executable code" part in its response (instead of, or alongside, a text or tool call). The runtime (`code_executor`) extracts that part, runs it in whichever sandbox you wired, captures stdout/stderr/return value, and feeds it back as a tool-result part on the next turn. The model then incorporates the result.

```
   model → executable_code(language="python", code="...")
                  │
                  ▼
   runtime: code_executor.execute(code) → stdout, stderr, return
                  │
                  ▼
   model ← code_execution_result(...)
                  │
                  ▼
   model emits final text answer to user
```

> ⚠️ **Gotcha.** This isn't tool calling. The code is `executable_code` parts, not `function_call` parts. Some debug tooling separates them — know which view you're looking at.

## What it's not

- Not a substitute for proper tools when the operation is well-defined. `multiply(a, b)` is faster, cheaper, and more reliable than a generated 3-line snippet.
- Not a way to "give the agent shell access" — even the unsafe local executor doesn't shell out unless the model writes `subprocess.run(...)`. (Which is exactly why "unsafe" is the right word — see 02.)

> ❓ **Ask the student:** "I want my agent to be able to fetch the current Bitcoin price. Tool or code execution?" *(Expected: tool. Well-defined operation, deterministic, doesn't benefit from being generated.)*

> 🤖 **Tutor:** The student often over-reaches for code execution because "the LLM can just write it." Push back. Tools first; code execution for the long tail of "I couldn't have predicted this transformation."

---

[← Prev: 12_CodeExecution/00_Overview]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/02_UnsafeLocalCodeExecutor →]
