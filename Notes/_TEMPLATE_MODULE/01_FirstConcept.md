---
module: NN_Topic
page: 01_FirstConcept
title: <Concept name — verb-led if hands-on, noun if explanatory>
estimated_minutes: 20
prereqs: [NN_Topic/00]
concepts: [<concept1>, <concept2>]
icon: 🧠
in_production: true
detours_suggested: [<PY_detour_if_relevant>]
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_NextConcept →](02_NextConcept.md)

You are here: 🗺 <Track Name> ▸ NN <Topic> ▸ 01 <Concept>

# 🧠 <Concept>

> 🤖 **Tutor:** open with one sentence of motivation ("why this concept exists"), then drive straight into the runnable script. Do not prose for more than 2 short paragraphs before the first code block. ADK is async-only — a `>>>` REPL is a lie for any agent code; use `# Work/NN_name.py` script style instead.

(One short paragraph — 2–3 sentences max — naming the concept and what it solves.)

## A first taste

```python
# Work/NN_first_taste.py — run with: uv run python Work/NN_first_taste.py
from google.adk.agents import LlmAgent

agent = LlmAgent(name="demo", model="gemini-2.5-flash", instruction="<...>")
print(agent.name)
```

```text
demo
```

> 🛠 **Have the student run:** the script above. Capture the output. If it errors, name the import path mistake (the #1 trip-up) before moving on.

## A second example — the variation

```python
# Work/NN_variation.py — run with: uv run python Work/NN_variation.py
# a small variation that shows the parameter that matters
```

## The rule (now that we've shown 3 examples)

(One declarative sentence that names the rule. Inductive → deductive per pedagogical rule #5.)

> ❓ **Ask the student:** "<one-sentence comprehension check that maps to a KC question>"

## 🚀 In Production

> **🚀 In Production**
>
> (Name the real-world gotcha + the standard mitigation.) For example: *"Forgetting `model=` defaults to `gemini-2.5-flash`, which is fine for dev but in prod you should pin a specific model version — `gemini-2.5-flash-001` — so the student's behavior does not change under you when Google releases a new minor."*

> 🧭 **If the student looks stuck:** suggest detour [[<PY_detour>]] — covers the underlying primitive in 20 min.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_NextConcept →](02_NextConcept.md)
