---
module: 19_Internals
page: 07_ModelRegistry
title: LLMRegistry — model resolution
estimated_minutes: 20
prereqs: [19_Internals/06]
concepts: [LLMRegistry, BaseLlm, lazy-import]
icon: 🧠
in_production: false
---

[← Prev: 19_Internals/06_WorkflowSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/08_AutoFlow →]

You are here: 🗺 Production Track ▸ 19 Internals ▸ 07 Model Registry

# 🧠 LLMRegistry — how `"gemini-2.5-flash"` becomes a class

File: `/home/carloscabral/study/adk-python/src/google/adk/models/registry.py` (182 lines).

## The data structure

```python
_llm_registry_dict: dict[str, Union[type[BaseLlm], _LazyEntry]] = {}
```

A dict from **regex** → either a `BaseLlm` subclass or a lazy `(module_path, class_name)` tuple. Lazy entries avoid importing `anthropic` / `litellm` until the user actually asks for a Claude / OpenAI model.

## The two entry points

```python
LLMRegistry.new_llm(model: str) -> BaseLlm   # build an instance
LLMRegistry.resolve(model: str) -> type[BaseLlm]   # just the class
```

`new_llm` calls `resolve`, then instantiates with the model name.

## `resolve` — line 119

```python
@lru_cache(maxsize=32)
def resolve(model: str) -> type[BaseLlm]:
    # 1. Honor prefix override: "openai:gpt-4" → force the OpenAI class.
    prefix, _ = LLMRegistry._parse_model(model)
    if prefix:
        for regex, entry in _llm_registry_dict.items():
            if _match_prefix(prefix, class_name_of(entry)):
                return load(entry)
    # 2. Regex-match against registered patterns.
    for regex, entry in _llm_registry_dict.items():
        if re.compile(regex).fullmatch(model):
            return load(entry)   # importing module if lazy
    # 3. Raise with a helpful message (e.g., "install anthropic" for claude-*).
    raise ValueError(...)
```

The `@lru_cache(maxsize=32)` matters — `resolve` is called every time `canonical_model` is read, and that's per-invocation per-agent. Caching the class lookup keeps it cheap.

## Registration

Two flavors:

- `LLMRegistry.register(cls)` — for in-package classes; uses `cls.supported_models()` which returns a list of regexes (e.g. `Gemini.supported_models()` returns `["gemini-1.*", "gemini-2.*"]`).
- `LLMRegistry._register_lazy(regexes, module, class_name)` — for optional providers. The class isn't imported until matched.

`models/__init__.py` does the eager registers; lazy entries are added there too (`anthropic_llm.Claude`, `lite_llm.LiteLlm`, etc.).

## Error messages have hints

If you ask for `claude-3-5-sonnet-v2@20241022` and `anthropic` isn't installed, the error tells you to `pip install google-adk[extensions]`. Same for provider-style strings like `groq/llama3` (LiteLLM hint). This is a quality-of-life touch in `resolve` lines 161-181.

> ⚠️ **Gotcha:** the prefix override `"openai:gpt-4"` only works if you've installed the OpenAI extras. Without `litellm` installed, the registry has no `OpenAILlm` to match against.

> 🛠 **Have the student run:** in a REPL, `from google.adk.models.registry import LLMRegistry; LLMRegistry.resolve("gemini-2.5-flash")` — they should see `<class '...Gemini'>`.

> ❓ **Ask the student:** "Why is `resolve` cached but `new_llm` is not?" *(Answer: class resolution is pure — same name always maps to same class. But `new_llm` returns an instance with state, so caching it would share connections / config across callers.)*

[← Prev: 19_Internals/06_WorkflowSource]  [↑ Map](../../MAP.md)  [Next: 19_Internals/08_AutoFlow →]
