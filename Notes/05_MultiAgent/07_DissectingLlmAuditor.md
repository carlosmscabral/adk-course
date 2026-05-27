---
module: 05_MultiAgent
page: 07_DissectingLlmAuditor
title: Dissecting the llm-auditor sample
estimated_minutes: 90
prereqs: [05_MultiAgent/06]
concepts: [SequentialAgent, sub_agents, output_key, after_model_callback, google_search]
icon: 🛠
in_production: false
detours_suggested: []
---

[← Prev: 05_MultiAgent/06_SequentialAgent]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/08_DissectingAgentTool →]

You are here: 🗺 Composition Track ▸ 05 Multi-Agent ▸ 07 Dissecting llm-auditor

## 🛠 The artifact

The canonical "critic → reviser" pipeline lives at:

```
adk-samples/python/agents/llm-auditor/
└── llm_auditor/
    ├── __init__.py
    ├── agent.py                          ← root: SequentialAgent
    └── sub_agents/
        ├── critic/
        │   ├── agent.py                  ← LlmAgent + google_search + after_model_callback
        │   └── prompt.py                 ← long instruction
        └── reviser/
            ├── agent.py                  ← LlmAgent + after_model_callback cleanup
            └── prompt.py
```

> 🛠 **Have the student open all five `.py` files in tabs before we start.** Reading-along is the point of this page.

## 📁 File 1 — `llm_auditor/agent.py` (root)

The whole root agent is *seven lines of meaningful code*:

```python
from google.adk.agents import SequentialAgent
from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent

llm_auditor = SequentialAgent(
    name="llm_auditor",
    description=(
        "Evaluates LLM-generated answers, verifies actual accuracy using the"
        " web, and refines the response to ensure alignment with real-world"
        " knowledge."
    ),
    sub_agents=[critic_agent, reviser_agent],
)

root_agent = llm_auditor
```

Observations:

1. The root is a **`SequentialAgent`**, not an `LlmAgent`. No model, no router prompt. Order is hard-coded.
2. `description=` is set anyway — useful when this whole pipeline becomes someone else's sub-agent (composability).
3. `root_agent = llm_auditor` — ADK's `adk run` / `adk web` finds the variable named exactly `root_agent`.

## 📁 File 2 — `sub_agents/critic/agent.py`

```python
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types
from . import prompt

def _render_reference(callback_context, llm_response):
    # Append grounding references (URLs from google_search) to the response text.
    ...

critic_agent = Agent(
    model="gemini-2.5-flash",
    name="critic_agent",
    instruction=prompt.CRITIC_PROMPT,
    tools=[google_search],
    after_model_callback=_render_reference,
)
```

Three things to notice:

1. **`Agent` is an alias for `LlmAgent`** — both imports work, samples use whichever reads cleaner.
2. **`google_search`** is a built-in tool, no wrapper needed. The critic uses it to fact-check.
3. **`after_model_callback=_render_reference`** — runs *after* the LLM responds. It scans `llm_response.grounding_metadata` for the URLs Google Search returned and appends them as a "Reference:" footnote. Without this callback, the user sees the verdict but no sources.

> 🧭 **If the student looks stuck on callbacks:** detour [[07_Callbacks/02_BeforeAfterModel]].

## 📁 File 3 — `sub_agents/critic/prompt.py`

A ~50-line `CRITIC_PROMPT` string. Notable:

- It defines a 3-step process (identify CLAIMS, verify each, overall verdict).
- It explicitly enumerates the verdicts: Accurate / Inaccurate / Disputed / Unsupported / Not Applicable.
- It expects the final output as a Markdown list — this is the *contract* the reviser depends on.

The critic does **not** set `output_key=`. Why? Because the next agent (reviser) reads the conversation history, not a state slot — the critic's final response is the "previous turn" the reviser sees.

> ⚠️ This is a subtle pattern. In other samples (and in our mini-drill) we'll prefer `output_key="criticism"` + `{criticism}` in the reviser's instruction. Both work; the explicit `output_key` is more debuggable.

## 📁 File 4 — `sub_agents/reviser/agent.py`

```python
from google.adk import Agent
from . import prompt

_END_OF_EDIT_MARK = "---END-OF-EDIT---"

def _remove_end_of_edit_mark(callback_context, llm_response):
    # Strip the sentinel marker the LLM appends to signal completion.
    ...

reviser_agent = Agent(
    model="gemini-2.5-flash",
    name="reviser_agent",
    instruction=prompt.REVISER_PROMPT,
    after_model_callback=_remove_end_of_edit_mark,
)
```

Key idea: the reviser's prompt instructs the LLM to end its output with `---END-OF-EDIT---`. The callback strips that sentinel before the user sees the response.

**Why the sentinel?** It's a hack to let the LLM signal "I'm done editing" without changing the streaming contract. Real-world prompt engineering at work.

## 📁 File 5 — `sub_agents/reviser/prompt.py`

The `REVISER_PROMPT` includes two worked examples (one accurate, one inaccurate) — few-shot prompting. The reviser is told to:

- Minimally edit (preserve structure/style/length).
- Never invent new claims.
- Soften unsupported claims, present multiple sides for disputed ones.

## 🧭 Tracing one execution on paper

User question: *"Who invented the lightbulb?"*
Input answer (from some other LLM): *"Thomas Edison invented the lightbulb in 1879. He was the only person ever to work on it."*

```
turn 1: llm_auditor receives input
        │
        ▼
turn 1: SequentialAgent runs critic_agent first
        │
        critic instruction loads
        critic calls google_search("invention of lightbulb history")
        critic gets back grounding chunks
        critic LLM responds with CLAIMS list:
            - "Edison invented the lightbulb in 1879" → Disputed
              (justification: Joseph Swan demoed in 1878; many predecessors)
            - "He was the only person ever to work on it" → Inaccurate
        after_model_callback appends "Reference: [BBC History](...)"
        │
        ▼
turn 1: SequentialAgent runs reviser_agent second
        │
        reviser sees the conversation: original Q+A + critic's findings
        reviser LLM produces:
            "Thomas Edison is widely credited with patenting a commercially
             viable lightbulb in 1879, though Joseph Swan demonstrated a
             working bulb a year earlier in England.---END-OF-EDIT---"
        after_model_callback strips the sentinel
        │
        ▼
user sees revised, balanced answer
```

## 🧠 What state plumbed them together?

Surprisingly **little**. In this sample the critic does not write `output_key`. The handoff is *conversational* — the reviser sees the critic's response as the prior assistant turn. This works because they share a Session and `SequentialAgent` doesn't reset the conversation between children.

**Compare with our mini-drill** (page 11): we'll wire `output_key="criticism"` so the reviser explicitly grabs `{criticism}`. Both styles are valid; the explicit one is easier to debug.

## ❓ Comprehension checks

> ❓ **Ask the student:**
> 1. If you removed `_render_reference`, what would the user lose?
> 2. Why is the root a `SequentialAgent` instead of an `LlmAgent` with `sub_agents=`?
> 3. The critic has `tools=[google_search]`; the reviser has none. Why is that fine?

(Answers in `AGENTS.md`.)

> 🛠 **Have the student run** `adk web` against this sample if they have the repo cloned. Watch the events panel — note the order: critic events first, then reviser events.

---

[← Prev: 05_MultiAgent/06_SequentialAgent]  [↑ Map](../../MAP.md)  [Next: 05_MultiAgent/08_DissectingAgentTool →]
