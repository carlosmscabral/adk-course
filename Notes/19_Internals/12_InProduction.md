---
module: 19_Internals
page: 12_InProduction
title: When to read the source, when not to
estimated_minutes: 15
prereqs: [19_Internals/11]
concepts: [source-vs-docs, version-pinning, contribution]
icon: 🚀
in_production: true
---

[← Prev: 19_Internals/11_TracingOneStateMutation]  [↑ Map](../../MAP.md)  [Next: 19_Internals/13_KnowledgeCheck →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 12 In Production

# 🚀 Source-reading discipline

## When you SHOULD read the source

1. **A behavior contradicts the docs.** Source wins — but file an issue.
2. **A stack trace lands in `adk/...`.** Open the file; identify whether the bug is yours (wrong arg type) or the framework's (genuine defect).
3. **You're extending with a custom `BaseAgent`/`BaseNode`/`BaseTool`/`Plugin`.** Read the contract first — the abstract method signatures are the truth.
4. **You're contributing back.** Always. Find the surrounding code's style and match it.
5. **You're debugging performance.** Profilers point you to functions; you need to know whether a hot path is "fundamental" or "fixable upstream."

## When you SHOULD NOT

1. **As a substitute for docs.** Source is pinned to a version. The `2026-05-27` GA source you read today is the wire layout of `2.0.0`. A patch release tomorrow can rename `_run_async_impl` → `_run_async`. **Pin your reading to your installed version.**
2. **To memorize.** You won't.
3. **To copy private APIs into your code.** Anything underscore-prefixed (`_node_runner.py`, `_workflow.py`, `extract_state_delta`) is private. The maintainers will break it without warning.
4. **To avoid asking.** GitHub Issues, Stack Overflow, and the Discord channel exist. If you're spending more than ~30 min spelunking a single behavior, ask.

## Version-pinning your source read

```bash
# What ADK version are you actually running?
python -c "from google.adk.version import __version__; print(__version__)"

# Check it out at that version for browsing:
cd /home/carloscabral/study/adk-python
git checkout v2.0.0     # or whatever your installed version reports
```

If you wrote a doc against `2.0.0` source and upgrade to `2.1.0`, **re-verify** before publishing.

## Public vs private API — the heuristic

| Visible from | Status |
|---|---|
| `from google.adk import X` | public, stable |
| `from google.adk.<subpackage> import X` | public if listed in `subpackage/__init__.py`'s `__all__` |
| `from google.adk.<sub>._<file> import X` | **private** — do not import |
| Methods starting with `_` | **private** — do not call |

## When extending

- Subclass `BaseAgent` for novel control flow (e.g., loop-with-budget, council-of-models). Override `_run_async_impl`. Yield `Event`s.
- Subclass `BaseTool` for novel tool types (e.g., a tool with custom auth flow). Implement `_get_declaration` and `run_async`.
- Subclass `BasePlugin` for cross-cutting concerns. Module 13 covers it.

The mini-drill at page 14 has you do exactly this for a custom `BaseAgent`.

## Contributing back

The `adk-python` repo has `CONTRIBUTING.md`. The fast path:

1. Open an issue describing the bug/feature.
2. Wait for a maintainer's "yes please."
3. PR with tests.

**Don't** PR a behavior change without an issue first — even small ones can collide with internal plans.

> ⚠️ **Gotcha:** "I'll just monkey-patch this in my project" is **tempting and wrong**. Monkey-patches are invisible to future you. If you must, isolate them in one file labelled `_patches/` so the next maintainer (you in 3 months) can find them.

[← Prev: 19_Internals/11_TracingOneStateMutation]  [↑ Map](../../MAP.md)  [Next: 19_Internals/13_KnowledgeCheck →]
