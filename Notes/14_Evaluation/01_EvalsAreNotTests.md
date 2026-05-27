---
module: 14_Evaluation
page: 01_EvalsAreNotTests
title: Evals are not tests
estimated_minutes: 15
prereqs: []
concepts: [eval vs test, non-determinism, behavior assertions]
icon: 🧠
in_production: false
detours_suggested: [PY_testing]
---

[← Prev: 14_Evaluation/00_Overview]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/02_EvalCaseEvalSet →]

You are here: 🗺 Runtime Track ▸ 14 Evaluation ▸ 01 Evals are not Tests

# 🧠 Two different verbs

| | Test | Eval |
|--|--|--|
| Verifies | code | *behavior* |
| Outcome | deterministic (true/false) | scored (0.0 – 1.0) |
| Failure means | the function is wrong | the model / prompt / system is off |
| Runs in | milliseconds | seconds-to-minutes per case |
| Cost per run | ~ free | $$ (LLM calls) |
| Fixes by | editing code | editing prompts, swapping models, adjusting tools |
| Tooling | pytest, unittest | `AgentEvaluator`, `adk eval` |

A test asks: "does `multiply(3, 4)` return `12`?" Answer: yes or no.

An eval asks: "does the agent compute and report the product 12 when asked 'what is 3 times 4'?" The answer is a score, because:

- The model might say `12`, `"twelve"`, `"It's 12."`, `"3*4=12, which is twelve."` — all correct.
- The model might call the calculator tool or do it in its head — both correct.
- The model might be slightly wrong in formatting; you decide how strict.

## Both matter

You still want tests:

- Tool functions are code. Test them with pytest. (See `[[PY_testing]]`.)
- Plugin logic is code. Test it.
- Schema validation is code. Test it.

You also want evals:

- Did the agent pick the right tool?
- Did it answer the user's question?
- Did it cite the source it claimed to?
- Did it hallucinate?

## The slogan

> **Test what's deterministic. Eval what isn't.**

If your agent is mostly orchestration glue around well-tested tools, your test:eval ratio is high. If your agent does open-ended reasoning, your eval surface is the bulk of your quality bar.

> ❓ **Ask the student:** "You added a new `summarize(text)` tool. What's a test for it, and what's an eval?" *(Expected: test = the function actually shortens, handles unicode, errors on empty. Eval = the agent picks `summarize` when the user asks for a TL;DR — and the response is faithful and concise.)*

> 🤖 **Tutor:** The student often wants to "just unit test the agent." Push back. Unit tests on stochastic systems are flaky-by-design. Evals are the right tool.

---

[← Prev: 14_Evaluation/00_Overview]  [↑ Map](../../MAP.md)  [Next: 14_Evaluation/02_EvalCaseEvalSet →]
