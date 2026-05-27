---
module: 2A_AgentConfig
page: 06_YamlVsPythonTradeoffs
title: YAML vs Python — an honest comparison
estimated_minutes: 15
prereqs: [2A_AgentConfig/05]
concepts: [tradeoffs, diffability, dynamic-instruction, iteration-speed]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 05_SubAgentReferences](05_SubAgentReferences.md)  [↑ Map](../../MAP.md)  [Next: 07_PythonOnlyFeatures →](07_PythonOnlyFeatures.md)

You are here: 🗺 Foundation Track ▸ 2A Agent Config ▸ 06 YAML vs Python Tradeoffs

# 🧠 YAML vs Python — an honest comparison

You have seen both forms now. This page is the decision matrix. Pin it.

## 🧠 The five dimensions that actually matter

| Dimension | YAML | Python |
|---|---|---|
| **Diffability in PR review** | ✅ Tiny, focused diffs (a 4-line prompt change is a 4-line diff). | ⚠️ Diffs mix prompt edits with code edits; reviewers must mentally filter. |
| **IDE support** | ✅ With `# yaml-language-server: $schema=...`, auto-complete and validation are excellent. | ✅ Full Python tooling (type checkers, jump-to-def, refactor). Better. |
| **Iteration speed (prompt-only changes)** | ✅ Edit YAML, restart. No risk of breaking imports. | ⚠️ Edit Python, restart. One stray paren breaks everything else. |
| **Iteration speed (behavior changes)** | ❌ Adding a callback means dropping back into Python anyway. | ✅ Single file, single language. |
| **CI / GitOps fit** | ✅ Same shape as k8s manifests. Argo / Helm / kustomize patterns transfer directly. | ⚠️ "Diff this Python file" reviews are noisier. |
| **Onboarding non-Python collaborators** | ✅ A prompt engineer can ship a change without touching `def`. | ❌ Non-Python collaborators need translation help. |
| **Expressive power** | ❌ Static strings + dotted-path tool references only. | ✅ Everything — callbacks, dynamic instructions, custom classes, plugins. |

The honest takeaway: **YAML wins on review/iteration ergonomics; Python wins on expressive power.** Most production agents need both — which is why pattern 2 from page 01 (YAML root + Python escape hatches) dominates.

## 🛠 A worked example — the same agent, three ways

Take a tutor agent that needs: a name, instruction, model, two tools, and one `after_model_callback` to log latency.

### Form A — all YAML, callback in a separate Python file referenced via a tool

```yaml
# Cannot inline the callback. You'd have to redesign the callback as a tool the LLM calls.
# This usually distorts the design. SKIP this form.
```

### Form B — YAML root + thin Python wrapper

```yaml
# tutor.yaml
agent_class: LlmAgent
name: tutor
model: gemini-2.5-flash
description: Tutor that explains concepts.
instruction: Explain things clearly and ask Socratic follow-ups.
tools:
  - name: my_tutor.tools.lookup_topic
```

```python
# my_tutor/main.py
from google.adk.agents import config_agent_utils
from google.adk.apps import App

def log_latency(callback_context, llm_response):
    # ...timing logic...
    return None

tutor = config_agent_utils.from_config("tutor.yaml")
tutor.after_model_callback = log_latency        # bolt the callback on after loading

app = App(name="tutor_app", root_agent=tutor)
```

YAML owns the shape. Python owns the callback. Clean.

### Form C — all Python

```python
# my_tutor/agent.py
from google.adk.agents import LlmAgent
from google.adk.apps import App
from my_tutor.tools import lookup_topic

def log_latency(callback_context, llm_response):
    # ...timing logic...
    return None

tutor = LlmAgent(
    name="tutor",
    model="gemini-2.5-flash",
    description="Tutor that explains concepts.",
    instruction="Explain things clearly and ask Socratic follow-ups.",
    tools=[lookup_topic],
    after_model_callback=log_latency,
)

app = App(name="tutor_app", root_agent=tutor)
```

One file. One language. Same agent.

## 🧠 Which one should you ship?

The decision tree, in three questions:

1. **Will a non-Python collaborator review prompt changes?** If yes → YAML (form B).
2. **Will you need ≥3 callbacks or dynamic instructions?** If yes → Python (form C); the YAML round-trip overhead isn't worth it.
3. **Otherwise** → pick by team preference. Both are first-class.

> ❓ **Ask the student:** "Your team has zero non-Python collaborators, the agent has one tool and no callbacks, and you want fast iteration. YAML or Python?"
> *(Expected: Python. The diffability win doesn't apply without non-Python reviewers, and a single Python file is one less file to keep in sync. YAML's win is real but situational — don't pay the cost when you don't get the benefit.)*

## 🧠 The trap to avoid — "YAML for everything because declarative is better"

Declarative is not universally better. Declarative is **better for shape**, **worse for behavior**. The teams that get burned by YAML are the ones who YAMLify behavior — encoding control flow into config, building DSLs on top of YAML to express what one Python `if` statement would have said. Don't do that. When the YAML starts to feel like you're rebuilding Python in a worse language, stop and use Python.

The seam ADK gives you (`agent_class:` + `tools: [{name: ...}]` + `sub_agents: [{config_path: ...}]`) is precisely *shape*. Stay on the right side of the seam.

## 🚀 In Production

> **🚀 In Production**
>
> If you adopt YAML, write a short style guide for the team: "instructions are YAML; callbacks/dynamic logic/custom tools are Python; the boundary is at the `LlmAgent` constructor." A two-paragraph doc prevents the gradual drift toward YAML-encoded behavior. The teams that ship clean ADK YAML projects all have this doc. The ones that don't, end up with 600-line YAMLs full of jinja-templated prompts six months in.

> 🛠 **Have the student do:** look at one of their existing Python agents and ask: "if I rewrote this in YAML form B (YAML + thin Python wrapper), what would I lose?" If the answer is "nothing — the callbacks could move to the wrapper cleanly," form B is a good fit. If the answer is "I'd have to fundamentally redesign," stay in Python.

---

[← Prev: 05_SubAgentReferences](05_SubAgentReferences.md)  [↑ Map](../../MAP.md)  [Next: 07_PythonOnlyFeatures →](07_PythonOnlyFeatures.md)
